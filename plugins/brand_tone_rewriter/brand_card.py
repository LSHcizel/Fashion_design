"""品牌习惯卡：只作为第二改写器读取已有设计的资料，不再写进第一改写器。"""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

_INDEX = (
    Path(__file__).resolve().parents[2]
    / "fashion_research_dir"
    / "season_themes_2026-09"
    / "index.json"
)

_KEEP_HEADER_LABELS = (
    ("silhouette & garment vocabulary", "Silhouette"),
    ("materials, craft & surface", "Craft"),
    ("color, stripe & graphic codes", "Palette"),
    ("accessories & finishing", "Construction"),
)

_ALIASES = {
    "ysl": "saint laurent",
    "yves saint laurent": "saint laurent",
    "mcqueen": "alexander mcqueen",
}

_SEASON_SUFFIX = re.compile(
    r"(?:^| )(?:ss|fw|aw|pf|cruise|pre|rs) ?\d{2,4}$",
    re.IGNORECASE,
)
_LOGO_NOISE = re.compile(r"\b(logo|monogram|interlocking)\b", re.IGNORECASE)
_LOGO_NEGATION = re.compile(
    r"\b(?:not|without|no)\b(?:\s+\w+){0,4}\s+\b(?:logo|monogram|interlocking)\b",
    re.IGNORECASE,
)
_HEADER_LINE = re.compile(r"^([^:\-][^:]{2,80}):\s*$")

_MAX_BULLETS = 3
_MAX_BULLET_CHARS = 220


def _fold(value: str) -> str:
    text = (value or "").strip().lower()
    for src, dst in (
        ("é", "e"),
        ("è", "e"),
        ("ê", "e"),
        ("ë", "e"),
        ("á", "a"),
        ("à", "a"),
        ("ö", "o"),
        ("ü", "u"),
    ):
        text = text.replace(src, dst)
    text = text.replace("'", "").replace("’", "").replace("`", "")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _strip_season(folded: str) -> str:
    return _SEASON_SUFFIX.sub("", folded).strip()


def _phrase_pattern(name: str) -> re.Pattern[str]:
    parts: List[str] = []
    for ch in name:
        low = ch.lower()
        if low in "eéèêë":
            parts.append("[eéèêëEÉÈÊË]")
        elif ch in "'’":
            parts.append("['’]?")
        elif ch in " -":
            parts.append(r"[\s\-]+")
        else:
            parts.append(re.escape(ch))
    if _fold(name) == "the row":
        parts.append(r"(?!\s+of\b)")
    body = "".join(parts)
    return re.compile(rf"(?<![A-Za-z0-9]){body}(?![A-Za-z0-9])", re.IGNORECASE)


def _clip_bullet(text: str) -> str:
    bullet = re.sub(r"\s+", " ", text).strip()
    if len(bullet) <= _MAX_BULLET_CHARS:
        return bullet
    window = bullet[:_MAX_BULLET_CHARS]
    for sep in (". ", "; "):
        idx = window.rfind(sep)
        if idx >= 40:
            return window[: idx + 1].strip()
    cut = window.rsplit(" ", 1)[0].rstrip(" ,;:")
    return cut or window.rstrip()


def _is_logo_inventory(bullet: str) -> bool:
    if not _LOGO_NOISE.search(bullet):
        return False
    return _LOGO_NEGATION.search(bullet) is None


def _keep_headers() -> Dict[str, str]:
    return {_fold(title): label for title, label in _KEEP_HEADER_LABELS}


def _section_bullets(description: str) -> Dict[str, List[str]]:
    headers = _keep_headers()
    buckets: Dict[str, List[str]] = {label: [] for _title, label in _KEEP_HEADER_LABELS}
    current: Optional[str] = None
    for raw in (description or "").replace("\r\n", "\n").split("\n"):
        line = raw.strip()
        if not line:
            continue
        header = _HEADER_LINE.match(line)
        if header:
            current = headers.get(_fold(header.group(1)))
            continue
        if not current or not line.startswith("-"):
            continue
        bullet = line.lstrip("-").strip()
        if not bullet or _is_logo_inventory(bullet):
            continue
        if len(buckets[current]) >= _MAX_BULLETS:
            continue
        buckets[current].append(_clip_bullet(bullet))
    return buckets


def _houses_with_habits(sections_by_house: Dict[str, Dict[str, List[str]]]) -> List[str]:
    houses = []
    for house, sections in sections_by_house.items():
        if any(sections.get(label) for label in ("Silhouette", "Craft", "Palette", "Construction")):
            houses.append(house)
    return houses


@lru_cache(maxsize=4)
def _load_catalog(index_path: str):
    path = Path(index_path)
    if not path.is_file():
        return {}, (), (), {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    by_key: Dict[str, str] = {}
    sections_by_house: Dict[str, Dict[str, List[str]]] = {}
    for row in payload.get("collections") or []:
        if not isinstance(row, dict):
            continue
        house = str(row.get("house") or "").strip()
        if not house:
            continue
        by_key[_fold(house)] = house
        sections_by_house[house] = _section_bullets(str(row.get("description") or ""))
    for alias, target in _ALIASES.items():
        house = by_key.get(target)
        if house:
            by_key[alias] = house
    houses = _houses_with_habits(sections_by_house)
    patterns = tuple(
        (_phrase_pattern(house), house)
        for house in sorted(houses, key=len, reverse=True)
    )
    alias_patterns = tuple(
        (_phrase_pattern(alias), by_key[alias])
        for alias in sorted(_ALIASES, key=len, reverse=True)
        if alias in by_key
    )
    return by_key, patterns, alias_patterns, sections_by_house


def _catalog(index_path: Optional[Path] = None):
    path = Path(index_path) if index_path else _INDEX
    return _load_catalog(str(path.resolve()))


def _match_in_text(text: str, patterns) -> Optional[str]:
    if not (text or "").strip():
        return None
    hits = []
    for pattern, house in patterns:
        found = pattern.search(text)
        if found:
            hits.append((found.start(), -len(found.group(0)), house))
    if not hits:
        return None
    hits.sort()
    return hits[0][2]


def resolve_brand(
    *,
    explicit: Optional[str] = None,
    texts: Sequence[str] = (),
    index_path: Optional[Path] = None,
) -> Optional[str]:
    """工作流品牌优先；否则按文本顺序找第一个已知品牌。找不到返回 None。"""
    by_key, patterns, alias_patterns, _sections = _catalog(index_path)
    if not by_key:
        return None
    raw = str(explicit or "").strip()
    if raw:
        folded = _fold(raw)
        for key in (folded, _strip_season(folded), _ALIASES.get(folded, "")):
            if key and key in by_key:
                return by_key[key]
        found = _match_in_text(raw, patterns + alias_patterns)
        if found:
            return found
    scan = patterns + alias_patterns
    for text in texts:
        found = _match_in_text(str(text or ""), scan)
        if found:
            return found
    return None


def iter_style_houses(index_path: Optional[Path] = None) -> Iterable[str]:
    _by_key, _patterns, _alias_patterns, sections_by_house = _catalog(index_path)
    return tuple(_houses_with_habits(sections_by_house))


def brand_preference_items(
    *,
    explicit: Optional[str] = None,
    texts: Sequence[str] = (),
    index_path: Optional[Path] = None,
) -> Tuple[str, List[Dict[str, str]]]:
    """把已解析品牌的习惯卡拆成单条做法。每条只含一个段名和一句做法。"""
    house = resolve_brand(explicit=explicit, texts=texts, index_path=index_path)
    if not house:
        return "", []
    _by_key, _patterns, _alias_patterns, sections_by_house = _catalog(index_path)
    buckets = sections_by_house.get(house) or {}
    items: List[Dict[str, str]] = []
    for label in ("Silhouette", "Craft", "Palette", "Construction"):
        for bullet in buckets.get(label) or []:
            text = str(bullet or "").strip()
            if text:
                items.append({"section": label, "text": text})
    return house, items


def format_existing_designs(house: str, items: Sequence[Dict[str, str]]) -> str:
    """把这家已有的四段做法列给第二改写器，不写成第一改写器的品牌卡。"""
    if not house or not items:
        return ""
    lines = [f"House: {house}", "Existing designs on file:"]
    for label in ("Silhouette", "Craft", "Palette", "Construction"):
        bullets = [str(item.get("text") or "").strip() for item in items if item.get("section") == label]
        bullets = [bullet for bullet in bullets if bullet]
        if not bullets:
            continue
        lines.append(f"{label}:")
        lines.extend(f"- {bullet}" for bullet in bullets)
    return "\n".join(lines)

