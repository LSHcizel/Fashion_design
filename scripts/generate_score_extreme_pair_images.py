"""抽出分数变化最大的对照，用现有 images/generations 接口给原文和改写生图。

逆解析：改写低于原文的组里，取总分下降最多的 10 组。
生成图：改写高于原文的组里，取总分上升最多的 10 组
（这 176 组没有降分，按同样的极端取法取提升最大的）。
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

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

SAMPLES = Path(r"c:\Users\lsh\Desktop\记录10.1\10.2\samples.jsonl")
ORIGINALS = Path(r"c:\Users\lsh\Desktop\记录10.1\original_scores.jsonl")
CORPUS = (
    REPO_ROOT
    / "fashion_research_dir"
    / "k_rewrite_instructions_2026-09-29"
    / "source_corpus.jsonl"
)
OUT_ROOT = Path(r"c:\Users\lsh\Desktop\记录10.1\生图对照")


def _is_original(rec: Dict[str, Any]) -> bool:
    try:
        if int(rec.get("candidate_index", 0)) < 0:
            return True
    except (TypeError, ValueError):
        pass
    return bool((rec.get("parallel_sampling") or {}).get("injected_original"))


def _load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _kind(sample_kind: str) -> str:
    return "inverse" if sample_kind == "inverse" else "generated"


def select_pairs() -> Dict[str, List[Dict[str, Any]]]:
    corpus = {
        r["source_id"]: _kind(str(r.get("sample_kind") or ""))
        for r in _load_jsonl(CORPUS)
    }
    originals = {r["group_id"]: r for r in _load_jsonl(ORIGINALS)}
    groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    with SAMPLES.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if _is_original(rec) or rec.get("S_fp") is None:
                continue
            groups[str(rec.get("group_id") or "")].append(rec)

    buckets: Dict[str, List[Dict[str, Any]]] = {"inverse": [], "generated": []}
    for gid, recs in groups.items():
        if gid not in originals or gid not in corpus:
            continue
        best = max(recs, key=lambda r: float(r["S_fp"]))
        orig = originals[gid]
        orig_s = float(orig["S_fp"])
        best_s = float(best["S_fp"])
        delta = best_s - orig_s
        kind = corpus[gid]
        if kind == "inverse" and delta >= -1e-9:
            continue
        if kind == "generated" and delta <= 1e-9:
            continue
        orig_text = str((orig.get("context") or {}).get("shared_source_text") or orig.get("completion") or "").strip()
        rewrite = str(best.get("completion") or "").strip()
        if not orig_text or not rewrite:
            continue
        buckets[kind].append(
            {
                "group_id": gid,
                "kind": kind,
                "orig_S": round(orig_s, 4),
                "best_S": round(best_s, 4),
                "delta": round(delta, 4),
                "candidate_index": best.get("candidate_index"),
                "orig_gates": orig.get("gates_compact"),
                "best_gates": best.get("gates_compact"),
                "orig_text": orig_text,
                "rewrite_text": rewrite,
            }
        )
    buckets["inverse"].sort(key=lambda r: r["delta"])
    buckets["generated"].sort(key=lambda r: r["delta"], reverse=True)
    return {"inverse": buckets["inverse"][:10], "generated": buckets["generated"][:10]}


def _slug(rank: int, delta: float) -> str:
    sign = "m" if delta < 0 else "p"
    return f"{rank:02d}_{sign}{abs(delta):.3f}"


def _write_case(folder: Path, item: Dict[str, Any], rank: int) -> Path:
    case = folder / _slug(rank, item["delta"])
    case.mkdir(parents=True, exist_ok=True)
    (case / "原文.txt").write_text(item["orig_text"], encoding="utf-8")
    (case / "改写.txt").write_text(item["rewrite_text"], encoding="utf-8")
    meta = {k: v for k, v in item.items() if k not in ("orig_text", "rewrite_text")}
    meta["rank"] = rank
    (case / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return case


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    log = logging.getLogger("pair-images")
    p = argparse.ArgumentParser()
    p.add_argument("--prompts-only", action="store_true")
    p.add_argument("--skip-existing", action="store_true")
    p.add_argument("--model", default="gpt-image-2")
    p.add_argument("--size", default="1024x1024")
    p.add_argument("--quality", default="high")
    p.add_argument("--timeout", type=int, default=360)
    p.add_argument("--retries", type=int, default=2)
    p.add_argument("--pause", type=float, default=3.0)
    args = p.parse_args()

    picked = select_pairs()
    folders = {
        "inverse": OUT_ROOT / "逆解析_降分最多10",
        "generated": OUT_ROOT / "生成图_提分最多10",
    }
    jobs: List[tuple[Path, str, str]] = []
    for kind, rows in picked.items():
        folder = folders[kind]
        folder.mkdir(parents=True, exist_ok=True)
        log.info("%s %s 组", kind, len(rows))
        for rank, item in enumerate(rows, start=1):
            case = _write_case(folder, item, rank)
            log.info(
                "  %s delta=%s orig=%s best=%s",
                case.name,
                item["delta"],
                item["orig_S"],
                item["best_S"],
            )
            jobs.append((case / "原文.png", item["orig_text"], case.name))
            jobs.append((case / "改写.png", item["rewrite_text"], case.name))
    if args.prompts_only:
        return

    api_key, api_base = load_generation_credentials(DEFAULT_CONFIG_PATH, api_key_arg=None, api_base_arg=None)
    failures = OUT_ROOT / "generation_failures.jsonl"
    ok = skipped = failed = 0
    for i, (out_png, prompt, label) in enumerate(jobs, start=1):
        if args.skip_existing and out_png.is_file() and out_png.stat().st_size > 0:
            log.info("[%s/%s] 已有 %s", i, len(jobs), out_png)
            skipped += 1
            continue
        log.info("[%s/%s] %s %s", i, len(jobs), label, out_png.name)
        parsed: Optional[Dict[str, Any]] = None
        last_err = ""
        for attempt in range(1, max(1, args.retries) + 1):
            try:
                parsed = generate_one_image(
                    api_key=api_key,
                    api_base=api_base,
                    prompt=prompt,
                    model=args.model,
                    size=args.size,
                    quality=args.quality,
                    verify_ssl=True,
                    timeout=args.timeout,
                )
                save_response_item(parsed, out_png, download_timeout=args.timeout)
                ok += 1
                last_err = ""
                break
            except Exception as exc:  # noqa: BLE001
                last_err = str(exc)[:2000]
                log.warning("失败 %s 第 %s/%s 次: %s", out_png.name, attempt, args.retries, last_err[:240])
                time.sleep(min(30.0, args.pause * attempt))
        if last_err:
            failed += 1
            with failures.open("a", encoding="utf-8") as f:
                f.write(json.dumps({"path": str(out_png), "error": last_err}, ensure_ascii=False) + "\n")
        elif args.pause:
            time.sleep(args.pause)
    log.info("完成 成功=%s 跳过=%s 失败=%s", ok, skipped, failed)


if __name__ == "__main__":
    main()
