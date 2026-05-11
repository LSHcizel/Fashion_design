"""
将 evaluate 模式产出的 JSON 转为可读 Markdown 测试报告。

用法:
  python -m plugins.text_description_evaluator.render_evaluation_markdown ^
    --input path/to/eval.json --output path/to/report.md
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


def _fmt_gates(gates: Dict[str, Any]) -> List[str]:
    if not gates:
        return ["- （无 gates 字段，可能为旧版 JSON）"]
    lines: List[str] = []
    sg = gates.get("score_gate") or {}
    pg = gates.get("penalty_gate") or {}
    lines.append(
        f"- **得分门限**：值 `{sg.get('value')}` / 阈 `{sg.get('threshold')}` / 通过 `{sg.get('passed')}`"
    )
    lines.append(
        f"- **惩罚门限**：total_penalty `{pg.get('total_penalty')}` / 阈 `{pg.get('threshold')}` / 通过 `{pg.get('passed')}`"
    )
    lines.append(f"- **双门限同时通过**：`{gates.get('both_passed')}`")
    return lines


def _fmt_penalties(penalties: Dict[str, Any], penalty_keys: List[str]) -> List[str]:
    lines: List[str] = []
    items = penalties.get("items") or {}
    for key in penalty_keys:
        if key not in items and key not in penalties:
            continue
        score = penalties.get(key, items.get(key, {}).get("score", 0))
        it = items.get(key, {})
        reason = it.get("reason", "")
        lines.append(f"- `{key}`: **{score}** — {reason or '—'}")
    lines.append(f"- **total_penalty**（均值）: `{penalties.get('total_penalty', '—')}`")
    return lines


def _default_penalty_keys() -> List[str]:
    return [
        "generation_content_penalty",
        "consistency_penalty",
        "coordination_penalty",
        "rationality_penalty",
    ]


def render_markdown(data: Dict[str, Any]) -> str:
    scores = data.get("scores") or {}
    qs = scores.get("quality_score") or {}
    penalties = qs.get("penalties") or {}
    metric_results = data.get("metric_results") or {}

    lines: List[str] = [
        "# 文本描述评估测试报告",
        "",
        "> **说明**：本报告由 **`evaluate` 单次评估** JSON 生成，**不包含**多轮优化过程。查看各轮改写全文请使用 `run_design_text_evaluator --mode optimize`（默认最多 **5** 轮，可 `--max-rounds` 调整），并打开生成的 `*_optimization_report.md` 中的 **「Round Texts（各轮优化全文）」** 章节。",
        "",
        f"- **来源**：`{data.get('source_name', '—')}`",
        f"- **Judge 模型**：`{data.get('judge_model', '—')}`",
        f"- **总分 total_score**：`{data.get('total_score', '—')}`",
        f"- **分档 score_band**：`{data.get('score_band', '—')}`",
        f"- **质量 base / penalized**：`{qs.get('base_score', '—')}` / `{qs.get('penalized_score', '—')}`",
        "",
        "## 1 双门限（gates）",
        "",
        *_fmt_gates(data.get("gates") or {}),
        "",
        "## 2 轴分与模块",
        "",
    ]

    for axis_key in ("coverage_score", "quality_score", "bonus_score"):
        block = scores.get(axis_key)
        if not isinstance(block, dict):
            continue
        lines.append(f"### {axis_key}")
        lines.append(f"- **轴分 score**：`{block.get('score', '—')}`")
        lines.append(f"- **适用指标数**：`{block.get('applicable_metrics', '—')}` / **命中**：`{block.get('hit_metrics', '—')}`")
        lines.append("")

    mod = scores.get("module_scores") or {}
    if mod:
        lines.append("### module_scores")
        for name, row in sorted(mod.items()):
            if isinstance(row, dict):
                lines.append(f"- `{name}`: `{row.get('score', '—')}`")
        lines.append("")

    lines.extend(
        [
            "## 3 Penalties",
            "",
            *_fmt_penalties(penalties, _default_penalty_keys()),
            "",
            "## 4 诊断摘要",
            "",
        ]
    )
    diag = data.get("diagnosis") or {}
    for key in ("missing_information", "quality_issues", "bonus_opportunities"):
        arr = diag.get(key) or []
        lines.append(f"- **{key}**：{len(arr)} 条")
    lines.append("")

    lines.extend(
        [
            "## 5 指标一览（适用且得分）",
            "",
            "| metric | axis | score | hit |",
            "|---|---|---|---|",
        ]
    )
    for name in sorted(metric_results.keys()):
        r = metric_results[name]
        if not r.get("applicable"):
            continue
        lines.append(
            f"| `{name}` | {r.get('axis', '')} | {r.get('score_value', '')} | {r.get('hit', '')} |"
        )
    lines.append("")
    lines.append("## 6 原文")
    lines.append("")
    lines.append("```")
    lines.append((data.get("text_description") or "").strip() or "—")
    lines.append("```")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Render evaluation JSON to Markdown report.")
    parser.add_argument("--input", required=True, help="Path to evaluation JSON file.")
    parser.add_argument("--output", required=True, help="Path to write Markdown report.")
    args = parser.parse_args()
    in_path = Path(args.input)
    data = json.loads(in_path.read_text(encoding="utf-8"))
    out_path = Path(args.output)
    out_path.write_text(render_markdown(data), encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
