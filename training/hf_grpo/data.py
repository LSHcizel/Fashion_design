"""
从 ``phase_a_sft.jsonl`` / ``phase_b_grpo.jsonl`` 加载样本并格式化为训练用文本。

不依赖 torch；供 ``train_sft`` / ``train_grpo`` 在运行时导入。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterator, List, Union

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


def build_prompt_only_messages(messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
    out: List[Dict[str, str]] = []
    for m in messages:
        if m.get("role") == "assistant":
            break
        out.append(dict(m))
    return out
