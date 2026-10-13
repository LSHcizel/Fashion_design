"""改写是否还落在正常词表上。与推理回退、GRPO 优势使用同一条规则。"""

from __future__ import annotations

from typing import Any, Dict

MIN_COMPLETION_CHARS = 20
MIN_MEANINGFUL_RATIO = 0.6
_MEANINGFUL_PUNCT = " .,;:!?-'\"（）《》「」‘’“”–—…"


def meaningful_char_ratio(text: str) -> float:
    """字母、数字和少量标点占全文的比例。空串为 0。"""
    body = text or ""
    if not body:
        return 0.0
    meaningful = sum(1 for ch in body if ch.isalnum() or ch in _MEANINGFUL_PUNCT)
    return meaningful / len(body)


def is_low_meaningful_completion(text: str) -> bool:
    """长度够、但有效字符比例低于 0.6。短文本另有长度回退，不算这一条。"""
    body = (text or "").strip()
    if len(body) < MIN_COMPLETION_CHARS:
        return False
    return meaningful_char_ratio(body) < MIN_MEANINGFUL_RATIO


def row_excluded_for_low_meaningful(row: Dict[str, Any]) -> bool:
    """样本原文或导出后的 completion 离开了正常词表。"""
    if is_low_meaningful_completion(str(row.get("completion") or "")):
        return True
    reasons = (row.get("training_filter") or {}).get("exclude_reasons") or []
    return "low_meaningful_chars" in reasons
