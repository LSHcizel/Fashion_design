#!/usr/bin/env python3
"""
临时脚本：仅执行主工作流「阶段2 — 按子主题逐章生成」。

依赖阶段1 产物：``theme_analysis.txt``（同目录下可选 ``description_key_elements.txt``）。

每章流程：概念头脑风暴 → 设计元素 → Look 描述（含可选 text-evaluator）
→ 单图 reflect（人工确认）→ 章节图片淘汰（人工确认）→ 全部完成后 Collection 反思。

在仓库根目录执行::

    python scripts/run_stage2_chapters.py --workflow-dir fashion_research_dir/workflow_0/2026-06-03
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
for _p in (REPO_ROOT, SCRIPTS_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from _workflow_stage_bootstrap import (  # noqa: E402
    build_workflow,
    hydrate_theme_analysis,
    load_config,
    resolve_api_key,
    resolve_config_path,
    resolve_workflow_dir,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="阶段2：按子主题逐章生成")
    p.add_argument("--config", "--yaml-location", dest="config", default="fashion_config.yaml")
    p.add_argument(
        "--workflow-dir",
        type=str,
        required=True,
        help="阶段1 输出目录（须含 theme_analysis.txt）",
    )
    p.add_argument("--workflow-index", type=int, default=None, help="覆盖 yaml 中的 workflow-index")
    p.add_argument(
        "--skip-collection-reflection",
        action="store_true",
        help="跳过全部 chapter 完成后的 collection reflection",
    )
    p.add_argument("--chapter-from", type=int, default=1, help="起始章节编号（含）")
    p.add_argument("--chapter-to", type=int, default=None, help="结束章节编号（含）；默认处理到最后一章")
    p.add_argument(
        "--skip-image-eval",
        action="store_true",
        help="跳过单图 reflect 与章节图片淘汰（非交互批量生成）",
    )
    return p.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    logger = logging.getLogger(__name__)

    cli = parse_args()
    args = load_config(resolve_config_path(cli.config))
    if cli.workflow_index is not None:
        args.workflow_index = cli.workflow_index

    workflow_dir = resolve_workflow_dir(cli.workflow_dir, workflow_index=args.workflow_index, create_if_missing=False)
    api_key = resolve_api_key(args)
    workflow = build_workflow(args, workflow_dir=workflow_dir, api_key=api_key)
    hydrate_theme_analysis(workflow, workflow_dir)

    sub_themes = workflow.theme_analyzer.sub_themes or []
    logger.info("阶段2 开始 | workflow_dir=%s | sub_themes=%s", workflow_dir.relative_to(REPO_ROOT), sub_themes)
    t0 = time.time()

    workflow.set_model(workflow.phase_models.get("concept brainstorming", args.llm_backend))
    workflow.process_chapters_sequentially(
        chapter_from=cli.chapter_from,
        chapter_to=cli.chapter_to,
        skip_image_eval=cli.skip_image_eval,
        skip_collection_reflection=cli.skip_collection_reflection,
    )

    workflow.phase_status["concept brainstorming"] = True
    if workflow.save:
        workflow.save_state("concept brainstorming")

    elapsed = time.time() - t0
    logger.info("阶段2 完成 | 耗时 %.1fs", elapsed)


if __name__ == "__main__":
    main()
