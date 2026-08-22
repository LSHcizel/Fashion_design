"""
第 5 步 — 阶段 B：组内奖励后处理与 GRPO 风格优势计算。

约定（与计划文档一致）：
- 主奖励 ``R`` 使用 ``R_content``（ODIN 内容通道）；若无则回退 ``total_score``。
- 组内标准化：Â_i = (R'_i - μ_G) / (σ_G + ε)；σ_G=0 时优势全 0。
- 可选「Rewarding the Unlikely」乘性修正：r_i = R_i × (1 - β_rank × (G - rank_i) / G)，
  rank 小 = 旧策略下更易生成；可由 ``training.pi_old_ranking`` 用 HF π_old 自动算 rank，
  或由调用方传入 ``old_policy_ranks``。
"""

from __future__ import annotations

from statistics import mean, pstdev
from typing import Any, Dict, List, Literal, Optional, Sequence, Tuple


def pick_reward_scalar(record: Dict[str, Any], *, prefer: Literal["R_content", "total_score"] = "R_content") -> float:
    """从单条训练样本中取标量奖励。"""
    if prefer == "R_content":
        g = record.get("grpo") or {}
        r = g.get("reward_scalar")
        if r is not None:
            return float(r)
        r_top = record.get("R_content")
        if r_top is not None:
            return float(r_top)
        rc = record.get("r_content") or {}
        if rc.get("enabled", True) and rc.get("R_content") is not None:
            return float(rc["R_content"])
    fs = record.get("S_fp")
    if fs is not None:
        return float(fs)
    fs = record.get("fashion_prompt_score")
    if fs is not None:
        return float(fs)
    sc = record.get("scores_compact") or {}
    if sc.get("S_fp") is not None:
        return float(sc["S_fp"])
    if sc.get("fashion_prompt_score") is not None:
        return float(sc["fashion_prompt_score"])
    return 0.0


def group_baseline_advantages(rewards: Sequence[float], eps: float = 1e-8) -> Tuple[List[float], float, float]:
    """对同一组奖励做均值方差标准化，返回 (advantages, μ, σ)。"""
    vals = [float(x) for x in rewards]
    G = len(vals)
    if G == 0:
        return [], 0.0, 0.0
    mu = mean(vals)
    if G == 1:
        return [0.0], mu, 0.0
    sig = pstdev(vals)
    if sig < eps:
        return [0.0] * G, mu, sig
    return [(v - mu) / sig for v in vals], mu, sig


def skip_rank_correction_for_group(rewards: Sequence[float], *, eps: float = 1e-12) -> bool:
    """
    「安全阀」：无意义的组跳过 Rewarding the Unlikely（不加载 π_old）。

    - G<2：无法做有意义的组内相对比较；
    - 全组 R≈0：计划文档约定 R=0 不参与打折，整组无正信号时可跳过；
    - 全组 R 几乎相同：修正前后排序噪声大，且标准化优势已为 0。
    """
    vals = [float(x) for x in rewards]
    if len(vals) < 2:
        return True
    if all(v <= eps for v in vals):
        return True
    if max(vals) - min(vals) <= eps:
        return True
    return False


def apply_rank_reward_multiplier(
    rewards: Sequence[float],
    ranks: Sequence[int],
    *,
    beta_rank: float,
) -> List[float]:
    """
    r_i = R_i × (1 - β_rank × (G - rank_i) / G)。R_i==0 保持 0。
    ``ranks``：每条在组内的 rank，1=最易生成 … G=最难；须与 len(rewards) 一致。
    """
    G = len(rewards)
    out: List[float] = []
    for r, rank in zip(rewards, ranks):
        rv = float(r or 0.0)
        if abs(rv) < 1e-12:
            out.append(0.0)
            continue
        rk = int(rank)
        mult = 1.0 - float(beta_rank) * (G - rk) / float(G)
        out.append(rv * mult)
    return out


def build_group_training_rows(
    records: List[Dict[str, Any]],
    *,
    reward_key: Literal["R_content", "total_score"] = "R_content",
    beta_rank: Optional[float] = None,
    old_policy_ranks: Optional[List[int]] = None,
    rank_correction_group_meta: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    将同一 ``group_id`` 的多条样本合并为带 ``advantage`` / ``r_i`` 的训练行。

    Parameters
    ----------
    old_policy_ranks :
        若提供，须与 ``records`` 顺序一致，且为 1…G 的易→难排名；与 ``beta_rank`` 同时启用。
    rank_correction_group_meta :
        写入每条 ``rank_reward`` 的公共字段（如 ``mode``、``pi_old_model``、``skip_reason``）；
        若含 ``old_policy_mean_logprobs``（与 ``records`` 对齐的列表），会拆成每行的
        ``old_policy_mean_logprob``。
    """
    if not records:
        return []
    rewards = [pick_reward_scalar(rec, prefer=reward_key) for rec in records]
    r_for_adv = list(rewards)
    mults: Optional[List[float]] = None
    if beta_rank is not None and old_policy_ranks is not None:
        r_for_adv = apply_rank_reward_multiplier(rewards, old_policy_ranks, beta_rank=beta_rank)
        G = len(rewards)
        mults = []
        for r, rnew, rank in zip(rewards, r_for_adv, old_policy_ranks):
            if abs(r) < 1e-12:
                mults.append(1.0)
            else:
                mults.append(rnew / r if r else 1.0)

    advs, mu, sig = group_baseline_advantages(r_for_adv)
    G = len(records)
    meta_common: Dict[str, Any] = {}
    logps_list: Optional[List[float]] = None
    if rank_correction_group_meta:
        meta_common = dict(rank_correction_group_meta)
        raw_lp = meta_common.pop("old_policy_mean_logprobs", None)
        if isinstance(raw_lp, list):
            logps_list = [float(x) for x in raw_lp]
    rows: List[Dict[str, Any]] = []
    for i, rec in enumerate(records):
        rr_mean_lp = None
        if logps_list is not None and i < len(logps_list):
            rr_mean_lp = round(logps_list[i], 8)
        row = {
            "schema_version": "grpo_phase_b_v1",
            "group_id": rec.get("group_id"),
            "group_round": rec.get("group_round"),
            "candidate_index": rec.get("candidate_index"),
            "context": rec.get("context"),
            "completion": rec.get("completion"),
            "char_len": rec.get("char_len"),
            "est_tokens_char_div_4": rec.get("est_tokens_char_div_4"),
            "S_fp": rec.get("S_fp"),
            "R_content": rec.get("R_content"),
            "R_base": rewards[i],
            "r_after_rank": r_for_adv[i] if r_for_adv else rewards[i],
            "advantage": advs[i] if i < len(advs) else 0.0,
            "group_stats": {
                "G": G,
                "mean_r_for_advantage": round(mu, 8),
                "std_r_for_advantage": round(sig, 8),
                "reward_key": reward_key,
            },
            "rank_reward": {
                **meta_common,
                "beta_rank": beta_rank,
                "old_policy_rank": old_policy_ranks[i] if old_policy_ranks else None,
                "multiplier": mults[i] if mults else None,
                "old_policy_mean_logprob": rr_mean_lp,
            },
            "gates_compact": rec.get("gates_compact"),
            "scores_compact": rec.get("scores_compact"),
            "penalties": rec.get("penalties"),
            "r_content": rec.get("r_content"),
            "training_filter": rec.get("training_filter"),
            "kl_constraint": {
                "note": "阶段 B 需在策略损失中相对参考模型 π_ref 施加 KL，防止为刷 R_content 跑飞。",
            },
        }
        rows.append(row)
    return rows
