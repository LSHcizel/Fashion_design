"""标量损失与 logprob 工具（需 torch）。"""

from __future__ import annotations

import math
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
    ``mean_logp`` 是长度归一化均值，只留给调用方查看。KL 用逐 token 的 k3，不用这个均值。
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


_KL_LOG_RATIO_CLAMP = 10.0


def sampled_token_logprobs(
    logits: torch.Tensor,
    input_ids: torch.Tensor,
    completion_start: torch.Tensor,
    attention_mask: Optional[torch.Tensor] = None,
) -> Tuple[torch.Tensor, torch.Tensor]:
    """采样 token 的 ``log π``，以及 completion 段掩码。掩码外的对数概率为 0。"""
    logp_all = F.log_softmax(logits[:, :-1].float(), dim=-1)
    targets = input_ids[:, 1:]
    gathered = logp_all.gather(-1, targets.unsqueeze(-1)).squeeze(-1)
    mask = _completion_logprob_mask(input_ids, completion_start, attention_mask)
    if mask.shape[1] != gathered.shape[1]:
        width = min(mask.shape[1], gathered.shape[1])
        mask = mask[:, :width]
        gathered = gathered[:, :width]
    return gathered.masked_fill(~mask, 0.0), mask


def token_kl_k3_sum(
    logp_policy: torch.Tensor,
    logp_ref: torch.Tensor,
    mask: torch.Tensor,
) -> torch.Tensor:
    """
    Schulman k3 在 completion token 上的和。最后一维是 token，前面的维保留。

    ``k3 = exp(log π_ref - log π) - (log π_ref - log π) - 1``。
    对数比限制在 ±10，避免参考概率远高于策略时指数溢出。
    """
    delta = (logp_ref.detach().float() - logp_policy.float()).clamp(
        -_KL_LOG_RATIO_CLAMP,
        _KL_LOG_RATIO_CLAMP,
    )
    k3 = torch.exp(delta) - delta - 1.0
    return k3.masked_fill(~mask, 0.0).sum(dim=-1)


def clipped_surrogate_sum(
    logp_policy: torch.Tensor,
    logp_ref: torch.Tensor,
    mask: torch.Tensor,
    advantage: torch.Tensor,
) -> torch.Tensor:
    """
    DeepSeekMath / PPO 的悲观替代目标，按 completion token 求和。

    ``min(ratio · A, clip(ratio) · A)``，``ratio = π_θ / π_SFT``。
    clip 取 ``exp(±√(2·KL_TARGET))``，即 ±0.1 nat。越出这段后，继续抬高
    正优势或压低负优势都不再减小损失。
    """
    from training.grpo_defaults import LOG_RATIO_BUDGET

    delta = (logp_policy.float() - logp_ref.detach().float()).clamp(
        -_KL_LOG_RATIO_CLAMP,
        _KL_LOG_RATIO_CLAMP,
    )
    ratio = torch.exp(delta)
    clipped = ratio.clamp(min=math.exp(-LOG_RATIO_BUDGET), max=math.exp(LOG_RATIO_BUDGET))
    adv = advantage.detach().to(dtype=ratio.dtype).reshape(-1, 1)
    chosen = torch.minimum(ratio * adv, clipped * adv)
    return chosen.masked_fill(~mask, 0.0).sum(dim=-1)


def group_rank_loss(
    mean_logprobs: torch.Tensor,
    advantages: torch.Tensor,
) -> Optional[torch.Tensor]:
    """组内排序损失。只用于观察，不参与反传。

    ``mean_logprobs`` 是每条 completion 的长度归一化 ``log π``。
    对所有 ``A_i > A_j`` 的配对取 ``softplus(ℓ_j - ℓ_i)`` 再平均。
    高低分概率相同时等于 ``log 2``（约 0.693）；高优势句更可能时朝 0 下降。
    没有严格高低对时返回 ``None``。
    """
    ell = mean_logprobs.detach().float().reshape(-1)
    adv = advantages.detach().float().reshape(-1)
    if ell.numel() != adv.numel() or ell.numel() < 2:
        return None
    higher = adv.unsqueeze(1) > adv.unsqueeze(0)
    if not bool(higher.any()):
        return None
    # diff[i, j] = ℓ_j - ℓ_i
    diff = ell.unsqueeze(0) - ell.unsqueeze(1)
    return F.softplus(diff)[higher].mean()


def grpo_loss(
    surrogate_sum: torch.Tensor,
    token_count: torch.Tensor,
    token_kl_sum: torch.Tensor,
    *,
    beta_max: float,
    group_tokens: Optional[torch.Tensor] = None,
) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    """
    策略项是 ``-sum(min(ratio·A, clip(ratio)·A)) / sum(T)``。

    KL 系数由当前 k3 决定：不超过 :data:`KL_TARGET` 时为 0，
    到 :data:`KL_SEVERE` 时升到 ``beta_max``。惩罚只加在超出预算的那一段。
    返回 ``(loss, policy_term, kl_term, beta)``。多条样本时按 token 加权后相加。
    """
    from training.grpo_defaults import KL_TARGET, dynamic_kl_coefficient

    counts = token_count.to(dtype=surrogate_sum.dtype).clamp(min=1)
    denom = (
        counts.sum().clamp(min=1)
        if group_tokens is None
        else group_tokens.to(dtype=surrogate_sum.dtype)
    )
    k3 = token_kl_sum.to(dtype=surrogate_sum.dtype)
    seq_kl = k3 / counts
    pol = -surrogate_sum.to(dtype=surrogate_sum.dtype) / denom
    share = counts / denom
    beta_row = torch.stack(
        [
            seq_kl.new_tensor(dynamic_kl_coefficient(float(value.detach()), beta_max))
            for value in seq_kl.reshape(-1)
        ]
    ).reshape(seq_kl.shape)
    excess = (seq_kl - KL_TARGET).clamp(min=0)
    loss = pol + beta_row * excess * share
    kl_share = k3 / denom
    beta_share = beta_row * share
    if loss.ndim > 0:
        return loss.sum(), pol.sum(), kl_share.sum(), beta_share.sum()
    return loss, pol, kl_share, beta_share
