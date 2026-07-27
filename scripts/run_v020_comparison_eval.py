#!/usr/bin/env python3
"""v0.2.x spec 对比评测：workflow 8 looks + WGSN 前 N 条 → 各自新时间戳目录。"""

from __future__ import annotations

import json
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from plugins.text_description_evaluator import load_default_evaluator  # noqa: E402
from plugins.text_description_evaluator.evaluation_export import (  # noqa: E402
    render_evaluation_markdown,
    summarize_evaluation_row,
)

WORKFLOW_ROOT = REPO_ROOT / "fashion_research_dir/workflow_0/2026-06-06"
WGSN_DIR = REPO_ROOT / "fashion_research_dir/wgsn_batch_image_inverse/20260524T044337Z"


def load_gate_config() -> Dict[str, float]:
    cfg_path = REPO_ROOT / "fashion_config.yaml"
    cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
    te = dict(cfg.get("text-evaluator") or {})
    return {
        "score_gate_min": float(te.get("score-gate-min", 0.7)),
        "penalty_gate_max": float(te.get("penalty-gate-max", 0.5)),
    }


def extract_text_description_block(md_text: str) -> str:
    m = re.search(r"(?msi)^##\s*text_description\s*\n+(.*?)(?=^\#\#\s|\Z)", md_text)
    if not m:
        raise ValueError("未找到 ## text_description 段落")
    return m.group(1).strip()


def md_index(name: str) -> Optional[int]:
    m = re.match(r"^(\d+)_", name)
    return int(m.group(1)) if m else None


def module_score(full: Dict[str, Any], name: str) -> Optional[float]:
    ms = (full.get("scores") or {}).get("module_scores") or {}
    val = ms.get(name, {}).get("score")
    return float(val) if val is not None else None


def write_artifacts(full: Dict[str, Any], out_dir: Path, stem: str, extra: Dict[str, Any]) -> Dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / f"{stem}_evaluation.json"
    md_path = out_dir / f"{stem}_report.md"
    json_path.write_text(json.dumps(full, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_evaluation_markdown(full), encoding="utf-8")
    slim = summarize_evaluation_row(full, extra=extra)
    slim["design_merit_module_score"] = module_score(full, "DesignMerit")
    with (out_dir / "scores.jsonl").open("a", encoding="utf-8") as jf:
        jf.write(json.dumps(slim, ensure_ascii=False) + "\n")
    return slim


def score_workflow(evaluator, gate_config, stamp: str) -> Path:
    out_dir = WORKFLOW_ROOT / "text_eval_scores" / stamp
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "scores.jsonl").unlink(missing_ok=True)
    summaries = []
    for chapter in ("chapter_01", "chapter_02"):
        ch_dir = WORKFLOW_ROOT / chapter
        for n in range(1, 5):
            look_path = ch_dir / f"look_{n:02d}.txt"
            if not look_path.is_file():
                continue
            logging.info("workflow 评测 %s/%s", chapter, look_path.name)
            full = evaluator.evaluate_txt_file(look_path, gate_config=gate_config)
            stem = f"{chapter}_look_{n:02d}"
            slim = write_artifacts(
                full,
                out_dir,
                stem,
                {
                    "chapter": chapter,
                    "look_number": n,
                    "source_txt": str(look_path.relative_to(REPO_ROOT)),
                },
            )
            summaries.append(slim)
    summary = {
        "run_utc": stamp,
        "spec_version": summaries[0].get("spec_version") if summaries else None,
        "workflow_root": str(WORKFLOW_ROOT.relative_to(REPO_ROOT)),
        "processed": len(summaries),
        "looks": summaries,
    }
    if summaries:
        ts = [float(s["total_score_S_fp"]) for s in summaries]
        summary["mean_total_score"] = round(sum(ts) / len(ts), 6)
        summary["min_total_score"] = round(min(ts), 6)
        summary["max_total_score"] = round(max(ts), 6)
        dm = [s["design_merit_module_score"] for s in summaries if s.get("design_merit_module_score") is not None]
        if dm:
            summary["mean_design_merit"] = round(sum(dm) / len(dm), 6)
    (out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_dir


def score_wgsn(evaluator, gate_config, stamp: str, limit: int = 10) -> Path:
    out_dir = WGSN_DIR / "text_description_scores" / stamp
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "scores.jsonl").unlink(missing_ok=True)
    mds = sorted(WGSN_DIR.glob("*_text_description.md"))[:limit]
    summaries = []
    for md_path in mds:
        logging.info("wgsn 评测 %s", md_path.name)
        desc = extract_text_description_block(md_path.read_text(encoding="utf-8"))
        full = evaluator.evaluate_text(desc, source_name=md_path.name, gate_config=gate_config)
        stem = md_path.stem.replace(" ", "_")
        slim = write_artifacts(
            full,
            out_dir,
            stem,
            {
                "source_md": str(md_path.relative_to(REPO_ROOT)),
                "md_index": md_index(md_path.name),
            },
        )
        summaries.append(slim)
    summary = {
        "run_utc": stamp,
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
        dm = [s["design_merit_module_score"] for s in summaries if s.get("design_merit_module_score") is not None]
        if dm:
            summary["mean_design_merit"] = round(sum(dm) / len(dm), 6)
    (out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_dir


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    gate_config = load_gate_config()
    evaluator = load_default_evaluator()
    wf_dir = score_workflow(evaluator, gate_config, stamp)
    wgsn_dir = score_wgsn(evaluator, gate_config, stamp, limit=10)
    print(f"WORKFLOW_OUT={wf_dir.relative_to(REPO_ROOT)}")
    print(f"WGSN_OUT={wgsn_dir.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
