"""
双头奖励模型（ODIN）：共用表征 + r_Q / r_L。

r_Q、r_L 是线性头输出，无 sigmoid、无 clip。
同组输赢只比 r_Q，差距对齐 S_fp 的差距；r_Q 同时拟合这条改写自己的 S_fp。r_L 只吸收句长。策略训练只取 r_Q。
"""

from __future__ import annotations

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


def linear_weight_vec(head: nn.Module) -> torch.Tensor:
    w = head.weight
    return w.reshape(-1)


def length_disentangle_term(rho_q: torch.Tensor, rho_l: torch.Tensor) -> torch.Tensor:
    """内容头与句长的相关停在 0；长度头继续吸收句长。

    ρ(r_Q, ℓ) 本身没有下界，直接最小化会把内容头推到越短越高。
    平方在 0 处梯度消失，正负相关都加损失，避免用删信息换短句。
    """
    return rho_q.square() - rho_l


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
) -> Tuple[torch.Tensor, Dict[str, float]]:
    """
    L = L_cmp + L_fit + λ_L [ρ(r_Q, ℓ)² − ρ(r_L, ℓ)] + λ_O |W_Q · W_L|

    同一组里的输赢只比 r_Q：
    L_cmp = mean( ((r_Q⁺ − r_Q⁻) − (S_fp⁺ − S_fp⁻))² )
    L_fit = mean( (r_Q − S_fp)² )
    长度头不进入这两项。
    """
    q_w = r_q_win.reshape(-1)
    q_l = r_q_lose.reshape(-1)
    s_w = teacher_win.reshape(-1).to(dtype=q_w.dtype)
    s_l = teacher_lose.reshape(-1).to(dtype=q_l.dtype)
    gap_q = q_w - q_l
    gap_s = s_w - s_l
    l_cmp = (gap_q - gap_s).square().mean()
    l_fit = 0.5 * ((q_w - s_w).square().mean() + (q_l - s_l).square().mean())

    r_q_all = torch.cat([q_w, q_l], dim=0)
    r_l_all = torch.cat([r_l_win.reshape(-1), r_l_lose.reshape(-1)], dim=0)
    s_all = torch.cat([s_w, s_l], dim=0)
    ell = torch.cat([log_len_win, log_len_lose], dim=0).reshape(-1).to(dtype=r_q_all.dtype)
    rho_q = batch_pearson(r_q_all, ell)
    rho_l = batch_pearson(r_l_all, ell)
    rho_qs = batch_pearson(r_q_all, s_all)
    l_corr = length_disentangle_term(rho_q, rho_l)

    wq = linear_weight_vec(head_q)
    wl = linear_weight_vec(head_l)
    l_orth = (wq * wl).sum().abs()

    total = l_cmp + l_fit + float(lambda_corr) * l_corr + float(lambda_orth) * l_orth
    stats = {
        "loss": float(total.detach()),
        "L_cmp": float(l_cmp.detach()),
        "L_fit": float(l_fit.detach()),
        "L_corr": float(l_corr.detach()),
        "L_orth": float(l_orth.detach()),
        "rho_q": float(rho_q.detach()),
        "rho_l": float(rho_l.detach()),
        "rho_qs": float(rho_qs.detach()),
        "acc_q": float((gap_q.detach() > 0).float().mean()),
    }
    return total, stats


class DualHeadRewardModel(nn.Module):
    """
    backbone：CausalLM / 任意带 last_hidden_state 的编码器。
    两个 Linear(d→1, bias=False) + weight_norm。
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
        head_q = nn.Linear(self.hidden_size, 1, bias=False)
        head_l = nn.Linear(self.hidden_size, 1, bias=False)
        self.head_q = nn.utils.parametrizations.weight_norm(head_q)
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
