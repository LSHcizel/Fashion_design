#!/usr/bin/env python3
"""从 GRPO samples.jsonl 取出每组负样本改写的最高分，调用 gpt-image-2 生图。

不含注入原文（candidate_index == -1），只在 K 路改写里取 max(R_content)。
生图走 ``scripts/generate_images_from_inverse_descriptions.py`` 的同一套
``POST {api-base}/images/generations`` 接口。
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from generate_images_from_inverse_descriptions import (  # type: ignore
    DEFAULT_CONFIG_PATH,
    generate_one_image,
    load_generation_credentials,
    save_response_item,
)


def _r_content(rec: Dict[str, Any]) -> float:
    v = rec.get("R_content")
    if v is None:
        v = (rec.get("grpo") or {}).get("reward_scalar")
    return float(v) if v is not None else -1.0


def extract_best_negative_rewrites(samples_jsonl: Path) -> List[Dict[str, Any]]:
    groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    with samples_jsonl.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if (rec.get("context") or {}).get("source_role") != "negative":
                continue
            if rec.get("candidate_index") == -1:
                continue
            completion = str(rec.get("completion") or "").strip()
            if not completion:
                continue
            groups[str(rec.get("group_id") or "")].append(rec)

    picked: List[Dict[str, Any]] = []
    for gid in sorted(groups):
        recs = groups[gid]
        best = max(recs, key=_r_content)
        ctx = best.get("context") or {}
        picked.append(
            {
                "group_id": gid,
                "candidate_index": best.get("candidate_index"),
                "R_content": _r_content(best),
                "gates_both_passed": bool((best.get("gates_compact") or {}).get("both_passed")),
                "char_len": best.get("char_len"),
                "source_path": ctx.get("source_path"),
                "n_rewrites_compared": len(recs),
                "prompt": str(best.get("completion") or "").strip(),
            }
        )
    return picked


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="负样本最高分改写 → gpt-image-2")
    p.add_argument(
        "--samples",
        type=Path,
        default=Path(r"c:\Users\lsh\Desktop\grpo_chanel_inverse_v3\samples.jsonl"),
    )
    p.add_argument(
        "--out-dir",
        type=Path,
        default=Path(r"c:\Users\lsh\Desktop\grpo_chanel_inverse_v3\neg_best_rewrite_images"),
    )
    p.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    p.add_argument("--model", default="gpt-image-2")
    p.add_argument("--size", default="1024x1024")
    p.add_argument("--quality", default="high")
    p.add_argument("--timeout", type=int, default=0)
    p.add_argument("--limit", type=int, default=0, help="只跑前 N 张；0=全部")
    p.add_argument("--skip-existing", action="store_true")
    p.add_argument("--continue-on-error", action="store_true")
    p.add_argument("--prompts-only", action="store_true", help="只写出 prompt，不调用生图")
    p.add_argument("--no-verify-ssl", action="store_true")
    return p.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    log = logging.getLogger(__name__)
    args = parse_args()

    samples = args.samples if args.samples.is_absolute() else REPO_ROOT / args.samples
    out_dir = args.out_dir if args.out_dir.is_absolute() else REPO_ROOT / args.out_dir
    if not samples.is_file():
        raise SystemExit(f"找不到 samples：{samples}")

    picked = extract_best_negative_rewrites(samples)
    if args.limit > 0:
        picked = picked[: args.limit]
    if not picked:
        raise SystemExit("没有负样本改写可生图")

    out_dir.mkdir(parents=True, exist_ok=True)
    prompts_path = out_dir / "best_negative_rewrites.jsonl"
    with prompts_path.open("w", encoding="utf-8") as f:
        for rec in picked:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            txt = out_dir / f"{rec['group_id']}.txt"
            txt.write_text(rec["prompt"], encoding="utf-8")
    log.info("已写出 %s 条最高分改写 → %s", len(picked), prompts_path)

    if args.prompts_only:
        return

    api_key, api_base = load_generation_credentials(
        args.config, api_key_arg=None, api_base_arg=None
    )
    manifest_path = out_dir / "generation_manifest.jsonl"
    failures_path = out_dir / "generation_failures.jsonl"
    ok = skipped = failed = 0

    for i, rec in enumerate(picked, start=1):
        gid = rec["group_id"]
        out_png = out_dir / f"{gid}_{args.model}.png"
        if args.skip_existing and out_png.is_file() and out_png.stat().st_size > 0:
            log.info("[%s/%s] 已有 PNG，跳过 %s", i, len(picked), out_png.name)
            skipped += 1
            continue
        log.info(
            "[%s/%s] %s idx=%s R=%.4f → %s",
            i,
            len(picked),
            gid,
            rec["candidate_index"],
            rec["R_content"],
            out_png.name,
        )
        try:
            parsed = generate_one_image(
                api_key=api_key,
                api_base=api_base,
                prompt=rec["prompt"],
                model=args.model,
                size=args.size,
                quality=args.quality,
                verify_ssl=not args.no_verify_ssl,
                timeout=args.timeout,
            )
            save_response_item(parsed, out_png, download_timeout=args.timeout)
        except Exception as exc:  # noqa: BLE001
            failed += 1
            err = str(exc)[:2000]
            log.warning("失败 %s: %s", gid, err[:300])
            with failures_path.open("a", encoding="utf-8") as lf:
                lf.write(
                    json.dumps({"group_id": gid, "error": err}, ensure_ascii=False) + "\n"
                )
            if not args.continue_on_error:
                raise
            continue

        with manifest_path.open("a", encoding="utf-8") as lf:
            lf.write(
                json.dumps(
                    {
                        "group_id": gid,
                        "candidate_index": rec["candidate_index"],
                        "R_content": rec["R_content"],
                        "gates_both_passed": rec["gates_both_passed"],
                        "source_path": rec["source_path"],
                        "output_png": str(out_png),
                        "model": args.model,
                        "prompt_chars": len(rec["prompt"]),
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
        ok += 1

    log.info("统计：成功 %s，跳过 %s，失败 %s；输出 %s", ok, skipped, failed, out_dir)


if __name__ == "__main__":
    main()
