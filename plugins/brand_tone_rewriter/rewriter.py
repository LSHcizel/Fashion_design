"""第二改写器：只改已经生成的 description。

输入是确切的品牌、品牌主题和这段 description。先读这家在该主题下的已有做法和相近做法，
找出体现品牌风格的特征点和标识点；再按这些点改写。只要符合品牌和主题调性，
并且设计合理，就允许较大幅度替换款式、廓形、体积、表面和搭配。
仍是一套能穿的衣服。只有换成另一家、叠成第二套，或出现严重冲突时才丢掉。
不经过评分器。模型走 API 的 gpt-5.4-mini。
"""

from __future__ import annotations

import json
import re
from typing import Any, Callable, Dict, List, Optional, Sequence

from plugins.brand_tone_rewriter.brand_card import (
    brand_preference_items,
    format_existing_designs,
)

MODEL_NAME = "gpt-5.4-mini"

_FEASIBLE = (
    "Large replacement is allowed when the result fits this house's tone under this theme "
    "and the design is reasonable: one worn look, one body, clothes a person can wear. "
    "Garment type, silhouette, volume, surface, closure, pairing, and color may all be replaced. "
    "Do not keep the generated clothes only because they are already written. "
    "Drop a replacement only when it imports another house, stacks a second outfit, "
    "or creates a serious conflicting inconsistency. "
    "The result stays fully dressed: clothes cover the chest, the torso, and the legs. "
    "An open or low neckline still has a shirt, a camisole, or a bodice. "
    "Do not write bare chest, bare breasts, lingerie worn as the outfit, sheer cloth that shows the body, "
    "or seductive, sensual, or erotic framing. "
    "A house habit of a plunge becomes a clothed neckline. A bold replacement stays a garment."
)

_ANALYZE_SYSTEM = (
    "You analyze existing and similar fashion designs for one house and one theme. "
    "You do not write the look. Feature points are visible design traits that carry this "
    "house's style into this theme, including the sharper and more avant-garde habits on file. "
    "Signature points are the few traits that would still identify the house if the color and "
    "the fabric changed. Similar designs are the on-file habits that may replace the generated clothes outright. "
    "Prefer the habit that most clearly carries this house's tone under this theme, "
    "including a large replacement of garment type, volume, or surface. "
    f"{_FEASIBLE} "
    "Do not drop a habit only because it is sharper, stranger, or from a more specific motif. "
    "Do not invent a house. "
    'Return JSON only: {"feature_points": ["..."], "signature_points": ["..."], '
    '"similar_designs": ["..."]}.'
)

_SUGGEST_SYSTEM = (
    "You propose edits that make one generated fashion description fit one house and one theme. "
    "This is not a score and not a repair. Large replacement is the expected move when it fits the tone. "
    "You may replace a garment type when another type belongs to this house under this theme: "
    "a jacket may become a coat, a knit, a shirt, a dress, or another piece this house would actually wear. "
    "You may replace the whole silhouette, volume, surface, and pairing. "
    f"{_FEASIBLE} "
    "Do not import another house or another house's logo. "
    "Use the feature points and signature points. Keep one worn look, one moment, one camera in front of her face. "
    "She faces the camera. Front view only, not from behind. "
    'Return JSON only: {"suggestions": [{"edit": "...", "where": "..."}]}.'
)

_REFLECT_SYSTEM = (
    "You judge only whether a combined design fits this house's tone under this theme. "
    "There is no score. Keep a large replacement when it fits this house's tone under this theme "
    "and remains a reasonable design. "
    f"{_FEASIBLE} "
    "Drop an edit only when the clash is a second outfit, another house, or a serious conflicting inconsistency. "
    "After that reflection, write one English paragraph: the new description. "
    "Write the replacement as the clothes the camera sees. Do not shrink a large replacement "
    "back into a small trim on the original garment. "
    "One moment, one body, one camera in front of her face. She faces the camera. "
    "Front view only, not from behind. No collage, no rear view, no second view, no text. "
    'Return JSON only: {"kept": ["..."], "dropped": ["..."], "reflection": "...", '
    '"description": "..."}.'
)


def _parse_json(raw: str) -> Dict[str, Any]:
    text = (raw or "").strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            return {}
        try:
            data = json.loads(match.group(0))
        except json.JSONDecodeError:
            return {}
    return data if isinstance(data, dict) else {}


def _string_list(value: object) -> List[str]:
    if not isinstance(value, list):
        return []
    lines = []
    for item in value:
        if isinstance(item, str) and item.strip():
            lines.append(item.strip())
        elif isinstance(item, dict):
            text = str(item.get("edit") or item.get("text") or "").strip()
            if text:
                lines.append(text)
    return lines


def _suggestions(value: object) -> List[Dict[str, str]]:
    if not isinstance(value, list):
        return []
    rows = []
    for item in value:
        if isinstance(item, str) and item.strip():
            rows.append({"edit": item.strip(), "where": ""})
        elif isinstance(item, dict):
            edit = str(item.get("edit") or "").strip()
            where = str(item.get("where") or "").strip()
            if edit:
                rows.append({"edit": edit, "where": where})
    return rows


def _call(generate_text: Callable[..., str], system_prompt: str, user_prompt: str, max_tokens: int) -> str:
    return generate_text(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0,
        max_tokens=max_tokens,
    )


def _default_generate_text() -> Callable[..., str]:
    from plugins.text_description_evaluator.design_text_evaluator_api import DesignTextEvaluator

    evaluator = DesignTextEvaluator(model=MODEL_NAME)
    return evaluator.judge.generate_text


def rewrite_generated_description(
    *,
    brand: str,
    theme: str,
    description: str,
    generate_text: Optional[Callable[..., str]] = None,
) -> Dict[str, Any]:
    """改写一条已经生成的 description。品牌和主题必须是调用方给出的确切值。"""
    brand = str(brand or "").strip()
    theme = str(theme or "").strip()
    description = str(description or "").strip()
    if not brand or not theme or not description:
        raise ValueError("brand, theme, and description are required")

    house, items = brand_preference_items(explicit=brand)
    result: Dict[str, Any] = {
        "brand": brand,
        "theme": theme,
        "house": house,
        "source_description": description,
        "model": MODEL_NAME,
        "feature_points": [],
        "signature_points": [],
        "similar_designs": [],
        "suggestions": [],
        "kept": [],
        "dropped": [],
        "reflection": "",
        "description": description,
    }
    if not house or not items:
        result["skipped"] = "no habit card for this brand"
        return result

    caller = generate_text or _default_generate_text()
    existing = format_existing_designs(house, items)
    analysis = _parse_json(
        _call(
            caller,
            _ANALYZE_SYSTEM,
            (
                f"BRAND: {house}\n"
                f"THEME: {theme}\n\n"
                f"{existing}\n\n"
                "GENERATED DESCRIPTION:\n"
                f"{description}\n\n"
                "Bring forward on-file habits that can replace the generated clothes at a large scale "
                "while staying inside this house's tone under this theme. "
                f"{_FEASIBLE} "
                "Name the feature points and the signature points, and list those feasible designs."
            ),
            700,
        )
    )
    result["feature_points"] = _string_list(analysis.get("feature_points"))
    result["signature_points"] = _string_list(analysis.get("signature_points"))
    result["similar_designs"] = _string_list(analysis.get("similar_designs"))
    if not result["feature_points"] and not result["signature_points"]:
        result["skipped"] = "no brand points"
        return result

    suggestions = _suggestions(
        _parse_json(
            _call(
                caller,
                _SUGGEST_SYSTEM,
                (
                    f"BRAND: {house}\nTHEME: {theme}\n\n"
                    f"FEATURE POINTS:\n- " + "\n- ".join(result["feature_points"]) + "\n\n"
                    f"SIGNATURE POINTS:\n- " + "\n- ".join(result["signature_points"]) + "\n\n"
                    "Rewrite for brand and theme fit. A large replacement is allowed when it is a "
                    "reasonable design in this house's tone under this theme. "
                    "Replace a garment type, the silhouette, the volume, or the surface when that fits. "
                    f"{_FEASIBLE}\n\n"
                    "GENERATED DESCRIPTION:\n"
                    f"{description}"
                ),
                800,
            )
        ).get("suggestions")
    )
    result["suggestions"] = suggestions
    if not suggestions:
        result["skipped"] = "no suggestions"
        return result

    reflected = _parse_json(
        _call(
            caller,
            _REFLECT_SYSTEM,
            _reflection_user(house, theme, description, result, suggestions),
            1200,
        )
    )
    result["kept"] = _string_list(reflected.get("kept"))
    result["dropped"] = _string_list(reflected.get("dropped"))
    result["reflection"] = str(reflected.get("reflection") or "").strip()
    rewritten = " ".join(str(reflected.get("description") or "").split())
    if rewritten:
        result["description"] = rewritten
    return result


def _reflection_user(
    house: str,
    theme: str,
    description: str,
    result: Dict[str, Any],
    suggestions: Sequence[Dict[str, str]],
) -> str:
    lines = [
        f"BRAND: {house}",
        f"THEME: {theme}",
        "",
        "SIGNATURE POINTS:",
    ]
    lines.extend(f"- {point}" for point in result["signature_points"])
    lines.append("")
    lines.append("SUGGESTED EDITS:")
    for index, item in enumerate(suggestions, start=1):
        where = f" ({item['where']})" if item.get("where") else ""
        lines.append(f"{index}. {item['edit']}{where}")
    lines.extend(
        [
            "",
            "GENERATED DESCRIPTION:",
            description,
            "",
            "Keep a suggestion when the combined look still fits this house's tone. "
            f"{_FEASIBLE} "
            "Then write the new description so each kept edit is visible.",
        ]
    )
    return "\n".join(lines)
