"""
短 GRPO 每轮后的验收摘要。

``data`` 是当前 ``phase_b`` 的奖励与门限。``score_lift`` 是同一批样本上
裁判的质量轴、七个质量模块和总分：改写相对同组原文的配对提升，以及
相对上一轮改写均值的提升。这些分是采样时打的，不会随本轮梯度自动变化。
要看刚写入的 policy，需用它重新采样后再跑本模块。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Union

from .record_builder import record_include_in_training

JsonPath = Union[str, Path]


def read_jsonl(path: JsonPath) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def _mean(xs: List[float]) -> Optional[float]:
    if not xs:
        return None
    return round(sum(xs) / len(xs), 6)


def _rate(ok: int, n: int) -> Optional[float]:
    if n <= 0:
        return None
    return round(ok / n, 6)


def summarize_rows(rows: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    """从 phase_b 或 samples 行汇总门限、奖励、长度。"""
    r_content: List[float] = []
    s_fp: List[float] = []
    penalties: List[float] = []
    char_lens: List[float] = []
    advs: List[float] = []
    n = 0
    n_train = 0
    both_ok = 0
    score_ok = 0
    penalty_ok = 0
    gate_n = 0
    groups = set()

    for rec in rows:
        n += 1
        gid = rec.get("group_id")
        if gid:
            groups.add(str(gid))
        if record_include_in_training(rec):
            n_train += 1

        r = (rec.get("grpo") or {}).get("reward_scalar")
        if r is None:
            r = rec.get("R_content")
        if r is None:
            rc = rec.get("r_content") or {}
            r = rc.get("R_content") or rc.get("r_Q")
        if r is not None:
            r_content.append(float(r))

        sf = rec.get("S_fp")
        if sf is None:
            sf = (rec.get("scores_compact") or {}).get("S_fp")
        if sf is not None:
            s_fp.append(float(sf))

        cl = rec.get("char_len")
        if cl is not None:
            char_lens.append(float(cl))

        adv = rec.get("advantage")
        if adv is not None:
            advs.append(float(adv))

        pen = rec.get("penalties") or {}
        tp = pen.get("total_penalty") if isinstance(pen, dict) else None
        if tp is None:
            tp = (rec.get("scores_compact") or {}).get("total_penalty")
        if tp is not None:
            penalties.append(float(tp))

        g = rec.get("gates_compact") or {}
        if g:
            gate_n += 1
            if g.get("both_passed") is True:
                both_ok += 1
            if g.get("score_gate_passed") is True:
                score_ok += 1
            if g.get("penalty_gate_passed") is True:
                penalty_ok += 1

    pos_adv = sum(1 for a in advs if a > 0)
    return {
        "rows": n,
        "groups": len(groups),
        "included_for_training": n_train,
        "mean_R_content": _mean(r_content),
        "mean_S_fp": _mean(s_fp),
        "mean_total_penalty": _mean(penalties),
        "mean_char_len": _mean(char_lens),
        "score_gate_pass_rate": _rate(score_ok, gate_n),
        "penalty_gate_pass_rate": _rate(penalty_ok, gate_n),
        "both_gates_pass_rate": _rate(both_ok, gate_n),
        "gate_rows": gate_n,
        "advantage_positive_rate": _rate(pos_adv, len(advs)) if advs else None,
        "mean_advantage": _mean(advs),
    }


# 质量轴 Q 的七个模块。分数是模块内适用指标的平均，设计价值已含其五项子指标。
QUALITY_MODULES = (
    ("DesignMerit", "设计价值"),
    ("InformationDensity", "信息密度"),
    ("ConcisenessAndDensity", "可见性优先级"),
    ("GenerationReadiness", "生成适配"),
    ("BindingAccuracy", "属性绑定"),
    ("LanguageClarity", "语言清晰"),
    ("StructuralClarity", "结构清晰"),
)


def _as_float(value: Any) -> Optional[float]:
    if value is None or isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _is_original(rec: Dict[str, Any]) -> bool:
    try:
        if int(rec.get("candidate_index", 0)) < 0:
            return True
    except (TypeError, ValueError):
        pass
    return bool((rec.get("parallel_sampling") or {}).get("injected_original"))


def _module_value(raw: Any) -> Optional[float]:
    if isinstance(raw, dict):
        return _as_float(raw.get("score"))
    return _as_float(raw)


def extract_axis_scores(rec: Dict[str, Any]) -> Dict[str, Any]:
    """从一条样本取出总分、质量轴、覆盖轴和七个质量模块。"""
    sc = rec.get("scores_compact") or {}
    s_fp = _as_float(rec.get("S_fp"))
    if s_fp is None:
        s_fp = _as_float(sc.get("S_fp"))
    quality = _as_float(sc.get("quality_base_score"))
    if quality is None:
        quality = _as_float(sc.get("quality_penalized_score"))
    penalty = None
    pen = rec.get("penalties")
    if isinstance(pen, dict):
        penalty = _as_float(pen.get("total_penalty"))
    if penalty is None:
        penalty = _as_float(sc.get("total_penalty"))
    modules: Dict[str, Optional[float]] = {}
    raw_modules = sc.get("module_scores") or {}
    if isinstance(raw_modules, dict):
        for name, _zh in QUALITY_MODULES:
            modules[name] = _module_value(raw_modules.get(name))
    gates = rec.get("gates_compact") or {}
    return {
        "S_fp": s_fp,
        "quality": quality,
        "coverage": _as_float(sc.get("coverage_axis_score")),
        "total_penalty": penalty,
        "modules": modules,
        "score_gate_passed": gates.get("score_gate_passed") if gates else None,
        "penalty_gate_passed": gates.get("penalty_gate_passed") if gates else None,
        "both_passed": gates.get("both_passed") if gates else None,
    }


def _mean_optional(values: List[Optional[float]]) -> Optional[float]:
    nums = [float(v) for v in values if v is not None]
    return _mean(nums)


def _rate_optional(flags: List[Any]) -> Optional[float]:
    known = [f for f in flags if isinstance(f, bool)]
    if not known:
        return None
    return _rate(sum(1 for f in known if f), len(known))


def _snapshot(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    axes = [extract_axis_scores(rec) for rec in rows]
    groups = {str(rec.get("group_id")) for rec in rows if rec.get("group_id")}
    modules: Dict[str, Any] = {}
    for name, zh in QUALITY_MODULES:
        modules[name] = {
            "zh": zh,
            "mean": _mean_optional([a["modules"].get(name) for a in axes]),
        }
    return {
        "rows": len(rows),
        "groups": len(groups),
        "mean_S_fp": _mean_optional([a["S_fp"] for a in axes]),
        "mean_quality": _mean_optional([a["quality"] for a in axes]),
        "mean_coverage": _mean_optional([a["coverage"] for a in axes]),
        "mean_total_penalty": _mean_optional([a["total_penalty"] for a in axes]),
        "score_gate_pass_rate": _rate_optional([a["score_gate_passed"] for a in axes]),
        "penalty_gate_pass_rate": _rate_optional([a["penalty_gate_passed"] for a in axes]),
        "both_gates_pass_rate": _rate_optional([a["both_passed"] for a in axes]),
        "modules": modules,
    }


def _delta(later: Optional[float], earlier: Optional[float]) -> Optional[float]:
    if later is None or earlier is None:
        return None
    return round(later - earlier, 6)


def _lift_between(later: Dict[str, Any], earlier: Dict[str, Any]) -> Dict[str, Any]:
    modules: Dict[str, Optional[float]] = {}
    later_m = later.get("modules") or {}
    earlier_m = earlier.get("modules") or {}
    for name, _zh in QUALITY_MODULES:
        modules[name] = _delta(
            (later_m.get(name) or {}).get("mean"),
            (earlier_m.get(name) or {}).get("mean"),
        )
    return {
        "S_fp": _delta(later.get("mean_S_fp"), earlier.get("mean_S_fp")),
        "quality": _delta(later.get("mean_quality"), earlier.get("mean_quality")),
        "coverage": _delta(later.get("mean_coverage"), earlier.get("mean_coverage")),
        "total_penalty": _delta(later.get("mean_total_penalty"), earlier.get("mean_total_penalty")),
        "score_gate_pass_rate": _delta(
            later.get("score_gate_pass_rate"), earlier.get("score_gate_pass_rate")
        ),
        "penalty_gate_pass_rate": _delta(
            later.get("penalty_gate_pass_rate"), earlier.get("penalty_gate_pass_rate")
        ),
        "both_gates_pass_rate": _delta(
            later.get("both_gates_pass_rate"), earlier.get("both_gates_pass_rate")
        ),
        "modules": modules,
    }


def _group_mean_axes(rows: List[Dict[str, Any]]) -> Dict[str, Optional[float]]:
    axes = [extract_axis_scores(rec) for rec in rows]
    out: Dict[str, Optional[float]] = {
        "S_fp": _mean_optional([a["S_fp"] for a in axes]),
        "quality": _mean_optional([a["quality"] for a in axes]),
        "coverage": _mean_optional([a["coverage"] for a in axes]),
        "total_penalty": _mean_optional([a["total_penalty"] for a in axes]),
    }
    for name, _zh in QUALITY_MODULES:
        out[name] = _mean_optional([a["modules"].get(name) for a in axes])
    return out


def _paired_lift(rows: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    """同一原文内：改写均值减去注入原文。再对有原文的组取平均。"""
    buckets: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
    for rec in rows:
        gid = str(rec.get("group_id") or "")
        if not gid:
            continue
        slot = buckets.setdefault(gid, {"original": [], "rewrite": []})
        slot["original" if _is_original(rec) else "rewrite"].append(rec)

    deltas: Dict[str, List[float]] = {
        "S_fp": [],
        "quality": [],
        "coverage": [],
        "total_penalty": [],
    }
    for name, _zh in QUALITY_MODULES:
        deltas[name] = []
    best_deltas: Dict[str, List[float]] = {k: [] for k in deltas}
    paired = 0
    best_higher = 0
    best_lower = 0
    best_tied = 0
    for slot in buckets.values():
        if not slot["original"] or not slot["rewrite"]:
            continue
        paired += 1
        orig = _group_mean_axes(slot["original"])
        rew = _group_mean_axes(slot["rewrite"])
        for key, bucket in deltas.items():
            d = _delta(rew.get(key), orig.get(key))
            if d is not None:
                bucket.append(d)
        best = max(slot["rewrite"], key=lambda rec: extract_axis_scores(rec)["S_fp"] or -1.0)
        best_axes = _group_mean_axes([best])
        for key, bucket in best_deltas.items():
            d = _delta(best_axes.get(key), orig.get(key))
            if d is not None:
                bucket.append(d)
        sfp_delta = _delta(best_axes.get("S_fp"), orig.get("S_fp"))
        if sfp_delta is None:
            continue
        if sfp_delta > 0:
            best_higher += 1
        elif sfp_delta < 0:
            best_lower += 1
        else:
            best_tied += 1

    def pack(src: Dict[str, List[float]]) -> Dict[str, Any]:
        modules = {name: _mean(src[name]) for name, _zh in QUALITY_MODULES}
        blob = {
            "groups": paired,
            "S_fp": _mean(src["S_fp"]),
            "quality": _mean(src["quality"]),
            "coverage": _mean(src["coverage"]),
            "total_penalty": _mean(src["total_penalty"]),
            "modules": modules,
        }
        if src is best_deltas:
            blob["groups_best_higher"] = best_higher
            blob["groups_best_lower"] = best_lower
            blob["groups_best_tied"] = best_tied
        return blob

    return {"mean_rewrite": pack(deltas), "best_rewrite": pack(best_deltas)}


def summarize_score_lift(
    rows: Iterable[Dict[str, Any]],
    *,
    previous_rewrites: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """质量轴、模块分和总分：改写相对原文，以及相对上一轮改写均值。"""
    materialized = list(rows)
    rewrites = [rec for rec in materialized if not _is_original(rec)]
    originals = [rec for rec in materialized if _is_original(rec)]
    rewrite_snap = _snapshot(rewrites)
    original_snap = _snapshot(originals)
    paired = _paired_lift(materialized)
    versus_previous = None
    if previous_rewrites:
        versus_previous = _lift_between(rewrite_snap, previous_rewrites)
    return {
        "note": (
            "rewrites / originals 是本轮采样时裁判打的分，不是本轮梯度更新之后重新生成的。"
            "展示用的提升是 best_rewrite_lift_vs_original：每组只取总分最高的一条改写，减去该原文，再对组取平均。"
            "lift_vs_original 仍是组内全部改写的均值减原文。"
            "lift_vs_previous_round 是本轮改写均值减上一轮改写均值；两边原文集合不同时，这是总体水平差。"
            "质量轴是 quality_base_score。模块分缺省时对应提升为 null，新采样会写入 module_scores。"
        ),
        "rewrites": rewrite_snap,
        "originals": original_snap,
        "lift_vs_original": paired["mean_rewrite"],
        "best_rewrite_lift_vs_original": paired["best_rewrite"],
        "lift_vs_previous_round": versus_previous,
    }


def summarize_jsonl(path: JsonPath) -> Dict[str, Any]:
    p = Path(path)
    summary = summarize_rows(read_jsonl(p))
    summary["path"] = str(p.resolve())
    return summary


HUMAN_CHECKLIST = (
    "抽看改写是否编造原文没有的事实",
    "主干单品是否对称稳定、能否直接当出图 prompt",
    "是否明显靠写长涨分",
    "得分门与惩罚门通过率是否好于上一轮抽检",
)


def build_round_accept(
    *,
    round_idx: int,
    policy_dir: Path,
    ref_dir: str,
    epochs: float,
    data_summary: Dict[str, Any],
    score_lift: Optional[Dict[str, Any]] = None,
    sft_dir: Optional[Path] = None,
    note: str = "",
) -> Dict[str, Any]:
    return {
        "round": int(round_idx),
        "policy_dir": str(Path(policy_dir).resolve()),
        "ref_dir": ref_dir,
        "sft_dir": str(Path(sft_dir).resolve()) if sft_dir else None,
        "epochs_this_round": float(epochs),
        "cold_start": {
            "dual_head_rm": "once",
            "sft": "once",
            "grpo": "short_rounds",
            "kl_ref": "frozen_at_cold_start",
        },
        "data": data_summary,
        "score_lift": score_lift,
        "human_checklist": list(HUMAN_CHECKLIST),
        "note": note
        or (
            "data 与 score_lift 统计的是当前 phase_b 上采样时的裁判分，不是本轮权重更新之后重新写出来的表现。"
            "score_lift.lift_vs_original 是改写相对同组原文的质量轴、模块分和总分提升；"
            "lift_vs_previous_round 是相对上一轮改写均值的提升。"
            "验收刚写入的 policy 请用 policy_dir 重新 K 路抽检。"
        ),
    }


def write_json(path: JsonPath, obj: Dict[str, Any]) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    return out
