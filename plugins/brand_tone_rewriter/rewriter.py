"""品牌调性改写：只改已经生成的 description，并且发生在评分之前。

品牌参照只来自这一场秀，而且抽取时不看已经生成的描述。
秀评单独收成立场句。成衣图单独收成风格描述句。两列互不代替。
再把描述里的原句按同一根轴去对。原句把该轴说反，才记为冲突。
秀评立场和图片风格句只要有一边至少一条冲突，就生成修改点并改写，而且只改这些冲突句。
两边都没有冲突，或缺少任意一列参照，就留下原文。这一步不另造品牌整体调性。
这一步不读质量分。改完再评分；门限不过时才做基于评分的质量改写。模型走 API 的 gpt-5.4-mini。
"""

from __future__ import annotations

import json
import re
from itertools import combinations
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from plugins.brand_tone_rewriter.brand_card import _is_logo_inventory
from plugins.brand_tone_rewriter.web_search import search_similar_designs

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

_REVIEW_STANCE_SYSTEM = (
    "You read one show review for one house and one theme. "
    "You do not see a generated outfit, and you do not see runway photographs. "
    "Write the review's design stances. Each stance is one axis and one direction: "
    "structure, volume, surface, or dressing. "
    "Do not list a garment inventory, and do not copy a look. "
    "At most four short English sentences. If the review states no design stance, return an empty list. "
    'Return JSON only: {"stances": ["..."]}.'
)

_IMAGE_STYLE_SYSTEM = (
    "You read evenly spaced runway photographs for one house and one theme. "
    "You do not see a generated outfit, and you do not see the show review. "
    "Write style description sentences for how the clothes read across these photographs. "
    "Each sentence is one axis and one direction: structure, volume, surface, or dressing. "
    "Do not list a garment inventory, and do not describe a single look. "
    "At most four short English sentences. If the photographs share no style, return an empty list. "
    'Return JSON only: {"styles": ["..."]}.'
)

_CHECK_SYSTEM = (
    "You compare one generated description with brand-style sentences. "
    "Review stances come from the show review. Image sentences come from runway photographs. "
    "For every sentence, name its axis, copy one short quote from the description, and mark a status. "
    "carried: the quote states the same direction on that axis. "
    "conflict: the quote states the opposite direction on that same axis. "
    "absent: the description does not state that axis. "
    "A different garment, color, or material name is not a conflict. "
    "Copy the quote from the description. Do not paraphrase it, and do not invent a word that is not written. "
    "If you cannot copy a quote, use absent and an empty quote. "
    "Copy each stance sentence unchanged. Do not suggest edits. Do not rewrite the description. "
    'Return JSON only: {"checks": [{"source": "review", "stance": "...", "axis": "...", "quote": "...", "status": "conflict"}]}.'
)

_POINTS_SYSTEM = (
    "You turn confirmed conflicts into concrete edit points for one generated description. "
    "Each conflict names one brand-style sentence, its axis, and the description quote that states the opposite. "
    "Each point repairs one conflict. It must say what to change, what that change is paired with, "
    "and that it drops the conflicting quote so the two do not stack into a second outfit. "
    "Do not add a point for a carried quote or an absent stance. "
    "Do not combine the points. Do not score them. Do not write the new description. "
    "At most four points. "
    f"{_FEASIBLE} "
    'Return JSON only: {"points": [{"edit": "...", "pair": "...", "drop": "..."}]}.'
)

_SCORE_SYSTEM = (
    "You give an abstract score to each combination of edit points. "
    "The score is from 0 to 1. It measures only how completely that combination repairs the confirmed conflicts "
    "in one coherent worn look, while every carried quote stays in place. "
    "The pairings agree, and the drops remove the conflicting quotes. "
    "Do not score photography, sentence length, or polish. Do not pick a winner. Do not write a description. "
    'Return JSON only: {"scores": [{"ids": [1], "score": 0.0}]}.'
)

_WRITE_SYSTEM = (
    "You write one English paragraph from one selected combination of edit points. "
    "Apply only those edits. Honor each pairing and each drop. "
    "Do not add an edit that was not selected. "
    f"{_FEASIBLE} "
    "One moment, one body, one camera in front of her face. She faces the camera. "
    "Front view only, not from behind. No collage, no rear view, no second view, no text. "
    'Return JSON only: {"description": "..."}.'
)

_MAX_DIRECTIONS = 4
_MAX_POINTS = 4


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


def _call(generate_text: Callable[..., str], system_prompt: str, user_prompt: str, max_tokens: int) -> str:
    return generate_text(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0,
        max_tokens=max_tokens,
    )


def _clean_lines(value: object, limit: int) -> List[str]:
    lines = []
    for line in _string_list(value):
        if _is_logo_inventory(line):
            continue
        lines.append(line)
        if len(lines) >= limit:
            break
    return lines


def _image_urls(hits: Sequence[Dict[str, Any]]) -> List[str]:
    urls: List[str] = []
    for hit in hits:
        for raw in hit.get("images") or []:
            url = str(raw or "").strip()
            if url and url not in urls:
                urls.append(url)
    return urls


def _format_hits(hits: Sequence[Dict[str, str]]) -> str:
    blocks = []
    for index, hit in enumerate(hits, start=1):
        title = str(hit.get("title") or "").strip()
        snippet = str(hit.get("snippet") or "").strip()
        blocks.append(f"{index}. {title}\n{snippet}".strip())
    return "\n\n".join(blocks)


def _fold_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip().casefold()


def _quote_in_description(quote: str, description: str) -> bool:
    folded = _fold_text(quote)
    return len(folded) >= 3 and folded in _fold_text(description)


def _format_references(brand: str, theme: str, review: Sequence[str], styles: Sequence[str]) -> str:
    lines = [f"House: {brand}", f"Theme: {theme}"]
    if review:
        lines.append("Review stances:")
        lines.extend(f"- {item}" for item in review)
    if styles:
        lines.append("Image style:")
        lines.extend(f"- {item}" for item in styles)
    return "\n".join(lines)


def _references_from_card(card: str) -> Tuple[List[str], List[str]]:
    """提供的卡可以分列。没有列名的条目算秀评立场。"""
    review: List[str] = []
    styles: List[str] = []
    bucket = "review"
    for raw in str(card or "").splitlines():
        text = raw.strip()
        header = text.rstrip(":").lower()
        if header in {"review stances", "abstract directions"}:
            bucket = "review"
            continue
        if header in {"image style", "image styles"}:
            bucket = "styles"
            continue
        if not text.startswith("- "):
            continue
        item = text[2:].strip()
        if not item or _is_logo_inventory(item):
            continue
        (styles if bucket == "styles" else review).append(item)
    return review[:_MAX_DIRECTIONS], styles[:_MAX_DIRECTIONS]


def _review_stance_prompt(brand: str, theme: str, hits: Sequence[Dict[str, str]]) -> str:
    return (
        f"BRAND: {brand}\nTHEME: {theme}\n\n"
        "SHOW REVIEW:\n"
        f"{_format_hits(hits)}\n\n"
        "Write the review's design stances. Do not write a garment inventory."
    )


def _image_style_prompt(brand: str, theme: str) -> str:
    return (
        f"BRAND: {brand}\nTHEME: {theme}\n\n"
        "The attached photographs are evenly spaced looks from this show.\n"
        "Write style description sentences from the photographs only."
    )


def _direction_images(user_text: str, images: Sequence[str]) -> List[Dict[str, Any]]:
    content: List[Dict[str, Any]] = [{"type": "text", "text": user_text}]
    for url in images:
        content.append({"type": "image_url", "image_url": {"url": url}})
    return content


def _references_from_retrieval(
    brand: str,
    theme: str,
    hits: Sequence[Dict[str, Any]],
    generate_text: Callable[..., str],
    generate_multimodal: Optional[Callable[..., str]] = None,
) -> Tuple[List[str], List[str], str]:
    """秀评和成衣图分开抽。都不看已经生成的描述，也不用品牌整体调性补句。"""
    review: List[str] = []
    styles: List[str] = []
    if hits:
        extracted = _parse_json(
            _call(
                generate_text,
                _REVIEW_STANCE_SYSTEM,
                _review_stance_prompt(brand, theme, hits),
                500,
            )
        )
        review = _clean_lines(extracted.get("stances"), _MAX_DIRECTIONS)
    images = _image_urls(hits)
    if images and generate_multimodal is not None:
        try:
            extracted = _parse_json(
                generate_multimodal(
                    system_prompt=_IMAGE_STYLE_SYSTEM,
                    user_content=_direction_images(_image_style_prompt(brand, theme), images),
                    temperature=0,
                    max_tokens=500,
                )
            )
        except Exception:
            extracted = {}
        styles = _clean_lines(extracted.get("styles"), _MAX_DIRECTIONS)
    if styles:
        source = "web_images"
    elif review:
        source = "web"
    else:
        source = ""
    return review, styles, source


_STATUS = {
    "carried": "carried",
    "conflict": "conflict",
    "absent": "absent",
    "contradicted": "conflict",
    "match": "carried",
    "matched": "carried",
    "missing": "absent",
}


def _bind_stance(
    stance: str,
    source: str,
    review: Sequence[str],
    styles: Sequence[str],
) -> Optional[Tuple[str, str]]:
    key = _fold_text(stance)
    if not key:
        return None
    pools = (("review", review), ("image", styles))
    named = dict(pools).get(source)
    if named:
        for item in named:
            if _fold_text(item) == key:
                return source, item
    for src, items in pools:
        for item in items:
            if _fold_text(item) == key:
                return src, item
    return None


def _accept_checks(
    payload: Dict[str, Any],
    review: Sequence[str],
    styles: Sequence[str],
    description: str,
) -> List[Dict[str, str]]:
    """冲突必须带回描述里的原句。对不上的冲突降为缺失，不能触发修改。"""
    accepted: List[Dict[str, str]] = []
    seen = set()
    for item in payload.get("checks") or []:
        if not isinstance(item, dict):
            continue
        bound = _bind_stance(str(item.get("stance") or ""), str(item.get("source") or ""), review, styles)
        if bound is None:
            continue
        source, stance = bound
        if stance in seen:
            continue
        seen.add(stance)
        axis = " ".join(str(item.get("axis") or "").split())
        quote = " ".join(str(item.get("quote") or "").split())
        status = _STATUS.get(str(item.get("status") or "").strip().lower(), "")
        quote_ok = bool(axis) and _quote_in_description(quote, description)
        if status == "conflict" and quote_ok:
            final = "conflict"
        elif status == "carried" and quote_ok:
            final = "carried"
        else:
            final = "absent"
            if not _quote_in_description(quote, description):
                quote = ""
        accepted.append(
            {"source": source, "stance": stance, "axis": axis, "quote": quote, "status": final}
        )
    return accepted


def _check_prompt(
    brand: str,
    theme: str,
    review: Sequence[str],
    styles: Sequence[str],
    description: str,
) -> str:
    def block(title: str, items: Sequence[str]) -> str:
        if not items:
            return f"{title}:\n（无）"
        return title + ":\n" + "\n".join(f"- {item}" for item in items)

    return (
        f"BRAND: {brand}\nTHEME: {theme}\n\n"
        f"{block('REVIEW STANCES', review)}\n\n"
        f"{block('IMAGE STYLE', styles)}\n\n"
        "GENERATED DESCRIPTION:\n"
        f"{description}\n\n"
        "Judge every review stance and every image style sentence. "
        "A conflict quote must be copied from the description and must state the opposite direction on the same axis."
    )


def _format_findings(items: Sequence[Dict[str, str]]) -> str:
    if not items:
        return "（无）"
    lines = []
    for index, item in enumerate(items, start=1):
        lines.append(
            f"{index}. source: {item['source']}\n"
            f"   stance: {item['stance']}\n"
            f"   axis: {item['axis']}\n"
            f"   quote: {item['quote']}"
        )
    return "\n".join(lines)


def _edit_points(value: object) -> List[Dict[str, str]]:
    if not isinstance(value, list):
        return []
    points = []
    for item in value:
        if isinstance(item, str) and item.strip():
            edit = item.strip()
            pair = ""
            drop = ""
        elif isinstance(item, dict):
            edit = str(item.get("edit") or "").strip()
            pair = str(item.get("pair") or "").strip()
            drop = str(item.get("drop") or "").strip()
        else:
            continue
        if not edit or _is_logo_inventory(edit):
            continue
        points.append({"edit": edit, "pair": pair, "drop": drop})
        if len(points) >= _MAX_POINTS:
            break
    return points


def _point_combinations(count: int) -> List[Tuple[int, ...]]:
    rows: List[Tuple[int, ...]] = []
    ids = list(range(1, count + 1))
    for size in range(1, count + 1):
        rows.extend(tuple(combo) for combo in combinations(ids, size))
    return rows


def _score_number(value: object) -> Optional[float]:
    try:
        number = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    if number != number or number < 0 or number > 1:
        return None
    return number


def _select_scores(
    count: int,
    payload: Dict[str, Any],
) -> Tuple[List[Dict[str, Any]], List[int], Optional[float]]:
    """模型只打分。得分最高的组合在这里选定；同分时保留更多修改点。"""
    valid = set(_point_combinations(count))
    best: Optional[Tuple[Tuple[float, int, Tuple[int, ...]], Tuple[int, ...], float]] = None
    rows: List[Dict[str, Any]] = []
    seen = set()
    for item in payload.get("scores") or []:
        if not isinstance(item, dict):
            continue
        raw_ids = item.get("ids")
        if not isinstance(raw_ids, list):
            continue
        try:
            key = tuple(sorted(int(piece) for piece in raw_ids))
        except (TypeError, ValueError):
            continue
        if key not in valid or key in seen:
            continue
        score = _score_number(item.get("score"))
        if score is None:
            continue
        seen.add(key)
        rows.append({"ids": list(key), "score": score})
        rank = (score, len(key), tuple(-piece for piece in key))
        if best is None or rank > best[0]:
            best = (rank, key, score)
    if best is None:
        return rows, [], None
    return rows, list(best[1]), best[2]


def _format_points(points: Sequence[Dict[str, str]]) -> str:
    lines = []
    for index, point in enumerate(points, start=1):
        lines.append(
            f"{index}. edit: {point['edit']}\n"
            f"   pair: {point['pair'] or '（未写）'}\n"
            f"   drop: {point['drop'] or '（未写）'}"
        )
    return "\n".join(lines)


def _format_combinations(count: int) -> str:
    lines = []
    for combo in _point_combinations(count):
        lines.append("ids " + ", ".join(str(piece) for piece in combo))
    return "\n".join(lines)


def _default_generators() -> Tuple[Callable[..., str], Callable[..., str]]:
    from plugins.text_description_evaluator.design_text_evaluator_api import DesignTextEvaluator

    judge = DesignTextEvaluator(model=MODEL_NAME).judge
    return judge.generate_text, judge.generate_multimodal


def rewrite_generated_description(
    *,
    brand: str,
    theme: str,
    description: str,
    generate_text: Optional[Callable[..., str]] = None,
    generate_multimodal: Optional[Callable[..., str]] = None,
    search_fn: Optional[Callable[..., List[Dict[str, Any]]]] = None,
    habit_card: Optional[str] = None,
) -> Dict[str, Any]:
    """先对照秀评立场和图片风格句。任意一边有冲突，就改写这条 description。"""
    brand = str(brand or "").strip()
    theme = str(theme or "").strip()
    description = str(description or "").strip()
    if not brand or not theme or not description:
        raise ValueError("brand, theme, and description are required")

    result: Dict[str, Any] = {
        "brand": brand,
        "theme": theme,
        "house": brand,
        "source_description": description,
        "model": MODEL_NAME,
        "directions": [],
        "review_stances": [],
        "image_styles": [],
        "checks": [],
        "conflicts": [],
        "feature_points": [],
        "signature_points": [],
        "similar_designs": [],
        "edit_points": [],
        "suggestions": [],
        "combination_scores": [],
        "selected_ids": [],
        "selected_score": None,
        "kept": [],
        "dropped": [],
        "reflection": "",
        "description": description,
        "retrieved": [],
        "habit_card": "",
        "card_source": "",
    }
    if generate_text is None:
        caller, default_multimodal = _default_generators()
        if generate_multimodal is None:
            generate_multimodal = default_multimodal
    else:
        caller = generate_text
    if habit_card is not None:
        hits: List[Dict[str, Any]] = []
        review, styles = _references_from_card(habit_card)
        card_source = "provided"
    else:
        search = search_fn or search_similar_designs
        try:
            hits = list(search(brand, theme) or [])
        except Exception:
            hits = []
        review, styles, card_source = _references_from_retrieval(
            brand, theme, hits, caller, generate_multimodal
        )
    result["retrieved"] = [
        {
            "title": str(hit.get("title") or ""),
            "url": str(hit.get("url") or ""),
            "snippet": str(hit.get("snippet") or ""),
            "images": [str(url) for url in (hit.get("images") or []) if str(url).strip()],
        }
        for hit in hits
    ]
    result["review_stances"] = review
    result["image_styles"] = styles
    result["directions"] = list(review) + list(styles)
    result["card_source"] = card_source
    result["habit_card"] = _format_references(brand, theme, review, styles) if review or styles else ""
    if not review or not styles:
        result["skipped"] = "no reference"
        return result

    checks = _accept_checks(
        _parse_json(
            _call(
                caller,
                _CHECK_SYSTEM,
                _check_prompt(brand, theme, review, styles, description),
                800,
            )
        ),
        review,
        styles,
        description,
    )
    review_conflicts = [item for item in checks if item["status"] == "conflict" and item["source"] == "review"]
    image_conflicts = [item for item in checks if item["status"] == "conflict" and item["source"] == "image"]
    carried = [item for item in checks if item["status"] == "carried"]
    result["checks"] = checks
    conflicts = review_conflicts + image_conflicts
    if not conflicts:
        result["skipped"] = "no conflict"
        return result
    result["conflicts"] = conflicts
    result["feature_points"] = [item["stance"] for item in conflicts]

    points = _edit_points(
        _parse_json(
            _call(
                caller,
                _POINTS_SYSTEM,
                (
                    f"BRAND: {brand}\nTHEME: {theme}\n\n"
                    "CONFIRMED CONFLICTS:\n"
                    f"{_format_findings(conflicts)}\n\n"
                    "CARRIED, DO NOT CHANGE:\n"
                    f"{_format_findings(carried)}\n\n"
                    "GENERATED DESCRIPTION:\n"
                    f"{description}\n\n"
                    "Write one concrete edit point for each conflict. "
                    "Each point needs an edit, a pairing, and a drop."
                ),
                800,
            )
        ).get("points")
    )
    result["edit_points"] = points
    result["suggestions"] = points
    if not points:
        result["skipped"] = "no edit points"
        return result

    scored = _parse_json(
        _call(
            caller,
            _SCORE_SYSTEM,
            (
                f"BRAND: {brand}\nTHEME: {theme}\n\n"
                "CONFIRMED CONFLICTS:\n"
                f"{_format_findings(conflicts)}\n\n"
                "CARRIED, DO NOT CHANGE:\n"
                f"{_format_findings(carried)}\n\n"
                "EDIT POINTS:\n"
                f"{_format_points(points)}\n\n"
                "COMBINATIONS TO SCORE:\n"
                f"{_format_combinations(len(points))}\n\n"
                "Give each combination an abstract score from 0 to 1. Do not choose a winner."
            ),
            800,
        )
    )
    rows, selected_ids, selected_score = _select_scores(len(points), scored)
    result["combination_scores"] = rows
    result["selected_ids"] = selected_ids
    result["selected_score"] = selected_score
    if not selected_ids:
        result["skipped"] = "no scores"
        return result

    chosen = [points[index - 1] for index in selected_ids]
    result["kept"] = [point["edit"] for point in chosen]
    result["dropped"] = [point["drop"] for point in chosen if point["drop"]]
    result["reflection"] = f"Selected combination {selected_ids} with abstract score {selected_score}."
    rewritten = " ".join(
        str(
            _parse_json(
                _call(
                    caller,
                    _WRITE_SYSTEM,
                    (
                        f"BRAND: {brand}\nTHEME: {theme}\n\n"
                        "SELECTED EDIT POINTS:\n"
                        f"{_format_points(chosen)}\n\n"
                        "GENERATED DESCRIPTION:\n"
                        f"{description}\n\n"
                        "Write the description from this combination only."
                    ),
                    700,
                )
            ).get("description")
            or ""
        ).split()
    )
    if rewritten:
        result["description"] = rewritten
    return result
