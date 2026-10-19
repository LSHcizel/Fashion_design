"""
双头奖励模型（ODIN）：共用表征 + r_Q / r_L。

r_Q 读最后一个 token 的两层映射，r_L 是线性头。都无 sigmoid、无 clip。
S_fp 是评分器原始分。r_Q 是主体，r_L 只占一小截，两者相加还原 S_fp。
句长上下浮动不大，或两侧 r_L 接近时，明显的 S_fp 分差要原样出现在 r_Q 上，偏大偏小都算损失。
高分一侧明显更长时，r_Q 分差按超长幅度缩小，长到约一倍时最多缩小 0.20。
只有超长一侧的 r_L 才取到 0.20。策略训练只取 r_Q。
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
# 句长差在这以内视为上下浮动不大。
LENGTH_CLOSE_NAT = 0.10
# 长到一倍视为超长，r_L 的惩罚在这里取满。
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


def length_excess_weight(abs_gap_ell: torch.Tensor) -> torch.Tensor:
    """两侧句长差。|Δℓ| ≤ 0.10 nat 为 0，差到一倍为 1。"""
    d = abs_gap_ell.reshape(-1)
    span = LENGTH_FAR_NAT - LENGTH_CLOSE_NAT
    return ((d - LENGTH_CLOSE_NAT) / span).clamp(0, 1)


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
    L = L_rec + L_gap + L_rl

    r_Q + r_L 还原 S_fp。还原项和分差项只计效果明显的对。
    r_L 的目标平时是 0。超长一侧的 r_L 目标才到 0.20，另一侧仍是 0。
    |S_fp 分差| 明显，且句长接近或两侧 r_L 接近时，r_Q 分差对齐 S_fp 分差，偏大偏小都算。
    高分一侧更长时，对齐的目标改为 max(S_fp 分差 − 0.20×超长幅度, 0)。
    """
    q_w = r_q_win.reshape(-1)
    q_l = r_q_lose.reshape(-1)
    l_w = r_l_win.reshape(-1).to(dtype=q_w.dtype)
    l_l = r_l_lose.reshape(-1).to(dtype=q_w.dtype)
    s_w = teacher_win.reshape(-1).float().to(dtype=q_w.dtype)
    s_l = teacher_lose.reshape(-1).float().to(dtype=q_w.dtype)
    _ = (source_log_win, source_log_lose)
    gap_q = q_w - q_l
    gap_s = s_w - s_l
    ell_w = log_len_win.reshape(-1).to(dtype=q_w.dtype)
    ell_l = log_len_lose.reshape(-1).to(dtype=q_w.dtype)
    gap_ell = ell_w - ell_l
    w_score = pair_gap_weight(gap_s).to(dtype=q_w.dtype)
    w_ex = length_excess_weight(gap_ell.abs()).to(dtype=q_w.dtype)
    w_close = 1.0 - w_ex
    # 分数差或长度差有一边明显，还原才进损失。两边都接近的对不拉动 r_Q。
    w_use = 1.0 - (1.0 - w_score) * (1.0 - w_ex)
    rec = 0.5 * ((q_w + l_w - s_w).square() + (q_l + l_l - s_l).square())
    l_rec = (w_use * rec).sum() / w_use.sum().clamp(min=1.0)
    # r_L 是否接近看头自己的输出，权重不反传，避免把 r_L 拉开去逃避分差项。
    gap_rl = l_w - l_l
    w_rl_close = (1.0 - pair_gap_weight(gap_rl.detach())).to(dtype=q_w.dtype)
    # 只在高分一侧更长时缩小分差。高分更短不减。
    w_hi_long = length_excess_weight(gap_ell.clamp(min=0)).to(dtype=q_w.dtype)
    gap_target = (gap_s - GAP_FULL * w_hi_long).clamp(min=0)
    w_gap = w_score * torch.maximum(torch.maximum(w_close, w_rl_close), w_hi_long)
    l_gap = (w_gap * (gap_q - gap_target).square()).sum() / w_gap.sum().clamp(min=1.0)
    # 长侧最多拿走 0.20，短侧目标是 0。句长差不到 0.10 nat 时两边目标都是 0。
    pen = GAP_FULL * w_ex
    longer_win = (gap_ell > 0).to(dtype=q_w.dtype)
    t_lw = pen * longer_win
    t_ll = pen * (1.0 - longer_win)
    l_rl = 0.5 * ((l_w - t_lw).square() + (l_l - t_ll).square()).mean()

    r_q_all = torch.cat([q_w, q_l], dim=0)
    r_l_all = torch.cat([l_w, l_l], dim=0)
    s_all = torch.cat([s_w, s_l], dim=0)
    ell = torch.cat([ell_w, ell_l], dim=0)
    rho_q = batch_pearson(r_q_all, ell)
    rho_l = batch_pearson(r_l_all, ell)
    rho_qs = batch_pearson(r_q_all, s_all)
    rho_rec = batch_pearson(r_q_all + r_l_all, s_all)

    _ = (head_q, head_l, lambda_corr, lambda_orth)
    total = l_rec + l_gap + l_rl
    open_mask = w_gap > 0
    if bool(open_mask.any()):
        acc_open = float((gap_q.detach()[open_mask] * gap_s.detach()[open_mask] > 0).float().mean())
        gap_mae = float((gap_q.detach()[open_mask] - gap_target.detach()[open_mask]).abs().mean())
    else:
        acc_open = 1.0
        gap_mae = float((gap_q.detach() - gap_s.detach()).abs().mean())
    stats = {
        "loss": float(total.detach()),
        "L_rec": float(l_rec.detach()),
        "L_gap": float(l_gap.detach()),
        "L_rl": float(l_rl.detach()),
        "open_frac": float((w_gap > 0).float().mean().detach()),
        "effect_frac": float((w_use > 0).float().mean().detach()),
        "rho_q": float(rho_q.detach()),
        "rho_l": float(rho_l.detach()),
        "rho_qs": float(rho_qs.detach()),
        "rho_rec": float(rho_rec.detach()),
        "gap_sfp_mae": gap_mae,
        "len_rank": float(w_close.detach().mean()),
        "acc_q": float((gap_q.detach() * gap_s.detach() > 0).float().mean()),
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
