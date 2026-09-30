"""
从 ``phase_a_sft.jsonl`` / ``phase_b_grpo.jsonl`` 加载样本并格式化为训练用文本。

不依赖 torch；供 ``train_sft`` / ``train_grpo`` 在运行时导入。
"""

from __future__ import annotations

import json
from pathlib import Path
from collections import defaultdict
from typing import Any, Dict, Iterator, List, Optional, Tuple, Union

JsonPath = Union[str, Path]


def _read_jsonl(path: Path) -> Iterator[Dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def load_phase_a_rows(path: JsonPath) -> List[Dict[str, Any]]:
    """``messages`` 列表，字段与 ``build_sft_record_for_group`` 输出一致。"""
    return list(_read_jsonl(Path(path)))


def load_phase_b_rows(path: JsonPath) -> List[Dict[str, Any]]:
    """``grpo_phase_b_v1`` 行：含 ``context`` / ``completion`` / ``advantage``。"""
    return list(_read_jsonl(Path(path)))


def phase_b_user_content(ctx: Dict[str, Any]) -> str:
    """与文本 K 路导出时 user 构造方式对齐（重写任务）。"""
    biz = str(ctx.get("business_context", "")).strip()
    src = str(ctx.get("shared_source_text", "")).strip()
    user_parts: List[str] = []
    if biz:
        user_parts.append(f"[Business context]\n{biz}")
    if src:
        user_parts.append(f"[Source text to rewrite]\n{src}")
    return "\n\n".join(user_parts).strip()


def messages_from_phase_b_row(
    row: Dict[str, Any],
    *,
    system_prompt: str = "",
) -> List[Dict[str, str]]:
    """将单行 phase_b 转为 chat messages（user + assistant）。"""
    ctx = row.get("context") or {}
    user = phase_b_user_content(ctx)
    assistant = str(row.get("completion") or "").strip()
    messages: List[Dict[str, str]] = []
    if system_prompt.strip():
        messages.append({"role": "system", "content": system_prompt.strip()})
    messages.append({"role": "user", "content": user})
    messages.append({"role": "assistant", "content": assistant})
    return messages


def render_chat_text(
    messages: List[Dict[str, str]],
    tokenizer,
) -> str:
    """优先 ``apply_chat_template``；否则简单角色拼接。"""
    if hasattr(tokenizer, "apply_chat_template") and getattr(tokenizer, "chat_template", None):
        try:
            return tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=False,
            )
        except Exception:
            pass
    parts: List[str] = []
    for m in messages:
        role = m.get("role", "user")
        content = m.get("content", "")
        parts.append(f"<|{role}|>\n{content}\n")
    return "".join(parts).strip()


def completion_token_start(
    tokenizer,
    messages: List[Dict[str, str]],
) -> int:
    """
    完整对话 token 序列中，**模型应参与损失的第一项 completion token** 的下标
    （即 ``input_ids`` 内 assistant 内容起始，含模板添加的 assistant 头）。

    依赖 ``apply_chat_template``；若无模板则退回「用户文本 token 长度 + 1」近似。
    """
    prompt_msgs: List[Dict[str, str]] = []
    for m in messages:
        if m.get("role") == "assistant":
            break
        prompt_msgs.append(dict(m))

    if hasattr(tokenizer, "apply_chat_template") and getattr(tokenizer, "chat_template", None):
        try:
            prompt_ids = tokenizer.apply_chat_template(
                prompt_msgs,
                tokenize=True,
                add_generation_prompt=True,
                return_tensors=None,
            )
            return len(prompt_ids)
        except Exception:
            pass

    prompt_text = render_chat_text(prompt_msgs, tokenizer)
    assistant_msg = next((m for m in messages if m.get("role") == "assistant"), None)
    if not assistant_msg:
        return len(tokenizer(prompt_text, add_special_tokens=True)["input_ids"])
    full_text = render_chat_text(messages, tokenizer)
    full_ids = tokenizer(full_text, add_special_tokens=True)["input_ids"]
    prompt_ids = tokenizer(prompt_text, add_special_tokens=True)["input_ids"]
    plen = min(len(prompt_ids), len(full_ids) - 1)
    if full_ids[:plen] != prompt_ids[:plen]:
        plen = 0
        for i in range(min(len(prompt_ids), len(full_ids))):
            if full_ids[i] != prompt_ids[i]:
                break
            plen = i + 1
    return max(plen, 1)


def group_reward_std(members: List[Dict[str, Any]]) -> Optional[float]:
    """组内奖励标准差。优先用导出时写下的 ``std_r_for_advantage``。"""
    if not members:
        return None
    stats = members[0].get("group_stats") or {}
    raw = stats.get("std_r_for_advantage")
    if raw is not None:
        return float(raw)
    vals: List[float] = []
    for row in members:
        if row.get("R_content") is not None:
            vals.append(float(row["R_content"]))
        elif row.get("r_after_rank") is not None:
            vals.append(float(row["r_after_rank"]))
    if len(vals) < 2:
        return None
    mu = sum(vals) / len(vals)
    var = sum((v - mu) ** 2 for v in vals) / len(vals)
    return var ** 0.5


def advantage_span(members: List[Dict[str, Any]]) -> float:
    advs = [float(row["advantage"]) for row in members if row.get("advantage") is not None]
    if len(advs) < 2:
        return 0.0
    return max(advs) - min(advs)


def select_grpo_rows(
    rows: List[Dict[str, Any]],
    *,
    min_reward_std: float = 0.05,
) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    """
    丢掉组内奖励几乎一样的组。

    这种组标准化后优势会被放大成 ±1，梯度方向是噪声。
    ``min_reward_std`` 作用在 ``R_content``（或导出时的奖励标准差）上，不是标准化后的优势。
    """
    buckets: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    order: List[str] = []
    for i, row in enumerate(rows):
        gid = str(row.get("group_id") or f"row-{i}")
        if gid not in buckets:
            order.append(gid)
        buckets[gid].append(row)

    kept: List[Dict[str, Any]] = []
    dropped_small = 0
    dropped_flat_adv = 0
    dropped_short = 0
    for gid in order:
        members = buckets[gid]
        if len(members) < 2:
            dropped_short += 1
            continue
        std = group_reward_std(members)
        if std is not None and std < float(min_reward_std):
            dropped_small += 1
            continue
        if advantage_span(members) < 1e-6:
            dropped_flat_adv += 1
            continue
        kept.extend(members)
    summary = {
        "groups_in": len(order),
        "groups_kept": len(order) - dropped_small - dropped_flat_adv - dropped_short,
        "groups_dropped_small_gap": dropped_small,
        "groups_dropped_flat_advantage": dropped_flat_adv,
        "groups_dropped_too_small": dropped_short,
        "rows_in": len(rows),
        "rows_kept": len(kept),
    }
    return kept, summary


def build_prompt_only_messages(messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
    out: List[Dict[str, str]] = []
    for m in messages:
        if m.get("role") == "assistant":
            break
        out.append(dict(m))
    return out
