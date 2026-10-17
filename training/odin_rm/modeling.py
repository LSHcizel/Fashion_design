"""
双头奖励模型（ODIN）：共用表征 + r_Q / r_L。

r_Q 读最后一个 token 的两层映射，r_L 是线性头。都无 sigmoid、无 clip。
r_Q 的目标就是 S_fp，不减长度。长度只由 r_L 拟合 log 句长差。
两条改写的 log 句长差在 0.10 nat 以内时，r_Q 按 S_fp 排序；差到一倍时这条对不再要求 r_Q 排序。
裁判分差不到 0.10 的对不比较，并把 r_Q 分差收到 0。策略训练只取 r_Q。
"""

from __future__ import annotations

import math
from typing import Any, Dict, Optional, Tuple

import torch
import torch.nn as nn


def last_token_hidden(hidden: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
    """右 padding 时取每条最后一个非 pad token 的 hidden。"""
    idx = attention_mask.long().sum(dim=1) - 1
    idx = idx.clamp(min=0)
    batch = hidden.size(0)
    return hidden[torch.arange(batch, device=hidden.device), idx]


def batch_pearson(x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
    """可反传的 Pearson ρ；样本不足或方差为 0 时返回 0。"""
    if x.numel() < 2:
        return x.new_zeros(())
    xf = x.reshape(-1).float()
    yf = y.reshape(-1).float()
    xf = xf - xf.mean()
    yf = yf - yf.mean()
    vx = (xf * xf).sum()
    vy = (yf * yf).sum()
    denom = torch.sqrt(vx * vy)
    if float(denom.detach()) < 1e-12:
        return x.new_zeros(())
    return (xf * yf).sum() / denom


# 低于此值的裁判分差，留出集方向一致率停在 0.50，不作为输赢目标。
GAP_MARGIN = 0.10
# 达到此值后比较损失满权重。这一档的方向一致率是 0.86。
GAP_FULL = 0.20
# 高分一侧最多只长这么多，仍视为长度接近，比较损失满权重。
LENGTH_CLOSE_NAT = 0.10
# 高分一侧长到一倍时，不再用这条对要求 r_Q 排序，长度交给 r_L。
LENGTH_FAR_NAT = math.log(2.0)


def length_disentangle_term(rho_q: torch.Tensor, rho_l: torch.Tensor) -> torch.Tensor:
    """内容头与句长的相关停在 0；长度头继续吸收句长。

    ρ(r_Q, ℓ) 本身没有下界，直接最小化会把内容头推到越短越高。
    平方在 0 处梯度消失，正负相关都加损失，避免用删信息换短句。
    """
    return rho_q.square() - rho_l


def pair_gap_weight(gap_t: torch.Tensor) -> torch.Tensor:
    """裁判分差越大，越要让 r_Q 跟上。0.10 以下权重为 0，0.20 及以上为 1。"""
    g = gap_t.reshape(-1).abs()
    span = GAP_FULL - GAP_MARGIN
    return ((g - GAP_MARGIN) / span).clamp(0, 1)


def length_rank_weight(gap_ell: torch.Tensor) -> torch.Tensor:
    """高分一侧不更长，或只长一点点时，比较损失满权重。

    gap_ell = ℓ⁺ − ℓ⁻。≤ 0.10 nat 为 1（含高分更短）；
    高分一侧长到一倍时为 0。高分更短不会把权重降下去。
    """
    d = gap_ell.reshape(-1)
    span = LENGTH_FAR_NAT - LENGTH_CLOSE_NAT
    return ((LENGTH_FAR_NAT - d) / span).clamp(0, 1)


def odin_rm_loss(
    r_q_win: torch.Tensor,
    r_l_win: torch.Tensor,
    r_q_lose: torch.Tensor,
    r_l_lose: torch.Tensor,
    log_len_win: torch.Tensor,
    log_len_lose: torch.Tensor,
    teacher_win: torch.Tensor,
    teacher_lose: torch.Tensor,
    *,
    head_q: nn.Module,
    head_l: nn.Module,
    lambda_corr: float = 1.0,
    lambda_orth: float = 1.0,
    source_log_win: Optional[torch.Tensor] = None,
    source_log_lose: Optional[torch.Tensor] = None,
) -> Tuple[torch.Tensor, Dict[str, float]]:
    """
    L = L_fit + L_cmp + L_tie + L_len

    r_Q 拟合 S_fp。长度不进 r_Q。
    |S_fp 分差| ≥ 0.20，且高分一侧不更长或只长一点点时，
    r_Q 分差至少达到 S_fp 分差；再缩小这项为正，达到后为 0。
    高分一侧长到一倍时，这条对不再逼 r_Q 排序。
    |S_fp 分差| ≤ 0.10 的对把 r_Q 分差收到 0。
    L_fit = mean((r_Q − S_fp)²)
    L_cmp = Σ w · relu(gap_s − gap_q)² / Σ w
    L_tie = mean((1 − w_score) · gap_q²)
    L_len = mean(((r_L⁺−r_L⁻) − (ℓ⁺−ℓ⁻))²)
    w = w_score · w_len。不把 ρ(r_Q, ℓ)² 加进损失。
    """
    q_w = r_q_win.reshape(-1)
    q_l = r_q_lose.reshape(-1)
    s_w = teacher_win.reshape(-1).float().to(dtype=q_w.dtype)
    s_l = teacher_lose.reshape(-1).float().to(dtype=q_w.dtype)
    _ = (source_log_win, source_log_lose)
    t_w = s_w
    t_l = s_l
    gap_q = q_w - q_l
    gap_s = s_w - s_l
    gap_t = gap_s
    l_fit = 0.5 * ((q_w - t_w).square().mean() + (q_l - t_l).square().mean())
    ell_w = log_len_win.reshape(-1).to(dtype=q_w.dtype)
    ell_l = log_len_lose.reshape(-1).to(dtype=q_w.dtype)
    gap_ell = ell_w - ell_l
    w_score = pair_gap_weight(gap_s).to(dtype=q_w.dtype)
    w_len = length_rank_weight(gap_ell).to(dtype=q_w.dtype)
    w = w_score * w_len
    denom = w.sum().clamp(min=1.0)
    shortfall = (gap_t - gap_q).clamp(min=0)
    l_cmp = (w * shortfall.square()).sum() / denom
    l_tie = ((1.0 - w_score) * gap_q.square()).mean()
    gap_rl = r_l_win.reshape(-1).to(dtype=q_w.dtype) - r_l_lose.reshape(-1).to(dtype=q_w.dtype)
    l_len = (gap_rl - gap_ell).square().mean()

    r_q_all = torch.cat([q_w, q_l], dim=0)
    r_l_all = torch.cat([r_l_win.reshape(-1), r_l_lose.reshape(-1)], dim=0)
    t_all = torch.cat([t_w, t_l], dim=0)
    ell = torch.cat([ell_w, ell_l], dim=0)
    rho_q = batch_pearson(r_q_all, ell)
    rho_l = batch_pearson(r_l_all, ell)
    rho_qs = batch_pearson(r_q_all, t_all)

    _ = (head_q, head_l, lambda_corr, lambda_orth)
    total = l_fit + l_cmp + l_tie + l_len
    open_mask = w > 0
    if bool(open_mask.any()):
        acc_open = float((gap_q.detach()[open_mask] * gap_t.detach()[open_mask] > 0).float().mean())
    else:
        acc_open = 1.0
    stats = {
        "loss": float(total.detach()),
        "L_fit": float(l_fit.detach()),
        "L_cmp": float(l_cmp.detach()),
        "L_tie": float(l_tie.detach()),
        "L_len": float(l_len.detach()),
        "open_frac": float((w > 0).float().mean().detach()),
        "rho_q": float(rho_q.detach()),
        "rho_l": float(rho_l.detach()),
        "rho_qs": float(rho_qs.detach()),
        "gap_sfp_mae": float((gap_q - gap_s).detach().abs().mean()),
        "len_rank": float(w_len.detach().mean()),
        "acc_q": float((gap_q.detach() * gap_t.detach() > 0).float().mean()),
        "acc_q_open": acc_open,
    }
    return total, stats


class DualHeadRewardModel(nn.Module):
    """
    backbone：CausalLM / 任意带 last_hidden_state 的编码器。
    r_Q 是两层映射；r_L 是 Linear(d→1) + weight_norm。
    """

    def __init__(self, backbone: nn.Module, hidden_size: Optional[int] = None) -> None:
        super().__init__()
        self.backbone = backbone
        d = hidden_size
        if d is None:
            cfg = getattr(backbone, "config", None)
            d = int(getattr(cfg, "hidden_size", 0) or 0)
        if d <= 0:
            raise ValueError("hidden_size 未知：请显式传入")
        self.hidden_size = int(d)
        # 线性读出在整次训练里都没把同组输赢分开（acc_q 停在 0.52）。
        # 两层映射仍只用缓存的 last-token，不解冻 7B。
        width = min(256, self.hidden_size)
        self.head_q = nn.Sequential(
            nn.Linear(self.hidden_size, width),
            nn.GELU(),
            nn.Linear(width, 1),
        )
        head_l = nn.Linear(self.hidden_size, 1, bias=False)
        self.head_l = nn.utils.parametrizations.weight_norm(head_l)

    def pool_hidden(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
    ) -> torch.Tensor:
        out = self.backbone(
            input_ids=input_ids,
            attention_mask=attention_mask,
            output_hidden_states=True,
            use_cache=False,
        )
        hidden = getattr(out, "last_hidden_state", None)
        if hidden is None:
            states = getattr(out, "hidden_states", None)
            if not states:
                raise RuntimeError("backbone 未返回 last_hidden_state / hidden_states")
            hidden = states[-1]
        return last_token_hidden(hidden, attention_mask)

    def scores_from_hidden(self, hidden: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        h = hidden.float()
        r_q = self.head_q(h).squeeze(-1)
        r_l = self.head_l(h).squeeze(-1)
        return r_q, r_l

    def forward(
        self,
        input_ids: Optional[torch.Tensor] = None,
        attention_mask: Optional[torch.Tensor] = None,
        hidden: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        if hidden is None:
            if input_ids is None or attention_mask is None:
                raise ValueError("需要 hidden 或 (input_ids, attention_mask)")
            hidden = self.pool_hidden(input_ids, attention_mask)
        return self.scores_from_hidden(hidden)

    def freeze_backbone(self) -> None:
        self.backbone.eval()
        for p in self.backbone.parameters():
            p.requires_grad_(False)

    def heads_state_dict(self) -> Dict[str, Any]:
        return {
            "head_q": self.head_q.state_dict(),
            "head_l": self.head_l.state_dict(),
            "hidden_size": self.hidden_size,
        }

    def load_heads_state_dict(self, blob: Dict[str, Any]) -> None:
        self.head_q.load_state_dict(blob["head_q"])
        self.head_l.load_state_dict(blob["head_l"])
