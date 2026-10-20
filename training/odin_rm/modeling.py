"""
双头奖励模型（ODIN）：共用表征 + 两个线性头 r_Q / r_L。

排序和分差都落在 r_Q 上。长度相关仍是式 (9)，但 λ_L 弱于分差项。
两个头都做 weight normalization。L(y) 是回复 token 数。策略训练只取 r_Q。
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


# 裁判分差不大于此值的对不进 RM 训练。比较用严格大于。
MIN_SCORE_GAP = 0.1
# λ_L 弱于论文的 1，避免长度相关把 S_fp 分差从 r_Q 里拖走。
LAMBDA_L = 0.1
# λ_O 仍约束两个头的方向分开。
LAMBDA_O = 1.0
# 分差项权重大于长度项：r_Q 分差对齐 S_fp 分差。
LAMBDA_GAP = 10.0


def length_correlation_loss(
    r_q: torch.Tensor,
    r_l: torch.Tensor,
    length: torch.Tensor,
) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """式 (9)：质量头与 token 数去相关，长度头与 token 数正相关。"""
    rho_q = batch_pearson(r_q, length)
    rho_l = batch_pearson(r_l, length)
    return rho_q.abs() - rho_l, rho_q, rho_l


def _projection_weight(head: nn.Module) -> torch.Tensor:
    weight = getattr(head, "weight", None)
    if weight is None:
        raise TypeError("ODIN 的头必须是线性层")
    return weight.float().reshape(-1)


def orthogonality_loss(head_q: nn.Module, head_l: nn.Module) -> torch.Tensor:
    """式 (10)：|W_Q W_L^T|。weight 已是 weight normalization 之后的投影。"""
    return torch.dot(_projection_weight(head_q), _projection_weight(head_l)).abs()


def odin_rm_loss(
    r_q_win: torch.Tensor,
    r_l_win: torch.Tensor,
    r_q_lose: torch.Tensor,
    r_l_lose: torch.Tensor,
    len_win: torch.Tensor,
    len_lose: torch.Tensor,
    teacher_win: torch.Tensor,
    teacher_lose: torch.Tensor,
    *,
    head_q: nn.Module,
    head_l: nn.Module,
    lambda_l: float = LAMBDA_L,
    lambda_o: float = LAMBDA_O,
    lambda_gap: float = LAMBDA_GAP,
) -> Tuple[torch.Tensor, Dict[str, float]]:
    """
    L = L^R + λ_gap L_gap + λ_L L^L(y_w) + λ_L L^L(y_l) + λ_O L^O。

    L^R 和 L_gap 只看 r_Q。L_gap 让 r_Q 分差等于 S_fp 分差。
    L^L 仍是式 (9)，λ_L 小于 λ_gap。
    """
    q_w = r_q_win.reshape(-1)
    q_l = r_q_lose.reshape(-1)
    l_w = r_l_win.reshape(-1).to(dtype=q_w.dtype)
    l_l = r_l_lose.reshape(-1).to(dtype=q_w.dtype)
    n_w = len_win.reshape(-1).to(dtype=q_w.dtype)
    n_l = len_lose.reshape(-1).to(dtype=q_w.dtype)
    s_w = teacher_win.reshape(-1).to(dtype=q_w.dtype)
    s_l = teacher_lose.reshape(-1).to(dtype=q_w.dtype)

    gap_q = q_w - q_l
    gap_s = s_w - s_l
    l_rank = -F.logsigmoid(gap_q).mean()
    l_gap = (gap_q - gap_s).square().mean()
    l_len_w, rho_q_w, rho_l_w = length_correlation_loss(q_w, l_w, n_w)
    l_len_l, rho_q_l, rho_l_l = length_correlation_loss(q_l, l_l, n_l)
    l_len = l_len_w + l_len_l
    l_orth = orthogonality_loss(head_q, head_l)
    total = (
        l_rank
        + float(lambda_gap) * l_gap
        + float(lambda_l) * l_len
        + float(lambda_o) * l_orth
    )

    margin_sum = (q_w + l_w) - (q_l + l_l)
    acc_sum = float((margin_sum.detach() > 0).float().mean())
    acc_q = float((gap_q.detach() > 0).float().mean())
    rho_q = 0.5 * (rho_q_w + rho_q_l)
    rho_l = 0.5 * (rho_l_w + rho_l_l)
    stats = {
        "loss": float(total.detach()),
        "L_R": float(l_rank.detach()),
        "L_gap": float(l_gap.detach()),
        "L_L": float(l_len.detach()),
        "L_O": float(l_orth.detach()),
        "gap_mae": float((gap_q.detach() - gap_s.detach()).abs().mean()),
        "rho_q": float(rho_q.detach()),
        "rho_l": float(rho_l.detach()),
        "rho_q_win": float(rho_q_w.detach()),
        "rho_q_lose": float(rho_q_l.detach()),
        "rho_l_win": float(rho_l_w.detach()),
        "rho_l_lose": float(rho_l_l.detach()),
        "acc_sum": acc_sum,
        "acc_q": acc_q,
    }
    return total, stats


def _weight_norm_linear(hidden_size: int) -> nn.Module:
    layer = nn.Linear(hidden_size, 1, bias=True)
    return nn.utils.parametrizations.weight_norm(layer)


class DualHeadRewardModel(nn.Module):
    """
    backbone：CausalLM / 任意带 last_hidden_state 的编码器。
    r_Q、r_L 都是 Linear(d→1) + weight_norm。
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
        self.head_q = _weight_norm_linear(self.hidden_size)
        self.head_l = _weight_norm_linear(self.hidden_size)

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
