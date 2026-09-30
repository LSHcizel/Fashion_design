"""标量损失与 logprob 工具（需 torch）。"""

from __future__ import annotations

from typing import Optional, Tuple

import torch
import torch.nn.functional as F


def _completion_logprob_mask(
    input_ids: torch.Tensor,
    completion_start: torch.Tensor,
    attention_mask: Optional[torch.Tensor] = None,
) -> torch.Tensor:
    """completion 段在 ``logits[:, :-1]`` 上的布尔掩码，形状 ``(B, L-1)``。"""
    seqlm1 = int(input_ids.shape[1]) - 1
    bsz = int(input_ids.shape[0])
    if seqlm1 <= 0:
        return torch.ones(bsz, 1, dtype=torch.bool, device=input_ids.device)
    if attention_mask is not None:
        attn_tail = attention_mask[:, 1:].bool()
    else:
        attn_tail = torch.ones(bsz, seqlm1, dtype=torch.bool, device=input_ids.device)
    mask = torch.zeros(bsz, seqlm1, dtype=torch.bool, device=input_ids.device)
    for b in range(bsz):
        s = int(completion_start[b].item())
        if s <= 0:
            s = 1
        start_lp = max(0, s - 1)
        mask[b, start_lp:seqlm1] = True
    return mask & attn_tail


def completion_token_counts(
    input_ids: torch.Tensor,
    completion_start: torch.Tensor,
    attention_mask: Optional[torch.Tensor] = None,
) -> torch.Tensor:
    """每条 completion 的有效 token 数，至少为 1。"""
    mask = _completion_logprob_mask(input_ids, completion_start, attention_mask)
    return mask.sum(dim=-1).clamp(min=1)


def sequence_completion_logprob_parts(
    logits: torch.Tensor,
    input_ids: torch.Tensor,
    completion_start: torch.Tensor,
    attention_mask: Optional[torch.Tensor] = None,
) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """
    返回 ``(sum_logp, token_count, mean_logp)``。

    ``sum_logp`` 是 completion 上 ``log p`` 之和，策略项用它，避免长句被自身长度除掉。
    ``mean_logp`` 仍是长度归一化均值，KL 继续用它，这样 ``beta_kl`` 的尺度不变。
    """
    logp_all = F.log_softmax(logits[:, :-1], dim=-1)
    targets = input_ids[:, 1:]
    gathered = logp_all.gather(-1, targets.unsqueeze(-1)).squeeze(-1)
    mask = _completion_logprob_mask(input_ids, completion_start, attention_mask)
    if mask.shape[1] != gathered.shape[1]:
        mask = mask[:, : gathered.shape[1]]
    gathered = gathered.masked_fill(~mask, 0.0)
    token_count = mask.sum(dim=-1).clamp(min=1).to(dtype=gathered.dtype)
    sum_logp = gathered.sum(dim=-1)
    return sum_logp, token_count, sum_logp / token_count


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
    _sum, _count, mean_logp = sequence_completion_logprob_parts(
        logits, input_ids, completion_start, attention_mask
    )
    return mean_logp


def grpo_loss(
    logp_policy: torch.Tensor,
    logp_ref: torch.Tensor,
    advantage: torch.Tensor,
    *,
    beta_kl: float,
    kl_squared: bool = True,
    sum_logp_policy: Optional[torch.Tensor] = None,
    token_count: Optional[torch.Tensor] = None,
) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """
    策略项默认是 token 上的 ``-sum(A * log p) / sum(T)``：每条句子不再先除以自己的长度。
    未提供 ``sum_logp_policy`` 时退回 ``-mean(A * mean_logp)``。

    KL 仍是 completion 平均对数概率差的平方均值，``beta_kl`` 尺度与原来一致。
    """
    if sum_logp_policy is not None:
        counts = token_count if token_count is not None else torch.ones_like(sum_logp_policy)
        denom = counts.to(dtype=sum_logp_policy.dtype).sum().clamp(min=1)
        pol = -(advantage.detach() * sum_logp_policy).sum() / denom
    else:
        pol = -(advantage.detach() * logp_policy).mean()
    diff = logp_policy - logp_ref.detach()
    if kl_squared:
        kl = (diff ** 2).mean()
    else:
        kl = diff.mean().abs()
    total = pol + beta_kl * kl
    return total, pol, kl
