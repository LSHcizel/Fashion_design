#!/usr/bin/env python3
"""
对 WGSN 逆解析目录下的 ``*_text_description.md`` 批量评分（默认走 local-llm / vLLM）。

在仓库根目录执行::

    # 全量（约 79 条，本地 3B 预计数小时）
    python scripts/run_wgsn_inverse_batch_eval.py

    # 先试 3 条
    python scripts/run_wgsn_inverse_batch_eval.py --limit 3

    # 指定目录与输出
    python scripts/run_wgsn_inverse_batch_eval.py \\
      --inverse-dir fashion_research_dir/wgsn_batch_image_inverse/20260524T044337Z \\
      --out-dir fashion_research_dir/wgsn_batch_image_inverse/20260524T044337Z/eval_local_qwen3b_20260809
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from plugins.local_llm import build_workflow_text_evaluator, resolve_local_llm_endpoint  # noqa: E402
from plugins.text_description_evaluator.evaluation_export import (  # noqa: E402
    summarize_evaluation_row,
    write_look_evaluation_artifacts,
)

DEFAULT_INVERSE_DIR = (
    REPO_ROOT / "fashion_research_dir/wgsn_batch_image_inverse/20260524T044337Z"
)


def load_text_description(path: Path) -> str:
    raw = path.read_text(encoding="utf-8").strip()
    if path.suffix.lower() == ".md":
        match = re.search(
            r"^##\s*text_description\s*\n+([\s\S]*?)(?:\n##\s|\Z)",
            raw,
            re.MULTILINE,
        )
        if match:
            return match.group(1).strip()
    return raw


def iter_inverse_md_paths(inverse_dir: Path) -> Iterable[Path]:
    for path in sorted(inverse_dir.glob("*_text_description.md")):
        if path.is_file():
            yield path


def stem_from_md(path: Path) -> str:
    name = path.name
    if name.endswith("_text_description.md"):
        return name[: -len("_text_description.md")]
    return path.stem


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="WGSN 逆解析 text_description 批量评分（local-llm）")
    p.add_argument(
        "--inverse-dir",
        type=Path,
        default=DEFAULT_INVERSE_DIR,
        help=f"逆解析输出目录（默认 {DEFAULT_INVERSE_DIR.relative_to(REPO_ROOT).as_posix()}）",
    )
    p.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="评分产物目录；默认在 inverse-dir 下 eval_local_<UTC>",
    )
    p.add_argument("--limit", type=int, default=-1, help="最多处理 N 条；-1 表示全量")
    p.add_argument(
        "--skip-if-exists",
        action="store_true",
        help="若 {stem}_evaluation.json 已存在则跳过（断点续跑）",
    )
    p.add_argument(
        "--no-markdown",
        action="store_true",
        help="不写逐条 report.md，仅 json + scores.jsonl",
    )
    return p.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    logger = logging.getLogger(__name__)
    args = parse_args()

    inverse_dir = args.inverse_dir
    if not inverse_dir.is_absolute():
        inverse_dir = REPO_ROOT / inverse_dir
    inverse_dir = inverse_dir.resolve()
    if not inverse_dir.is_dir():
        raise SystemExit(f"找不到逆解析目录：{inverse_dir}")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = args.out_dir
    if out_dir is None:
        out_dir = inverse_dir / f"eval_local_{stamp}"
    elif not out_dir.is_absolute():
        out_dir = REPO_ROOT / out_dir
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    ep = resolve_local_llm_endpoint()
    if not ep:
        raise SystemExit(
            "local-llm 未启用或未配置。请确认 fashion_config.yaml → local-llm.enabled=true "
            "且 vLLM 已在 api-base 地址运行。"
        )

    candidates = list(iter_inverse_md_paths(inverse_dir))
    if not candidates:
        raise SystemExit(f"目录内没有 *_text_description.md：{inverse_dir}")
    if args.limit >= 0:
        candidates = candidates[: max(0, args.limit)]

    evaluator = build_workflow_text_evaluator()
    logger.info(
        "逆解析目录=%s | 输出=%s | 待评 %d 条 | judge=%s @ %s",
        inverse_dir,
        out_dir,
        len(candidates),
        ep["model"],
        ep["api_base"],
    )

    run_meta = {
        "inverse_dir": str(inverse_dir),
        "out_dir": str(out_dir),
        "judge_model": ep["model"],
        "judge_api_base": ep["api_base"],
        "started_at_utc": stamp,
        "total_planned": len(candidates),
        "completed": [],
        "skipped": [],
        "failed": [],
    }

    for i, md_path in enumerate(candidates, start=1):
        stem = stem_from_md(md_path)
        eval_json = out_dir / f"{stem}_evaluation.json"
        if args.skip_if_exists and eval_json.is_file():
            logger.info("[%d/%d] 跳过（已存在）%s", i, len(candidates), stem)
            run_meta["skipped"].append(stem)
            continue

        text = load_text_description(md_path)
        if len(text.strip()) < 20:
            logger.warning("[%d/%d] 文本过短，跳过 %s", i, len(candidates), md_path.name)
            run_meta["skipped"].append(stem)
            continue

        logger.info("[%d/%d] 评分 %s …", i, len(candidates), md_path.name)
        try:
            full = evaluator.evaluate_text(text, source_name=md_path.name)
            extra = {"inverse_md": str(md_path.relative_to(REPO_ROOT))}
            if args.no_markdown:
                eval_json.write_text(json.dumps(full, ensure_ascii=False, indent=2), encoding="utf-8")
                summary = summarize_evaluation_row(full, extra=extra)
                with (out_dir / "scores.jsonl").open("a", encoding="utf-8") as jf:
                    jf.write(json.dumps(summary, ensure_ascii=False) + "\n")
            else:
                write_look_evaluation_artifacts(
                    full,
                    out_dir=out_dir,
                    stem=stem,
                    extra_summary=extra,
                )
            run_meta["completed"].append(
                {
                    "stem": stem,
                    "source_name": md_path.name,
                    "total_score": full.get("total_score"),
                    "score_band": full.get("score_band"),
                }
            )
            logger.info(
                "  → S_fp=%s band=%s",
                full.get("total_score"),
                full.get("score_band"),
            )
        except Exception as exc:
            logger.exception("[%d/%d] 失败 %s: %s", i, len(candidates), md_path.name, exc)
            run_meta["failed"].append({"stem": stem, "error": str(exc)})

    run_meta["finished_at_utc"] = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    meta_path = out_dir / "run_meta.json"
    meta_path.write_text(json.dumps(run_meta, ensure_ascii=False, indent=2), encoding="utf-8")

    logger.info(
        "完成：成功 %d，跳过 %d，失败 %d | 摘要 scores.jsonl | 元数据 %s",
        len(run_meta["completed"]),
        len(run_meta["skipped"]),
        len(run_meta["failed"]),
        meta_path,
    )


if __name__ == "__main__":
    main()
