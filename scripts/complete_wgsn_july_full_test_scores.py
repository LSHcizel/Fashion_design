#!/usr/bin/env python3
"""补齐 WGSN 逆解析 text_description 评分（跳过已有 *_evaluation.json），并更新 summary。"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.run_v020_comparison_eval import (  # noqa: E402
    WGSN_DIR,
    extract_text_description_block,
    load_gate_config,
    md_index,
    module_score,
    write_artifacts,
)
from plugins.text_description_evaluator import load_default_evaluator  # noqa: E402
from plugins.text_description_evaluator.evaluation_export import summarize_evaluation_row  # noqa: E402

OUT_DIR = WGSN_DIR / "text_description_scores" / "20260712T104516Z"
RENAMED_DIR = WGSN_DIR / "text_description_scores" / "七月完整测试"


def rebuild_summary(out_dir: Path) -> None:
    summaries: list[Dict[str, Any]] = []
    for json_path in sorted(out_dir.glob("*_evaluation.json")):
        full = json.loads(json_path.read_text(encoding="utf-8"))
        source_name = full.get("source_name") or json_path.stem.replace("_evaluation", "") + ".md"
        slim = summarize_evaluation_row(
            full,
            extra={
                "source_md": str((WGSN_DIR / source_name).relative_to(REPO_ROOT)),
                "md_index": md_index(source_name),
            },
        )
        slim["design_merit_module_score"] = module_score(full, "DesignMerit")
        summaries.append(slim)

    summaries.sort(key=lambda s: s.get("md_index") or 0)
    jsonl_path = out_dir / "scores.jsonl"
    jsonl_path.write_text(
        "\n".join(json.dumps(s, ensure_ascii=False) for s in summaries) + ("\n" if summaries else ""),
        encoding="utf-8",
    )

    summary: Dict[str, Any] = {
        "run_utc": "20260712T104516Z",
        "label": "七月完整测试",
        "spec_version": summaries[0].get("spec_version") if summaries else None,
        "inverse_dir": str(WGSN_DIR.relative_to(REPO_ROOT)),
        "processed": len(summaries),
        "looks": summaries,
    }
    if summaries:
        ts = [float(s["total_score_S_fp"]) for s in summaries]
        summary["mean_total_score"] = round(sum(ts) / len(ts), 6)
        summary["min_total_score"] = round(min(ts), 6)
        summary["max_total_score"] = round(max(ts), 6)
        passed = sum(1 for s in summaries if s.get("gates_both_passed"))
        summary["gates_both_passed_count"] = passed
        summary["gates_both_passed_rate"] = round(passed / len(summaries), 6)
        dm = [s["design_merit_module_score"] for s in summaries if s.get("design_merit_module_score") is not None]
        if dm:
            summary["mean_design_merit"] = round(sum(dm) / len(dm), 6)
    (out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    logger = logging.getLogger(__name__)

    out_dir = OUT_DIR.resolve()
    if not out_dir.is_dir():
        raise SystemExit(f"找不到输出目录：{out_dir}")

    gate_config = load_gate_config()
    evaluator = load_default_evaluator()

    mds = sorted(WGSN_DIR.glob("*_text_description.md"))
    pending = []
    for md_path in mds:
        stem = md_path.stem.replace(" ", "_")
        if (out_dir / f"{stem}_evaluation.json").is_file():
            continue
        pending.append(md_path)

    logger.info("共 %s 条 md，待评测 %s 条", len(mds), len(pending))

    errors: list[Dict[str, Any]] = []
    for i, md_path in enumerate(pending, start=1):
        logger.info("[%s/%s] 评测 %s", i, len(pending), md_path.name)
        try:
            desc = extract_text_description_block(md_path.read_text(encoding="utf-8"))
            full = evaluator.evaluate_text(desc, source_name=md_path.name, gate_config=gate_config)
        except Exception as exc:
            logger.exception("评测失败，跳过：%s", md_path.name)
            errors.append({"source_md": str(md_path.relative_to(REPO_ROOT)), "error": str(exc)})
            continue
        stem = md_path.stem.replace(" ", "_")
        write_artifacts(
            full,
            out_dir,
            stem,
            {
                "source_md": str(md_path.relative_to(REPO_ROOT)),
                "md_index": md_index(md_path.name),
            },
        )

    if errors:
        err_path = out_dir / "errors.jsonl"
        with err_path.open("a", encoding="utf-8") as ef:
            for rec in errors:
                ef.write(json.dumps(rec, ensure_ascii=False) + "\n")
        logger.warning("失败 %s 条，已写入 %s", len(errors), err_path.name)

    rebuild_summary(out_dir)
    done = len(list(out_dir.glob("*_evaluation.json")))
    logger.info("summary 已更新，共 %s 条", done)

    if done < len(mds):
        logger.warning("尚有 %s 条未评分，跳过重命名", len(mds) - done)
        return

    target = RENAMED_DIR.resolve()
    if out_dir != target:
        if target.exists():
            raise SystemExit(f"目标目录已存在：{target}")
        out_dir.rename(target)
        logger.info("目录已重命名为 %s", target.name)


if __name__ == "__main__":
    main()
