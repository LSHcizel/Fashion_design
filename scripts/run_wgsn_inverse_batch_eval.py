#!/usr/bin/env python3
"""
对 WGSN 逆解析目录下的 ``*_text_description.md`` 批量评分（默认走 local-llm / vLLM），
并默认追加 ``workflow_0/2026-06-06`` 下 chapter_01/02 共 8 条 ``look_*.txt`` 描述。

在仓库根目录执行::

    # 全量（WGSN 79 条 + workflow 8 条 = 87 条）
    python scripts/run_wgsn_inverse_batch_eval.py

    # 仅逆解析 md
    python scripts/run_wgsn_inverse_batch_eval.py --sources inverse

    # 仅 workflow look 描述（生成图文本）
    python scripts/run_wgsn_inverse_batch_eval.py --sources workflow

    # 各跑 1 条对比（逆解析 1 + workflow 1）
    python scripts/run_wgsn_inverse_batch_eval.py --sources both --limit-inverse 1 --limit-workflow 1

    # 指定目录与输出
    python scripts/run_wgsn_inverse_batch_eval.py \\
      --inverse-dir fashion_research_dir/wgsn_batch_image_inverse/20260524T044337Z \\
      --out-dir fashion_research_dir/wgsn_batch_image_inverse/20260524T044337Z/eval_local_qwen3b_20260809

    # 兼容旧参数：等价于 --sources inverse
    python scripts/run_wgsn_inverse_batch_eval.py --no-workflow-extra
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
    inverse_dir: Path | None,
    workflow_extra_dir: Path | None,
    *,
    include_inverse: bool,
    include_workflow: bool,
    limit_inverse: int = -1,
    limit_workflow: int = -1,
) -> List[EvalCandidate]:
    candidates: List[EvalCandidate] = []
    if include_inverse:
        if inverse_dir is None:
            raise ValueError("include_inverse 需要 inverse_dir")
        inverse_list = list(iter_inverse_candidates(inverse_dir))
        if limit_inverse >= 0:
            inverse_list = inverse_list[: max(0, limit_inverse)]
        candidates.extend(inverse_list)
    if include_workflow:
        if workflow_extra_dir is None:
            raise ValueError("include_workflow 需要 workflow_extra_dir")
        workflow_list = list(iter_workflow_look_candidates(workflow_extra_dir))
        if limit_workflow >= 0:
            workflow_list = workflow_list[: max(0, limit_workflow)]
        candidates.extend(workflow_list)
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


def resolve_path(path: Path) -> Path:
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path.resolve()


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="WGSN 逆解析 / workflow look 文本批量评分（local-llm）")
    p.add_argument(
        "--sources",
        choices=("inverse", "workflow", "both"),
        default="both",
        help="评分来源：inverse=*_text_description.md；workflow=chapter_*/look_*.txt；both=两者（默认）",
    )
    p.add_argument(
        "--inverse-dir",
        type=Path,
        default=DEFAULT_INVERSE_DIR,
        help=f"逆解析 md 目录（--sources inverse|both 时必需；默认 {DEFAULT_INVERSE_DIR.relative_to(REPO_ROOT).as_posix()}）",
    )
    p.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="评分产物目录；默认在输入目录下 eval_local_<UTC>",
    )
    p.add_argument(
        "--limit",
        type=int,
        default=-1,
        help="合并列表后最多 N 条（-1 全量）；在 --limit-inverse/--limit-workflow 之后生效",
    )
    p.add_argument(
        "--limit-inverse",
        type=int,
        default=-1,
        help="逆解析 md 最多 N 条（-1 全量；仅 --sources inverse|both 时有效）",
    )
    p.add_argument(
        "--limit-workflow",
        type=int,
        default=-1,
        help="workflow look 最多 N 条（-1 全量；仅 --sources workflow|both 时有效）",
    )
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
            "workflow look 目录（--sources workflow|both 时必需；默认 "
            f"{DEFAULT_WORKFLOW_EXTRA_DIR.relative_to(REPO_ROOT).as_posix()}）"
        ),
    )
    p.add_argument(
        "--no-workflow-extra",
        action="store_true",
        help="等价于 --sources inverse（保留兼容）",
    )
    return p.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    logger = logging.getLogger(__name__)
    args = parse_args()

    sources = "inverse" if args.no_workflow_extra else args.sources
    include_inverse = sources in ("inverse", "both")
    include_workflow = sources in ("workflow", "both")

    inverse_dir: Path | None = None
    if include_inverse:
        inverse_dir = resolve_path(args.inverse_dir)
        if not inverse_dir.is_dir():
            raise SystemExit(f"找不到逆解析目录：{inverse_dir}")

    workflow_extra_dir: Path | None = None
    if include_workflow:
        workflow_extra_dir = resolve_path(args.workflow_extra_dir)
        if not workflow_extra_dir.is_dir():
            raise SystemExit(f"找不到 workflow 目录：{workflow_extra_dir}")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = args.out_dir
    if out_dir is None:
        base = inverse_dir if include_inverse else workflow_extra_dir
        out_dir = base / f"eval_local_{stamp}"  # type: ignore[operator]
    else:
        out_dir = resolve_path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    ep = resolve_local_llm_endpoint()
    if not ep:
        raise SystemExit(
            "local-llm 未启用或未配置。请确认 fashion_config.yaml → local-llm.enabled=true "
            "且 vLLM 已在 api-base 地址运行。"
        )

    candidates = collect_candidates(
        inverse_dir,
        workflow_extra_dir,
        include_inverse=include_inverse,
        include_workflow=include_workflow,
        limit_inverse=args.limit_inverse,
        limit_workflow=args.limit_workflow,
    )
    if args.limit >= 0:
        candidates = candidates[: max(0, args.limit)]
    if not candidates:
        raise SystemExit(
            f"没有可评分的文本（sources={sources}，inverse={inverse_dir}，workflow={workflow_extra_dir}）"
        )

    workflow_count = sum(1 for c in candidates if c.source_kind == "workflow_txt")
    inverse_count = len(candidates) - workflow_count

    evaluator = build_workflow_text_evaluator()
    logger.info(
        "sources=%s | 逆解析目录=%s | workflow目录=%s | 输出=%s | 待评 %d 条（inverse %d + workflow %d）| judge=%s @ %s",
        sources,
        inverse_dir if include_inverse else "(disabled)",
        workflow_extra_dir if include_workflow else "(disabled)",
        out_dir,
        len(candidates),
        inverse_count,
        workflow_count,
        ep["model"],
        ep["api_base"],
    )

    run_meta = {
        "sources": sources,
        "inverse_dir": str(inverse_dir) if include_inverse else None,
        "workflow_extra_dir": str(workflow_extra_dir) if include_workflow else None,
        "limit_inverse": args.limit_inverse if include_inverse else None,
        "limit_workflow": args.limit_workflow if include_workflow else None,
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
