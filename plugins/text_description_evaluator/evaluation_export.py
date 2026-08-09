"""将 DesignTextEvaluator 完整评测结果导出为 JSON / JSONL / Markdown 报告。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, Optional


def summarize_evaluation_row(
    full: Dict[str, Any],
    *,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    scores = full.get("scores") or {}
    cov = scores.get("coverage_score") or {}
    qual = scores.get("quality_score") or {}
    pen = qual.get("penalties") or {}
    gates = full.get("gates") or {}
    rc = full.get("r_content") or {}
    sf = full.get("score_formula") or {}
    length_step = next((s for s in (sf.get("steps") or []) if s.get("id") == "length_disentangle"), {})
    length_info = length_step.get("length") or {}
    row = {
        "source_name": full.get("source_name"),
        "evaluator_spec": full.get("name"),
        "spec_version": full.get("version"),
        "judge_model": full.get("judge_model"),
        "total_score_S_fp": full.get("total_score"),
        "score_band": full.get("score_band"),
        "gates_both_passed": gates.get("both_passed"),
        "score_gate_passed": (gates.get("score_gate") or {}).get("passed"),
        "penalty_gate_passed": (gates.get("penalty_gate") or {}).get("passed"),
        "score_gate_value": (gates.get("score_gate") or {}).get("value"),
        "score_gate_threshold": (gates.get("score_gate") or {}).get("threshold"),
        "penalty_gate_total_penalty": (gates.get("penalty_gate") or {}).get("total_penalty"),
        "penalty_gate_threshold": (gates.get("penalty_gate") or {}).get("threshold"),
        "coverage_axis_score": cov.get("score"),
        "quality_axis_score_raw": qual.get("score"),
        "quality_base_score": qual.get("base_score"),
        "quality_penalized_score": qual.get("penalized_score"),
        "s_fp_base": scores.get("s_fp_base"),
        "length_disentangle_applied": (scores.get("length_disentangle") or {}).get("applied"),
        "penalties_total_penalty_mean": pen.get("total_penalty"),
        "metric_totals": full.get("metric_totals"),
        "R_content_scalar": rc.get("R_content") if rc.get("enabled") else None,
        "r_content_enabled": bool(rc.get("enabled", False)),
        "prompt_char_len": len((full.get("text_description") or "").strip()),
        "eval_prose_char_len": len((full.get("eval_prose") or "").strip()),
        "length_reference_char_len": length_info.get("reference_char_len"),
        "length_component": length_info.get("length_component") or (scores.get("length_disentangle") or {}).get("length_component"),
        "length_interpretation_zh": length_info.get("interpretation_zh"),
        "length_adjustment_per_1000_chars": (length_info.get("substitution") or {}).get("per_1000_chars"),
        "score_formula_one_liner": sf.get("formula_one_liner"),
        "r_content_interpretation_zh": rc.get("interpretation_zh"),
    }
    if extra:
        row.update(extra)
    return row


def backfill_gate_thresholds_in_jsonl(
    jsonl_path: Path,
    *,
    score_gate_threshold: float = 0.7,
    penalty_gate_threshold: float = 0.5,
) -> int:
    """为已有 scores.jsonl 行补写 score_gate_threshold / penalty_gate_threshold。"""
    jsonl_path = Path(jsonl_path)
    lines = jsonl_path.read_text(encoding="utf-8").splitlines()
    updated: list[str] = []
    count = 0
    for line in lines:
        line = line.strip()
        if not line:
            continue
        obj = json.loads(line)
        changed = False
        if obj.get("score_gate_threshold") is None:
            obj["score_gate_threshold"] = score_gate_threshold
            changed = True
        if obj.get("penalty_gate_threshold") is None:
            obj["penalty_gate_threshold"] = penalty_gate_threshold
            changed = True
        if changed:
            count += 1
        updated.append(json.dumps(obj, ensure_ascii=False))
    jsonl_path.write_text("\n".join(updated) + ("\n" if updated else ""), encoding="utf-8")
    return count


def load_gate_thresholds_from_fashion_config(config_path: Path) -> Dict[str, float]:
    """读取 fashion_config.yaml → text-evaluator 双门限。"""
    import yaml

    cfg: Dict[str, Any] = {}
    config_path = Path(config_path)
    if config_path.is_file():
        with config_path.open("r", encoding="utf-8") as fp:
            cfg = yaml.safe_load(fp) or {}
    te = dict(cfg.get("text-evaluator") or {})
    return {
        "score_gate_threshold": float(te.get("score-gate-min", 0.7)),
        "penalty_gate_threshold": float(te.get("penalty-gate-max", 0.5)),
    }


METRIC_ZH_LABELS: Dict[str, str] = {
    "garment_category": "服装品类",
    "silhouette": "廓形",
    "length_hemline": "长度/下摆",
    "shoulder_architecture": "肩部结构",
    "body_coverage": "裸露/包裹",
    "fabric_family": "材质类别",
    "surface_finish": "表面性质",
    "primary_color": "主色",
    "secondary_color": "副色",
    "color_relationship_logic": "配色逻辑",
    "pattern_type": "图案",
    "closure": "开合方式",
    "functional_detail": "功能细节",
    "construction_technique": "结构工艺",
    "deconstruction": "解构",
    "hardware_embellishment": "五金装饰",
    "bag": "包袋",
    "footwear": "鞋履",
    "jewelry": "首饰",
    "belt": "腰带/腰胯附件",
    "layering": "叠搭层次",
    "top_bottom_proportion": "上下比例",
    "asymmetry": "不对称",
    "cross_garment_binding": "跨单品区分",
    "attribute_entity_binding": "属性实体绑定",
    "multi_garment_binding": "多单品绑定",
    "reference_clarity": "指代清晰度",
    "quantity_accuracy": "数量准确性",
    "information_ordering": "信息顺序",
    "garment_scope_grouping": "层级单品聚合",
    "generation_readiness": "生图提示词适配",
    "spatial_coherence": "空间关系",
    "bilateral_coherence": "左右一致性",
    "visibility_priority": "可见性优先级",
    "design_distinctiveness": "设计独特性",
    "visual_observation_grounding": "视觉观察锚定",
    "craft_embellishment_salience": "工艺装饰显著度",
    "silhouette_combination_originality": "组合原创性",
    "design_signal_purity": "设计信号纯度",
}

PENALTY_ZH_LABELS: Dict[str, str] = {
    "generation_content_penalty": "非生成导向内容",
    "consistency_penalty": "一致性",
    "coordination_penalty": "协调性",
    "rationality_penalty": "合理性",
    "formula_template_penalty": "公式模板",
}

AXIS_ZH_LABELS: Dict[str, str] = {
    "coverage_score": "覆盖轴",
    "quality_score": "质量轴",
    "bonus_score": "加分项",
}

COVERAGE_AXIS_SCORING_NOTE = "每项命中 1 分、未命中 0 分，只对适用指标取平均"
QUALITY_AXIS_SCORING_NOTE = "各指标五档计分（0 / 0.25 / 0.5 / 0.75 / 1.0），模块分 = 适用指标算术平均"

MODULE_SCORE_LEGEND = (
    "维度｜适用｜命中｜模块分 — "
    "维度：评估模块；适用：该模块下参与计分的指标数；"
    "命中：判定为「是」的指标数；"
    "模块分：该模块得分。"
)
COVERAGE_METRIC_LEGEND = (
    "指标｜得分｜命中｜说明 — "
    "指标：具体评估项；得分：1 分命中 / 0 分未命中；"
    "命中：文本是否覆盖该指标；说明：判定理由。"
)
QUALITY_METRIC_LEGEND = (
    "指标｜得分｜命中｜说明 — "
    "指标：具体评估项；得分：五档分（0 / 0.25 / 0.5 / 0.75 / 1.0）；"
    "命中：是否达到该指标要求；说明：判定理由。"
)
PENALTY_LEGEND = (
    "惩罚项｜得分｜说明 — "
    "惩罚项：惩罚维度；得分：惩罚分（0 最好，1 最差）；说明：判定理由。"
)

COVERAGE_MODULE_ZH_LABELS: Dict[str, str] = {
    "GarmentCore": "服装主体",
    "MaterialColor": "材质颜色",
    "ConstructionDetail": "结构细节",
    "StylingSet": "造型配件",
    "Composition": "造型关系",
}

COVERAGE_MODULE_ORDER: tuple[str, ...] = (
    "GarmentCore",
    "MaterialColor",
    "ConstructionDetail",
    "StylingSet",
    "Composition",
)

COVERAGE_MODULE_METRICS: Dict[str, tuple[str, ...]] = {
    "GarmentCore": (
        "garment_category",
        "silhouette",
        "length_hemline",
        "shoulder_architecture",
        "body_coverage",
    ),
    "MaterialColor": (
        "fabric_family",
        "surface_finish",
        "primary_color",
        "secondary_color",
        "color_relationship_logic",
        "pattern_type",
    ),
    "ConstructionDetail": (
        "closure",
        "functional_detail",
        "construction_technique",
        "deconstruction",
        "hardware_embellishment",
    ),
    "StylingSet": (
        "bag",
        "footwear",
        "jewelry",
        "belt",
        "layering",
    ),
    "Composition": (
        "top_bottom_proportion",
        "asymmetry",
        "cross_garment_binding",
    ),
}

METRIC_COVERAGE_MODULE: Dict[str, str] = {
    metric: module
    for module, metrics in COVERAGE_MODULE_METRICS.items()
    for metric in metrics
}

# 与 质量轴.md 模块顺序一致（设计价值 → 可见性 → 生成适配 → 绑定 → 语言 → 结构）
QUALITY_MODULE_ZH_LABELS: Dict[str, str] = {
    "DesignMerit": "设计价值",
    "ConcisenessAndDensity": "可见性优先级",
    "GenerationReadiness": "生成适配",
    "BindingAccuracy": "属性绑定",
    "LanguageClarity": "语言清晰",
    "StructuralClarity": "结构清晰",
}

QUALITY_MODULE_ORDER: tuple[str, ...] = (
    "DesignMerit",
    "ConcisenessAndDensity",
    "GenerationReadiness",
    "BindingAccuracy",
    "LanguageClarity",
    "StructuralClarity",
)

QUALITY_MODULE_METRICS: Dict[str, tuple[str, ...]] = {
    "DesignMerit": (
        "design_distinctiveness",
        "visual_observation_grounding",
        "craft_embellishment_salience",
        "silhouette_combination_originality",
        "design_signal_purity",
    ),
    "ConcisenessAndDensity": ("visibility_priority",),
    "GenerationReadiness": (
        "generation_readiness",
        "bilateral_coherence",
        "spatial_coherence",
    ),
    "BindingAccuracy": (
        "attribute_entity_binding",
        "multi_garment_binding",
    ),
    "LanguageClarity": (
        "quantity_accuracy",
        "reference_clarity",
    ),
    "StructuralClarity": (
        "information_ordering",
        "garment_scope_grouping",
    ),
}

METRIC_QUALITY_MODULE: Dict[str, str] = {
    metric: module
    for module, metrics in QUALITY_MODULE_METRICS.items()
    for metric in metrics
}


def _metric_zh_label(metric_key: str) -> str:
    return METRIC_ZH_LABELS.get(metric_key, metric_key)


def _penalty_zh_label(penalty_key: str) -> str:
    return PENALTY_ZH_LABELS.get(penalty_key, penalty_key)


def _axis_zh_label(axis_key: str) -> str:
    return AXIS_ZH_LABELS.get(axis_key, axis_key)


def _format_hit(hit: Any, *, chinese_labels: bool) -> str:
    if hit is None:
        return ""
    if chinese_labels:
        if hit in (1, "1", True):
            return "是"
        if hit in (0, "0", False):
            return "否"
    return str(hit)


def _quality_module_sort_key(module_key: str) -> tuple[int, str]:
    try:
        return (QUALITY_MODULE_ORDER.index(module_key), module_key)
    except ValueError:
        return (len(QUALITY_MODULE_ORDER), module_key)


def _coverage_module_sort_key(module_key: str) -> tuple[int, str]:
    try:
        return (COVERAGE_MODULE_ORDER.index(module_key), module_key)
    except ValueError:
        return (len(COVERAGE_MODULE_ORDER), module_key)


def _metric_order_in_quality_module(metric: str, module_key: str) -> int:
    metrics = QUALITY_MODULE_METRICS.get(module_key, ())
    try:
        return metrics.index(metric)
    except ValueError:
        return len(metrics)


def _metric_order_in_coverage_module(metric: str, module_key: str) -> int:
    metrics = COVERAGE_MODULE_METRICS.get(module_key, ())
    try:
        return metrics.index(metric)
    except ValueError:
        return len(metrics)


def _quality_module_label(module_key: str, *, chinese_labels: bool) -> str:
    if chinese_labels:
        return QUALITY_MODULE_ZH_LABELS.get(module_key, module_key or "其他")
    return module_key or "Other"


def module_zh_label(module_key: str) -> str:
    return (
        COVERAGE_MODULE_ZH_LABELS.get(module_key)
        or QUALITY_MODULE_ZH_LABELS.get(module_key)
        or module_key
        or "其他"
    )


def sort_modules_by_order(spec_modules: list, module_order: tuple[str, ...]) -> list:
    order = {name: idx for idx, name in enumerate(module_order)}
    return sorted(spec_modules, key=lambda mod: order.get(mod.get("name", ""), len(module_order)))


def sort_coverage_modules(spec_modules: list) -> list:
    return sort_modules_by_order(spec_modules, COVERAGE_MODULE_ORDER)


def sort_quality_modules(spec_modules: list) -> list:
    return sort_modules_by_order(spec_modules, QUALITY_MODULE_ORDER)


def _iter_metrics_by_axis(
    metric_results: Dict[str, Any],
    axis: str,
    *,
    applicable_only: bool = True,
) -> Iterable[Dict[str, Any]]:
    for name, item in sorted(metric_results.items()):
        if item.get("axis") != axis:
            continue
        if applicable_only and not item.get("applicable"):
            continue
        yield {
            "metric": name,
            "score_value": item.get("score_value"),
            "hit": item.get("hit"),
            "rule": item.get("rule"),
            "reason": item.get("reason"),
            "matched_terms": item.get("matched_terms") or [],
            "quality_dimension_zh": item.get("quality_dimension_zh"),
        }


def _md_heading(level: int, text: str) -> str:
    level = max(1, min(level, 6))
    return f"{'#' * level} {text}"


def format_axis_description(score_axes: Dict[str, Any], axis_key: str) -> str:
    axis = score_axes.get(axis_key) or {}
    weight = axis.get("weight")
    question = axis.get("question", "")
    description = axis.get("description", "")
    scoring = (
        COVERAGE_AXIS_SCORING_NOTE
        if axis_key == "coverage_score"
        else QUALITY_AXIS_SCORING_NOTE
    )
    return f"轴权重 {weight}；问题：{question}。{description}。{scoring}。"


def render_evaluation_markdown(
    full: Dict[str, Any],
    *,
    include_r_content: bool = True,
    include_score_formula: bool = True,
    include_report_header: bool = True,
    include_gates: bool = True,
    include_bonus_score: bool = True,
    include_coverage: bool = True,
    include_quality: bool = True,
    include_penalties: bool = True,
    include_missing: bool = True,
    include_quality_issues: bool = True,
    include_skipped: bool = True,
    chinese_labels: bool = False,
    coverage_heading_level: int = 2,
    quality_heading_level: int = 2,
    coverage_module_heading_level: int = 3,
    quality_module_heading_level: int = 3,
    section_heading_level: int = 2,
) -> str:
    scores = full.get("scores") or {}
    cov = scores.get("coverage_score") or {}
    qual = scores.get("quality_score") or {}
    pen = qual.get("penalties") or {}
    gates = full.get("gates") or {}
    diag = full.get("diagnosis") or {}
    metric_results = full.get("metric_results") or {}
    rc = full.get("r_content") or {}

    lines: list[str] = []
    if include_report_header:
        lines.extend([
            "# Text Evaluation Report",
            "",
            f"- **Source:** {full.get('source_name', '')}",
            f"- **Judge model:** {full.get('judge_model', '')}",
            f"- **Total score (S_fp):** {full.get('total_score')} ({full.get('score_band', '')})",
            f"- **Coverage axis:** {cov.get('score')}",
            f"- **Quality axis (weighted / effective):** "
            f"{qual.get('base_score')} / {qual.get('penalized_score')}",
            f"- **Penalties (mean, gate-only):** {pen.get('total_penalty')} "
            f"(does not reduce S_fp{' or R_content' if include_r_content else ''})",
        ])
        if include_r_content:
            lines.append(f"- **R_content:** {rc.get('R_content') if rc.get('enabled') else 'n/a'}")
        lines.append("")
    if include_gates:
        lines.extend([
            "## Gates",
            "",
            f"- Score gate: {(gates.get('score_gate') or {}).get('value')} "
            f"(threshold {(gates.get('score_gate') or {}).get('threshold')}) "
            f"→ **{'PASS' if (gates.get('score_gate') or {}).get('passed') else 'FAIL'}**",
            f"- Penalty gate: {(gates.get('penalty_gate') or {}).get('total_penalty')} "
            f"(max {(gates.get('penalty_gate') or {}).get('threshold')}) "
            f"→ **{'PASS' if (gates.get('penalty_gate') or {}).get('passed') else 'FAIL'}**",
            f"- Both passed: **{gates.get('both_passed')}**",
            "",
        ])

    sf = full.get("score_formula") or {}
    if include_score_formula and sf.get("steps"):
        lines.extend(["## 得分公式分解 (Score formula)", ""])
        chain = sf.get("formula_chain_symbolic") or sf.get("formula_chain_zh") or []
        if not include_r_content:
            chain = [ln for ln in chain if not ln.startswith("R_content")]
        if chain:
            lines.append("**符号公式链：**")
            for i, ln in enumerate(chain, start=1):
                lines.append(f"{i}. `{ln}`")
            lines.append("")
        if sf.get("formula_one_liner"):
            one_liner = sf["formula_one_liner"]
            if not include_r_content and ";" in one_liner:
                one_liner = one_liner.split(";", 1)[0].strip()
            lines.append(f"**一行式：** `{one_liner}`")
            lines.append("")
        modes = sf.get("mode_explanations") or {}
        if modes:
            lines.append("**模式说明：**")
            ld = modes.get("length_disentangle") or {}
            if ld:
                lines.append(
                    f"- **长度去相关 · {ld.get('active_mode')}（{ld.get('name_zh', '')}）**："
                    f"{ld.get('interpretation_zh', '')}"
                )
            if include_r_content:
                pm = modes.get("r_content_penalty_merge") or {}
                if pm:
                    lines.append(
                        f"- **R_content 惩罚并入 · multiply（{pm.get('name_zh', '')}）**："
                        f"{pm.get('effective_note_zh', '')} {pm.get('interpretation_zh', '')}"
                    )
                ctx = modes.get("r_content_evaluation_context") or {}
                grpo = ctx.get("grpo_group") or {}
                single = ctx.get("single_sample") or {}
                lines.append(f"- **单条评分**：{single.get('interpretation_zh', '')}")
                lines.append(f"- **GRPO 组内**：{grpo.get('interpretation_zh', '')}")
            lines.append("")
        params = sf.get("parameters") or {}
        if params:
            lines.append("**本 spec 参数：**")
            for k, v in params.items():
                lines.append(f"- `{k}` = {v}")
            lines.append("")
        outputs = sf.get("outputs") or {}
        if outputs:
            if include_r_content:
                lines.append(
                    f"**输出：** S_fp = **{outputs.get('S_fp')}**，"
                    f"R_content = **{outputs.get('R_content')}**，P̄ = **{outputs.get('P̄')}**"
                )
            else:
                lines.append(
                    f"**输出：** S_fp = **{outputs.get('S_fp')}**，P̄ = **{outputs.get('P̄')}**"
                )
            lines.append("")
        r_content_step_ids = {"r_content_input", "penalty_soft_merge", "group_z_len"}
        formula_steps = sf["steps"]
        if not include_r_content:
            formula_steps = [st for st in formula_steps if st.get("id") not in r_content_step_ids]
        lines.extend(
            [
                "| 步骤 | 名称 | 符号公式 | 本条结果 |",
                "| ---: | --- | --- | ---: |",
            ]
        )
        for st in formula_steps:
            formula = (st.get("formula") or st.get("formula_symbolic") or "").replace("|", "\\|")
            val = st.get("value")
            lines.append(f"| {st.get('step')} | {st.get('label_zh')} | `{formula}` | {val} |")
        lines.append("")
        lines.append("**本条代入（substitution）见各步 JSON 或 evaluation.json → score_formula.steps[].substitution**")
        lines.append("")
        length_step = next((s for s in formula_steps if s.get("id") == "length_disentangle"), None)
        if length_step:
            length = length_step.get("length") or {}
            if length.get("interpretation_zh"):
                lines.append(f"- **长度：** {length['interpretation_zh']}")
        if include_r_content and rc.get("interpretation_zh"):
            lines.append(f"- **R_content：** {rc['interpretation_zh']}")
        lines.append("")

    def _metric_table(title: str, axis: str, heading_level: int) -> None:
        rows = list(_iter_metrics_by_axis(metric_results, axis))
        if not rows:
            return
        lines.extend([_md_heading(heading_level, title), ""])
        for r in rows:
            reason = (r.get("reason") or "").replace("\n", " ")
            dim = r.get("quality_dimension_zh") or ""
            hit = _format_hit(r.get("hit"), chinese_labels=chinese_labels)
            metric_label = _metric_zh_label(r["metric"]) if chinese_labels else r["metric"]
            dim_part = f"，{dim}" if dim else ""
            lines.append(
                f"- {metric_label}：{r.get('score_value')}，{hit}{dim_part} — {reason[:200]}"
            )
        lines.append("")

    def _coverage_metric_table_grouped() -> None:
        rows = list(_iter_metrics_by_axis(metric_results, "coverage_score"))
        if not rows:
            return
        groups: Dict[str, list[Dict[str, Any]]] = {}
        for row in rows:
            module_key = METRIC_COVERAGE_MODULE.get(row["metric"], "")
            groups.setdefault(module_key or "_other", []).append(row)

        title = "覆盖项" if chinese_labels else "Coverage metrics (覆盖项)"
        lines.extend([_md_heading(coverage_heading_level, title), ""])
        if chinese_labels:
            lines.extend([COVERAGE_METRIC_LEGEND, ""])
        for module_key in sorted(groups.keys(), key=_coverage_module_sort_key):
            group_rows = sorted(
                groups[module_key],
                key=lambda r: _metric_order_in_coverage_module(r["metric"], module_key),
            )
            module_label = module_zh_label(module_key) if chinese_labels else module_key
            lines.extend([_md_heading(coverage_module_heading_level, module_label), ""])
            for r in group_rows:
                reason = (r.get("reason") or "").replace("\n", " ")
                hit = _format_hit(r.get("hit"), chinese_labels=chinese_labels)
                metric_label = _metric_zh_label(r["metric"]) if chinese_labels else r["metric"]
                lines.append(
                    f"- {metric_label}：{r.get('score_value')}，{hit} — {reason[:200]}"
                )
            lines.append("")

    def _quality_metric_table_grouped() -> None:
        rows = list(_iter_metrics_by_axis(metric_results, "quality_score"))
        if not rows:
            return
        groups: Dict[str, list[Dict[str, Any]]] = {}
        for row in rows:
            module_key = METRIC_QUALITY_MODULE.get(row["metric"], "")
            groups.setdefault(module_key or "_other", []).append(row)

        title = "质量项" if chinese_labels else "Quality metrics (质量项)"
        lines.extend([_md_heading(quality_heading_level, title), ""])
        if chinese_labels:
            lines.extend([QUALITY_METRIC_LEGEND, ""])
        for module_key in sorted(groups.keys(), key=_quality_module_sort_key):
            group_rows = sorted(
                groups[module_key],
                key=lambda r: _metric_order_in_quality_module(r["metric"], module_key),
            )
            module_label = _quality_module_label(module_key, chinese_labels=chinese_labels)
            lines.extend([_md_heading(quality_module_heading_level, module_label), ""])
            for r in group_rows:
                reason = (r.get("reason") or "").replace("\n", " ")
                hit = _format_hit(r.get("hit"), chinese_labels=chinese_labels)
                metric_label = _metric_zh_label(r["metric"]) if chinese_labels else r["metric"]
                lines.append(
                    f"- {metric_label}：{r.get('score_value')}，{hit} — {reason[:200]}"
                )
            lines.append("")

    if include_coverage:
        if chinese_labels:
            _coverage_metric_table_grouped()
        else:
            _metric_table(
                "Coverage metrics (覆盖项)",
                "coverage_score",
                coverage_heading_level,
            )
    if include_quality:
        if chinese_labels:
            _quality_metric_table_grouped()
        else:
            _metric_table(
                "Quality metrics (质量项)",
                "quality_score",
                quality_heading_level,
            )

    penalty_items = pen.get("items") or {}
    if include_penalties and penalty_items:
        title = "惩罚项" if chinese_labels else "Penalties (扣分项)"
        lines.extend([_md_heading(section_heading_level, title), ""])
        if chinese_labels:
            lines.extend([PENALTY_LEGEND, ""])
        for key, item in sorted(penalty_items.items()):
            if not isinstance(item, dict):
                continue
            reason = (item.get("reason") or "").replace("\n", " ")
            label = _penalty_zh_label(key) if chinese_labels else key
            lines.append(f"- {label}：{item.get('score')} — {reason[:240]}")
        lines.append("")

    missing = diag.get("missing_information") or []
    if include_missing and missing:
        title = "未覆盖" if chinese_labels else "Missing coverage (未覆盖)"
        lines.extend([_md_heading(section_heading_level, title), ""])
        for item in missing:
            metric_key = item.get("metric", "")
            metric_label = _metric_zh_label(metric_key) if chinese_labels else f"`{metric_key}`"
            if chinese_labels:
                lines.append(f"- **{metric_label}** — {item.get('reason', '')}")
            else:
                lines.append(f"- **`{metric_key}`** — {item.get('reason', '')}")
        lines.append("")

    quality_issues = diag.get("quality_issues") or []
    if include_quality_issues and quality_issues:
        title = "质量短板" if chinese_labels else "Quality issues (质量短板)"
        lines.extend([_md_heading(section_heading_level, title), ""])
        for item in quality_issues:
            metric_key = item.get("metric", "")
            metric_label = _metric_zh_label(metric_key) if chinese_labels else f"`{metric_key}`"
            if chinese_labels:
                lines.append(
                    f"- **{metric_label}**（得分 {item.get('score_value')}）— {item.get('reason', '')}"
                )
            else:
                lines.append(
                    f"- **`{metric_key}`** (score {item.get('score_value')}) — {item.get('reason', '')}"
                )
        lines.append("")

    skipped = full.get("skipped_metrics") or []
    if not include_bonus_score:
        skipped = [item for item in skipped if item.get("axis") != "bonus_score"]
    if include_skipped and skipped:
        title = "不适用" if chinese_labels else "Skipped metrics (不适用)"
        lines.extend([_md_heading(section_heading_level, title), ""])
        for item in skipped[:20]:
            metric_key = item.get("metric", "")
            if chinese_labels:
                metric_label = _metric_zh_label(metric_key)
                axis_label = _axis_zh_label(item.get("axis", ""))
                lines.append(f"- {metric_label}（{axis_label}）— {item.get('reason', '')}")
            else:
                lines.append(f"- `{metric_key}` ({item.get('axis')}) — {item.get('reason', '')}")
        if len(skipped) > 20:
            suffix = f"- … 另有 {len(skipped) - 20} 项" if chinese_labels else f"- … and {len(skipped) - 20} more"
            lines.append(suffix)
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def write_look_evaluation_artifacts(
    full: Dict[str, Any],
    *,
    out_dir: Path,
    stem: str,
    extra_summary: Optional[Dict[str, Any]] = None,
) -> Dict[str, str]:
    """
    写入单条 look 评测产物：
    - ``{stem}_evaluation.json``
    - ``{stem}_report.md``
    - 追加 ``scores.jsonl`` 摘要行
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / f"{stem}_evaluation.json"
    md_path = out_dir / f"{stem}_report.md"
    jsonl_path = out_dir / "scores.jsonl"

    json_path.write_text(json.dumps(full, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_evaluation_markdown(full), encoding="utf-8")

    summary = summarize_evaluation_row(full, extra=extra_summary)
    with jsonl_path.open("a", encoding="utf-8") as jf:
        jf.write(json.dumps(summary, ensure_ascii=False) + "\n")

    return {
        "evaluation_json": str(json_path),
        "report_md": str(md_path),
        "scores_jsonl": str(jsonl_path),
    }
