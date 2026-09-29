"""从 consistency_defect_k18_v6 里取出入选改写，调用 gpt-image-2 生图。

入选规则与 plugins/parallel_k_rewrite/select_best.py 一致：
总分严格高于原文，且惩罚严格低于原文；多条同时满足时取总分最高、惩罚更低的一条。
16 没有入选，不会出图。
"""

from __future__ import annotations

import json
import logging
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = REPO_ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from generate_images_from_inverse_descriptions import (  # type: ignore
    DEFAULT_CONFIG_PATH,
    generate_one_image,
    load_generation_credentials,
    save_response_item,
)

HERE = Path(__file__).resolve().parent
SAMPLES = Path(r"c:\Users\lsh\Desktop\consistency_defect_k18_v6\samples.jsonl")
MODEL = "gpt-image-2"
OUT = HERE / "generated_rewrite_v6"


def _s_fp(rec: dict[str, Any]) -> float | None:
    value = rec.get("S_fp")
    if value is None:
        return None
    return float(value)


def _penalty(rec: dict[str, Any]) -> float | None:
    value = (rec.get("scores_compact") or {}).get("total_penalty")
    if value is None:
        return None
    return float(value)


def select_rewrites(samples: Path) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    with samples.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rec = json.loads(line)
                groups[str(rec["group_id"])].append(rec)

    picked: list[dict[str, Any]] = []
    for gid in sorted(groups):
        recs = groups[gid]
        base = next(r for r in recs if r.get("candidate_index") == -1)
        base_score, base_penalty = _s_fp(base), _penalty(base)
        if base_score is None or base_penalty is None:
            continue
        eligible = []
        for rec in recs:
            if rec.get("candidate_index") == -1 or rec.get("error"):
                continue
            score, penalty = _s_fp(rec), _penalty(rec)
            if score is None or penalty is None:
                continue
            if score > base_score and penalty < base_penalty:
                eligible.append(rec)
        if not eligible:
            continue
        best = max(eligible, key=lambda rec: (_s_fp(rec), -(_penalty(rec) or 0.0)))
        prompt = str(best.get("completion") or "").strip()
        if not prompt:
            continue
        picked.append(
            {
                "group_id": gid,
                "candidate_index": best.get("candidate_index"),
                "S_fp": _s_fp(best),
                "total_penalty": _penalty(best),
                "baseline_S_fp": base_score,
                "baseline_penalty": base_penalty,
                "n_eligible": len(eligible),
                "prompt": prompt,
            }
        )
    return picked


def _save_with_download_retry(parsed: dict, out_png: Path, tries: int = 4) -> None:
    last: Exception | None = None
    for attempt in range(1, tries + 1):
        try:
            save_response_item(parsed, out_png, download_timeout=0)
            if out_png.is_file() and out_png.stat().st_size > 10_000:
                return
            raise OSError(f"下载结果过小：{out_png}")
        except Exception as exc:
            last = exc
            logging.getLogger("rewrite_v6_images").warning(
                "下载第 %s/%s 次失败：%s", attempt, tries, str(exc)[:180]
            )
    assert last is not None
    raise last


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    log = logging.getLogger("rewrite_v6_images")
    if not SAMPLES.is_file():
        raise SystemExit(f"找不到采样：{SAMPLES}")
    picked = select_rewrites(SAMPLES)
    if not picked:
        raise SystemExit("没有入选改写")
    OUT.mkdir(parents=True, exist_ok=True)
    prompts_path = OUT / "selected_rewrites.jsonl"
    with prompts_path.open("w", encoding="utf-8") as handle:
        for rec in picked:
            handle.write(json.dumps(rec, ensure_ascii=False) + "\n")
    log.info("入选 %s 条，提示已写入 %s", len(picked), prompts_path)

    api_key, api_base = load_generation_credentials(
        DEFAULT_CONFIG_PATH, api_key_arg=None, api_base_arg=None
    )
    log.info("输出 %s；base=%s", OUT, api_base)
    manifest = OUT / "generation_manifest.jsonl"
    failures = OUT / "generation_failures.jsonl"
    ok = skipped = failed = 0
    for i, rec in enumerate(picked, start=1):
        gid = rec["group_id"]
        out_png = OUT / f"{gid}_{MODEL}.png"
        if out_png.is_file() and out_png.stat().st_size > 10_000:
            log.info("[%s/%s] 已有 PNG，跳过 %s", i, len(picked), out_png.name)
            skipped += 1
            continue
        log.info(
            "[%s/%s] %s idx=%s %.2f/%.2f → %s",
            i,
            len(picked),
            gid,
            rec["candidate_index"],
            rec["S_fp"],
            rec["total_penalty"],
            out_png.name,
        )
        try:
            parsed = None
            last_exc: Exception | None = None
            for attempt in range(1, 4):
                try:
                    parsed = generate_one_image(
                        api_key=api_key,
                        api_base=api_base,
                        prompt=rec["prompt"],
                        model=MODEL,
                        size="1024x1024",
                        quality="high",
                        verify_ssl=True,
                        timeout=0,
                    )
                    _save_with_download_retry(parsed, out_png)
                    last_exc = None
                    break
                except Exception as exc:
                    last_exc = exc
                    message = str(exc)
                    retryable = "IncompleteRead" in type(exc).__name__ or "IncompleteRead" in message
                    retryable = retryable or "连接中断" in message
                    if not retryable:
                        raise
                    log.warning("连接中断，第 %s/3 次重试 %s", attempt, gid)
            if last_exc is not None:
                raise last_exc
        except Exception as exc:
            failed += 1
            log.warning("失败 %s: %s", gid, str(exc)[:400])
            with failures.open("a", encoding="utf-8") as handle:
                handle.write(
                    json.dumps({"group_id": gid, "error": str(exc)[:2000]}, ensure_ascii=False)
                    + "\n"
                )
            continue
        ok += 1
        with manifest.open("a", encoding="utf-8") as handle:
            handle.write(
                json.dumps(
                    {
                        "group_id": gid,
                        "candidate_index": rec["candidate_index"],
                        "S_fp": rec["S_fp"],
                        "total_penalty": rec["total_penalty"],
                        "output_png": out_png.name,
                        "model": MODEL,
                        "prompt_chars": len(rec["prompt"]),
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
        log.info("[%s/%s] 已保存 %s (%s bytes)", i, len(picked), out_png.name, out_png.stat().st_size)
    log.info("统计：成功 %s，跳过已有 %s，失败 %s", ok, skipped, failed)


if __name__ == "__main__":
    main()
