"""
双头奖励模型（ODIN）：共用表征 + r_Q / r_L。

r_Q、r_L 是线性头输出，无 sigmoid、无 clip。
训 RM 时排序用 r_sum = r_Q + r_L；策略训练只取 r_Q。
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F


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


def odin_rm_loss(
    r_q_win: torch.Tensor,
    r_l_win: torch.Tensor,
    r_q_lose: torch.Tensor,
    r_l_lose: torch.Tensor,
    log_len_win: torch.Tensor,
    log_len_lose: torch.Tensor,
    *,
    head_q: nn.Module,
    head_l: nn.Module,
    lambda_corr: float = 1.0,
    lambda_orth: float = 1.0,
) -> Tuple[torch.Tensor, Dict[str, float]]:
    """
    L = L_rank + λ_L [ρ(r_Q, ℓ) − ρ(r_L, ℓ)] + λ_O |W_Q · W_L|

    L_rank = mean( −log σ( (r_Q+r_L)_win − (r_Q+r_L)_lose ) )
    """
    r_sum_w = r_q_win + r_l_win
    r_sum_l = r_q_lose + r_l_lose
    delta = r_sum_w - r_sum_l
    l_rank = F.softplus(-delta).mean()

    r_q_all = torch.cat([r_q_win, r_q_lose], dim=0)
    r_l_all = torch.cat([r_l_win, r_l_lose], dim=0)
    ell = torch.cat([log_len_win, log_len_lose], dim=0).to(dtype=r_q_all.dtype)
    rho_q = batch_pearson(r_q_all, ell)
    rho_l = batch_pearson(r_l_all, ell)
    l_corr = rho_q - rho_l

    wq = linear_weight_vec(head_q)
    wl = linear_weight_vec(head_l)
    l_orth = (wq * wl).sum().abs()

    total = l_rank + float(lambda_corr) * l_corr + float(lambda_orth) * l_orth
    stats = {
        "loss": float(total.detach()),
        "L_rank": float(l_rank.detach()),
        "L_corr": float(l_corr.detach()),
        "L_orth": float(l_orth.detach()),
        "rho_q": float(rho_q.detach()),
        "rho_l": float(rho_l.detach()),
        "acc_sum": float((delta.detach() > 0).float().mean()),
        "acc_q": float(((r_q_win - r_q_lose).detach() > 0).float().mean()),
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
