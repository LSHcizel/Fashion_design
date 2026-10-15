"""
双头奖励模型（ODIN）：共用表征 + r_Q / r_L。

r_Q 读最后一个 token 的两层映射，r_L 是线性头。都无 sigmoid、无 clip。
r_Q 的分差对齐 S_fp 的分差，只把长过原文的冗长扣分当作这条分差上的修正：
不长过原文不扣；比原文长 10% 以内只扣约 0.005；长到原文两倍扣一个组内标准差（0.053）。
点对点误差很容易靠预测组均值把分差缩掉，所以分差项按组内标准差加权。策略训练只取 r_Q。
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


# 15603 条改写里，组内 S_fp 标准差的中位数。稍长扣分要明显小于这个数。
WITHIN_GROUP_SFP_STD = 0.053
# 比原文长 0.10 nat（约 10%）仍算稍许偏长。
MILD_OVER_NAT = 0.10
# 稍许偏长的尽头只扣组内标准差的一成。
MILD_PENALTY = 0.1 * WITHIN_GROUP_SFP_STD
# 长到原文两倍时，扣一个组内标准差。
DOUBLE_SOURCE_NAT = math.log(2.0)
# 分差项的权重。漏掉一个组内标准差的代价，要大于靠组均值把分差缩掉省下的点对点误差。
GAP_MATCH_WEIGHT = 1.0 / WITHIN_GROUP_SFP_STD


def length_disentangle_term(rho_q: torch.Tensor, rho_l: torch.Tensor) -> torch.Tensor:
    """内容头与句长的相关停在 0；长度头继续吸收句长。

    ρ(r_Q, ℓ) 本身没有下界，直接最小化会把内容头推到越短越高。
    平方在 0 处梯度消失，正负相关都加损失，避免用删信息换短句。
    """
    return rho_q.square() - rho_l


def verbosity_penalty(excess: torch.Tensor) -> torch.Tensor:
    """比原文长出来的 log 字数。不长过原文为 0；稍许偏长几乎不扣；再长按超出段的平方加。"""
    e = excess.clamp(min=0)
    mild = e.clamp(max=MILD_OVER_NAT)
    over = (e - MILD_OVER_NAT).clamp(min=0)
    slope = MILD_PENALTY / MILD_OVER_NAT
    span = DOUBLE_SOURCE_NAT - MILD_OVER_NAT
    quad = (WITHIN_GROUP_SFP_STD - MILD_PENALTY) / (span * span)
    return slope * mild + quad * over.square()


def content_target(
    teacher: torch.Tensor,
    log_len: torch.Tensor,
    source_log_len: Optional[torch.Tensor],
) -> Tuple[torch.Tensor, torch.Tensor]:
    """r_Q 要拟合的分数：S_fp 减去冗长扣分。没有原文长度时不扣。"""
    score = teacher.reshape(-1).float()
    ell = log_len.reshape(-1).float()
    if source_log_len is None:
        return score, score.new_zeros(score.shape)
    src = source_log_len.reshape(-1).float()
    pen = verbosity_penalty(ell - src)
    return score - pen, pen


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
    L = L_fit + L_cmp + L_len

    目标 t = S_fp − verbosity(ℓ − ℓ_source)。
    分差： (r_Q⁺−r_Q⁻) 对齐 (S_fp⁺−S_fp⁻) − (verbosity⁺−verbosity⁻)。
    拟合完成时，r_Q 分差与 S_fp 分差只差冗长扣分；稍许偏长几乎不动，过度冗长才把分差拉开。
    L_fit = mean((r_Q − t)²)
    L_cmp = (1/0.053) · mean(((r_Q⁺−r_Q⁻) − (t⁺−t⁻))²)
    L_len = mean(((r_L⁺−r_L⁻) − (ℓ⁺−ℓ⁻))²)
    不把 ρ(r_Q, ℓ)² 加进损失，否则稍许偏长的那一点扣分会被压成 0。
    """
    q_w = r_q_win.reshape(-1)
    q_l = r_q_lose.reshape(-1)
    s_w = teacher_win.reshape(-1).float().to(dtype=q_w.dtype)
    s_l = teacher_lose.reshape(-1).float().to(dtype=q_w.dtype)
    t_w, pen_w = content_target(teacher_win, log_len_win, source_log_win)
    t_l, pen_l = content_target(teacher_lose, log_len_lose, source_log_lose)
    t_w = t_w.to(dtype=q_w.dtype)
    t_l = t_l.to(dtype=q_l.dtype)
    pen_w = pen_w.to(dtype=q_w.dtype)
    pen_l = pen_l.to(dtype=q_w.dtype)
    gap_q = q_w - q_l
    gap_s = s_w - s_l
    gap_v = pen_w - pen_l
    gap_t = t_w - t_l
    l_fit = 0.5 * ((q_w - t_w).square().mean() + (q_l - t_l).square().mean())
    l_cmp = GAP_MATCH_WEIGHT * (gap_q - gap_t).square().mean()
    ell_w = log_len_win.reshape(-1).to(dtype=q_w.dtype)
    ell_l = log_len_lose.reshape(-1).to(dtype=q_w.dtype)
    gap_ell = ell_w - ell_l
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
    total = l_fit + l_cmp + l_len
    stats = {
        "loss": float(total.detach()),
        "L_fit": float(l_fit.detach()),
        "L_cmp": float(l_cmp.detach()),
        "L_len": float(l_len.detach()),
        "rho_q": float(rho_q.detach()),
        "rho_l": float(rho_l.detach()),
        "rho_qs": float(rho_qs.detach()),
        "mean_verb": float(0.5 * (pen_w.mean() + pen_l.mean()).detach()),
        "gap_sfp_mae": float((gap_q - gap_s).detach().abs().mean()),
        "verb_resid_mae": float(((gap_s - gap_q) - gap_v).detach().abs().mean()),
        "acc_q": float((gap_q.detach() * gap_t.detach() > 0).float().mean()),
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
