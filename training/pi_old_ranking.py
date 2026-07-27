"""
π_old（参考 / 旧策略）下按 completion 的平均 logprob 排序，供 EMNLP 2025
「Rewarding the Unlikely」组内排名（rank 小 = 更易生成 = 更高 π_old 概率）。

依赖 PyTorch + transformers；导入失败时 ``compute_old_policy_ranks_for_group`` 不可用。
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

RowDict = Dict[str, Any]


def _sample_row_to_phase_b_row(rec: RowDict) -> RowDict:
    return {"context": rec.get("context") or {}, "completion": rec.get("completion") or ""}


def completion_mean_logprob_for_record(
    rec: RowDict,
    *,
    tokenizer,
    model,
    device,
    max_length: int,
    system_prompt: str = "",
) -> float:
    """单条样本：对话模板下 completion 段的平均 logprob（与 ``hf_grpo.modeling`` 一致）。"""
    import torch

    from .hf_grpo.data import completion_token_start, messages_from_phase_b_row, render_chat_text
    from .hf_grpo.modeling import sequence_completion_log_probs

    row = _sample_row_to_phase_b_row(rec)
    messages = messages_from_phase_b_row(row, system_prompt=system_prompt)
    text = render_chat_text(messages, tokenizer)
    enc = tokenizer(
        text,
        max_length=max_length,
        truncation=True,
        return_tensors="pt",
    )
    enc = {k: v.to(device) for k, v in enc.items()}
    with torch.inference_mode():
        out = model(**enc)
        logits = out.logits
    comp_start = completion_token_start(tokenizer, messages)
    comp_start_t = torch.tensor([min(comp_start, enc["input_ids"].shape[1] - 1)], device=device, dtype=torch.long)
    lp = sequence_completion_log_probs(logits, enc["input_ids"], comp_start_t, enc["attention_mask"])
    return float(lp[0].item())


def compute_old_policy_ranks_for_group(
    records: List[RowDict],
    *,
    tokenizer,
    model,
    device,
    max_length: int,
    system_prompt: str = "",
) -> Tuple[List[int], List[float]]:
    """
    返回与 ``records`` **同序**的 rank（1…G）与 mean_logprob。

    rank 定义：π_old 下「越容易生成」→ logprob 越高 → **rank=1**；最难 → **rank=G**。
    logprob 平局时按 ``candidate_index`` 升序稳定决胜。
    """
    logps: List[float] = []
    for rec in records:
        logps.append(
            completion_mean_logprob_for_record(
                rec,
                tokenizer=tokenizer,
                model=model,
                device=device,
                max_length=max_length,
                system_prompt=system_prompt,
            )
        )
    G = len(records)
    indices = list(range(G))
    indices.sort(
        key=lambda i: (-logps[i], int(records[i].get("candidate_index") or i)),
    )
    ranks = [0] * G
    for rank_pos, idx in enumerate(indices):
        ranks[idx] = rank_pos + 1
    return ranks, logps


def load_pi_old_model_and_tokenizer(
    model_id: str,
    *,
    dtype: str = "bf16",
):
    """加载因果 LM 与 tokenizer（eval；梯度关闭由调用方保证）。"""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    dtype_map = {"bf16": torch.bfloat16, "fp16": torch.float16, "fp32": torch.float32}
    torch_dtype = dtype_map.get(dtype, torch.bfloat16)
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    common_kw: Dict[str, Any] = {"trust_remote_code": True}
    if dtype != "fp32":
        common_kw["torch_dtype"] = torch_dtype
    model = AutoModelForCausalLM.from_pretrained(model_id, **common_kw)
    if hasattr(model.config, "use_cache"):
        model.config.use_cache = False
    model.eval()
    return model, tokenizer
