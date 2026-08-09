"""
将 S_fp / R_content 全链路拆解为符号公式 + 参数表 + 本条代入值。
公式展示一律使用字母，数值仅出现在 parameters / substitution 字段。
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# 符号表（全链路统一命名）
# ---------------------------------------------------------------------------
FORMULA_SYMBOLS: Dict[str, str] = {
    "C": "覆盖度轴得分，适用 coverage 指标的算术平均",
    "Q_u": "质量轴未加权均分",
    "Q_w": "质量模块加权均分",
    "Q": "质量有效分 quality_effective",
    "w_c": "覆盖度轴权重（spec score_axes.coverage_score.weight）",
    "w_q": "质量轴权重（spec score_axes.quality_score.weight）",
    "w_i": "各 quality 子模块权重（spec quality_module_weights）",
    "cap_q": "质量分上限 quality_cap",
    "cap_t": "总分上限 total_cap",
    "s_fp_base": "长度校正前的内容主分",
    "L": "eval_prose 字符数（strip 后正文长度）",
    "x": "对数长度 x = ln(1 + L)",
    "x_0": "留出集对数长度中心 log_len_center（spec holdout_regression）",
    "L_ref": "基准字符长度 L_ref = exp(x_0) - 1",
    "a": "长度斜率（spec holdout_regression.a，留出集拟合）",
    "Δ_len": "长度校正量 Δ_len = a · (x - x_0)",
    "S_fp": "最终综合分 total_score",
    "P̄": "惩罚项算术平均 total_penalty",
    "γ": "惩罚软并入系数 gamma_penalty（spec r_content_for_rl）",
    "β": "组内长度修正系数 beta_z_len（spec r_content_for_rl）",
    "z_len": "组内 log 长度 z-score（GRPO 同组多条时）",
    "τ_s": "得分门限 score_gate_min",
    "τ_p": "惩罚门限 penalty_gate_max",
    "R_content": "RL/GRPO 内容主导奖励标量",
}

# ---------------------------------------------------------------------------
# 两种可配置「模式」的设计说明（公式层）
# ---------------------------------------------------------------------------
LENGTH_DISENTANGLE_MODES: Dict[str, Dict[str, str]] = {
    "centered_slope": {
        "name_zh": "居中斜率（当前默认）",
        "formula": "Δ_len = a · (x - x_0)，S_fp = clip(s_fp_base - Δ_len, 0, 1)",
        "when_to_use": "生产评分与门限；以留出集典型长度 x_0 为锚，只校正相对偏长/偏短。",
        "interpretation_zh": (
            "在 L = L_ref 处 Δ_len = 0，不改动内容分；"
            "比典型更长 → Δ_len > 0 → 扣分（抑制写长刷分）；"
            "比典型更短 → Δ_len < 0 → 略加分（奖励同等信息量下更精炼）。"
            "相对 legacy_regression，不会在全体样本上叠加常数截距 b 带来的系统偏移。"
        ),
    },
    "legacy_regression": {
        "name_zh": "经典回归残差",
        "formula": "pred = a · x + b，S_fp = clip(s_fp_base - pred, 0, 1)",
        "when_to_use": "离线 ODIN 复现或研究；需同时拟合 a 与 b。",
        "interpretation_zh": (
            "从 s_fp_base 中减去「长度线性模型 pred 预测的全部分数」，含截距 b。"
            "所有样本都会被减去与长度相关的仿射项，短文本也可能被整体抬高。"
            "对门限业务不够直观，故现行 S_fp 默认不用此模式。"
        ),
    },
}

R_CONTENT_PENALTY_MERGE: Dict[str, str] = {
    "name_zh": "乘性折扣（唯一方式）",
    "formula": "r_soft = clip(S_fp · (1 - γ · P̄), 0, 1)",
    "interpretation_zh": (
        "把 P̄ 当作质量折扣率：P̄ 越高，保留比例 (1-γ·P̄) 越低，惩罚随 S_fp 同比缩放。"
        "当前 γ=0 时不生效，P̄ 仅用于 penalty_gate。"
    ),
}


def explain_length_mode(mode: str) -> Dict[str, str]:
    return LENGTH_DISENTANGLE_MODES.get(mode, LENGTH_DISENTANGLE_MODES["centered_slope"])


def explain_penalty_merge() -> Dict[str, str]:
    return dict(R_CONTENT_PENALTY_MERGE)


def build_mode_explanations(
    *,
    holdout_mode: str,
    gamma: float,
    has_group_z_len: bool,
) -> Dict[str, Any]:
    """汇总当前样本/ spec 下各模式说明与生效状态。"""
    len_mode = explain_length_mode(holdout_mode)
    pen_mode = explain_penalty_merge()
    return {
        "length_disentangle": {
            "active_mode": holdout_mode,
            **len_mode,
        },
        "r_content_penalty_merge": {
            "penalty_merge": "multiply",
            "gamma": gamma,
            "effective": gamma > 0,
            **pen_mode,
            "effective_note_zh": (
                "γ=0：惩罚不进入 R_content，P̄ 仅用于 penalty_gate。"
                if gamma <= 0
                else f"γ={gamma}：r_soft = clip(S_fp·(1-γ·P̄))。"
            ),
        },
        "r_content_evaluation_context": {
            "single_sample": {
                "formula": "R_content = r_soft（无 z_len）",
                "interpretation_zh": "单条 evaluate_text；不做组内长度相对比较。",
            },
            "grpo_group": {
                "formula": "R_content = clip(r_soft - β · z_len, 0, 1)",
                "interpretation_zh": (
                    "同 prompt 下 K 个候选并行评分后，对 log 长度做组内 z-score；"
                    "相对更长者 z_len>0 略降 R_content，使 GRPO 组内对比时长度-neutral。"
                ),
                "active_this_sample": has_group_z_len,
            },
        },
    }


def _r(x: float, nd: int = 4) -> float:
    return round(float(x), nd)


def length_reference_char_len(log_len_center: float) -> int:
    return int(round(math.expm1(float(log_len_center))))


def length_adjustment_per_1000_chars(char_len: int, slope_a: float) -> float:
    c = max(0, int(char_len))
    if c <= 0:
        return 0.0
    return float(slope_a) * 1000.0 / (1.0 + c)


def interpret_length_disentangle(
    char_len: int,
    length_disentangle: Dict[str, Any],
    hold_cfg: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    hold_cfg = hold_cfg or {}
    ld = length_disentangle or {}
    a = float(ld.get("slope_a") or hold_cfg.get("a") or 0.0)
    center_ll = ld.get("log_len_center")
    if center_ll is None and hold_cfg.get("log_len_center") is not None:
        center_ll = float(hold_cfg["log_len_center"])
    ref_chars = length_reference_char_len(float(center_ll)) if center_ll is not None else None
    delta_chars = (char_len - ref_chars) if ref_chars is not None else None
    component = float(ld.get("length_component") or 0.0)
    per_1k = length_adjustment_per_1000_chars(char_len, a) if ld.get("applied") else 0.0
    log_len = ld.get("log_len")

    if not ld.get("applied"):
        interpretation = "长度去相关未启用：S_fp = s_fp_base。"
    elif abs(component) < 1e-6:
        interpretation = "L ≈ L_ref，故 Δ_len ≈ 0，S_fp ≈ s_fp_base。"
    elif component > 0:
        interpretation = (
            f"L > L_ref（ΔL = L - L_ref = {delta_chars:+d}），"
            f"Δ_len = a·(x - x_0) > 0，从 s_fp_base 扣 Δ_len。"
            if delta_chars is not None
            else "Δ_len = a·(x - x_0) > 0，从 s_fp_base 扣分。"
        )
    else:
        interpretation = (
            f"L < L_ref（ΔL = {delta_chars:+d}），"
            f"Δ_len = a·(x - x_0) < 0，S_fp 略高于 s_fp_base。"
            if delta_chars is not None
            else "Δ_len = a·(x - x_0) < 0，S_fp 略高于 s_fp_base。"
        )

    return {
        "formula_symbolic": "Δ_len = a · (x - x_0)，其中 x = ln(1 + L)",
        "formula_S_fp": "S_fp = clip(s_fp_base - Δ_len, 0, 1)",
        "eval_prose_char_len": char_len,
        "reference_char_len": ref_chars,
        "char_len_delta_vs_reference": delta_chars,
        "substitution": {
            "L": char_len,
            "L_ref": ref_chars,
            "x": log_len,
            "x_0": center_ll,
            "a": a,
            "Δ_len": ld.get("length_component"),
            "per_1000_chars": _r(per_1k, 6),
        },
        "interpretation_zh": interpretation,
    }


def build_r_content_formula_steps(r_content: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not r_content.get("enabled"):
        return []

    steps: List[Dict[str, Any]] = []
    s_fp = float(r_content.get("S_fp") or 0.0)
    gamma = float(r_content.get("gamma_penalty") or 0.0)
    penalty = float(r_content.get("total_penalty") or 0.0)
    r_soft = float(r_content.get("r_after_soft_penalty") or s_fp)
    beta_z = float(r_content.get("beta_z_len") or 0.0)
    z_len = r_content.get("z_len")
    r_final = float(r_content.get("R_content") or r_soft)

    steps.append(
        {
            "step": 1,
            "id": "r_content_input",
            "label_zh": "RL 奖励输入",
            "formula": "r_in = S_fp",
            "value": _r(s_fp, 6),
        }
    )

    pen_expl = explain_penalty_merge()
    if gamma > 0:
        steps.append(
            {
                "step": 2,
                "id": "penalty_soft_merge",
                "label_zh": "惩罚软并入（multiply）",
                "formula": pen_expl["formula"],
                "mode_explanation_zh": pen_expl["interpretation_zh"],
                "value": _r(r_soft, 6),
                "substitution": {"S_fp": s_fp, "γ": gamma, "P̄": penalty},
            }
        )
    else:
        steps.append(
            {
                "step": 2,
                "id": "penalty_soft_merge",
                "label_zh": "惩罚软并入（multiply）",
                "formula": "r_soft = S_fp（γ = 0；P̄ 仅用于 penalty_gate）",
                "mode_explanation_zh": pen_expl["interpretation_zh"],
                "value": _r(r_soft, 6),
                "substitution": {"γ": gamma, "P̄": penalty},
            }
        )

    if z_len is not None and beta_z != 0.0:
        zf = float(z_len)
        steps.append(
            {
                "step": 3,
                "id": "group_z_len",
                "label_zh": "组内长度 z-score 修正（GRPO）",
                "formula": "R_content = clip(r_soft - β · z_len, 0, 1)",
                "value": _r(r_final, 6),
                "substitution": {"r_soft": r_soft, "β": beta_z, "z_len": _r(zf, 6)},
            }
        )
    else:
        steps.append(
            {
                "step": 3,
                "id": "group_z_len",
                "label_zh": "组内长度修正",
                "formula": "R_content = r_soft（单条评分，无 z_len）",
                "value": _r(r_final, 6),
            }
        )

    return steps


def refresh_score_formula_r_content(evaluation: Dict[str, Any]) -> None:
    sf = evaluation.get("score_formula")
    rc = evaluation.get("r_content") or {}
    if not isinstance(sf, dict) or not rc.get("enabled"):
        return
    base_steps = [s for s in (sf.get("steps") or []) if int(s.get("step") or 0) < 9]
    merged = base_steps + build_r_content_formula_steps(rc)
    for i, st in enumerate(merged, start=1):
        st["step"] = i
    sf["steps"] = merged
    outputs = sf.get("outputs") or {}
    outputs["R_content"] = rc.get("R_content")
    sf["outputs"] = outputs


def _formula_chain_symbolic() -> List[str]:
    return [
        "C = (1/n_c) · Σ coverage_i",
        "Q_w = (Σ w_i · m_i) / (Σ w_i)",
        "Q = min(Q_w, cap_q)",
        "s_fp_base = min(w_c · C + w_q · Q, cap_t)",
        "x = ln(1 + L)",
        "Δ_len = a · (x - x_0)",
        "S_fp = clip(s_fp_base - Δ_len, 0, 1)",
        "R_content = clip(r_soft - β · z_len, 0, 1)，其中 r_soft = S_fp 或 clip(S_fp · (1 - γ·P̄))",
    ]


def build_score_formula_breakdown(
    *,
    spec: Dict[str, Any],
    coverage_score: float,
    quality_axis_unweighted: float,
    quality_weighted: float,
    quality_effective: float,
    quality_cap: float,
    total_penalty: float,
    weights: Dict[str, float],
    s_fp_base: float,
    total_cap: float,
    char_len: int,
    length_disentangle: Dict[str, Any],
    fashion_prompt_score: float,
    r_content: Dict[str, Any],
    module_scores: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    w_cov = float(weights.get("coverage", 0.2))
    w_qual = float(weights.get("quality", 0.8))
    hold_cfg = (spec.get("r_content_for_rl") or {}).get("holdout_regression") or {}
    rcfg = spec.get("r_content_for_rl") or {}
    gates = spec.get("optimization_gates") or {}
    length_interp = interpret_length_disentangle(char_len, length_disentangle, hold_cfg)

    a = float(hold_cfg.get("a") or length_disentangle.get("slope_a") or 0.0)
    x_0 = hold_cfg.get("log_len_center") or length_disentangle.get("log_len_center")
    gamma = float(rcfg.get("gamma_penalty") or 0.0)
    beta_z = float(rcfg.get("beta_z_len") or 0.0)
    tau_s = float(gates.get("score_gate_min", 0.7))
    tau_p = float(gates.get("penalty_gate_max", 0.5))

    cap_reasons: List[str] = []
    if module_scores:
        if module_scores.get("BindingAccuracy", {}).get("score", 1.0) < 0.5:
            cap_reasons.append("BindingAccuracy 模块分 < 0.5 → cap_q 收紧")

    uncapped = _r(w_cov * coverage_score + w_qual * quality_effective, 4)
    length_component = float(length_disentangle.get("length_component") or 0.0)
    ld_applied = bool(length_disentangle.get("applied"))
    log_len = length_disentangle.get("log_len")
    holdout_mode = str(hold_cfg.get("mode", "centered_slope"))

    parameters = {
        "w_c": w_cov,
        "w_q": w_qual,
        "cap_q": _r(quality_cap),
        "cap_t": _r(total_cap),
        "a": a,
        "x_0": x_0,
        "L_ref": length_interp.get("reference_char_len"),
        "γ": gamma,
        "β": beta_z,
        "τ_s": tau_s,
        "τ_p": tau_p,
    }

    steps: List[Dict[str, Any]] = [
        {
            "step": 1,
            "id": "coverage_axis",
            "label_zh": "覆盖度轴 C",
            "formula": "C = (1/n_c) · Σ coverage_i",
            "value": _r(coverage_score),
            "substitution": {"C": _r(coverage_score)},
        },
        {
            "step": 2,
            "id": "quality_weighted",
            "label_zh": "质量模块加权 Q_w",
            "formula": "Q_w = (Σ w_i · m_i) / (Σ w_i)",
            "value": _r(quality_weighted),
            "substitution": {"Q_w": _r(quality_weighted)},
        },
        {
            "step": 3,
            "id": "quality_effective",
            "label_zh": "质量有效分 Q",
            "formula": "Q = min(Q_w, cap_q)",
            "value": _r(quality_effective),
            "substitution": {"Q_w": _r(quality_weighted), "cap_q": _r(quality_cap), "Q": _r(quality_effective)},
            "cap_reasons": cap_reasons or None,
        },
        {
            "step": 4,
            "id": "s_fp_base",
            "label_zh": "内容主分 s_fp_base",
            "formula": "s_fp_base = min(w_c · C + w_q · Q, cap_t)",
            "value": _r(s_fp_base),
            "substitution": {
                "w_c": w_cov,
                "C": _r(coverage_score),
                "w_q": w_qual,
                "Q": _r(quality_effective),
                "cap_t": _r(total_cap),
                "uncapped": uncapped,
                "s_fp_base": _r(s_fp_base),
            },
        },
        {
            "step": 5,
            "id": "length_disentangle",
            "label_zh": "长度去相关",
            "formula": (
                "Δ_len = a · (x - x_0)，x = ln(1+L)；S_fp = clip(s_fp_base - Δ_len, 0, 1)"
                if ld_applied and holdout_mode == "centered_slope"
                else (
                    "pred = a·x + b；S_fp = clip(s_fp_base - pred, 0, 1)"
                    if ld_applied
                    else "S_fp = s_fp_base（holdout 长度去相关关闭）"
                )
            ),
            "mode": holdout_mode if ld_applied else None,
            "mode_explanation_zh": explain_length_mode(holdout_mode)["interpretation_zh"] if ld_applied else None,
            "value": _r(fashion_prompt_score),
            "substitution": {
                "L": char_len,
                "x": log_len,
                "x_0": x_0,
                "a": a,
                "Δ_len": _r(length_component, 6),
                "s_fp_base": _r(s_fp_base),
                "S_fp": _r(fashion_prompt_score),
            },
            "length": length_interp,
        },
        {
            "step": 6,
            "id": "S_fp",
            "label_zh": "最终 S_fp",
            "formula": "S_fp = total_score",
            "value": _r(fashion_prompt_score),
        },
        {
            "step": 7,
            "id": "penalty_gate",
            "label_zh": "惩罚门限（不进 S_fp）",
            "formula": "penalty_gate: P̄ ≤ τ_p",
            "value": _r(total_penalty, 4),
            "substitution": {"P̄": _r(total_penalty, 4), "τ_p": tau_p, "passed": total_penalty <= tau_p},
        },
    ]

    r_steps = build_r_content_formula_steps(r_content)
    for i, st in enumerate(r_steps, start=8):
        st["step"] = i
        steps.append(st)

    r_val = r_content.get("R_content") if r_content.get("enabled") else None
    has_z = r_content.get("z_len") is not None

    return {
        "spec_name": spec.get("name"),
        "spec_version": spec.get("version"),
        "symbols": FORMULA_SYMBOLS,
        "mode_explanations": build_mode_explanations(
            holdout_mode=holdout_mode,
            gamma=gamma,
            has_group_z_len=has_z,
        ),
        "parameters": parameters,
        "formula_chain_symbolic": _formula_chain_symbolic(),
        "formula_one_liner": (
            "S_fp = clip(min(w_c·C + w_q·Q, cap_t) - a·(ln(1+L) - x_0), 0, 1); "
            "R_content = clip(r_soft - β·z_len, 0, 1)"
        ),
        "outputs": {
            "S_fp": _r(fashion_prompt_score),
            "R_content": None if r_val is None else _r(float(r_val), 6),
            "P̄": _r(total_penalty, 4),
        },
        "steps": steps,
    }
