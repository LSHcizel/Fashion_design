"""
《改进方案》第 1 步：在同一条业务背景下并行生成 K 份互不相同的英文改写。

- 评判侧与 `DesignTextEvaluator.evaluate_text`（spec 双门限与 R_content）对齐；仓库内已不再提供多轮自动 optimize。
- 默认对有效候选调用 `DesignTextEvaluator.evaluate_text`，**完全沿用** `fashion_prompt_optimizer_spec.json`
  中的 coverage/quality/penalty 合成、`score_gate` / `penalty_gate` 以及 `r_content_for_rl`；
  同组多条会再执行 `apply_group_z_len_r_content`（档 1：β·z_len；档 3：跳过，改由 `training/odin_rm` 的 r_Q 作为 R_content）。
- 输出结构便于后续组编号、字段对齐与去重（训练 JSONL 见方案第 4 步）。
"""

from __future__ import annotations

import logging
import re
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

from ..text_description_evaluator.design_text_evaluator_api import (
    JudgeConnectionError,
    detect_consistency_conflicts,
    grpo_parallel_k_rewrite_config,
    is_connection_failure,
)
from ..text_description_evaluator.r_content_reward import apply_group_z_len_r_content

if TYPE_CHECKING:
    from ..text_description_evaluator.design_text_evaluator_api import DesignTextEvaluator


REWRITE_STYLE_CONCEPT_LOCK = (
    "THEME AND CONCEPT LOCK: First extract the theme and the design concept already present "
    "in SOURCE (collection story, dualities, aesthetic register, and design intent). "
    "If SOURCE names a theme and concept and then also describes garments from a different "
    "theme or concept, keep only the stated theme and concept. Delete or replace those "
    "conflicting garments. Do not treat that second register as part of the concept you must "
    "preserve. Do not switch to a different theme or a different concept."
)

REWRITE_WHOLE_LOOK_SCOPE = (
    "WHOLE-LOOK CHANGE (allowed, inside theme/concept): You MAY change the overall clothing "
    "so the rewrite is a new realization of the SAME extracted theme and concept — including "
    "color and palette, garment pairing and categories (what is worn with what), silhouette "
    "and layering, and detail design (trim, surface, construction, local craft, accessories). "
    "A color restyle or a different pairing that still reads as that theme/concept is in-scope. "
    "Do not keep SOURCE's current SKU just to be faithful. "
    "When a DELETE list is attached, color and detail may still change, and every garment "
    "already in SOURCE that is not on that list stays. "
    "Out of scope: leaving the theme or design concept, or jumping to a competing register."
)

REWRITE_ELEMENT_RECONSTRUCTION = (
    "ELEMENT RECONSTRUCTION: After extracting theme and concept, redesign the look's elements "
    "to raise DesignMerit: recompose color, pairing, silhouette, layering, surface, edge "
    "treatment, volume, local construction, and detail design while the theme and concept "
    "still read as the same. Acceptable reconstruction may change color and detail. "
    "A garment that is not on the DELETE list stays. "
    "It must not abandon the extracted theme/concept, and must not treat a "
    "collection-shared interchangeable garment formula as the identity."
)

REWRITE_DESIGN_MERIT = (
    "DESIGN MERIT GOAL: Optimize for a higher DesignMerit score. "
    "Write the feature that would still identify this look if the color, the fabric, and the brand "
    "name were swapped. Do not spend the paragraph on a complete wardrobe list. "
    "The number of such features is not fixed: use as many as this look needs, including more than one. "
    "Every feature must serve the theme and concept already extracted from SOURCE, and you must say "
    "where it sits on the garment. "
    "Examples (a menu, not an assignment and not a quota): a pattern, texture, or print covering the "
    "whole cloth; decoration that traces the neckline, front, hem, or cuff; an open outer over a "
    "same-theme inner piece visible in that opening while worn. "
    "A second sleeve, a second bottom, a second shoe, or clothes from another theme is a contradiction, "
    "not that feature. "
    "Do not merely paraphrase SOURCE, retighten wording, or only change pose/background. "
    "If SOURCE already has such a feature, you may strengthen, relocate, or rescale it, and you may "
    "change color and detail, so the generated image can diverge from a clone of SOURCE's "
    "current SKU. A garment that is not on the DELETE list stays. "
    "If SOURCE is only formulaic wardrobe grammar, create that kind of feature inside that theme. "
    "Do not treat factory finishing (topstitching, hidden placket), ordinary dressing "
    "(tucked shirt), brand hardware as identity, or theme dualities as the identity. "
    "Compress promenade/salon/stance commentary. "
    "When a repair brief lists exposed consistency problems or penalty deductions, resolve those "
    "consistency problems and lower those penalty scores in this rewrite."
)

_CONSISTENCY_METRICS = (
    ("bilateral_coherence", "left-right consistency"),
    ("spatial_coherence", "spatial / layering consistency"),
)
_PENALTY_LABELS = {
    "generation_content_penalty": "non-visual or redundant content",
    "consistency_penalty": "trunk consistency",
    "coordination_penalty": "styling coordination",
    "rationality_penalty": "wearability / physical plausibility",
    "formula_template_penalty": "formula template",
}


def _clip_reason(text: str, limit: int = 360) -> str:
    s = " ".join((text or "").split())
    if len(s) <= limit:
        return s
    return s[: limit - 1].rstrip() + "…"


def _reason_for_brief(text: str) -> str:
    """中文评判理由会把改写带成中文，简报里只留英文理由。"""
    reason = _clip_reason(text)
    cjk = len(re.findall(r"[\u4e00-\u9fff]", reason))
    latin = len(re.findall(r"[A-Za-z]", reason))
    if cjk and cjk >= latin:
        return ""
    return reason


_SIDE_SLOT = r"(?:half|side|sleeve|arm|leg|foot|shoe)"


def _clause_side(clause: str) -> str:
    """一句里只有一侧时返回 left 或 right。左右都有则返回 both。"""
    left = re.search(rf"\bleft\s+{_SIDE_SLOT}\b", clause, re.I) or re.search(
        r"\bon the left\b(?!\s+front\b)", clause, re.I
    )
    right = re.search(rf"\bright\s+{_SIDE_SLOT}\b", clause, re.I) or re.search(
        r"\bon the right\b", clause, re.I
    )
    if left and right:
        return "both"
    if right:
        return "right"
    if left:
        return "left"
    return ""


def _garment_payload(clause: str) -> str:
    """去掉 left/right 前缀，只留衣服本身，避免模型把侧别词抄进正文。"""
    text = re.sub(r"^at the same time\s+", "", clause.strip(), flags=re.I)
    text = re.sub(rf"^(?:the\s+)?(?:left|right)\s+{_SIDE_SLOT}\b", "", text, flags=re.I)
    text = re.sub(
        r"^(?:of\s+(?:this|the|that)\s+(?:one\s+)?(?:same\s+)?[A-Za-z]+\s+)?"
        r"(?:is|are|reads as|has)\s+",
        "",
        text.strip(),
        flags=re.I,
    )
    text = re.sub(r"\s+on the left(?:\s+(?:leg|foot|side|arm))?\b", "", text, flags=re.I)
    return text.strip(" ,;.")


_LEFT_RIGHT_EXAMPLE = (
    "LEFT-RIGHT EXAMPLE. Copy this edit. Do not copy the example's clothes.\n"
    "Source: Gold buttons and a crochet bag remain. "
    "The left half is a matte wool jacket and a black trouser. "
    "The right half is a silk dress and a red sandal.\n"
    "Rewrite: Gold buttons and a crochet bag remain, with a matte wool jacket and a black trouser.\n"
    "Keep one side of the contradiction. Also keep every other garment already in SOURCE. "
    "Do not write left or right."
)

_SAME_ELEMENT_EXAMPLE = (
    "SAME-ELEMENT EXAMPLES. Copy these edits. Do not copy the example's clothes.\n"
    "Example 1. Source: The coat closes with a concealed placket. "
    "The same coat also functions as double-breasted.\n"
    "Rewrite: The coat closes with a concealed placket.\n"
    "Example 2. Source: The jacket closes with a concealed placket and ends at the hip. "
    "The same jacket is also double-breasted. The same hem brushes the floor.\n"
    "Rewrite: The jacket closes with a concealed placket and ends at the hip.\n"
    "Delete every later binding, not only one. "
    "A DELETE line must not move onto another garment. "
    "A button, a bag, a trim, or any other garment that is not a DELETE line stays."
)

_SAME_AND_SPLIT = re.compile(
    r"\s+and\s+(?=(?:the|that|those)\s+same\s+)",
    re.I,
)
_SAME_COPULA = re.compile(
    r"^(?:the|that|those)\s+same\s+(?:[A-Za-z-]+\s+){1,3}"
    r"(?:is|are|has|have|reads as)\s+(?:also\s+)?(?:given\s+)?",
    re.I,
)
_SAME_NOUN = re.compile(
    r"^(?:the|that|those)\s+same\s+[A-Za-z-]+\s+",
    re.I,
)


_FOREIGN_SHOE = re.compile(
    r"((?:[A-Za-z'-]+\s+){0,3}"
    r"(?:stilettos?|mules?|pumps?|sandals?|boots?|oxfords?|flats?|slingbacks?|loafers?|heels?|shoes?))",
    re.I,
)


def _shoes_with_foreign_theme(source_text: str, terms: List[str]) -> List[str]:
    """异主题那一句里点名的鞋，跟那些词一起删。不把穆勒或细高跟做成全局禁词。"""
    if not terms:
        return []
    found: List[str] = []
    seen = set()
    for sentence in re.split(r"[。.!?;\n]", source_text or ""):
        low = sentence.lower()
        if not any(term.lower() in low for term in terms):
            continue
        for match in _FOREIGN_SHOE.finditer(sentence):
            snippet = re.sub(r"^(?:with|and|the|a|an)\s+", "", match.group(1).strip(" ,;."), flags=re.I)
            key = snippet.lower()
            if not key or key in seen:
                continue
            seen.add(key)
            found.append(snippet)
    return found


def _left_right_action(source_text: str) -> str:
    """把左右两套拆成必须留下的名词和必须删除的名词。"""
    keep: List[str] = []
    delete: List[str] = []
    chunks = re.split(r"(?<=[.;])\s+|\s+\bwhile\b\s+", source_text or "")
    pending: List[str] = []
    for chunk in chunks:
        clause = chunk.strip(" ;.")
        if not clause:
            continue
        side = _clause_side(clause)
        if side == "both":
            pieces = re.split(r"\s+and\s+(?=the\s+right\b)", clause, flags=re.I)
            pending.extend(pieces)
            continue
        pending.append(clause)
    expanded: List[str] = []
    for clause in pending:
        if _clause_side(clause) == "right" and re.search(r"\band\s+the\s+right\b", clause, re.I):
            expanded.extend(re.split(r"\s+and\s+(?=the\s+right\b)", clause, flags=re.I))
        else:
            expanded.append(clause)
    for clause in expanded:
        side = _clause_side(clause)
        payload = _garment_payload(clause)
        if side == "left" and payload:
            keep.append(payload)
        elif side == "right" and payload:
            delete.append(payload)
        elif _shared_keep_clause(clause):
            keep.append(clause)
    return _keep_delete_block(keep, delete)


def _binding_payload(clause: str) -> str:
    text = clause.strip(" ;.")
    stripped = _SAME_COPULA.sub("", text, count=1)
    if stripped == text:
        stripped = _SAME_NOUN.sub("", text, count=1)
    return stripped.strip(" ,;.")


def _same_element_action(source_text: str) -> str:
    """概念句和 “the same” 之前的绑定留下，每个 “the same” 后面的绑定删除。"""
    keep: List[str] = []
    delete: List[str] = []
    concept = re.search(r"\bConcept:\s*([^.]+)", source_text or "", re.I)
    if concept:
        keep.append(concept.group(1).strip(" ,;."))
    for sentence in re.split(r"[。.!?;\n]", source_text or ""):
        sentence = sentence.strip()
        if not sentence or re.match(r"^(?:theme|concept)\b", sentence, re.I):
            continue
        parts = _SAME_AND_SPLIT.split(sentence)
        if len(parts) == 1:
            if re.match(r"^(?:the|that|those)\s+same\s+", sentence, re.I):
                payload = _binding_payload(sentence)
                if payload:
                    delete.append(payload)
            elif _shared_keep_clause(sentence):
                keep.append(sentence)
            continue
        kept = parts[0].strip(" ,;.")
        if kept and not re.match(r"^(?:the|that|those)\s+same\s+", kept, re.I):
            keep.append(kept)
        for part in parts[1:]:
            payload = _binding_payload(part)
            if payload:
                delete.append(payload)
    return _keep_delete_block(keep, delete)


def _is_meta_clause(text: str) -> bool:
    """说明句不是衣服：生成指令、主题对照，以及 whichever 这种改写旁白。"""
    if re.match(r"^please generate\b", text, re.I):
        return True
    return bool(re.search(r"\b(?:do not share|do not belong|whichever)\b", text, re.I))


def _shared_keep_clause(clause: str) -> bool:
    """没有左右或 the same 的句子是已有要素，不因冲突被删掉。"""
    text = re.sub(r"^at the same time\s+", "", clause.strip(), flags=re.I)
    if not text or _is_meta_clause(text):
        return False
    return True


def _foreign_keep_delete(source_text: str, terms: List[str]) -> str:
    """异主题：白天那一套留下，冒号后的另一套删掉。"""
    keep: List[str] = []
    delete: List[str] = []
    for sentence in re.split(r"[。.!?;\n]", source_text or ""):
        sentence = sentence.strip()
        if not sentence or _is_meta_clause(sentence):
            continue
        low = sentence.lower()
        if any(term.lower() in low for term in terms):
            payload = sentence.split(":")[-1]
            payload = re.sub(r"\breplace the [^,.;]+", "", payload, flags=re.I)
            payload = payload.strip(" ,;.")
            if payload:
                delete.append(payload)
            continue
        keep.append(sentence)
    return _keep_delete_block(keep, delete)


def _keep_delete_block(keep: List[str], delete: List[str]) -> str:
    if not delete:
        return ""
    lines = [
        "KEEP THIS SIDE OF THE CONTRADICTION, and keep every other garment already in SOURCE that is not listed under DELETE:",
    ]
    lines.extend(f"- {item}" for item in keep)
    lines.append(
        "DELETE THESE GARMENTS. They must not appear in the paragraph, "
        "including on another garment, after while, transitions to, no, without, or not:"
    )
    lines.extend(f"- {item}" for item in delete)
    lines.append(
        "Copying a DELETE line, or moving it onto another garment, "
        "is a failed rewrite."
    )
    return "\n".join(lines)


def format_conflict_target(source_text: str) -> str:
    """按正文里的冲突类型写删除指令，而不是再复述两边。"""
    found = detect_consistency_conflicts(source_text or "")
    if not found.get("active"):
        return ""
    lines = [
        "TARGETED DELETE (do this first; do not name the deleted branch in the paragraph):"
    ]
    action = _left_right_action(source_text)
    if action:
        lines.append(_LEFT_RIGHT_EXAMPLE)
        lines.append(action)
    if int(found.get("same_element_bindings") or 0) > 0:
        same_action = _same_element_action(source_text)
        if same_action:
            lines.append(_SAME_ELEMENT_EXAMPLE)
            lines.append(same_action)
    foreign = found.get("foreign_terms") or []
    if foreign:
        foreign_action = _foreign_keep_delete(source_text, foreign)
        if foreign_action:
            lines.append(foreign_action)
        lines.append(
            "These names are a delete list for you. They must not appear in the paragraph, "
            "including after no, without, or not, and not as an inner layer or a reveal: "
            + ", ".join(foreign[:8])
            + "."
        )
        lines.append(
            "Do not rename a deleted garment into a new pattern, a new shoe, or an inner layer."
        )
        foreign_shoes = _shoes_with_foreign_theme(source_text, foreign)
        if foreign_shoes:
            lines.append(
                "Also delete the shoes named with that other theme. Do not rename them: "
                + "; ".join(foreign_shoes)
                + "."
            )
    alternatives = found.get("alternative_slots") or []
    if alternatives:
        lines.append(
            "Or-choice in "
            + ", ".join(alternatives)
            + ". Name one garment in that slot. Do not write or between two bottoms, two shoes, "
            "two necklines, or two sleeve states."
        )
    if found.get("repair_voice"):
        lines.append(
            "Repair narration is in the paragraph. Delete conflicting, replace, delete, restore, "
            "and do not. Write only the garment the camera sees."
        )
    return "\n".join(lines)


def format_exposed_repair_brief(
    evaluation: Optional[Dict[str, Any]],
    source_text: str = "",
) -> str:
    """把原文评判里已暴露的一致性问题和惩罚扣分写成改写必须处理的简报。"""
    target = format_conflict_target(source_text) if (source_text or "").strip() else ""
    if not isinstance(evaluation, dict):
        return target

    consistency_lines: List[str] = []
    metric_results = evaluation.get("metric_results") or {}
    if isinstance(metric_results, dict):
        for key, label in _CONSISTENCY_METRICS:
            row = metric_results.get(key) or {}
            if not isinstance(row, dict) or not row.get("applicable"):
                continue
            try:
                score = float(row.get("score_value"))
            except (TypeError, ValueError):
                continue
            if score >= 1.0:
                continue
            reason = _reason_for_brief(str(row.get("reason") or ""))
            consistency_lines.append(
                f"- {label} ({key}) score={score:.2f}" + (f": {reason}" if reason else "")
            )

    penalty_lines: List[str] = []
    items = (
        ((evaluation.get("scores") or {}).get("quality_score") or {})
        .get("penalties") or {}
    ).get("items") or {}
    if isinstance(items, dict):
        for key, item in items.items():
            if not isinstance(item, dict):
                continue
            try:
                score = float(item.get("score", 0.0) or 0.0)
            except (TypeError, ValueError):
                continue
            if score <= 0:
                continue
            label = _PENALTY_LABELS.get(str(key), str(key))
            reason = _reason_for_brief(str(item.get("reason") or ""))
            line = f"- {label} ({key}) score={score:.2f}" + (f": {reason}" if reason else "")
            penalty_lines.append(line)
            if key == "consistency_penalty":
                consistency_lines.append(line)

    if not consistency_lines and not penalty_lines and not target:
        return ""

    parts = [
        "REPAIR BRIEF (from the current evaluation of SOURCE; required):",
        "Write the paragraph in English. Do not copy these notes into it.",
        "Delete the other set of clothes and strictly unify into one set: "
        "one footwear family, and one contradictory binding removed.",
    ]
    if target:
        parts.insert(1, target)
    if consistency_lines:
        parts.append("EXPOSED CONSISTENCY:")
        parts.extend(consistency_lines)
    if penalty_lines:
        parts.append("EXPOSED PENALTY DEDUCTIONS:")
        parts.extend(penalty_lines)
    return "\n".join(parts)

REWRITE_BRAND_LOGO_LOCK = (
    "BRAND LOGO LOCK (hard): You do not see the original image; SOURCE plus any business "
    "context is the ground for logos. If a house logo, monogram, interlocking-letter mark, "
    "branded buckle, or letter motif is described (or the house is named in context and a "
    "chest/belt/hardware mark is present): keep that SAME house and the SAME mark family. "
    "You MAY change its placement and scale. You MUST NOT replace it with another brand "
    "(no YSL, Dior, Gucci, Louis Vuitton, or any other maison when SOURCE/context is that house). "
    "Do not paraphrase a specific house mark into a generic 'interlocking letters' that an "
    "image model could render as a different brand — name or keep the same mark identity. "
    "If SOURCE has no logo/monogram, do not invent another house's logo."
)

REWRITE_SINGLE_FRAME = (
    "SINGLE FRAME (hard): The paragraph is one moment, one body, one camera, and only what that "
    "camera sees on the worn clothes. No collage, no flat lay, no product shot, no second view, "
    "no back panel, and no text in the image. Do not write a Look number or a look title. "
    "Do not write if removed, its own garment, complete the look, or finish the look. "
    "An inner layer stays visible in the opening of this same view. Accessories stay on the body. "
    "Do not copy the single-frame instruction line into the paragraph."
)

REWRITE_CONSISTENCY_REPAIR = (
    "STRICT UNIFICATION. Delete the other set of clothes and strictly unify into one set: "
    "one sleeve grammar, one bottom, one footwear family, one neckline, one length, one closure, one shell. "
    "When KEEP and DELETE lines or a LEFT-RIGHT EXAMPLE or a SAME-ELEMENT EXAMPLE are attached, "
    "copy that edit. Keep one side of each contradiction, and keep every other garment already in SOURCE. "
    "Do not copy the example's clothes. "
    "A DELETE line must not appear on another garment. "
    "A fluent sentence that still contains both sets is a failed rewrite. "
    "Keep one binding and delete the contradictory binding. "
    "A brooch, an off-center bow, one slit, a wrap, a drape, or an uneven hem on the kept garment "
    "is placement, not a second garment. "
    "Do not write or between two bottoms, two shoes, two necklines, or two sleeve states. "
    "Do not keep the deleted set with while, transitions to, or on the right. "
    "The paragraph is only what the camera sees. Do not write conflicting, replace, delete, restore, or do not."
)

REWRITE_SHARED_STRATEGY = (
    "SHARED STRATEGY (theme/concept lock + logo lock; whole-look change inside that lock): "
    "1) Extract theme and concept from SOURCE only — there is no separate chapter brief. "
        "2) You may change color and detail so this sample is not a wording-only clone of SOURCE. "
        "Stay inside the extracted theme and concept. When a DELETE list is attached, every "
        "garment already in SOURCE that is not on that list stays. Do not keep a second sleeve, "
        "bottom, shoe, or another theme's garment in order to make the look fuller. "
        "Visible ideas have no fixed count; each one "
    "must serve that extracted theme and concept. Idea kinds are a menu, not a quota and not a "
    "per-candidate assignment. "
    "3) Keep any original house logo/monogram as the same brand mark (placement/scale may change). "
    "4) Output one coherent English paragraph. "
    "5) If a repair brief is attached, follow its KEEP and DELETE lines and lower its exposed penalty deductions. "
    "6) Obey the consistency repair above."
)

# Backward-compatible name used by workflow extra_context.
REWRITE_LOCAL_EDITS_ALLOWED = REWRITE_ELEMENT_RECONSTRUCTION


def build_rewrite_user_prompt(
    source_text: str,
    k: int,
    candidate_index: int,
    extra_context: str = "",
) -> str:
    """K 路改写 user prompt：原文和业务上下文在前，规则在后，避免 7B 先读长规则而漏掉正文。"""
    user = (
        "PARALLEL REWRITE TASK\n"
        f"You are producing rewrite candidate #{candidate_index + 1} of {k} for the SAME source. "
        "Candidates are sampled separately at different temperatures.\n"
        "The SOURCE TEXT below is complete. Any BUSINESS CONTEXT below is complete. "
        "Read both in full so you can see which element contradicts another. "
        "Keep one side of each contradiction. Keep every other garment already in SOURCE.\n\n"
        f"SOURCE TEXT TO REWRITE:\n{source_text.strip()}\n\n"
    )
    if extra_context.strip():
        user += (
            f"BUSINESS CONTEXT / CONSTRAINTS (shared across all {k} candidates):\n"
            f"{extra_context.strip()}\n\n"
        )
    user += (
        "RULES FOR THE TEXT ABOVE:\n"
        "Their count is not fixed. Each idea must serve the theme and concept extracted from SOURCE.\n\n"
        f"{REWRITE_CONSISTENCY_REPAIR}\n\n"
        f"{REWRITE_SINGLE_FRAME}\n\n"
        f"{REWRITE_SHARED_STRATEGY}\n"
        f"{REWRITE_STYLE_CONCEPT_LOCK}\n"
        f"{REWRITE_WHOLE_LOOK_SCOPE}\n"
        f"{REWRITE_BRAND_LOGO_LOCK}\n"
        f"{REWRITE_ELEMENT_RECONSTRUCTION}\n"
        f"{REWRITE_DESIGN_MERIT}\n\n"
        "OUTPUT RULES:\n"
        "1. Output exactly one English paragraph: the optimized fashion image prompt only. Do not write Chinese.\n"
        "2. No markdown fences, no numbering, no preamble or commentary.\n"
        "3. After the other set of clothes is deleted, lead with the kept idea, then outer-to-inner visual order.\n"
        "4. Whole-look change is allowed (color, pairing, details) only inside SOURCE's theme and concept.\n"
        "5. If SOURCE or business context has a house logo/monogram, keep that same brand mark "
        "(placement and size may change; never another house).\n"
        "6. If a repair brief is present, resolve every listed consistency problem and lower every listed penalty.\n"
        "7. Omit the contradictory side. Keep every other garment already in SOURCE. "
        "Omitting the other set is required.\n"
        "8. One moment, one body, one camera. No Look number, no collage, no flat lay, "
        "no product shot, and no off-body catalog sentence.\n"
    )
    return user


def _normalize_for_dedup(text: str) -> str:
    s = (text or "").strip().lower()
    s = re.sub(r"\s+", " ", s)
    return s


def _dedupe_by_normalized_text(
    candidates: List[Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], int]:
    seen: set[str] = set()
    kept: List[Dict[str, Any]] = []
    removed = 0
    for c in candidates:
        key = _normalize_for_dedup(str(c.get("text", "")))
        if not key:
            removed += 1
            c = {**c, "dedupe_kept": False, "dedupe_reason": "empty"}
            kept.append(c)
            continue
        if key in seen:
            removed += 1
            kept.append({**c, "dedupe_kept": False, "dedupe_reason": "duplicate_normalized"})
            continue
        seen.add(key)
        kept.append({**c, "dedupe_kept": True})
    return kept, removed


def _default_evaluator() -> "DesignTextEvaluator":
    from ..local_llm import build_parallel_k_evaluator

    return build_parallel_k_evaluator()


def _one_rewrite(
    evaluator: "DesignTextEvaluator",
    source_text: str,
    k: int,
    candidate_index: int,
    extra_context: str,
    temperature_floor: float,
    temperature_step: float,
    temperature_cap: float,
) -> Dict[str, Any]:
    """Worker：单次生成一条候选。"""
    t = min(temperature_cap, temperature_floor + candidate_index * temperature_step)
    user = build_rewrite_user_prompt(
        source_text,
        k,
        candidate_index,
        extra_context,
    )
    try:
        raw = evaluator.judge.generate_text(
            system_prompt=evaluator.optimizer_system_prompt,
            user_prompt=user,
            temperature=t,
            max_tokens=evaluator.judge.max_tokens,
        )
        text = evaluator._validate_optimized_text(raw, source_text)
        text = evaluator._normalize_optimized_text(text)
        return {
            "candidate_index": candidate_index,
            "text": text,
            "char_len": len(text),
            "temperature": t,
            "error": None,
        }
    except Exception as exc:  # noqa: BLE001
        if isinstance(exc, JudgeConnectionError) or is_connection_failure(exc):
            raise JudgeConnectionError(str(exc)) from exc
        return {
            "candidate_index": candidate_index,
            "text": "",
            "char_len": 0,
            "temperature": t,
            "error": str(exc),
        }


def _evaluate_candidates_with_spec(
    evaluator: "DesignTextEvaluator",
    deduped: List[Dict[str, Any]],
    *,
    gate_config: Optional[Dict[str, Any]],
    eval_source_prefix: str,
    eval_max_workers: int,
) -> List[Dict[str, Any]]:
    """
    对去重后保留的候选逐条 `evaluate_text`，并在同组上应用 z_len 修正 R_content。
    返回参与组内 R_content 修正的 evaluate 结果列表（与 candidate_index 升序一致）。
    """
    work_items: List[Tuple[int, Dict[str, Any]]] = []

    for c in deduped:
        if not c.get("dedupe_kept"):
            c["evaluation"] = None
            c["evaluation_skipped"] = "duplicate_or_empty"
            continue
        if c.get("error"):
            c["evaluation"] = None
            c["evaluation_skipped"] = "rewrite_error"
            continue
        work_items.append((int(c["candidate_index"]), c))

    if not work_items:
        return []

    def run_one(
        idx: int, cand: Dict[str, Any]
    ) -> Tuple[int, Dict[str, Any], Optional[Dict[str, Any]], Optional[str]]:
        src = f"{eval_source_prefix}.c{idx}"
        try:
            result = evaluator.evaluate_text(cand["text"], source_name=src, gate_config=gate_config)
            return idx, cand, result, None
        except JudgeConnectionError:
            raise
        except Exception as exc:  # noqa: BLE001
            if is_connection_failure(exc):
                raise JudgeConnectionError(str(exc)) from exc
            return idx, cand, None, str(exc)

    def _apply_eval(
        cand: Dict[str, Any],
        ev: Optional[Dict[str, Any]],
        err: Optional[str],
    ) -> None:
        if err:
            cand["evaluation"] = None
            cand["evaluation_skipped"] = "judge_eval_error"
            cand["evaluation_error"] = err
            logger.warning(
                "skip evaluate for %s.c%s: %s",
                eval_source_prefix,
                cand.get("candidate_index"),
                err,
            )
            return
        cand["evaluation"] = ev

    if len(work_items) == 1:
        idx, cand = work_items[0]
        _, _, ev, err = run_one(idx, cand)
        _apply_eval(cand, ev, err)
    else:
        n_workers = max(1, min(eval_max_workers, len(work_items)))
        futures = {}
        with ThreadPoolExecutor(max_workers=n_workers) as pool:
            for idx, cand in work_items:
                futures[pool.submit(run_one, idx, cand)] = (idx, cand)
            for fut in as_completed(futures):
                idx, cand, ev, err = fut.result()
                _apply_eval(cand, ev, err)

    ordered_evals: List[Dict[str, Any]] = []
    for c in sorted(deduped, key=lambda x: int(x["candidate_index"])):
        ev = c.get("evaluation")
        if isinstance(ev, dict) and (ev.get("r_content") or {}).get("enabled"):
            ordered_evals.append(ev)

    if ordered_evals:
        rcfg = evaluator.spec.get("r_content_for_rl") or {}
        apply_group_z_len_r_content(ordered_evals, rcfg)

    return ordered_evals


def generate_k_parallel_rewrites(
    text_description: str,
    k: Optional[int] = None,
    *,
    evaluator: Optional["DesignTextEvaluator"] = None,
    group_id: Optional[str] = None,
    extra_context: str = "",
    max_workers: Optional[int] = None,
    temperature_floor: float = 0.15,
    temperature_step: float = 0.05,
    temperature_cap: float = 0.55,
    evaluate_candidates: bool = True,
    gate_config: Optional[Dict[str, Any]] = None,
    eval_source_prefix: str = "parallel_k",
    eval_max_workers: Optional[int] = None,
) -> Dict[str, Any]:
    """
    同一背景文本下并行生成 K 条英文改写候选。

    Parameters
    ----------
    text_description : str
        当前待改写的时尚描述正文（与同组 K 条共享）。
    k : int, optional
        候选条数；为 ``None`` 时使用 ``fashion_config.yaml`` → ``grpo.parallel-k-rewrite.k``（缺省 **8**）。
    evaluator :
        可选；默认新建 `DesignTextEvaluator()` 以复用 `fashion_sys_prompt.txt` 与 API 配置。
    group_id :
        可选；不传则生成 UUID，供 GRPO 组编号对齐。
    extra_context :
        各候选共享的额外业务说明（与同组字段对齐）。
    max_workers :
        改写线程池大小；默认 ``min(k, 8)``。
    temperature_floor / temperature_step / temperature_cap :
        按 candidate_index 递进温度；各路独立选择识别性想法，不预分配种类。
    evaluate_candidates :
        为 True（默认）时，对去重保留的候选调用 `evaluate_text`，门限与分数与
        `plugins/text_description_evaluator` 完全一致；False 则仅生成文本（旧行为）。
    gate_config :
        传入 `evaluate_text` 的门限覆盖，例如 ``{"score_gate_min": 0.8, "penalty_gate_max": 0.25}``；
        为 None 时使用 spec 中 ``optimization_gates`` 默认。
    eval_source_prefix :
        评判 `source_name` 前缀，单条为 ``{prefix}.c{index}``。
    eval_max_workers :
        评判并发数；默认 ``min(k, 4)``（评判 API 调用更重，默认略保守）。

    Returns
    -------
    dict
        含 ``group_id``、``candidates``（可含 ``evaluation`` 全量评判字典）、``duplicates_removed``、``errors``。
    """
    _pk = grpo_parallel_k_rewrite_config()
    if k is None:
        k = int(_pk.get("k", 8))
    if k < 1:
        raise ValueError("k must be >= 1")
    if "temperature-floor" in _pk:
        temperature_floor = float(_pk["temperature-floor"])
    if "temperature-step" in _pk:
        temperature_step = float(_pk["temperature-step"])
    if "temperature-cap" in _pk:
        temperature_cap = float(_pk["temperature-cap"])
    if max_workers is None and _pk.get("max-workers") is not None:
        max_workers = int(_pk["max-workers"])
    if eval_max_workers is None and _pk.get("eval-max-workers") is not None:
        eval_max_workers = int(_pk["eval-max-workers"])
    if "evaluate-candidates" in _pk:
        evaluate_candidates = bool(_pk["evaluate-candidates"])
    if "eval-source-prefix" in _pk and _pk.get("eval-source-prefix") is not None:
        eval_source_prefix = str(_pk["eval-source-prefix"])
    ev = evaluator or _default_evaluator()
    gid = group_id or str(uuid.uuid4())
    workers = min(k, max_workers) if max_workers is not None else min(k, 8)

    futures = {}
    with ThreadPoolExecutor(max_workers=max(1, workers)) as ex:
        for i in range(k):
            futures[
                ex.submit(
                    _one_rewrite,
                    ev,
                    text_description,
                    k,
                    i,
                    extra_context,
                    temperature_floor,
                    temperature_step,
                    temperature_cap,
                )
            ] = i

        rows: List[Dict[str, Any]] = []
        for fut in as_completed(futures):
            rows.append(fut.result())
    rows.sort(key=lambda r: r["candidate_index"])

    deduped, dup_count = _dedupe_by_normalized_text(rows)
    errors = [r for r in deduped if r.get("error")]
    for row in errors:
        if is_connection_failure(row.get("error")):
            raise JudgeConnectionError(str(row.get("error")))

    eval_workers = eval_max_workers if eval_max_workers is not None else min(k, 4)
    group_evals: List[Dict[str, Any]] = []
    if evaluate_candidates:
        group_evals = _evaluate_candidates_with_spec(
            ev,
            deduped,
            gate_config=gate_config,
            eval_source_prefix=f"{eval_source_prefix}.{gid[:8]}",
            eval_max_workers=eval_workers,
        )

    candidates_evaluated = sum(1 for c in deduped if c.get("evaluation") is not None)

    return {
        "group_id": gid,
        "source_text": text_description,
        "k_requested": k,
        "k_returned": len(deduped),
        "candidates": deduped,
        "duplicates_removed": dup_count,
        "errors": errors,
        "extra_context": extra_context,
        "evaluate_candidates": evaluate_candidates,
        "gate_config": gate_config,
        "candidates_evaluated": candidates_evaluated,
        "r_content_group_size": len(group_evals),
    }


def build_candidate_group_payload(
    parallel_result: Dict[str, Any],
    *,
    group_round: int = 0,
    source_name: str = "inline",
) -> Dict[str, Any]:
    """
    将 ``generate_k_parallel_rewrites`` 的结果整理为与训练契约对齐的扁平结构（字段名可按方案第 4 步扩展）。

    每条候选占一条子记录，共享同一 ``group_id``，便于 JSONL 写出。
    """
    gid = parallel_result.get("group_id")
    base = {
        "group_id": gid,
        "group_round": group_round,
        "source_name": source_name,
    }
    rows: List[Dict[str, Any]] = []
    for c in parallel_result.get("candidates") or []:
        row: Dict[str, Any] = {
            **base,
            "candidate_index": c.get("candidate_index"),
            "rewrite_text": c.get("text", ""),
            "char_len": c.get("char_len", 0),
            "dedupe_kept": c.get("dedupe_kept", True),
            "temperature": c.get("temperature"),
            "error": c.get("error"),
        }
        ev = c.get("evaluation")
        if isinstance(ev, dict):
            gates = ev.get("gates") or {}
            sg = gates.get("score_gate") or {}
            pg = gates.get("penalty_gate") or {}
            rc = ev.get("r_content") or {}
            row.update(
                {
                    "total_score": ev.get("total_score"),
                    "S_fp": ev.get("total_score"),
                    "score_gate_passed": sg.get("passed"),
                    "penalty_gate_passed": pg.get("passed"),
                    "total_penalty": (ev.get("scores") or {})
                    .get("quality_score", {})
                    .get("penalties", {})
                    .get("total_penalty"),
                    "R_content": rc.get("R_content") if rc.get("enabled", True) else None,
                    "evaluation_source_name": ev.get("source_name"),
                }
            )
        rows.append(row)
    return {
        "group_id": gid,
        "group_round": group_round,
        "source_name": source_name,
        "rows": rows,
        "duplicates_removed": parallel_result.get("duplicates_removed", 0),
    }
