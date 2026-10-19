"""
双头奖励模型（ODIN）：共用表征 + r_Q / r_L。

r_Q 读最后一个 token 的两层映射，r_L 是线性头。都无 sigmoid、无 clip。
长度标准是本组改写原文的字数。r_L 报出改写超出原文的幅度，短于原文的目标是 0。
r_Q 分差始终对齐 S_fp 分差。S_fp 一样时，字数不同也不把 r_Q 拉开。
ρ(r_Q, 相对原文字数) 只写入日志。验收看扣掉 S_fp 之后的残差还跟不跟字数走。策略训练只取 r_Q。
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


def length_disentangle_term(rho_q: torch.Tensor, rho_l: torch.Tensor) -> torch.Tensor:
    """内容头与句长的相关停在 0；长度头继续吸收句长。

    ρ(r_Q, ℓ) 本身没有下界，直接最小化会把内容头推到越短越高。
    平方在 0 处梯度消失，正负相关都加损失，避免用删信息换短句。
    """
    return rho_q.square() - rho_l


# S_fp 分差低于此值，视为原得分一样。只用于给同分长度对打标记，不改变 r_Q 目标。
MIN_SCORE_GAP = 0.10
# 超长幅度差达到此值，造对时标成 same_score_length，便于事后检查。
RL_CLOSE = 0.10


def over_source_length(log_len: torch.Tensor, source_log: torch.Tensor) -> torch.Tensor:
    """超出本组原文字数的 log 幅度。短于或等于原文时为 0。"""
    return (log_len - source_log).clamp(min=0)


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
    lambda_corr: float = 0.02,
    lambda_orth: float = 1.0,
    source_log_win: Optional[torch.Tensor] = None,
    source_log_lose: Optional[torch.Tensor] = None,
) -> Tuple[torch.Tensor, Dict[str, float]]:
    """
    L = L_gap + λ_orth · L_len

    L_len 让 r_L 等于改写超出原文的 log 幅度。短于原文时期望 r_L 为 0。
    L_gap 让 r_Q 分差始终对齐 S_fp 分差，不按超长差扣减。
    组内比较对不论 S_fp 分差大小都计入。
    ρ(r_Q, ℓ − ℓ_原文) 只写入统计，不进损失。
    """
    q_w = r_q_win.reshape(-1)
    q_l = r_q_lose.reshape(-1)
    l_w = r_l_win.reshape(-1).to(dtype=q_w.dtype)
    l_l = r_l_lose.reshape(-1).to(dtype=q_w.dtype)
    s_w = teacher_win.reshape(-1).float().to(dtype=q_w.dtype)
    s_l = teacher_lose.reshape(-1).float().to(dtype=q_w.dtype)
    _ = (head_q, head_l, lambda_corr)
    ell_w = log_len_win.reshape(-1).to(dtype=q_w.dtype)
    ell_l = log_len_lose.reshape(-1).to(dtype=q_w.dtype)
    src_w = ell_w if source_log_win is None else source_log_win.reshape(-1).to(dtype=q_w.dtype)
    src_l = ell_l if source_log_lose is None else source_log_lose.reshape(-1).to(dtype=q_w.dtype)
    excess_w = over_source_length(ell_w, src_w).detach()
    excess_l = over_source_length(ell_l, src_l).detach()
    gap_q = q_w - q_l
    gap_s = s_w - s_l
    gap_excess = excess_w - excess_l
    len_err = 0.5 * ((l_w - excess_w).square() + (l_l - excess_l).square())
    l_len = len_err.mean()
    l_gap = (gap_q - gap_s).square().mean()

    dev = torch.cat([ell_w - src_w, ell_l - src_l], dim=0)
    r_q_all = torch.cat([q_w, q_l], dim=0)
    r_l_all = torch.cat([l_w, l_l], dim=0)
    s_all = torch.cat([s_w, s_l], dim=0)
    excess_all = torch.cat([excess_w, excess_l], dim=0)
    rho_q = batch_pearson(r_q_all, dev)
    rho_l = batch_pearson(r_l_all, excess_all)
    rho_qs = batch_pearson(r_q_all, s_all)
    l_orth = rho_q.square()
    total = l_gap + float(lambda_orth) * l_len
    score_ok = gap_s.abs() >= MIN_SCORE_GAP
    len_ok = gap_excess.abs() >= RL_CLOSE
    gap_mae = float((gap_q.detach() - gap_s.detach()).abs().mean())
    acc_q = float((gap_q.detach() * gap_s.detach() > 0).float().mean())
    same_score = ((~score_ok) & len_ok).to(dtype=q_w.dtype)
    stats = {
        "loss": float(total.detach()),
        "L_gap": float(l_gap.detach()),
        "L_len": float(l_len.detach()),
        "L_orth": float(l_orth.detach()),
        "usable_frac": 1.0,
        "same_score_frac": float(same_score.mean().detach()),
        "rho_q": float(rho_q.detach()),
        "rho_l": float(rho_l.detach()),
        "rho_qs": float(rho_qs.detach()),
        "gap_sfp_mae": gap_mae,
        "acc_q": acc_q,
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
