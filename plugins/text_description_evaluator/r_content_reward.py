"""
第 2 步 / ODIN 思想：在沿用既有 fashion_prompt_score（S_fp）的前提下，
构造供 RL（如 GRPO）使用的内容主导标量 R_content，削弱「越长越容易涨分」的单一通道优化。
penalties.total_penalty（P̄）默认不参与 S_fp / R_content，仅用于 penalty_gate；若 spec 将 gamma_penalty>0 则可软并入 R_content。

- 评判准则与 S_fp 合成仍完全由 design_text_evaluator_api.evaluate_text 负责；本模块只做**后处理标量**。
- 参考 ICML 2024 ODIN：RL 阶段避免让「长度泄漏」主导梯度 → 显式记入长度诊断、软并入惩罚通道、可选组内 z_len 与留出集长度回归残差。

见项目计划文档「落地到本仓库」三档公式。
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Sequence, Tuple


def char_len_of(text: str) -> int:
    return len((text or "").strip())


def log_len_char(text: str) -> float:
    return math.log1p(float(max(0, char_len_of(text))))


def _clip01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def _soft_penalty_merge(
    r: float,
    total_penalty: float,
    gamma: float,
    formula: str,
) -> float:
    """方案第 2 步：R ∋ 冗长通道 — 乘性并入 P̄ 或 clip 减法。"""
    p = float(total_penalty or 0.0)
    g = float(gamma)
    if formula == "subtract_clip":
        return _clip01(r - g * p)
    # default: multiply
    return _clip01(r * (1.0 - g * p))


def build_r_content_payload(
    text_description: str,
    S_fp: float,
    total_penalty: float,
    cfg: Optional[Dict[str, Any]] = None,
    *,
    z_len: Optional[float] = None,
) -> Dict[str, Any]:
    """
    由单次评判结果构造 r_content 块（不含组内 z_len 时可先令 z_len=None）。

    Parameters
    ----------
    text_description:
        被判分的正文（用于 char_len / log_len；与 evaluate_text 输入一致）。
    S_fp:
        与返回体 total_score / scores.fashion_prompt_score 相同。
    total_penalty:
        scores.quality_score.penalties.total_penalty。
    cfg:
        spec 中 ``r_content_for_rl`` 一段；None 时使用空 dict（全默认）。
    z_len:
        组内对 log_len 的标准分数；单条样本可为 None。
    """
    cfg = cfg or {}
    if not bool(cfg.get("enabled", True)):
        return {"enabled": False}

    gamma = float(cfg.get("gamma_penalty", 0.0))
    formula = str(cfg.get("formula", "multiply"))
    beta_z = float(cfg.get("beta_z_len", 0.0))
    hold = cfg.get("holdout_regression") or {}

    c_len = char_len_of(text_description)
    ll = math.log1p(float(c_len))

    length_pred: Optional[float] = None
    r_after_resid = float(S_fp)
    if bool(hold.get("enabled")) and not bool(cfg.get("length_already_applied")):
        disent = apply_length_disentangle(S_fp, c_len, hold)
        length_pred = disent.get("length_component")
        r_after_resid = float(disent["adjusted_score"])
    elif bool(hold.get("enabled")) and bool(cfg.get("length_already_applied")):
        r_after_resid = float(S_fp)

    r_soft = _soft_penalty_merge(r_after_resid, total_penalty, gamma, formula)

    z_applied = z_len if (z_len is not None and beta_z != 0.0) else None
    r_final = r_soft
    if z_applied is not None:
        r_final = _clip01(r_soft - beta_z * float(z_applied))

    return {
        "enabled": True,
        "odin_reference": "ICML 2024 ODIN (disentangled reward): RL uses content-dominant scalar; "
        "length diagnostics + soft penalty channel reduce length hacking vs. raw S_fp alone.",
        "S_fp": round(float(S_fp), 6),
        "total_penalty": round(float(total_penalty or 0.0), 6),
        "gamma_penalty": gamma,
        "formula": formula,
        "beta_z_len": beta_z,
        "char_len": c_len,
        "log_len": round(ll, 6),
        "est_tokens_char_div_4": round(c_len / 4.0, 2),
        "holdout_length_prediction": None if length_pred is None else round(float(length_pred), 6),
        "r_after_length_residual": round(r_after_resid, 6),
        "r_after_soft_penalty": round(r_soft, 6),
        "z_len": None if z_applied is None else round(float(z_applied), 6),
        "R_content": round(r_final, 6),
    }


def z_len_from_char_lens(char_lens: Sequence[int], *, use_log: bool = True) -> List[float]:
    """对组内每条长度做 z-score（log 域或线性域）；长度全相同返回全 0。"""
    vals = [float(c) for c in char_lens]
    if use_log:
        vals = [math.log1p(max(0.0, c)) for c in vals]
    if not vals:
        return []
    m = sum(vals) / len(vals)
    if len(vals) == 1:
        return [0.0]
    var = sum((v - m) ** 2 for v in vals) / len(vals)
    sig = math.sqrt(var)
    if sig < 1e-9:
        return [0.0 for _ in vals]
    return [(v - m) / sig for v in vals]


def apply_group_z_len_r_content(evaluations: Sequence[Dict[str, Any]], cfg: Optional[Dict[str, Any]] = None) -> None:
    """
    就地更新一批 evaluate_text 结果：为组内各条写入 z_len 并重算 R_content（需每条已有 r_content 且 enabled）。

    典型用法：同一 group_id 下 K 个候选先各 evaluate_text，再调用本函数。
    """
    cfg = cfg or {}
    if not evaluations:
        return
    use_log = bool(cfg.get("length_use_log", True))

    rows = [e.get("r_content") or {} for e in evaluations]
    if not all(isinstance(r, dict) and r.get("enabled", True) for r in rows):
        return

    char_lens = [int(r.get("char_len", 0) or 0) for r in rows]
    zs = z_len_from_char_lens(char_lens, use_log=use_log)
    texts = [str(e.get("text_description", "") or "") for e in evaluations]
    penalties = [
        float(
            (e.get("scores") or {})
            .get("quality_score", {})
            .get("penalties", {})
            .get("total_penalty", 0.0)
            or 0.0
        )
        for e in evaluations
    ]
    sfps = [float(e.get("total_score", 0.0) or 0.0) for e in evaluations]

    for i, ev in enumerate(evaluations):
        ev["r_content"] = build_r_content_payload(
            texts[i],
            sfps[i],
            penalties[i],
            cfg,
            z_len=zs[i],
        )


def fit_holdout_length_regression(
    S_fp_values: Sequence[float],
    char_lens: Sequence[int],
) -> Tuple[float, float]:
    """
    留出集上拟合 S_fp ≈ a * log(1 + len) + b（简单最小二乘）。
    将 a,b 写入 spec ``holdout_regression`` 后启用 enabled 即可在训练管线扣分长度可解释部分。
    """
    xs: List[float] = []
    ys: List[float] = []
    for s, c in zip(S_fp_values, char_lens):
        xs.append(math.log1p(float(max(0, int(c)))))
        ys.append(float(s))
    if len(xs) < 2:
        return 0.0, sum(ys) / len(ys) if ys else 0.0
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    vxx = sum((x - mx) ** 2 for x in xs)
    if vxx < 1e-12:
        return 0.0, my
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    a = cov / vxx
    b = my - a * mx
    return float(a), float(b)


def fit_holdout_length_centered(
    S_fp_values: Sequence[float],
    char_lens: Sequence[int],
) -> Tuple[float, float]:
    """拟合 centered slope：S_fp_adj = clip(S_fp - a * (log1p(len) - log_len_center))。"""
    ll = [math.log1p(float(max(0, int(c)))) for c in char_lens]
    ys = [float(s) for s in S_fp_values]
    if not ll:
        return 0.0, 0.0
    m_ll = sum(ll) / len(ll)
    m_y = sum(ys) / len(ys)
    v_ll = sum((x - m_ll) ** 2 for x in ll)
    if v_ll < 1e-12:
        return 0.0, m_ll
    cov = sum((x - m_ll) * (y - m_y) for x, y in zip(ll, ys))
    return float(cov / v_ll), float(m_ll)


def apply_length_disentangle(
    s_fp: float,
    char_len: int,
    hold_cfg: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    统一长度去相关（ODIN / holdout）：从 S_fp 中减去可由长度解释的分量。
    centered_slope：仅惩罚高于 log_len_center 的冗长；legacy_regression：减 a*log1p(len)+b。
    """
    hold_cfg = hold_cfg or {}
    ll = math.log1p(float(max(0, int(char_len))))
    if not bool(hold_cfg.get("enabled")):
        return {
            "adjusted_score": round(float(s_fp), 4),
            "length_component": 0.0,
            "log_len": round(ll, 6),
            "applied": False,
        }

    mode = str(hold_cfg.get("mode", "centered_slope"))
    a = float(hold_cfg.get("a", 0.0))
    if mode == "legacy_regression":
        b = float(hold_cfg.get("b", 0.0))
        component = a * ll + b
        center = None
    else:
        center = float(hold_cfg.get("log_len_center", ll))
        component = a * (ll - center)

    adjusted = _clip01(float(s_fp) - component)
    out: Dict[str, Any] = {
        "adjusted_score": round(adjusted, 4),
        "length_component": round(component, 6),
        "log_len": round(ll, 6),
        "slope_a": a,
        "mode": mode,
        "applied": True,
    }
    if center is not None:
        out["log_len_center"] = round(center, 6)
    return out
