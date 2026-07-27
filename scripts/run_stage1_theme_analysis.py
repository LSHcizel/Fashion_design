#!/usr/bin/env python3
"""
临时脚本：仅执行主工作流「阶段1 — 主题分析」。

产出（默认写入新日期目录）：
  - description_key_elements.txt（若 description 非空且模型已提交）
  - theme_analysis.txt

在仓库根目录执行::

    python scripts/run_stage1_theme_analysis.py
    python scripts/run_stage1_theme_analysis.py --workflow-dir fashion_research_dir/workflow_0/2026-06-03
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
    load_config,
    resolve_api_key,
    resolve_config_path,
    resolve_workflow_dir,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="阶段1：主题分析（ThemeAnalysisAgent）")
    p.add_argument("--config", "--yaml-location", dest="config", default="fashion_config.yaml")
    p.add_argument("--workflow-dir", type=str, default=None, help="运行目录；默认在 workflow_{index} 下新建日期子目录")
    p.add_argument("--workflow-index", type=int, default=None, help="覆盖 yaml 中的 workflow-index")
    return p.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    logger = logging.getLogger(__name__)

    cli = parse_args()
    args = load_config(resolve_config_path(cli.config))
    if cli.workflow_index is not None:
        args.workflow_index = cli.workflow_index

    workflow_dir = resolve_workflow_dir(cli.workflow_dir, workflow_index=args.workflow_index, create_if_missing=True)
    api_key = resolve_api_key(args)
    workflow = build_workflow(args, workflow_dir=workflow_dir, api_key=api_key)

    logger.info("阶段1 开始 | workflow_dir=%s", workflow_dir.relative_to(REPO_ROOT))
    t0 = time.time()

    repeat = True
    while repeat:
        repeat = workflow.theme_analysis()

    workflow.phase_status["theme analysis"] = True
    if workflow.save:
        workflow.save_state("theme analysis")

    elapsed = time.time() - t0
    sub_themes = workflow.theme_analyzer.sub_themes or []
    logger.info("阶段1 完成 | 耗时 %.1fs | sub_themes=%s", elapsed, sub_themes)
    logger.info("产物：%s", (workflow_dir / "theme_analysis.txt").relative_to(REPO_ROOT))
    key_file = workflow_dir / "description_key_elements.txt"
    if key_file.is_file():
        logger.info("产物：%s", key_file.relative_to(REPO_ROOT))
    logger.info("阶段2 请执行：python scripts/run_stage2_chapters.py --workflow-dir %s", workflow_dir.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
