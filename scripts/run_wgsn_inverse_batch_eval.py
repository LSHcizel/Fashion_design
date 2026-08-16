#!/usr/bin/env python3
"""
对 WGSN 逆解析目录下的 ``*_text_description.md`` 批量评分（默认走 local-llm / vLLM），
并默认追加 ``workflow_0/2026-06-06`` 下 chapter_01/02 共 8 条 ``look_*.txt`` 描述。

在仓库根目录执行::

    # 全量（WGSN 79 条 + workflow 8 条 = 87 条）
    python scripts/run_wgsn_inverse_batch_eval.py

    # 先试 3 条（仅 WGSN 前 3 条）
    python scripts/run_wgsn_inverse_batch_eval.py --limit 3

    # 不含 workflow 八张描述
    python scripts/run_wgsn_inverse_batch_eval.py --no-workflow-extra

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
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List

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
DEFAULT_WORKFLOW_EXTRA_DIR = REPO_ROOT / "fashion_research_dir/workflow_0/2026-06-06"


@dataclass(frozen=True)
class EvalCandidate:
    path: Path
    stem: str
    source_name: str
    source_kind: str


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


def iter_inverse_candidates(inverse_dir: Path) -> Iterable[EvalCandidate]:
    for path in iter_inverse_md_paths(inverse_dir):
        yield EvalCandidate(
            path=path,
            stem=stem_from_md(path),
            source_name=path.name,
            source_kind="inverse_md",
        )


def iter_workflow_look_candidates(workflow_dir: Path) -> Iterable[EvalCandidate]:
    for chapter_dir in sorted(workflow_dir.glob("chapter_*")):
        if not chapter_dir.is_dir():
            continue
        chapter_name = chapter_dir.name
        for path in sorted(chapter_dir.glob("look_*.txt")):
            if not path.is_file():
                continue
            look_stem = path.stem
            yield EvalCandidate(
                path=path,
                stem=f"{chapter_name}_{look_stem}",
                source_name=f"{chapter_name}/{path.name}",
                source_kind="workflow_txt",
            )


def collect_candidates(
    inverse_dir: Path,
    workflow_extra_dir: Path | None,
    *,
    include_workflow_extra: bool,
) -> List[EvalCandidate]:
    candidates = list(iter_inverse_candidates(inverse_dir))
    if include_workflow_extra and workflow_extra_dir is not None:
        candidates.extend(iter_workflow_look_candidates(workflow_extra_dir))
    return candidates


def candidate_extra_fields(candidate: EvalCandidate) -> dict:
    rel = str(candidate.path.relative_to(REPO_ROOT))
    extra = {
        "source_path": rel,
        "source_kind": candidate.source_kind,
    }
    if candidate.source_kind == "inverse_md":
        extra["inverse_md"] = rel
    else:
        extra["workflow_txt"] = rel
    return extra


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
    p.add_argument(
        "--workflow-extra-dir",
        type=Path,
        default=DEFAULT_WORKFLOW_EXTRA_DIR,
        help=(
            "追加评分的 workflow 目录（默认含 chapter_*/look_*.txt；"
            f"{DEFAULT_WORKFLOW_EXTRA_DIR.relative_to(REPO_ROOT).as_posix()}）"
        ),
    )
    p.add_argument(
        "--no-workflow-extra",
        action="store_true",
        help="不追加 workflow 目录下的 look 描述（默认会追加 8 条）",
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

    include_workflow_extra = not args.no_workflow_extra
    workflow_extra_dir = args.workflow_extra_dir
    if not workflow_extra_dir.is_absolute():
        workflow_extra_dir = REPO_ROOT / workflow_extra_dir
    workflow_extra_dir = workflow_extra_dir.resolve()
    if include_workflow_extra and not workflow_extra_dir.is_dir():
        logger.warning("找不到 workflow 追加目录，将仅评 WGSN：%s", workflow_extra_dir)
        include_workflow_extra = False
        workflow_extra_dir = None

    candidates = collect_candidates(
        inverse_dir,
        workflow_extra_dir if include_workflow_extra else None,
        include_workflow_extra=include_workflow_extra,
    )
    if not candidates:
        raise SystemExit(f"没有可评分的文本：{inverse_dir}")
    if args.limit >= 0:
        candidates = candidates[: max(0, args.limit)]

    workflow_count = sum(1 for c in candidates if c.source_kind == "workflow_txt")
    inverse_count = len(candidates) - workflow_count

    evaluator = build_workflow_text_evaluator()
    logger.info(
        "逆解析目录=%s | workflow追加=%s | 输出=%s | 待评 %d 条（WGSN %d + workflow %d）| judge=%s @ %s",
        inverse_dir,
        workflow_extra_dir if include_workflow_extra else "(disabled)",
        out_dir,
        len(candidates),
        inverse_count,
        workflow_count,
        ep["model"],
        ep["api_base"],
    )

    run_meta = {
        "inverse_dir": str(inverse_dir),
        "workflow_extra_dir": str(workflow_extra_dir) if include_workflow_extra else None,
        "include_workflow_extra": include_workflow_extra,
        "out_dir": str(out_dir),
        "judge_model": ep["model"],
        "judge_api_base": ep["api_base"],
        "started_at_utc": stamp,
        "total_planned": len(candidates),
        "completed": [],
        "skipped": [],
        "failed": [],
    }

    for i, candidate in enumerate(candidates, start=1):
        stem = candidate.stem
        eval_json = out_dir / f"{stem}_evaluation.json"
        if args.skip_if_exists and eval_json.is_file():
            logger.info("[%d/%d] 跳过（已存在）%s", i, len(candidates), stem)
            run_meta["skipped"].append(stem)
            continue

        text = load_text_description(candidate.path)
        if len(text.strip()) < 20:
            logger.warning("[%d/%d] 文本过短，跳过 %s", i, len(candidates), candidate.path.name)
            run_meta["skipped"].append(stem)
            continue

        logger.info("[%d/%d] 评分 %s …", i, len(candidates), candidate.source_name)
        try:
            full = evaluator.evaluate_text(text, source_name=candidate.source_name)
            extra = candidate_extra_fields(candidate)
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
                    "source_name": candidate.source_name,
                    "source_kind": candidate.source_kind,
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
            logger.exception("[%d/%d] 失败 %s: %s", i, len(candidates), candidate.source_name, exc)
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
