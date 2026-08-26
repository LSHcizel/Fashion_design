"""
ODIN 内容通道：单条 R_content = s_fp_base；GRPO 组内才减 β·z_len。
长度回归默认不进 S_fp / R_content，只作泄漏诊断（ρ(R, log_len)）。
penalties.total_penalty（P̄）默认不参与分数，仅用于 penalty_gate。

参考 ICML 2024 ODIN：RL 只用内容通道，丢掉长度可解释部分。
本仓库档 1 用裁判内容主分近似 r^Q；档 3 见 ``training/odin_rm``（双头 RM，GRPO 只用 r_Q）。
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .score_formula import refresh_score_formula_r_content


def char_len_of(text: str) -> int:
    return len((text or "").strip())


def log_len_char(text: str) -> float:
    return math.log1p(float(max(0, char_len_of(text))))


def _clip01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def _soft_penalty_merge(r: float, total_penalty: float, gamma: float) -> float:
    """乘性并入 P̄：clip(r · (1 - γ·P̄))。γ=0 时不改变 r。"""
    p = float(total_penalty or 0.0)
    g = float(gamma)
    return _clip01(r * (1.0 - g * p))


def _holdout_mixes_into_score(hold: Dict[str, Any]) -> bool:
    if not bool(hold.get("enabled")):
        return False
    if "mix_into_score" in hold:
        return bool(hold.get("mix_into_score"))
    return True


def pearson_corr(xs: Sequence[float], ys: Sequence[float]) -> Optional[float]:
    """批内 Pearson ρ；n<2 或方差为 0 时返回 None。"""
    n = min(len(xs), len(ys))
    if n < 2:
        return None
    xv = [float(x) for x in xs[:n]]
    yv = [float(y) for y in ys[:n]]
    mx = sum(xv) / n
    my = sum(yv) / n
    vxx = sum((x - mx) ** 2 for x in xv)
    vyy = sum((y - my) ** 2 for y in yv)
    if vxx < 1e-18 or vyy < 1e-18:
        return None
    cov = sum((x - mx) * (y - my) for x, y in zip(xv, yv))
    return float(cov / math.sqrt(vxx * vyy))


def summarize_length_leakage(evaluations: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    """
    ODIN Table 1 的本仓库对照：奖励与对数长度的 Pearson。
    内容通道健康时 ρ(R_content, log_len) 应接近 0。
    """
    bases: List[float] = []
    rewards: List[float] = []
    log_lens: List[float] = []
    for ev in evaluations:
        scores = ev.get("scores") or {}
        rc = ev.get("r_content") or {}
        base = scores.get("s_fp_base")
        if base is None:
            base = ev.get("total_score")
        rew = rc.get("R_content") if rc.get("enabled", True) else base
        ll = rc.get("log_len")
        if ll is None:
            prose = ev.get("eval_prose") or ev.get("text_description") or ""
            ll = math.log1p(float(len(str(prose).strip())))
        if base is None or rew is None:
            continue
        bases.append(float(base))
        rewards.append(float(rew))
        log_lens.append(float(ll))
    rho_base = pearson_corr(bases, log_lens)
    rho_r = pearson_corr(rewards, log_lens)
    return {
        "n": len(rewards),
        "pearson_s_fp_base_vs_log_len": None if rho_base is None else round(rho_base, 4),
        "pearson_R_content_vs_log_len": None if rho_r is None else round(rho_r, 4),
        "target_zh": "接近 0 表示内容通道几乎不靠写长涨分（ODIN 用 r^Q 对长度的相关作验收）。",
    }


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
        内容主分。现行口径等于 s_fp_base / total_score。
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
    beta_z = float(cfg.get("beta_z_len", 0.0))
    hold = cfg.get("holdout_regression") or {}

    c_len = char_len_of(text_description)
    ll = math.log1p(float(c_len))

    length_pred: Optional[float] = None
    r_after_resid = float(S_fp)
    mix = _holdout_mixes_into_score(hold)
    if mix and not bool(cfg.get("length_already_applied")):
        disent = apply_length_disentangle(S_fp, c_len, hold)
        length_pred = disent.get("length_component")
        r_after_resid = float(disent["adjusted_score"])
    elif mix and bool(cfg.get("length_already_applied")):
        r_after_resid = float(S_fp)

    r_soft = _soft_penalty_merge(r_after_resid, total_penalty, gamma)

    z_applied = z_len if (z_len is not None and beta_z != 0.0) else None
    r_final = r_soft
    if z_applied is not None:
        r_final = _clip01(r_soft - beta_z * float(z_applied))

    if not gamma:
        penalty_note = "γ=0，P̄ 不进 R_content（仅 penalty_gate）。"
    else:
        penalty_note = "r_soft = clip(s_fp_base·(1 - γ·P̄))。"
    if z_applied is not None:
        z_note = f"R_content = clip(r_soft - β·z_len)，z_len={float(z_applied):.4f}。"
    else:
        z_note = "无组内 z_len：R_content = s_fp_base。"
    interpretation_zh = f"{penalty_note}{z_note}"

    return {
        "enabled": True,
        "odin_reference": "ICML 2024 ODIN: RL uses content channel only. "
        "Here r^Q ≈ s_fp_base; length is diagnostic except GRPO β·z_len.",
        "odin_stage": int(cfg.get("odin_stage") or 1),
        "S_fp": round(float(S_fp), 6),
        "total_penalty": round(float(total_penalty or 0.0), 6),
        "gamma_penalty": gamma,
        "penalty_merge": "multiply",
        "beta_z_len": beta_z,
        "char_len": c_len,
        "log_len": round(ll, 6),
        "est_tokens_char_div_4": round(c_len / 4.0, 2),
        "holdout_length_prediction": None if length_pred is None else round(float(length_pred), 6),
        "length_mixed_into_score": mix,
        "r_after_length_residual": round(r_after_resid, 6),
        "r_after_soft_penalty": round(r_soft, 6),
        "z_len": None if z_applied is None else round(float(z_applied), 6),
        "R_content": round(r_final, 6),
        "interpretation_zh": interpretation_zh,
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
    if int(cfg.get("odin_stage") or 1) >= 3:
        leakage = summarize_length_leakage(evaluations)
        for ev in evaluations:
            ev["odin_diagnostics"] = leakage
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
    sfps: List[float] = []
    for e in evaluations:
        base = (e.get("scores") or {}).get("s_fp_base")
        if base is None:
            base = e.get("total_score", 0.0)
        sfps.append(float(base or 0.0))

    for i, ev in enumerate(evaluations):
        ev["r_content"] = build_r_content_payload(
            texts[i],
            sfps[i],
            penalties[i],
            cfg,
            z_len=zs[i],
        )
        refresh_score_formula_r_content(ev)

    leakage = summarize_length_leakage(evaluations)
    for ev in evaluations:
        ev["odin_diagnostics"] = leakage


def fit_holdout_length_regression(
    S_fp_values: Sequence[float],
    char_lens: Sequence[int],
) -> Tuple[float, float]:
    """
    留出集上拟合 S_fp ≈ a * log(1 + len) + b（简单最小二乘）。
    仅当 spec holdout_regression.mix_into_score=true 时才会扣进分数。
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
    """拟合 centered slope：诊断用 Δ_len = a * (log1p(len) - log_len_center)。"""
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
    长度回归诊断。mix_into_score=true 时才从分数中减去长度分量；
    现行默认只记录 Δ_len，S_fp 仍等于 s_fp_base。
    """
    hold_cfg = hold_cfg or {}
    ll = math.log1p(float(max(0, int(char_len))))
    mix = _holdout_mixes_into_score(hold_cfg)
    if not bool(hold_cfg.get("enabled")):
        return {
            "adjusted_score": round(float(s_fp), 4),
            "length_component": 0.0,
            "log_len": round(ll, 6),
            "applied": False,
            "role": "off",
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

    if mix:
        adjusted = _clip01(float(s_fp) - component)
        applied = True
        role = "score"
    else:
        adjusted = round(float(s_fp), 4)
        applied = False
        role = "diagnostic"
    out: Dict[str, Any] = {
        "adjusted_score": round(adjusted, 4) if mix else round(float(s_fp), 4),
        "length_component": round(component, 6),
        "log_len": round(ll, 6),
        "slope_a": a,
        "mode": mode,
        "applied": applied,
        "role": role,
    }
    if center is not None:
        out["log_len_center"] = round(center, 6)
    return out
