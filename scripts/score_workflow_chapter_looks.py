#!/usr/bin/env python3
"""
对工作流 chapter 目录下已有 ``look_XX.txt`` 批量 TextEval，并导出覆盖/质量明细文件。

产物目录：``<chapter-dir>/text_eval_scores/``
  - look_01_evaluation.json   完整评测 JSON（含 metric_results）
  - look_01_report.md         覆盖项 / 质量项 / 扣分 Markdown 报告
  - scores.jsonl              各 look 摘要一行

在仓库根目录执行::

    python scripts/score_workflow_chapter_looks.py \\
      --chapter-dir fashion_research_dir/workflow_0/2026-06-06/chapter_01 \\
      --look-from 1 --look-to 4
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from typing import Any, Dict, Optional

import yaml

from plugins.text_description_evaluator import load_default_evaluator  # noqa: E402
from plugins.text_description_evaluator.evaluation_export import (  # noqa: E402
    summarize_evaluation_row,
    write_look_evaluation_artifacts,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="对工作流 look_XX.txt 批量 TextEval 并导出明细")
    p.add_argument("--chapter-dir", type=Path, required=True)
    p.add_argument("--look-from", type=int, default=1)
    p.add_argument("--look-to", type=int, default=4)
    p.add_argument("--config", type=Path, default=REPO_ROOT / "fashion_config.yaml")
    p.add_argument("--fresh", action="store_true", help="清空 text_eval_scores 后重写")
    return p.parse_args()


def load_gate_config_from_fashion(config_path: Path) -> Dict[str, float]:
    cfg: Dict[str, Any] = {}
    if config_path.is_file():
        with config_path.open("r", encoding="utf-8") as fp:
            cfg = yaml.safe_load(fp) or {}
    te = dict(cfg.get("text-evaluator") or {})
    if not te.get("enabled", False):
        raise SystemExit("text-evaluator.enabled 为 false，请在 fashion_config.yaml 中启用")
    return {
        "score_gate_min": float(te.get("score-gate-min", 0.7)),
        "penalty_gate_max": float(te.get("penalty-gate-max", 0.5)),
    }


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    logger = logging.getLogger(__name__)
    cli = parse_args()

    chapter_dir = cli.chapter_dir if cli.chapter_dir.is_absolute() else REPO_ROOT / cli.chapter_dir
    chapter_dir = chapter_dir.resolve()
    if not chapter_dir.is_dir():
        raise SystemExit(f"找不到目录：{chapter_dir}")

    gate_config: Optional[Dict[str, float]] = load_gate_config_from_fashion(cli.config.resolve())
    evaluator = load_default_evaluator()

    out_dir = chapter_dir / "text_eval_scores"
    if cli.fresh and out_dir.is_dir():
        for p in out_dir.glob("*"):
            if p.is_file():
                p.unlink()
    out_dir.mkdir(parents=True, exist_ok=True)

    summaries = []
    for n in range(cli.look_from, cli.look_to + 1):
        look_path = chapter_dir / f"look_{n:02d}.txt"
        if not look_path.is_file():
            logger.warning("跳过：未找到 %s", look_path.name)
            continue
        logger.info("评测 %s ...", look_path.name)
        full = evaluator.evaluate_txt_file(look_path, gate_config=gate_config)
        paths = write_look_evaluation_artifacts(
            full,
            out_dir=out_dir,
            stem=f"look_{n:02d}",
            extra_summary={
                "chapter_dir": str(chapter_dir.relative_to(REPO_ROOT)),
                "look_number": n,
                "source_txt": look_path.name,
            },
        )
        slim = summarize_evaluation_row(
            full,
            extra={"look_number": n, "source_txt": look_path.name},
        )
        summaries.append(slim)
        gates = full.get("gates") or {}
        status = "PASS" if gates.get("both_passed") else "FAIL"
        logger.info(
            "  look_%02d: total=%.3f coverage=%.3f quality=%.3f penalty=%.3f → [%s] | %s",
            n,
            float(full.get("total_score") or 0),
            float((full.get("scores") or {}).get("coverage_score", {}).get("score") or 0),
            float((full.get("scores") or {}).get("quality_score", {}).get("penalized_score") or 0),
            float(
                (full.get("scores") or {})
                .get("quality_score", {})
                .get("penalties", {})
                .get("total_penalty")
                or 0
            ),
            status,
            paths.get("report_md"),
        )

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    summary_path = out_dir / "summary.json"
    summary_path.write_text(
        json.dumps(
            {
                "run_utc": stamp,
                "chapter_dir": str(chapter_dir.relative_to(REPO_ROOT)),
                "processed": len(summaries),
                "looks": summaries,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    logger.info("完成：%s 条 → %s", len(summaries), out_dir.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
