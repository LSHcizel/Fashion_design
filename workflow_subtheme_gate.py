"""子主题去留：改写是否被采纳，以及补位时如何替换标题。不依赖模型客户端。"""

from __future__ import annotations

import re

SUB_THEMES_MARKER = "**Sub-themes for chapter development:**"

# 同一章位上，原文子主题因改写未被采纳而废弃后，最多再补几个新子主题。
MAX_SUBTHEME_REPLACEMENTS = 3


def look_rewrite_not_adopted(eval_result: dict | None, *, evaluator_enabled: bool) -> bool:
    """门限失败且改写没有被写回。评估器关闭时不据此剔除 look。"""
    if not evaluator_enabled or not isinstance(eval_result, dict):
        return False
    if eval_result.get("mode") in ("k_rewrite", "passthrough"):
        return False
    return not bool(eval_result.get("both_gates_passed") or eval_result.get("passed"))


def look_kept_for_reflect(eval_result: dict | None, *, evaluator_enabled: bool) -> bool:
    """原文双门限通过，或改写被写回的 look，进入单图和多图 reflect。"""
    if not evaluator_enabled or not isinstance(eval_result, dict):
        return False
    if eval_result.get("mode") == "k_rewrite":
        return True
    return bool(eval_result.get("both_gates_passed") or eval_result.get("passed"))


def subtheme_discarded(eval_results: list | None, *, evaluator_enabled: bool) -> bool:
    """本章每一条已评判 look 都是改写未被采纳时，废弃整个子主题。"""
    rows = list(eval_results or [])
    if not evaluator_enabled or not rows:
        return False
    return all(look_rewrite_not_adopted(row, evaluator_enabled=True) for row in rows)


def replace_sub_theme_heading(
    theme_analysis: str,
    old_name: str,
    new_name: str,
    chapter_index: int | None = None,
) -> str:
    """把主题分析里的章节子主题标题换成补位标题。"""
    text = theme_analysis or ""
    if not new_name or old_name == new_name or SUB_THEMES_MARKER not in text:
        return text
    head, tail = text.split(SUB_THEMES_MARKER, 1)
    if old_name:
        for src, dst in (
            (f"**{old_name}:**", f"**{new_name}:**"),
            (f"**{old_name}**", f"**{new_name}**"),
        ):
            if src in tail:
                return head + SUB_THEMES_MARKER + tail.replace(src, dst, 1)
    if chapter_index is None or chapter_index < 1:
        return text
    ordinal = 0
    for match in re.finditer(r"\*\*([^*]+?)(?::)?\*\*", tail):
        name = re.sub(r"^\d+\.\s*", "", match.group(1).strip()).strip()
        if not name:
            continue
        ordinal += 1
        if ordinal != chapter_index:
            continue
        raw = match.group(0)
        repl = f"**{new_name}:**" if raw.endswith(":**") else f"**{new_name}**"
        start, end = match.span()
        return head + SUB_THEMES_MARKER + tail[:start] + repl + tail[end:]
    return text
