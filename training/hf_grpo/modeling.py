"""标量损失与 logprob 工具（需 torch）。"""

from __future__ import annotations

from typing import Optional, Tuple

import torch
import torch.nn.functional as F


def sequence_completion_log_probs(
    logits: torch.Tensor,
    input_ids: torch.Tensor,
    completion_start: torch.Tensor,
    attention_mask: Optional[torch.Tensor] = None,
) -> torch.Tensor:
    """
    对每条样本，对 completion 段求长度归一化的 ``mean_t log p(x_t | x_{<t})``（仅非 padding 位置）。

    Parameters
    ----------
    logits :
        ``(B, L, V)``，HF CausalLM：位置 ``i`` 的向量用于预测 ``input_ids[:, i+1]``。
    input_ids :
        ``(B, L)``
    completion_start :
        ``(B,)``，第一条计入 completion 的 ``input_ids`` 下标。
    attention_mask :
        ``(B, L)``，padding 为 0。
    """
    logp_all = F.log_softmax(logits[:, :-1], dim=-1)
    targets = input_ids[:, 1:]
    gathered = logp_all.gather(-1, targets.unsqueeze(-1)).squeeze(-1)
    if attention_mask is not None:
        attn_tail = attention_mask[:, 1:].bool()
    else:
        attn_tail = torch.ones_like(gathered, dtype=torch.bool)
    mask = torch.zeros_like(gathered, dtype=torch.bool)
    bsz, seqlm1 = gathered.shape
    for b in range(bsz):
        s = int(completion_start[b].item())
        if s <= 0:
            s = 1
        start_lp = max(0, s - 1)
        mask[b, start_lp:seqlm1] = True
    mask = mask & attn_tail
    gathered = gathered.masked_fill(~mask, 0.0)
    lengths = mask.sum(dim=-1).clamp(min=1)
    return gathered.sum(dim=-1) / lengths.float()


def grpo_loss(
    logp_policy: torch.Tensor,
    logp_ref: torch.Tensor,
    advantage: torch.Tensor,
    *,
    beta_kl: float,
    kl_squared: bool = True,
) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """
    ``L = - mean(A * logp_policy) + beta * KL_aux``，
    ``KL_aux`` 为 completion 上 ``(logp_policy - logp_ref)^2`` 的均值。
    """
    pol = -(advantage.detach() * logp_policy).mean()
    diff = logp_policy - logp_ref.detach()
    if kl_squared:
        kl = (diff ** 2).mean()
    else:
        kl = diff.mean().abs()
    total = pol + beta_kl * kl
    return total, pol, kl
