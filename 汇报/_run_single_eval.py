"""One-off: evaluate text description and write report to 汇报/."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from plugins.local_llm import build_workflow_text_evaluator
from plugins.text_description_evaluator.design_text_evaluator_api import DesignTextEvaluator, FASHION_CONFIG
from plugins.text_description_evaluator.evaluation_export import (
    MODULE_SCORE_LEGEND,
    format_axis_description,
    module_zh_label,
    render_evaluation_markdown,
    sort_coverage_modules,
    sort_quality_modules,
)

TEXT_MD = ROOT / (
    "fashion_research_dir/wgsn_batch_image_inverse/20260524T044337Z/"
    "10_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__010_media_cha_biarritz_ps27_031_text_description.md"
)
OUT_MD = Path(__file__).resolve().parent / "010_ps27_031_完整评分报告.md"
OUT_JSON = Path(__file__).resolve().parent / "010_ps27_031_完整评分报告.json"


def _module_lines(module_scores: dict, spec_modules: list) -> list[str]:
    lines = ["### 模块分", "", MODULE_SCORE_LEGEND, ""]
    for mod in spec_modules:
        name = mod["name"]
        ms = module_scores.get(name) or {}
        label = module_zh_label(name)
        lines.append(
            f"- {label}：适用 {ms.get('applicable_metrics', 0)}，"
            f"命中 {ms.get('hit_metrics', 0)}，模块分 {ms.get('score', 0)}"
        )
    lines.append("")
    return lines


def _detail_markdown(full: dict, **kwargs) -> str:
    return render_evaluation_markdown(
        full,
        include_r_content=False,
        include_score_formula=False,
        include_report_header=False,
        include_gates=False,
        include_bonus_score=False,
        chinese_labels=True,
        coverage_heading_level=3,
        quality_heading_level=3,
        coverage_module_heading_level=4,
        quality_module_heading_level=4,
        section_heading_level=2,
        **kwargs,
    )


def build_report(
    full: dict,
    *,
    title: str = "Look 010 完整评分报告",
    source_name: str | None = None,
) -> str:
    scores = full.get("scores") or {}
    cov = scores.get("coverage_score") or {}
    qual = scores.get("quality_score") or {}
    pen = qual.get("penalties") or {}
    gates = full.get("gates") or {}
    module_scores = scores.get("module_scores") or {}
    spec = full.get("_spec_modules") or {}
    score_axes = full.get("_score_axes") or {}
    source_label = source_name or full.get("source_name", "")

    lines = [
        f"# {title}",
        "",
        f"- **文本来源**：`{source_label}`",
        f"- **Judge model**：{full.get('judge_model', '')}",
        "",
        "## 总览",
        "",
        f"- 覆盖轴 C：{cov.get('score')}",
        f"- 质量轴（加权 Q_w）：{qual.get('base_score')}",
        f"- 内容主分 s_fp_base：{scores.get('s_fp_base')}",
        f"- **最终 S_fp**：**{full.get('total_score')}** ({full.get('score_band', '')})",
        f"- 惩罚综合 P̄：{pen.get('total_penalty')}",
        "",
        "### 门限",
        "",
        f"- Score gate：{(gates.get('score_gate') or {}).get('value')} / {(gates.get('score_gate') or {}).get('threshold')} → "
        f"**{'PASS' if (gates.get('score_gate') or {}).get('passed') else 'FAIL'}**",
        f"- Penalty gate：{(gates.get('penalty_gate') or {}).get('total_penalty')} / {(gates.get('penalty_gate') or {}).get('threshold')} → "
        f"**{'PASS' if (gates.get('penalty_gate') or {}).get('passed') else 'FAIL'}**",
        f"- 双门限：**{gates.get('both_passed')}**",
        "",
        "## S_fp 计算",
        "",
        f"- s_fp_base：{scores.get('s_fp_base')}",
        f"- **S_fp**：**{full.get('total_score')}**",
        "",
    ]

    if spec:
        lines.extend([
            "## 覆盖轴",
            "",
            format_axis_description(score_axes, "coverage_score"),
            "",
        ])
        lines.extend(_module_lines(module_scores, sort_coverage_modules(spec.get("coverage", []))))
        lines.extend(_detail_markdown(
            full,
            include_coverage=True,
            include_quality=False,
            include_penalties=False,
            include_missing=False,
            include_quality_issues=False,
            include_skipped=False,
        ).splitlines())
        lines.append("")
        lines.extend([
            "## 质量轴",
            "",
            format_axis_description(score_axes, "quality_score"),
            "",
        ])
        lines.extend(_module_lines(module_scores, sort_quality_modules(spec.get("quality", []))))
        lines.extend(_detail_markdown(
            full,
            include_coverage=False,
            include_quality=True,
            include_penalties=True,
            include_missing=True,
            include_quality_issues=True,
            include_skipped=True,
        ).splitlines())

    return "\n".join(lines).rstrip() + "\n"


def evaluate_and_write(
    text_path: Path,
    *,
    out_md: Path,
    out_json: Path,
    title: str,
) -> dict:
    text = text_path.read_text(encoding="utf-8").strip()
    evaluator = build_workflow_text_evaluator(
        api_key=FASHION_CONFIG.get("api-key"),
        api_base=FASHION_CONFIG.get("api-base"),
        model=(FASHION_CONFIG.get("grpo") or {}).get("design-text-evaluator", {}).get("model") or "gpt-5.4-mini",
    )
    if not isinstance(evaluator, DesignTextEvaluator):
        evaluator = DesignTextEvaluator(
            api_key=FASHION_CONFIG.get("api-key"),
            api_base=FASHION_CONFIG.get("api-base"),
            model="gpt-5.4-mini",
        )
    full = evaluator.evaluate_text(text, source_name=text_path.name)
    full["_spec_modules"] = {
        "coverage": evaluator.spec.get("coverage_modules", []),
        "quality": evaluator.spec.get("quality_modules", []),
    }
    full["_score_axes"] = evaluator.spec.get("score_axes", {})
    out_json.write_text(json.dumps(full, ensure_ascii=False, indent=2), encoding="utf-8")
    out_md.write_text(
        build_report(full, title=title, source_name=text_path.name),
        encoding="utf-8",
    )
    return full


def rebuild_report_from_json(
    json_path: Path,
    *,
    out_md: Path,
    title: str,
    source_name: str | None = None,
) -> None:
    spec_path = ROOT / "plugins/text_description_evaluator/fashion_prompt_optimizer_spec.json"
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    full = json.loads(json_path.read_text(encoding="utf-8"))
    full["_spec_modules"] = {
        "coverage": spec.get("coverage_modules", []),
        "quality": spec.get("quality_modules", []),
    }
    full["_score_axes"] = spec.get("score_axes", {})
    out_md.write_text(
        build_report(
            full,
            title=title,
            source_name=source_name or full.get("source_name"),
        ),
        encoding="utf-8",
    )


def main() -> None:
    full = evaluate_and_write(
        TEXT_MD,
        out_md=OUT_MD,
        out_json=OUT_JSON,
        title="Look 010 完整评分报告",
    )
    print(f"Saved: {OUT_MD}")
    print(f"Saved: {OUT_JSON}")
    print(f"S_fp={full.get('total_score')} band={full.get('score_band')}")


if __name__ == "__main__":
    main()
