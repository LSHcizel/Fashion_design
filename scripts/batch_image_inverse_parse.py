#!/usr/bin/env python3
"""Batch inverse-parse images under a directory (skip existing outputs).

Example:
  python scripts/batch_image_inverse_parse.py \\
    --image-dir fashion_research_dir/image_inverse/vogue_cn_fw26_batch2 \\
    --out-dir fashion_research_dir/image_inverse/vogue_cn_fw26_batch2/text \\
    --limit 800
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import traceback
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from plugins.image_inverse_parser import ImageInverseParser  # noqa: E402

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Batch image inverse parse")
    p.add_argument("--image-dir", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, default=None)
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--skip-existing", action="store_true", default=True)
    p.add_argument("--no-skip-existing", action="store_true")
    p.add_argument("--model", default="")
    p.add_argument("--api-base", default="", help="覆盖 image inverse API base（如大陆 CDN）")
    p.add_argument("--sleep", type=float, default=0.2)
    p.add_argument("--workers", type=int, default=1, help="并行 worker 数（>1 时分片处理）")
    p.add_argument("--shard-index", type=int, default=0)
    p.add_argument("--shard-count", type=int, default=1)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    image_dir = args.image_dir if args.image_dir.is_absolute() else REPO_ROOT / args.image_dir
    out_dir = args.out_dir
    if out_dir is None:
        out_dir = image_dir / "text"
    if not out_dir.is_absolute():
        out_dir = REPO_ROOT / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    skip = args.skip_existing and not args.no_skip_existing
    images = sorted(
        p for p in image_dir.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_SUFFIXES
    )
    if args.shard_count > 1:
        images = [p for i, p in enumerate(images) if i % args.shard_count == args.shard_index]
    if args.limit and args.limit > 0:
        images = images[: args.limit]

    overrides = {"output_dir": out_dir}
    if args.model.strip():
        overrides["model"] = args.model.strip()
    if args.api_base.strip():
        overrides["api_base"] = args.api_base.strip()
    parser = ImageInverseParser(**overrides)

    log_path = out_dir / "batch_parse_log.jsonl"
    ok = 0
    skipped = 0
    failed = 0
    t0 = time.time()

    with log_path.open("a", encoding="utf-8") as logf:
        for i, image_path in enumerate(images, 1):
            stem = image_path.stem
            md_path = out_dir / f"{stem}_text_description.md"
            if skip and md_path.exists() and md_path.stat().st_size > 50:
                skipped += 1
                print(f"[{i}/{len(images)}] skip existing {md_path.name}", flush=True)
                continue
            row = {"image": str(image_path), "ok": False}
            try:
                result = parser.parse_image(image_path)
                output_path = parser.write_text_description_document(result)
                row.update({"ok": True, "output": str(output_path)})
                ok += 1
                print(
                    f"[{i}/{len(images)}] OK {image_path.name} -> {Path(output_path).name}",
                    flush=True,
                )
            except Exception as exc:  # noqa: BLE001
                failed += 1
                row["error"] = f"{type(exc).__name__}: {exc}"
                row["traceback"] = traceback.format_exc(limit=5)
                print(f"[{i}/{len(images)}] FAIL {image_path.name}: {exc}", flush=True)
            logf.write(json.dumps(row, ensure_ascii=False) + "\n")
            logf.flush()
            time.sleep(args.sleep)

    summary = {
        "image_dir": str(image_dir),
        "out_dir": str(out_dir),
        "total": len(images),
        "ok": ok,
        "skipped": skipped,
        "failed": failed,
        "elapsed_sec": round(time.time() - t0, 1),
    }
    (out_dir / "batch_parse_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
