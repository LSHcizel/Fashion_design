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
        "length_component": (scores.get("length_disentangle") or {}).get("length_component"),
        "penalties_total_penalty_mean": pen.get("total_penalty"),
        "metric_totals": full.get("metric_totals"),
        "R_content_scalar": rc.get("R_content") if rc.get("enabled") else None,
        "r_content_enabled": bool(rc.get("enabled", False)),
        "prompt_char_len": len((full.get("text_description") or "").strip()),
        "eval_prose_char_len": len((full.get("eval_prose") or "").strip()),
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


def render_evaluation_markdown(full: Dict[str, Any]) -> str:
    scores = full.get("scores") or {}
    cov = scores.get("coverage_score") or {}
    qual = scores.get("quality_score") or {}
    pen = qual.get("penalties") or {}
    gates = full.get("gates") or {}
    diag = full.get("diagnosis") or {}
    metric_results = full.get("metric_results") or {}
    rc = full.get("r_content") or {}

    lines = [
        "# Text Evaluation Report",
        "",
        f"- **Source:** {full.get('source_name', '')}",
        f"- **Judge model:** {full.get('judge_model', '')}",
        f"- **Spec:** {full.get('name', '')} v{full.get('version', '')}",
        f"- **Total score (S_fp):** {full.get('total_score')} ({full.get('score_band', '')})",
        f"- **Coverage axis:** {cov.get('score')}",
        f"- **Quality axis (unweighted / weighted / effective):** "
        f"{qual.get('score')} / {qual.get('base_score')} / {qual.get('penalized_score')}",
        f"- **Penalties (mean, gate-only):** {pen.get('total_penalty')} "
        f"(does not reduce S_fp or R_content)",
        f"- **R_content:** {rc.get('R_content') if rc.get('enabled') else 'n/a'}",
        "",
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
    ]

    def _metric_table(title: str, axis: str) -> None:
        rows = list(_iter_metrics_by_axis(metric_results, axis))
        if not rows:
            return
        lines.extend([f"## {title}", "", "| Metric | Score | Hit | Dimension | Reason |", "| --- | ---: | --- | --- | --- |"])
        for r in rows:
            reason = (r.get("reason") or "").replace("|", "\\|").replace("\n", " ")
            dim = r.get("quality_dimension_zh") or ""
            hit = "" if r.get("hit") is None else r.get("hit")
            lines.append(
                f"| `{r['metric']}` | {r.get('score_value')} | {hit} | {dim} | {reason[:200]} |"
            )
        lines.append("")

    _metric_table("Coverage metrics (覆盖项)", "coverage_score")
    _metric_table("Quality metrics (质量项)", "quality_score")

    penalty_items = pen.get("items") or {}
    if penalty_items:
        lines.extend(["## Penalties (扣分项)", "", "| Key | Score | Reason |", "| --- | ---: | --- |"])
        for key, item in sorted(penalty_items.items()):
            if not isinstance(item, dict):
                continue
            reason = (item.get("reason") or "").replace("|", "\\|").replace("\n", " ")
            lines.append(f"| `{key}` | {item.get('score')} | {reason[:240]} |")
        lines.append("")

    missing = diag.get("missing_information") or []
    if missing:
        lines.extend(["## Missing coverage (未覆盖)", ""])
        for item in missing:
            lines.append(f"- **`{item.get('metric')}`** — {item.get('reason', '')}")
        lines.append("")

    quality_issues = diag.get("quality_issues") or []
    if quality_issues:
        lines.extend(["## Quality issues (质量短板)", ""])
        for item in quality_issues:
            lines.append(
                f"- **`{item.get('metric')}`** (score {item.get('score_value')}) — {item.get('reason', '')}"
            )
        lines.append("")

    skipped = full.get("skipped_metrics") or []
    if skipped:
        lines.extend(["## Skipped metrics (不适用)", ""])
        for item in skipped[:20]:
            lines.append(f"- `{item.get('metric')}` ({item.get('axis')}) — {item.get('reason', '')}")
        if len(skipped) > 20:
            lines.append(f"- … and {len(skipped) - 20} more")
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
