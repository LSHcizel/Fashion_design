"""
API-based LLM-as-a-judge DesignTextEvaluator for fashion text descriptions.
"""

from __future__ import annotations

import json
import logging
import math
import os
import re
import ssl
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union
from urllib.parse import urlparse

import yaml

from .r_content_reward import apply_length_disentangle, build_r_content_payload
from .score_formula import build_score_formula_breakdown


class JudgeConnectionError(RuntimeError):
    """Judge / rewriter API unreachable (connection refused, reset, DNS, etc.)."""


JUDGE_JSON_PARSE_ATTEMPTS = 3
# Temperature 0 still loops on short evidence tokens. vLLM lowers those logits.
JUDGE_REPETITION_PENALTY = 1.1
_JSON_STRING = r'"(?:\\.|[^"\\])*"'
_REPEAT_SAME_JSON_STRING = re.compile(rf"({_JSON_STRING})(?:\s*,\s*\1){{2,}}")
_REPEAT_PAIR_JSON_STRING = re.compile(
    rf"({_JSON_STRING})\s*,\s*({_JSON_STRING})(?:\s*,\s*\1\s*,\s*\2){{2,}}"
)


def _collapse_repeated_json_strings(text: str) -> str:
    """Drop a stuck evidence loop such as \"red\", \"black\", \"red\", \"black\"."""
    prev = None
    cur = text
    while cur != prev:
        prev = cur
        cur = _REPEAT_PAIR_JSON_STRING.sub(r"\1, \2", cur)
        cur = _REPEAT_SAME_JSON_STRING.sub(r"\1", cur)
    return cur


def _close_truncated_json(text: str) -> str:
    """Close a JSON object cut off by max tokens after a repetition loop."""
    start = text.find("{")
    if start < 0:
        return text
    body = text[start:]
    stack: List[str] = []
    in_string = False
    escape = False
    for ch in body:
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == "{":
            stack.append("}")
        elif ch == "[":
            stack.append("]")
        elif ch in "}]" and stack and stack[-1] == ch:
            stack.pop()
    if in_string:
        body += '"'
    body = re.sub(r",\s*$", "", body.rstrip())
    while stack:
        body += stack.pop()
    return body


_CONNECTION_FAILURE_MARKERS = (
    "connection refused",
    "connection reset",
    "connection aborted",
    "urlerror",
    "remotedisconnected",
    "failed to establish a new connection",
    "network is unreachable",
    "name or service not known",
    "nodename nor servname",
    "errno 111",
    "errno 104",
    "winerror 10061",
    "winerror 10054",
)


def is_connection_failure(err: Any) -> bool:
    """True when ``err`` is (or describes) an API transport / connection failure."""
    if err is None:
        return False
    if isinstance(err, JudgeConnectionError):
        return True
    if isinstance(err, (ConnectionError, ConnectionRefusedError, ConnectionResetError, ConnectionAbortedError)):
        return True
    if isinstance(err, urllib.error.URLError):
        return True
    text = str(err).lower()
    return any(marker in text for marker in _CONNECTION_FAILURE_MARKERS)


def _load_env_file() -> None:
    """Load simple KEY=VALUE pairs from local env files if present."""
    candidate_paths = [
        Path(__file__).resolve().parent / "api_env.local",
        Path(__file__).resolve().parent / ".env.local",
        Path(__file__).resolve().parent / ".env",
        Path(__file__).resolve().parent.parent / ".env.local",
        Path(__file__).resolve().parent.parent / ".env",
    ]
    for env_path in candidate_paths:
        if not env_path.exists():
            continue
        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value
        break


_load_env_file()


def coerce_judge_result_items(raw_results: Any) -> List[Dict[str, Any]]:
    """Local 7B sometimes returns ``results`` as strings or a metric-keyed dict."""
    if raw_results is None:
        return []
    if isinstance(raw_results, dict):
        items: List[Dict[str, Any]] = []
        for key, val in raw_results.items():
            if isinstance(val, dict):
                row = dict(val)
                row.setdefault("metric", key)
                items.append(row)
            else:
                items.append({"metric": str(key), "score": val})
        return items
    if not isinstance(raw_results, list):
        return []
    items = []
    for item in raw_results:
        if isinstance(item, dict):
            items.append(item)
        elif isinstance(item, str) and item.strip():
            items.append({"metric": item.strip()})
    return items


def _load_fashion_config() -> Dict[str, Any]:
    """Load shared project config when available."""
    config_path = Path(__file__).resolve().parents[2] / "fashion_config.yaml"
    if not config_path.exists():
        return {}
    try:
        with config_path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


FASHION_CONFIG = _load_fashion_config()


def grpo_config() -> Dict[str, Any]:
    """``fashion_config.yaml`` 中 ``grpo:`` 段。"""
    return dict(FASHION_CONFIG.get("grpo") or {})


def grpo_design_text_evaluator_config() -> Dict[str, Any]:
    return dict(grpo_config().get("design-text-evaluator") or {})


def grpo_parallel_k_rewrite_config() -> Dict[str, Any]:
    return dict(grpo_config().get("parallel-k-rewrite") or {})


def grpo_rewriter_llm_config() -> Dict[str, Any]:
    """改写专用 vLLM / HF 权重（``grpo.rewriter-llm``）。"""
    return dict(grpo_config().get("rewriter-llm") or {})


def grpo_training_data_config() -> Dict[str, Any]:
    return dict(grpo_config().get("training-data") or {})


DEFAULT_HF_LOCAL_GRPO_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"


def grpo_hf_local_training_config() -> Dict[str, Any]:
    """本地 ``training/hf_grpo`` SFT/GRPO 所用 HuggingFace 默认模型等。"""
    return dict(grpo_config().get("hf-local-training") or {})


def default_hf_local_grpo_model() -> str:
    """SFT/GRPO 训练对象：``grpo.hf-local-training.model`` → ``grpo.rewriter-llm.model-path``。"""
    hf = grpo_hf_local_training_config()
    m = hf.get("model")
    if isinstance(m, str) and m.strip():
        return m.strip()
    rw = grpo_rewriter_llm_config().get("model-path")
    if isinstance(rw, str) and rw.strip():
        return rw.strip()
    return DEFAULT_HF_LOCAL_GRPO_MODEL


def default_hf_local_grpo_ref_model() -> str:
    """GRPO KL 锚点：``grpo.hf-local-training.ref-model``，缺省同 ``default_hf_local_grpo_model()``。"""
    hf = grpo_hf_local_training_config()
    ref = hf.get("ref-model")
    if isinstance(ref, str) and ref.strip():
        return ref.strip()
    return default_hf_local_grpo_model()


def default_hf_grpo_rounds() -> int:
    """冷启动后 GRPO 轮数；``grpo.hf-local-training.grpo-rounds``，缺省 1。"""
    hf = grpo_hf_local_training_config()
    try:
        return max(1, int(hf.get("grpo-rounds", 1)))
    except (TypeError, ValueError):
        return 1


def default_hf_grpo_epochs_per_round() -> float:
    """每轮 GRPO 的 epoch；``grpo.hf-local-training.grpo-epochs-per-round``，缺省 1。"""
    hf = grpo_hf_local_training_config()
    try:
        val = float(hf.get("grpo-epochs-per-round", 1.0))
    except (TypeError, ValueError):
        return 1.0
    return val if val > 0 else 1.0


def grpo_odin_rm_config() -> Dict[str, Any]:
    """``grpo.odin-rm``：双头 RM 蒸馏裁判。"""
    return dict(grpo_config().get("odin-rm") or {})


def default_odin_rm_model() -> str:
    """
    RM backbone：``grpo.odin-rm.model`` → 基座 ``local-llm.model-path``。

    不要默认指向 rewriter：RM 应冻在裁判同侧基座上，与正在训的改写器分开。
    """
    cfg = grpo_odin_rm_config()
    m = cfg.get("model")
    if isinstance(m, str) and m.strip():
        return m.strip()
    ll = FASHION_CONFIG.get("local-llm") or {}
    p = ll.get("model-path")
    if isinstance(p, str) and p.strip():
        return p.strip()
    return default_hf_local_grpo_model()


def _yaml_opt_str(value: Any) -> Optional[str]:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


APPLICABILITY_HINTS = {
    "always": "Always judge this metric.",
    "when_shape_is_salient": "Only applicable when the text clearly mentions silhouette, shape, or structural contour.",
    "when_length_or_hem_is_salient": "Only applicable when the text mentions length, hemline, slit, or garment length.",
    "when_exposure_is_salient": "Only applicable when the text mentions exposure, coverage, cutout, or body reveal.",
    "when_material_is_inferable": "Only applicable when the text provides enough information about the main material.",
    "when_surface_trait_is_salient": "Only applicable when the text mentions gloss, matte, drape, stiffness, pleats, or surface traits.",
    "when_secondary_color_is_salient": "Only applicable when the text clearly includes secondary color or color relationship information.",
    "when_multi_tone_or_strong_color_story": "Only applicable when the text implies multiple color blocks, strong inner/outer contrast, stripe-vs-ground relations, tonal vs accented palette, or another non-trivial color story beyond a single flat hue.",
    "when_shoulder_is_salient": "Only applicable when the text implies prominent shoulder design: pads/structured shoulders, dropped shoulder, one-shoulder/off-shoulder, strapless neckline, or other salient shoulder/sleeve anchor cues.",
    "when_construction_technique_is_salient": "Only applicable when the text implies notable fabrication techniques such as directional/sunray/fan pleating, quilting, embroidery, cut-outs, engineered pleat architecture, lace/engineered panel work, or similar craft—not merely generic “details”.",
    "when_pattern_exists": "Only applicable when the text describes pattern or print information.",
    "when_closure_is_salient": "Only applicable when the text mentions button, zipper, tie, buckle, or closure details.",
    "when_functional_detail_is_salient": "Only applicable when the text mentions pockets, straps, utility parts, or functional details.",
    "when_deconstruction_exists": "Only applicable when the text mentions deconstruction, splicing, displacement, or reconstruction.",
    "when_hardware_is_salient": "Only applicable when the text mentions chains, studs, metal rings, crystals, or similar embellishment.",
    "when_full_look_and_bag_exists": "Only applicable when the text describes a full look and the bag is an important part of it.",
    "when_full_look_and_footwear_exists": "Only applicable when the text describes a full look and footwear is an important part of it.",
    "when_jewelry_is_salient": "Only applicable when jewelry or body ornament is explicitly present.",
    "when_belt_or_waist_strap_is_salient": "Only applicable when the text mentions or clearly implies a visible belt, sash, waist cincher, or waist/hip retention strap/harness—not mere silhouette waist shaping from cut (e.g. defined waist, peplum, princess seams, high/low waist proportion).",
    "when_layering_exists": "Only applicable when the text describes layering or multi-layer garment relations.",
    "when_proportion_is_salient": "Only applicable when the text describes top-bottom proportion, waist position, or visual balance.",
    "when_asymmetry_exists": "Only applicable when the text describes asymmetry, one-shoulder, single sleeve, or uneven structure.",
    "when_bilateral_difference_exists": "Only applicable when the text explicitly distinguishes left/right sides or other bilateral elements such as shoes, sleeves, legs, or shoulders.",
    "when_spatial_relation_exists": "Only applicable when the text describes layering, front/back, inside/outside, attached position, crossing paths, or other explicit spatial relations.",
    "when_multiple_garments_exist": "Only applicable when the text includes multiple garments or multi-item relations.",
    "when_quantity_is_used": "Only applicable when the text includes numbers, counts, or explicit quantity relations.",
    "when_style_goal_is_explicit": "Applicable when the text expresses aesthetic or style vocabulary—including styling tone, mood, or collection-context phrases (e.g. sporty-luxe, polished, cruise resort).",
    "when_reference_is_grounded": "Applicable when the text provides cultural, historical, or setting context that is self-contained in the prose (e.g. resort, Biarritz, workwear heritage)—external user background is not required.",
    "when_gender_expression_is_relevant": "Only applicable when the text explicitly mentions gender expression or androgyny.",
    "when_series_theme_is_known": "Applicable when the text includes theme, setting, mood, or collection-context narrative—even a single closing overall mood/palette sentence counts.",
    "when_brand_goal_is_explicit": "Applicable when the text reflects brand-consistent craft, silhouette, or palette language—even without naming the brand or stating an explicit brand task.",
    "when_absence_is_important": "Only applicable when absence or exclusion of an element matters in the text.",
    "when_craft_or_embellishment_is_salient": "Applicable when the text mentions craft, embellishment, trim path, appliqué, braid, quilting, embroidery, deconstruction, patch decoration, OR treats seam topstitching, piping, binding, hidden placket, or brand hardware as a visual feature. In the latter case, score as factory finishing unless it is an identifying surface or edge path.",
}

QUALITY_ALLOWED_SCORES = [0.0, 0.25, 0.5, 0.75, 1.0]
QUALITY_FULL_HIT_THRESHOLD = 0.75
DESIGN_MERIT_DIMENSIONS = {
    "DesignDistinctiveness",
    "VisualGrounding",
    "CraftSalience",
    "CombinationOriginality",
    "DesignSignalPurity",
}
# Single DesignMerit judge block: used only in the DesignMerit user prompt (not repeated in system).
DESIGN_MERIT_JUDGE_GUIDE = (
    "Score the feature that would still identify this look if color, fabric, and brand words were swapped. "
    "Do not score completeness, layout, or garment category.\n"
    "DESIGN (may stay 0.75–1.0): one of these on a single outfit — "
    "a pattern, texture, or print covering the whole cloth; "
    "decoration that traces one outline (appliqué, trim, fringe, scallop, or beading "
    "along the neckline, front, hem, cuff, or slit); "
    "or an inner garment of the SAME theme that still reads as its own piece when the outer is opened. "
    "A small placement on one side of that same garment is not a second idea and not a conflict.\n"
    "CONFLICT is not design. Cap the metric at 0.25, and do not keep it high because the facts are specific: "
    "two sleeve grammars, two bottoms, or two shoe types; "
    "one garment with two bindings for neckline, sleeve, length, closure, or shell; "
    "or a garment from another theme (bridal, coronation, flamenco, mourning, masquerade, "
    "morning dress, rococo, or the same kind of foreign register), including as an inner layer. "
    "Two trunks colliding in volume is not one of those three features.\n"
    "Low 0.25–0.5 when none of those three features is present and there is no conflict: "
    "hem/cuff reveal, self-belt, tucked shirt, factory finishing (concealed placket, topstitch, piping), "
    "brand hardware, fabric-mood, theme dualities, "
    "or a collection-shared interchangeable trunk-garment formula. "
    "Factory finishing on one identity does not by itself force 0.25. "
    "Do not copy one score onto every axis. "
    "Do not lower merely for a coat, cropped jacket, or shorts as a category. Ignore T2I preamble.\n"
    "Reason: name that feature in one clause, or name the conflict; then pick the score. "
    "Evidence: quote that feature, or quote the conflicting garments."
)
# Per-axis floors after the judge. Shared series/finishing grammar stays low on idea axes.
DESIGN_MERIT_AUX_CAP_DISTINCTIVENESS_ORDINARY = 0.25
DESIGN_MERIT_AUX_CAP_DISTINCTIVENESS_CEILING = 0.5
DESIGN_MERIT_AUX_CAP_GROUNDING = 0.5
DESIGN_MERIT_AUX_CAP_CRAFT = 0.25
DESIGN_MERIT_AUX_CAP_COMBINATION = 0.25
DESIGN_MERIT_AUX_CAP_COMBINATION_WEAK = 0.5
DESIGN_MERIT_AUX_CAP_PURITY_THEME = 0.25
DESIGN_MERIT_AUX_CAP_PURITY_CEILING = 0.5
DESIGN_MERIT_AUX_CAP = DESIGN_MERIT_AUX_CAP_DISTINCTIVENESS_ORDINARY
_DESIGN_MERIT_METRIC_NAMES = (
    "design_distinctiveness",
    "visual_observation_grounding",
    "craft_embellishment_salience",
    "silhouette_combination_originality",
    "design_signal_purity",
)
_SURFACE_EDGE_EXEMPT_METRICS = frozenset(
    {
        "design_distinctiveness",
        "visual_observation_grounding",
        "craft_embellishment_salience",
        "design_signal_purity",
    }
)
_COMBO_EXEMPT_METRICS = frozenset(
    {
        "design_distinctiveness",
        "visual_observation_grounding",
        "silhouette_combination_originality",
        "design_signal_purity",
    }
)
_DESIGN_IDENTIFYING_SIGNATURES = (
    (
        "edge_path",
        re.compile(
            r"(appliqu[eé]|frayed|fringe[d]?\b|cutwork|crochet|"
            r"bead(?:ed|work)|charm-like|tassel|rosette|feather trim|braided trim|"
            r"zigzag|scalloped|decorative (?:border|trim|edging)|banded trim|"
            r"(?:sequin|ruffle|trim|edging|border|binding)\w*.{0,80}"
            r"(?:along|down|at|from|outlines?|running|borders?)\s+"
            r"(?:the\s+)?(?:neckline|front|hem|cuff|opening|sleeve|slit|neck|waist))",
            re.I,
        ),
    ),
    (
        "surface_field",
        re.compile(
            r"(all-?over|densely (?:covered|textured)|painterly|scenic (?:print|landscape)|"
            r"chevron|shaggy|boucl[eé]|starburst|patchwork|floral surface|"
            r"graphic (?:panel|motif|cutout|check)|geometric panel|"
            r"irregular (?:stripe|panel|plaid)|mismatched panel|mixed-?print|"
            r"contrast panels?\s+(?:curve|run|along)|"
            r"oversized (?:white |abstract )?(?:motif|curved)|"
            r"branch-like|bow-and-scroll)",
            re.I,
        ),
    ),
    (
        "second_identity",
        re.compile(
            r"(?:worn open(?:\s+at the neck)?\s+over|"
            r"sits open over|"
            r"opens (?:fully )?over|"
            r"open-front \w+(?:/\w+)?(?: \w+){0,4} worn over|"
            r"frames a)\s+.{0,120}?"
            r"(shorts?|dress|skirt|vest|tunic|bike|cycling|stripe|top|shirt|blouse|layer)",
            re.I,
        ),
    ),
)
_FACTORY_FINISHING_CUES = re.compile(
    r"(topstitch(?:ing)?|hidden placket|concealed (?:placket|closure)|"
    r"tonal piping|contrast piping|double c\b|clean salon line|"
    r"lining (?:peek|glimpses?|peeks))",
    re.I,
)
_ORDINARY_DRESSING_CUES = re.compile(
    r"(self-belt|"
    r"tucked into (?:the )?(?:waist|trousers|pants|skirt|shorts|jacket|belt|waistband)|"
    r"(?:shirt|blouse|top)s?\b.{0,40}tucked into|"
    r"can be worn (?:fully open|open|belted))",
    re.I,
)
_THEME_POSE_CUES = re.compile(
    r"(stance should|promenade in sea)",
    re.I,
)
# Collection-shared cruise / shoreline wardrobe — not an identifying idea by itself.
_SERIES_FORMULA_CUES = re.compile(
    r"(shoreline|marina jacket|bleu de travail|sailor (?:trousers|pants)|"
    r"nautical jacket|the outerwear|"
    r"look\s+\d+\s*:|"
    r"cropped (?:marina|navy|nautical|canvas))",
    re.I,
)
# Union of factory + dressing; kept for callers that still test "ordinary finishing".
_ORDINARY_FINISHING_CUES = re.compile(
    r"(topstitch(?:ing)?|hidden placket|concealed (?:placket|closure)|"
    r"tonal piping|contrast piping|self-belt|"
    r"double c\b|"
    r"lining (?:peek|glimpses?|peeks)|"
    r"tucked into (?:the )?(?:waist|trousers|pants|skirt|shorts|jacket|belt|waistband)|"
    r"(?:shirt|blouse|top)s?\b.{0,40}tucked into|"
    r"can be worn (?:fully open|open|belted)|"
    r"clean salon line)",
    re.I,
)


def list_design_identifying_signatures(text: str) -> List[str]:
    """Return inverse-style identifying signatures present in the look text."""
    found: List[str] = []
    body = text or ""
    for name, pattern in _DESIGN_IDENTIFYING_SIGNATURES:
        if pattern.search(body):
            found.append(name)
    return found


def list_design_merit_cue_families(text: str) -> Dict[str, bool]:
    """Detect finishing / dressing / theme / shared-series grammar."""
    body = text or ""
    return {
        "factory_finishing": bool(_FACTORY_FINISHING_CUES.search(body)),
        "ordinary_dressing": bool(_ORDINARY_DRESSING_CUES.search(body)),
        "theme_pose": bool(_THEME_POSE_CUES.search(body)),
        "series_formula": bool(_SERIES_FORMULA_CUES.search(body)),
    }


def _design_merit_exempt_metrics(signatures: List[str]) -> Set[str]:
    exempt: Set[str] = set()
    for sig in signatures:
        if sig in ("surface_field", "edge_path"):
            exempt |= _SURFACE_EDGE_EXEMPT_METRICS
        elif sig == "second_identity":
            exempt |= _COMBO_EXEMPT_METRICS
    return exempt


# 左右对打：只认成对的左/右身体分区，并且两侧服装词不同。
_LR_SIDE = re.compile(
    r"\b(left|right)\s+(half|side|sleeve|arm|leg|foot|shoe)\b",
    re.I,
)
_CN_LR_SIDE = re.compile(r"(左|右)(半边|半侧|半|侧|袖|臂|腿|脚|鞋)")
_LR_ZONE = {
    "half": "sleeve",
    "side": "sleeve",
    "sleeve": "sleeve",
    "arm": "sleeve",
    "半边": "sleeve",
    "半侧": "sleeve",
    "半": "sleeve",
    "侧": "sleeve",
    "袖": "sleeve",
    "臂": "sleeve",
    "leg": "leg",
    "腿": "leg",
    "foot": "shoe",
    "shoe": "shoe",
    "脚": "shoe",
    "鞋": "shoe",
}
_ZONE_TOKEN = re.compile(
    r"(wool|silk|sequin|tweed|satin|leather|gabardine|canvas|knit|crepe|"
    r"pencil|culotte|palazzo|trouser|pants|shorts|skirt|harem|"
    r"pump|sandal|boot|mule|oxford|ballet|slingback|stiletto|"
    r"sleeveless|bishop|one-shoulder|cold shoulder|set-in|shawl|"
    r"羊毛|丝绸|亮片|粗花呢|缎面|皮革|西裤|阔腿|铅笔裙|短裤|"
    r"高跟鞋|凉鞋|短靴|穆勒|无袖|长袖|翻领)",
    re.I,
)
# 同件互斥：原文用 “the same coat/hem/shell …” 把第二个绑定接上去。
_SAME_BINDING = re.compile(
    r"\b(?:the same|that same|those same)\s+"
    r"(?:jacket|coat|dress|hem|shell|neckline|sleeve|sleeves|garment|lower garment)\b",
    re.I,
)
_BINDING_PAIRS = (
    (
        re.compile(r"(concealed (?:button )?placket|hidden placket|暗门襟)", re.I),
        re.compile(r"(double-breasted|double breasted|双排扣)", re.I),
    ),
    (
        re.compile(r"(stand[\s-]collar|mandarin collar|高立领|(?<![长短])立领)", re.I),
        re.compile(
            r"(plunging|deep\s*v|square[d]?(?:\s+to\s+scoop|[\s-]neck(?:line)?|[\s-]scoop)|方领|深\s*V)",
            re.I,
        ),
    ),
    (
        re.compile(r"\bcollarless\b", re.I),
        re.compile(r"\bnotched lapel\b", re.I),
    ),
    (
        re.compile(r"(sleeveless|cutaway armholes|无袖)", re.I),
        re.compile(r"(long set-in sleeves|long sleeves|set-in sleeves|长袖|长直筒袖)", re.I),
    ),
)
_CN_BOTH_BINDINGS = re.compile(r"既[^。]{0,16}又")
# 用 or 并列两个不能同时穿的品类。材质不确定（silk or crepe）不在这三栏里。
_OR_SPLIT = re.compile(r"\s+\bor\b\s+", re.I)
_SLOT_TOKEN = {
    "bottom": re.compile(
        r"\b(skirts?|trousers?|pants?|shorts?(?!\s+(?:sleeve|draped|drape|cap|hair))|culottes?|palazzos?|harems?)\b",
        re.I,
    ),
    "shoe": re.compile(
        r"\b(flats?|pumps?|sandals?|boots?|mules?|oxfords?|slingbacks?|stilettos?|loafers?)\b",
        re.I,
    ),
    "neckline": re.compile(
        r"\b(strapless|off[-\s]?shoulder|one[-\s]?shoulder|square neck|halter|stand collar|plunging)\b",
        re.I,
    ),
}
_BARE_ARM = re.compile(
    r"\b(?:sleeveless|cold shoulder|bare arm|one[-\s]?shoulder)\b",
    re.I,
)
_COVERED_SLEEVE = re.compile(
    r"\b(?:long|set-in|bishop|tailored)\s+(?:[A-Za-z]+\s+){0,2}sleeves?\b",
    re.I,
)
_OTHER_SIDE_BARE = re.compile(
    r"\bother side\b.{0,48}\b(?:sleeveless|one[-\s]?shoulder|bare)\b"
    r"|\b(?:sleeveless|one[-\s]?shoulder)\b.{0,48}\bother side\b",
    re.I,
)
_REPAIR_VOICE = re.compile(
    r"\bconflicting\b|\bto replace the\b|\brestore a coherent\b|\bdo not\b|\bdelete the\b",
    re.I,
)
# 另一主题：反面样例里种进去的异质服装，不把披肩、开衩、胸针算进去。
_FOREIGN_THEME = re.compile(
    r"(bridal|cathedral gown|tulle veil|orange-blossom|"
    r"coronation|ermine|\bstate crown\b|\bcrown\b|"
    r"flamenco|mourning|masquerade|"
    r"morning dress|tailcoat|top hat|"
    r"panniers?|powdered coiffure|beauty patch|rococo|robe à la française|"
    r"harlequin|masquerade mask|jeweled mask|feathered fan|"
    r"新娘|头纱|加冕|王冠|弗拉明戈|丧服|假面|晨礼服|燕尾服|礼帽|撑裙|洛可可|美人痣)",
    re.I,
)
CONSISTENCY_PENALTY_FLOOR = 0.75
CONSISTENCY_PENALTY_SEVERE = 1.0
# 冲突还在时，质量项是总分里的 0.8 加成，封在这里，脏稿的 S_fp 起不来。
CONFLICT_QUALITY_CAP = 0.25
_SIDE_MARK = re.compile(
    r"\b(left|right)\s+(half|side|sleeve|arm|leg|foot|shoe)\b"
    r"|\bon the (left|right)\b(?!\s+front\b)",
    re.I,
)
_BOTTOM_WORD = re.compile(
    r"\b(skirts?|trousers?|pants?|shorts?(?!\s+(?:sleeve|draped|drape|cap|hair))|culottes?|palazzos?|harems?)\b",
    re.I,
)
_SHOE_WORD = re.compile(
    r"\b(pumps?|sandals?|boots?|mules?|oxfords?|flats?|slingbacks?|stilettos?|loafers?)\b",
    re.I,
)
_SLEEVE_WORD = re.compile(
    r"\b(?:sleeveless|cold shoulder|one[\s-]shoulder|bishop|set[\s-]in|cropped sleeve)\b"
    r"|\bfloor[\s-]grazing(?:\s+[A-Za-z]+){0,4}\s+sleeve\b",
    re.I,
)
_SHORT_SLEEVE = re.compile(r"\b(?:cropped sleeve|above the elbow|elbow-length sleeve)\b", re.I)
_LONG_SLEEVE = re.compile(
    r"\b(?:bishop|set[\s-]in|long)\s+(?:[A-Za-z]+(?:-[A-Za-z]+)*\s+){0,3}sleeves?\b"
    r"|\bfloor[\s-]grazing(?:\s+[A-Za-z]+(?:-[A-Za-z]+)*){0,4}\s+sleeve\b"
    r"|\bsleeves?\s+to the (?:wrist|knee)\b",
    re.I,
)
_SHELL_VERSION = re.compile(r"\b(?:available in|either version)\b", re.I)
_SHORT_HEM = re.compile(r"(just below the knee|knee-length)", re.I)
_FLOOR_HEM = re.compile(
    r"(brushes the floor|sweeps the floor|floor[\s-]sweeping|floor[\s-]length|floor[\s-]grazing|pools on the floor)",
    re.I,
)
_HEM_LENGTHS = (
    ("hip", re.compile(r"cropped to the hip|hip-length", re.I)),
    ("waist", re.compile(r"cropped to the waist", re.I)),
    ("knee", re.compile(r"just below the knee|knee-length", re.I)),
    ("calf", re.compile(r"brushes the calf|mid-calf|to the calf", re.I)),
    ("floor", re.compile(
        r"brushes the floor|sweeps the floor|floor[\s-](?:length|grazing|sweeping)|pools on the floor|(?:with|in)\s+a\s+train\b",
        re.I,
    )),
)
_OUTER_LENGTH_OWNER = re.compile(r"\b(?:jacket|coat|dress|hem)\b", re.I)
_BOTTOM_LENGTH_OWNER = re.compile(r"\b(?:skirts?|trousers?|pants?|shorts?|gown)\b", re.I)
_CONFLICT_QUALITY_METRICS = (
    "generation_readiness",
    "design_distinctiveness",
    "silhouette_combination_originality",
    "design_signal_purity",
)


def _slot_lemma(slot: str, token: str) -> str:
    word = token.lower()
    if slot == "bottom":
        if word.startswith("skirt"):
            return "skirt"
        if word.startswith("trouser") or word.startswith("pant"):
            return "trouser"
        if word.startswith("short"):
            return "shorts"
        if word.startswith("culotte"):
            return "culotte"
        if word.startswith("palazzo"):
            return "palazzo"
        return "harem"
    if slot == "shoe":
        if word.startswith("flat"):
            return "flat"
        if word.startswith("pump"):
            return "pump"
        if word.startswith("sandal"):
            return "sandal"
        if word.startswith("boot"):
            return "boot"
        if word.startswith("mule"):
            return "mule"
        if word.startswith("oxford"):
            return "oxford"
        if word.startswith("slingback"):
            return "slingback"
        if word.startswith("stiletto"):
            return "stiletto"
        return "loafer"
    return word


_SLOT_FILLER = {
    "a", "an", "the", "or", "and", "with", "in", "of", "her", "his", "its", "to", "for",
}
_UNCERTAINTY = re.compile(
    r"\b(?:appears?\s+to\s+be|visible\s+as|seems?\s+to|suggesting|possibly|may\s+be|might\s+be)\b"
    r"|-\s*like\b",
    re.I,
)


def _has_slot_modifier(snippet: str, token: str) -> bool:
    """品类词前还有自己的款式或颜色词。光写 skirt or shorts 不算两套。"""
    head = snippet[: snippet.lower().rfind(token.lower())]
    words = [w.lower() for w in re.findall(r"[A-Za-z]+(?:-[A-Za-z]+)?", head)]
    return any(word not in _SLOT_FILLER for word in words[-3:])


def _alternative_slots(body: str) -> List[str]:
    """or 两边各是一个写全的不同品类。同一件衣服的两种叫法不算。"""
    found: List[str] = []
    for sentence in re.split(r"[。.!?;\n]", body):
        if _UNCERTAINTY.search(sentence):
            continue
        parts = _OR_SPLIT.split(sentence)
        if len(parts) < 2:
            continue
        for index in range(len(parts) - 1):
            left = parts[index][-48:]
            right = parts[index + 1][:48]
            for slot, pattern in _SLOT_TOKEN.items():
                left_hits = list(pattern.finditer(left))
                right_hits = list(pattern.finditer(right))
                if not left_hits or not right_hits:
                    continue
                left_lemmas = {_slot_lemma(slot, match.group(1)) for match in left_hits}
                right_lemmas = {_slot_lemma(slot, match.group(1)) for match in right_hits}
                if not left_lemmas.isdisjoint(right_lemmas):
                    continue
                if not _has_slot_modifier(left, left_hits[-1].group(1)):
                    continue
                if not _has_slot_modifier(right, right_hits[0].group(1)):
                    continue
                if slot not in found:
                    found.append(slot)
    return found


def _has_two_sleeve_states(body: str) -> bool:
    """一侧有袖、另一侧无袖，或把这种对打改写成单肩，仍是两种袖。"""
    for sentence in re.split(r"[。.!?;\n]", body):
        if _OTHER_SIDE_BARE.search(sentence):
            return True
        for bare in _BARE_ARM.finditer(sentence):
            start = max(0, bare.start() - 40)
            end = min(len(sentence), bare.end() + 40)
            window = sentence[start:end]
            if _COVERED_SLEEVE.search(window):
                return True
    return False


def _garment_lemmas(pattern, text: str, slot: str) -> Set[str]:
    return {_slot_lemma(slot, match.group(1)) for match in pattern.finditer(text)}


def _clause_zones(sentence: str) -> List[str]:
    """把每个裤、鞋、袖词归到最近的左/右。on the right 带出的另一件也算分套。"""
    marks = list(_SIDE_MARK.finditer(sentence))
    found: List[str] = []
    if len(marks) >= 2:
        buckets: Dict[str, Dict[str, Set[str]]] = {"sleeve": {}, "leg": {}, "shoe": {}}

        def _side(mark: re.Match) -> str:
            return (mark.group(1) or mark.group(3) or "").lower()

        def _nearest(pos: int) -> re.Match:
            return min(
                marks,
                key=lambda mark: min(abs(pos - mark.start()), abs(pos - mark.end())),
            )

        for pattern, zone, slot in (
            (_SLEEVE_WORD, "sleeve", ""),
            (_BOTTOM_WORD, "leg", "bottom"),
            (_SHOE_WORD, "shoe", "shoe"),
        ):
            for match in pattern.finditer(sentence):
                side = _side(_nearest(match.start()))
                if not side:
                    continue
                token = _slot_lemma(slot, match.group(1)) if slot else match.group(0).lower()
                buckets[zone].setdefault(side, set()).add(token)
        for zone, sides in buckets.items():
            left = sides.get("left") or set()
            right = sides.get("right") or set()
            if left and right and left.isdisjoint(right):
                found.append(zone)
    if re.search(r"\bwhile\b", sentence, re.I):
        if len(_garment_lemmas(_BOTTOM_WORD, sentence, "bottom")) >= 2 and "leg" not in found:
            found.append("leg")
        if len(_garment_lemmas(_SHOE_WORD, sentence, "shoe")) >= 2 and "shoe" not in found:
            found.append("shoe")
    return found


def _unlabeled_counterpart(body: str, pattern, slot: str) -> bool:
    """已经点了一侧，正文里又出现第二种裤或鞋。"""
    lemmas: Set[str] = set()
    sided = False
    for sentence in re.split(r"[。.!?;\n]", body):
        found = _garment_lemmas(pattern, sentence, slot)
        if not found:
            continue
        lemmas |= found
        if _SIDE_MARK.search(sentence):
            sided = True
    return sided and len(lemmas) >= 2


def _sleeve_grammars_conflict(body: str) -> bool:
    """短袖和拖地袖如果还写着左右袖或左右半边，仍是两种袖。左右腿不算。"""
    sleeve_side = re.search(
        r"\b(?:left|right)\s+(?:half|side|sleeve|arm)\b",
        body,
        re.I,
    )
    if not sleeve_side:
        return False
    short = bool(_SHORT_SLEEVE.search(body))
    long = bool(_LONG_SLEEVE.search(body))
    bare = bool(_BARE_ARM.search(body))
    return sum(int(flag) for flag in (short, long, bare)) >= 2


def conflict_quality_cap(conflicts: Dict[str, Any]) -> Optional[float]:
    """冲突还在时，压低进入总分的质量加成。"""
    if not conflicts.get("active"):
        return None
    return CONFLICT_QUALITY_CAP


def _length_owner(sentence: str, start: int, end: int) -> str:
    nearest = ""
    nearest_dist = 10**9
    for kind, pattern in (("bottom", _BOTTOM_LENGTH_OWNER), ("outer", _OUTER_LENGTH_OWNER)):
        for match in pattern.finditer(sentence):
            dist = min(abs(match.start() - start), abs(match.end() - end))
            if dist < nearest_dist:
                nearest_dist = dist
                nearest = kind
    return nearest


def _two_lengths_one_piece(sentence: str) -> bool:
    """同一件外套、大衣或下摆上的两个长度是冲突。短外套配拖地裙是叠穿。"""
    found = []
    for name, pattern in _HEM_LENGTHS:
        for match in pattern.finditer(sentence):
            found.append((name, _length_owner(sentence, match.start(), match.end())))
    classes = {name for name, _owner in found}
    if len(classes) < 2:
        return False
    owners = {owner for _name, owner in found if owner}
    if "bottom" in owners and "outer" in owners:
        return False
    return True


def _nearby_binding_hits(body: str) -> int:
    """互斥属性拆到相邻句时仍然算冲突。袖型对打仍只看同一句，避免内层无袖被误伤。"""
    hits = 0
    for left_pat, right_pat in _BINDING_PAIRS[:3]:
        for left in left_pat.finditer(body):
            window = body[max(0, left.start() - 320) : min(len(body), left.end() + 320)]
            if right_pat.search(window):
                hits += 1
                break
    for short in _SHORT_HEM.finditer(body):
        window = body[max(0, short.start() - 400) : min(len(body), short.end() + 400)]
        if re.search(r"\bhem\b", window, re.I) and _FLOOR_HEM.search(window):
            hits += 1
            break
    return hits


_LAYERING_WORD = re.compile(r"\b(?:under|over|beneath|below)\b", re.I)


_SECOND_BOTTOM_CUE = re.compile(
    r"\b(?:that same|lower body|instead of)\b",
    re.I,
)


def _unlayered_bottom_pair(body: str) -> bool:
    """同一套下装被写成第二种裤子，且没有叠穿在同一句里。单数 short 不当下装。"""
    if not _SECOND_BOTTOM_CUE.search(body):
        return False
    layered_together: Set[str] = set()
    all_lemmas: Set[str] = set()
    for sentence in re.split(r"[。.!?;\n]", body):
        lemmas: Set[str] = set()
        for match in _BOTTOM_WORD.finditer(sentence):
            token = match.group(1)
            if token.lower() == "short":
                continue
            lemmas.add(_slot_lemma("bottom", token))
        if not lemmas:
            continue
        if len(lemmas) >= 2 and re.search(r"\bor\b", sentence, re.I):
            continue
        all_lemmas |= lemmas
        if len(lemmas) >= 2 and _LAYERING_WORD.search(sentence):
            layered_together |= lemmas
    return len(all_lemmas - layered_together) >= 2


def detect_consistency_conflicts(text: str) -> Dict[str, Any]:
    """区分设计与冲突。

    设计（不在这里）：一套衣服上的表面场、沿边路径、同一主题里敞开后仍可读的内层，
    以及胸针、偏心结、一条开衩、裹襟、垂褶、不齐下摆这类落点。
    冲突：左右两套袖/裤/鞋、同一要素两个互斥绑定、另一主题的服装还在正文里、
    用 or 并列两个品类、把左右袖改写成单肩、把改写说明写进正文。
    """
    body = text or ""
    zones: Dict[str, Dict[str, Set[str]]] = {"sleeve": {}, "leg": {}, "shoe": {}}

    def _note(zone: str, side: str, start: int) -> None:
        window = body[start:start + 96]
        tokens = {m.group(0).lower() for m in _ZONE_TOKEN.finditer(window)}
        zones[zone].setdefault(side, set()).update(tokens)

    for match in _LR_SIDE.finditer(body):
        _note(_LR_ZONE[match.group(2).lower()], match.group(1).lower(), match.end())
    for match in _CN_LR_SIDE.finditer(body):
        side = "left" if match.group(1) == "左" else "right"
        _note(_LR_ZONE[match.group(2)], side, match.end())

    split_zones: List[str] = []
    for zone, sides in zones.items():
        left = sides.get("left")
        right = sides.get("right")
        if left is None or right is None:
            continue
        if left != right and (left or right):
            split_zones.append(zone)
    for sentence in re.split(r"[。.!?;\n]", body):
        for zone in _clause_zones(sentence):
            if zone not in split_zones:
                split_zones.append(zone)
    if _unlabeled_counterpart(body, _BOTTOM_WORD, "bottom") and "leg" not in split_zones:
        split_zones.append("leg")
    if _unlabeled_counterpart(body, _SHOE_WORD, "shoe") and "shoe" not in split_zones:
        split_zones.append("shoe")
    if _unlayered_bottom_pair(body) and "leg" not in split_zones:
        split_zones.append("leg")

    same_hits = len(_SAME_BINDING.findall(body)) + len(_CN_BOTH_BINDINGS.findall(body))
    same_hits += _nearby_binding_hits(body)
    for sentence in re.split(r"[。.!?\n]", body):
        for left_pat, right_pat in _BINDING_PAIRS:
            if left_pat.search(sentence) and right_pat.search(sentence):
                same_hits += 1
        if _SHELL_VERSION.search(sentence) and re.search(r"sequin", sentence, re.I) and re.search(
            r"wool|gabardine", sentence, re.I
        ):
            same_hits += 1
        if (
            re.search(r"\bhem\b", sentence, re.I)
            and _SHORT_HEM.search(sentence)
            and _FLOOR_HEM.search(sentence)
        ) or _two_lengths_one_piece(sentence):
            same_hits += 1
    foreign = sorted({m.group(0).lower() for m in _FOREIGN_THEME.finditer(body)})
    alternatives = _alternative_slots(body)
    two_sleeve_states = _has_two_sleeve_states(body) or _sleeve_grammars_conflict(body)
    repair_voice = bool(_REPAIR_VOICE.search(body))
    active = bool(
        split_zones or same_hits or foreign or alternatives or two_sleeve_states or repair_voice
    )
    extra_hits = len(alternatives) + int(two_sleeve_states) + int(repair_voice)
    severe = len(split_zones) >= 2 or same_hits >= 2 or extra_hits >= 2
    reasons: List[str] = []
    if split_zones:
        reasons.append("left-right split in " + ", ".join(split_zones))
    if same_hits:
        reasons.append(f"same-element bindings ×{same_hits}")
    if foreign:
        reasons.append("foreign theme: " + ", ".join(foreign[:4]))
    if alternatives:
        reasons.append("or-choice in " + ", ".join(alternatives))
    if two_sleeve_states:
        reasons.append("two sleeve states")
    if repair_voice:
        reasons.append("repair narration")
    return {
        "active": active,
        "severe": severe,
        "zones": split_zones,
        "same_element_bindings": same_hits,
        "foreign_terms": foreign,
        "alternative_slots": alternatives,
        "two_sleeve_states": two_sleeve_states,
        "repair_voice": repair_voice,
        "reason": "; ".join(reasons),
    }


def _layout_board_body(text: str) -> str:
    kept: List[str] = []
    for line in (text or "").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if _is_t2i_preamble(stripped) or _is_single_frame_line(stripped):
            continue
        kept.append(stripped)
    return "\n".join(kept)


def _positive_board_hit(text: str) -> bool:
    for match in _BOARD_LAYOUT_RE.finditer(text or ""):
        window = (text or "")[max(0, match.start() - 16):match.start()]
        if re.search(r"(?i)\b(?:no|not|without|never)\b\s*$", window):
            continue
        return True
    return False


def detect_layout_board(text: str) -> Dict[str, Any]:
    """正文若还在要拼贴、平铺、离身货品或 Look 编号，记为单帧失败。

    官方单帧开场白（No collage, no flat lay…）不计入。
    """
    body = _layout_board_body(text)
    classes: List[str] = []
    if _LOOK_LABEL_RE.search(body):
        classes.append("look label")
    if _positive_board_hit(body):
        classes.append("collage or flat lay")
    if _OFF_BODY_RE.search(body):
        classes.append("off-body catalog")
    severe = len(classes) >= 2 or "collage or flat lay" in classes
    return {
        "active": bool(classes),
        "severe": severe,
        "classes": classes,
        "reason": "; ".join(classes),
    }


def apply_layout_board_penalty_floor(penalties: Dict[str, Any], layout: Dict[str, Any]) -> Dict[str, Any]:
    """拼贴/平铺/Look 编号还在时，把 generation_content_penalty 抬到高档。"""
    if not layout.get("active"):
        return penalties
    floor = LAYOUT_BOARD_PENALTY_SEVERE if layout.get("severe") else LAYOUT_BOARD_PENALTY_FLOOR
    note = str(layout.get("reason") or "single-frame layout")
    key = "generation_content_penalty"
    try:
        current = float(penalties.get(key) or 0.0)
    except (TypeError, ValueError):
        current = 0.0
    updated = max(current, floor)
    penalties[key] = updated
    item = (penalties.get("items") or {}).get(key)
    if isinstance(item, dict):
        item["score"] = updated
        if current + 1e-9 < floor:
            reason = (item.get("reason") or "").strip()
            item["reason"] = (reason + " " if reason else "") + f"[code floor {floor:g}: {note}]"
            if isinstance(penalties.get("reasons"), dict):
                penalties["reasons"][key] = item["reason"]
    items = penalties.get("items") or {}
    keys = [name for name in items if name in penalties]
    if keys:
        penalties["total_penalty"] = round(sum(float(penalties[name]) for name in keys) / len(keys), 4)
    return penalties


def apply_layout_board_quality_caps(metric_results: Dict[str, Any], layout: Dict[str, Any]) -> None:
    """单帧失败时，生成适配、可见性优先级和信息密度封顶。"""
    if not layout.get("active"):
        return
    note = str(layout.get("reason") or "single-frame layout")
    for name in ("generation_readiness", "visibility_priority", "information_density"):
        row = metric_results.get(name)
        if not isinstance(row, dict) or not row.get("applicable"):
            continue
        try:
            score = float(row.get("score_value"))
        except (TypeError, ValueError):
            continue
        if score <= 0.25:
            continue
        row["score_value"] = 0.25
        row["hit"] = 0
        row["reason"] = (row.get("reason") or "") + f" [stays at 0.25: {note}]"


def apply_consistency_penalty_floor(penalties: Dict[str, Any], conflicts: Dict[str, Any]) -> Dict[str, Any]:
    """裁判把冲突打成 0 时，仍把一致性和协调性抬到下限，再重算五项平均。"""
    if not conflicts.get("active"):
        return penalties
    floor = CONSISTENCY_PENALTY_SEVERE if conflicts.get("severe") else CONSISTENCY_PENALTY_FLOOR
    note = str(conflicts.get("reason") or "consistency conflict")
    for key in ("consistency_penalty", "coordination_penalty"):
        try:
            current = float(penalties.get(key) or 0.0)
        except (TypeError, ValueError):
            current = 0.0
        updated = max(current, floor)
        penalties[key] = updated
        item = (penalties.get("items") or {}).get(key)
        if isinstance(item, dict):
            item["score"] = updated
            if current + 1e-9 < floor:
                reason = (item.get("reason") or "").strip()
                item["reason"] = (reason + " " if reason else "") + f"[code floor {floor:g}: {note}]"
                if isinstance(penalties.get("reasons"), dict):
                    penalties["reasons"][key] = item["reason"]
    items = penalties.get("items") or {}
    keys = [key for key in items if key in penalties]
    if keys:
        penalties["total_penalty"] = round(sum(float(penalties[key]) for key in keys) / len(keys), 4)
    return penalties


def apply_conflict_quality_caps(metric_results: Dict[str, Any], conflicts: Dict[str, Any]) -> None:
    """冲突还在时，相关质量分在代码里封顶，不靠裁判记住提示。"""
    if not conflicts.get("active"):
        return
    binding_cap = 0.0 if int(conflicts.get("same_element_bindings") or 0) >= 2 else 0.25
    caps = {name: 0.25 for name in _CONFLICT_QUALITY_METRICS}
    if int(conflicts.get("same_element_bindings") or 0) > 0:
        caps["attribute_entity_binding"] = binding_cap
    for name, cap in caps.items():
        row = metric_results.get(name)
        if not isinstance(row, dict) or not row.get("applicable"):
            continue
        try:
            score = float(row.get("score_value"))
        except (TypeError, ValueError):
            continue
        if score <= cap:
            continue
        row["score_value"] = cap
        row["hit"] = 1 if cap >= QUALITY_FULL_HIT_THRESHOLD else 0
        row["reason"] = (row.get("reason") or "") + f" [stays at {cap:g}: consistency conflict is not design]"
    density = metric_results.get("information_density")
    if isinstance(density, dict) and density.get("applicable"):
        try:
            density_score = float(density.get("score_value"))
        except (TypeError, ValueError):
            density_score = 0.0
        if density_score > 0.5:
            density["score_value"] = 0.5
            density["hit"] = 1 if 0.5 >= QUALITY_FULL_HIT_THRESHOLD else 0
            density["reason"] = (density.get("reason") or "") + " [stays at 0.5: a second identity is not an extra imageable fact]"


def compute_design_merit_metric_caps(
    text: str,
    conflicts: Optional[Dict[str, Any]] = None,
) -> Dict[str, Dict[str, Any]]:
    """Per-axis floors: identifying ideas stay high; shared series grammar stays low.

    A consistency conflict is not an identifying idea, so it caps the idea axes
    even when a surface, an edge, or a same-theme inner is also present.
    Factory finishing on one identity does not force the 0.25 floor.
    """
    signatures = list_design_identifying_signatures(text)
    cues = list_design_merit_cue_families(text)
    conflict = conflicts if conflicts is not None else detect_consistency_conflicts(text)
    exempt = set() if conflict.get("active") else _design_merit_exempt_metrics(signatures)
    has_any_sig = bool(signatures) and not conflict.get("active")
    has_combo_sig = "second_identity" in signatures and not conflict.get("active")
    shared_wardrobe = cues["ordinary_dressing"] or cues["series_formula"]
    caps: Dict[str, Dict[str, Any]] = {}

    def _propose(metric: str, cap: float, reason: str) -> None:
        if metric in exempt:
            return
        prev = caps.get(metric)
        if prev is None or cap < float(prev["cap"]):
            caps[metric] = {"cap": cap, "reason": reason}

    if not has_any_sig:
        if shared_wardrobe:
            _propose(
                "design_distinctiveness",
                DESIGN_MERIT_AUX_CAP_DISTINCTIVENESS_ORDINARY,
                "no identifying idea; shared finishing or series wardrobe",
            )
        else:
            _propose(
                "design_distinctiveness",
                DESIGN_MERIT_AUX_CAP_DISTINCTIVENESS_CEILING,
                "no identifying idea",
            )

    if not has_any_sig and shared_wardrobe:
        _propose(
            "visual_observation_grounding",
            DESIGN_MERIT_AUX_CAP_GROUNDING,
            "observation is cut/finishing, not an identifying idea",
        )

    if not has_combo_sig:
        if cues["ordinary_dressing"] or cues["series_formula"]:
            _propose(
                "silhouette_combination_originality",
                DESIGN_MERIT_AUX_CAP_COMBINATION,
                "ordinary or series stacking, no second identity",
            )
        elif not has_any_sig:
            _propose(
                "silhouette_combination_originality",
                DESIGN_MERIT_AUX_CAP_COMBINATION_WEAK,
                "no same-theme inner identity",
            )

    if not has_any_sig:
        if cues["theme_pose"] or cues["series_formula"]:
            _propose(
                "design_signal_purity",
                DESIGN_MERIT_AUX_CAP_PURITY_THEME,
                "theme or series narrative without an identifying idea",
            )
        else:
            _propose(
                "design_signal_purity",
                DESIGN_MERIT_AUX_CAP_PURITY_CEILING,
                "no identifying idea",
            )

    if conflict.get("active"):
        for metric in (
            "design_distinctiveness",
            "silhouette_combination_originality",
            "design_signal_purity",
        ):
            caps[metric] = {
                "cap": DESIGN_MERIT_AUX_CAP_PURITY_THEME,
                "reason": "consistency conflict is not an identifying idea",
            }

    return {
        "caps": caps,
        "signatures": signatures,
        "cues": cues,
        "conflicts": conflict,
        "exempt_metrics": sorted(exempt),
    }


def design_merit_auxiliary_cap(text: str) -> Optional[float]:
    """Strictest per-metric cap, or None if no DesignMerit axis is capped."""
    payload = compute_design_merit_metric_caps(text)
    caps = payload.get("caps") or {}
    if not caps:
        return None
    return min(float(item["cap"]) for item in caps.values())


def apply_design_merit_auxiliary_caps(text: str, module_output: Dict) -> Dict:
    """Clamp DesignMerit scores after the judge when the look has no identifying idea."""
    payload = compute_design_merit_metric_caps(text)
    caps: Dict[str, Dict[str, Any]] = payload["caps"]
    signatures = payload["signatures"]
    patched = dict(module_output or {})
    if caps:
        reason = "; ".join(
            f"{metric}≤{item['cap']:g} ({item['reason']})"
            for metric, item in caps.items()
        )
    elif signatures:
        reason = "identifying idea present; matching axes not floored"
    else:
        reason = "no design floor applied"
    patched["auxiliary_caps"] = {
        "applied": bool(caps),
        "cap": min((float(item["cap"]) for item in caps.values()), default=None),
        "per_metric": caps,
        "signatures": signatures,
        "cues": payload["cues"],
        "exempt_metrics": payload["exempt_metrics"],
        "reason": reason,
    }
    if not caps:
        return patched
    results = []
    for item in coerce_judge_result_items(patched.get("results")):
        row = dict(item)
        metric = row.get("metric")
        spec = caps.get(metric) if isinstance(metric, str) else None
        score = row.get("score")
        if (
            spec
            and row.get("applicable")
            and isinstance(score, (int, float))
            and float(score) > float(spec["cap"])
        ):
            cap = float(spec["cap"])
            row["score"] = cap
            row["hit"] = 1 if cap >= QUALITY_FULL_HIT_THRESHOLD else 0
            row["score_cap"] = cap
            row["reason"] = (row.get("reason") or "") + (
                f" [{metric} stays at {cap:g}: {spec['reason']}]"
            )
        results.append(row)
    patched["results"] = results
    return patched


TOTAL_SCORE_BANDS = [
    (0.90, "Excellent"),
    (0.75, "Strong"),
    (0.55, "Usable"),
    (0.35, "Weak"),
    (0.00, "Poor"),
]

_T2I_MANDATORY_LINE = "Please generate female models and the matching clothing for them."
_T2I_MANDATORY_PATTERNS = (
    re.compile(
        r"^please\s+generate\s+(?:female\s+)?models?\s+and\s+the\s+matching\s+clothing\s+for\s+them\.?\s*$",
        re.IGNORECASE,
    ),
    re.compile(r"^请生成(?:女(?:性|士)?)?模(?:特)?(?:及|和)?(?:其)?(?:对应)?(?:的)?(?:服装|穿搭|造型)?。?\s*$"),
)


def _is_t2i_preamble(line: str) -> bool:
    stripped = (line or "").strip()
    if stripped == _T2I_MANDATORY_LINE:
        return True
    return any(p.match(stripped) for p in _T2I_MANDATORY_PATTERNS)


def _is_single_frame_line(line: str) -> bool:
    """官方单帧开场白本身不计罚；正文里再写拼贴/平铺/Look 编号才计。"""
    stripped = (line or "").strip()
    return stripped.lower().startswith("one photograph of one woman at one moment")


_SECTION_HEADER_RE = re.compile(r"^\s*\d+\.\s+The\s+", re.IGNORECASE)
_LOOK_TITLE_RE = re.compile(r"(?i)^look[\s_]+\d+\b")
_LOOK_LABEL_RE = re.compile(r"(?i)\blook[\s_]+\d+\b")
_BOARD_LAYOUT_RE = re.compile(
    r"(?i)\b(?:collage|flat\s*-?\s*lay|flatlay|product\s+shot|lookbook|"
    r"contact\s+sheet|ghost\s+mannequin|multiple\s+views|separate\s+panels)\b"
)
_OFF_BODY_RE = re.compile(
    r"(?i)(?:"
    r"if (?:the )?(?:outer|coat|jacket|layer).{0,48}removed"
    r"|if removed"
    r"|its own garment"
    r"|read as its own"
    r"|completes? the look"
    r"|finish(?:es)? the look"
    r")"
)
LAYOUT_BOARD_PENALTY_FLOOR = 0.75
LAYOUT_BOARD_PENALTY_SEVERE = 1.0


def strip_eval_boilerplate(text: str, *, preserve_structure: bool = False) -> str:
    """Remove T2I boilerplate, titles, and optionally section headers / key-element lists."""
    raw = (text or "").strip()
    if not raw:
        return ""

    key_split = re.split(r"(?im)^\s*key\s+elements\s*:\s*$", raw, maxsplit=1)
    body = key_split[0].strip()

    kept_lines: List[str] = []
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped:
            if kept_lines and kept_lines[-1] != "":
                kept_lines.append("")
            continue
        if _is_t2i_preamble(stripped) or _is_single_frame_line(stripped):
            continue
        if stripped.lower() == "look textual description":
            continue
        if _LOOK_TITLE_RE.match(stripped):
            continue
        if not preserve_structure and _SECTION_HEADER_RE.match(stripped):
            continue
        if not preserve_structure and re.match(r"^\s*[\*\-•]\s+", line):
            continue
        kept_lines.append(stripped)

    prose = re.sub(r"\n{3,}", "\n\n", "\n".join(kept_lines).strip())
    return re.sub(r"[ \t]+\n", "\n", prose).strip()


class ApiLLMJudge:
    """OpenAI-compatible API judge that returns structured JSON."""

    DEFAULT_SYSTEM_PROMPT = """You are Design_text_Evaluator.

Your task is to judge a fashion text_description against a list of fine-grained metrics.

Judging principles:
1. Hit verification must be semantic, not rigid keyword matching.
2. Synonyms, paraphrases, fashion-specific near-equivalents, hypernyms, and hyponyms should count as hits when they clearly cover the target concept.
3. Only mark hit=1 when the text clearly supports it. Do not hallucinate missing facts.
4. applicable decides whether a metric should enter scoring for this text. If applicable is false, hit must be null.
5. evidence should quote short spans from the original text whenever possible. Each evidence array has at most 3 short quotes (under 20 words each); do not enumerate the whole look.
6. When bilateral differences exist, distinguish trunk from accessories. Trunk = all clothing that defines the worn look: outerwear, inner/base tops, bottoms, and footwear. If the text still gives the trunk two sleeve grammars, two leg garments, or two shoe types, bilateral_coherence must be at most 0.5; if two or more of those zones remain, at most 0.25. Calling the split cohesive or deconstructed does not raise the score. Score 0.75 or above only when sleeve, bottom, and shoe are each one identity. A small placement on one side of that same garment is not a second identity and must not lower the score. A single-breasted closure is not a left-right defect. A same-element contradiction (one garment, two incompatible bindings for neckline, sleeve, length, closure, or shell material) scores attribute_entity_binding, generation_readiness, and design_signal_purity at most 0.25 until one binding remains. Two or more conflicting bindings score attribute_entity_binding 0.0. Clear or Chinese wording does not raise these scores. Garments from a different theme or concept that are still in the text, including as an inner layer, a second subject, or a cohesive contrast, score design_distinctiveness, silhouette_combination_originality, design_signal_purity, and generation_readiness at most 0.25. Do not treat that clash as an identifying idea or as a readable inner identity. These caps override the dimension rubric, a visible-facts floor, and any instruction to keep a specific description high. Mild accessory-only differences are lenient only when the trunk is already one identity.
7. When spatial relations exist, judge whether layering, inside-outside, front-back, and attachment positions remain visually coherent and imageable.
8. For visibility priority, reward texts that emphasize visible, image-dominant details over hidden interior or low-visibility details.
9. For quality_score metrics other than DesignMerit, use the provided quality_dimension and quality_scoring_rubric as the primary grading standard, not only the generic scale. An explicit score cap in a metric rule overrides that rubric.
10. For DesignMerit, score only the identifying idea (module guide). Completeness, precision, and imageability are other modules. Ignore T2I preamble.
11. For ConcisenessAndDensity (visibility_priority), prioritize **visible, image-dominant garment facts** over hidden details, model pose/stance/psychology, and abstract field/identity commentary. The standard single-frame line and the old T2I preamble are fixed boilerplate—ignore them; never penalize them alone. A Look number, a collage, a flat lay, a product shot, or an off-body catalog clause in the paragraph ("if removed", "its own garment", "complete the look") is not boilerplate: generation_readiness and visibility_priority stay at most 0.25 while it remains.
12. For StructuralClarity and GenerationReadiness, judge whether garment information is semantically ordered and **directly usable as one worn photograph**. Do NOT lower scores solely because the text uses numbered sections or bullet lists if the underlying content is imaging-rich. Imaging-rich wording does not override a same-element, theme-clash, or single-frame score cap. A Look title, collage, flat lay, product shot, second view, or off-body garment keeps generation_readiness at most 0.25.
13. For coverage_score metrics, follow each metric's rule field strictly: when a rule requires compound coverage (e.g. construction_technique needs named craft plus approximate body/garment zone; bag or footwear need at least two of three listed facets when applicable; color_relationship_logic needs a color relationship such as dominance, contrast, or tonal layering—not merely listing hue names), hit=1 only if those facets are clearly satisfied in the text. For belt: applicable only when an actual belt/sash/waist-strap/harness accessory is present or described; structural waist emphasis from garment cut alone (defined waist, peplum, seaming, proportion) does not make belt applicable and must not be scored as a belt miss.
14. For information_density, score whether each clause adds a new imageable fact. Do not score character count: shorter is not higher, longer is not lower. High density keeps the identifying anchors (craft path, the surface that makes this look recognizable, inside-outside layering) and does not restate them. Dropping those anchors to get a shorter paragraph caps the score at 0.5. A near-copy or a fact rewritten in new words is restatement, not a new fact. One closing palette/mood sentence does not lower the score. Two identities or a same-element contradiction still in the text caps the score at 0.5.
15. Output strict JSON only. Do not output markdown fences or extra commentary.

Return format:
{
  "module": "module_name",
  "results": [
    {
      "metric": "metric_name",
      "applicable": true,
      "score": 1,
      "evidence": ["short evidence phrase 1", "short evidence phrase 2"],
      "reason": "short explanation"
    }
  ]
}
"""

    QUALITY_PENALTY_SYSTEM_PROMPT = """Deprecated constant. Use _build_quality_penalty_system_prompt()."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.0,
        top_p: float = 1.0,
        max_tokens: int = 1600,
        timeout: int = 120,
        verify_ssl: Optional[bool] = None,
    ) -> None:
        if not logging.getLogger(__name__).handlers:
            logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        _grpo_ev = grpo_design_text_evaluator_config()
        config_api_key = (
            _yaml_opt_str(_grpo_ev.get("api-key"))
            or FASHION_CONFIG.get("api-key")
            or FASHION_CONFIG.get("openai-api-key")
        )
        config_api_base = (
            _yaml_opt_str(_grpo_ev.get("api-base"))
            or FASHION_CONFIG.get("api-base")
            or FASHION_CONFIG.get("openai-api-base")
        )

        self.api_key = api_key or os.environ.get("AI_API_KEY") or config_api_key
        self.api_base = (
            api_base
            or os.environ.get("AI_API_BASE")
            or config_api_base
        ).rstrip("/")
        self.model = (
            model
            or os.environ.get("AI_API_MODEL")
            or os.environ.get("AI_MODEL")
            or _yaml_opt_str(_grpo_ev.get("model"))
            or _yaml_opt_str(FASHION_CONFIG.get("llm-backend"))
            or "gpt-5.4-mini"
        )
        if _grpo_ev.get("max-tokens") is not None:
            max_tokens = int(_grpo_ev["max-tokens"])
        if _grpo_ev.get("timeout") is not None:
            timeout = int(_grpo_ev["timeout"])
        if "temperature" in _grpo_ev:
            temperature = float(_grpo_ev["temperature"])
        self.temperature = temperature
        self.top_p = top_p
        te = dict(FASHION_CONFIG.get("text-evaluator") or {})
        self.design_merit_temperature = float(te.get("design-merit-temperature", temperature))
        self.design_merit_top_p = float(te.get("design-merit-top-p", top_p))
        merit_seed = te.get("design-merit-seed")
        self.design_merit_seed = int(merit_seed) if merit_seed is not None else None
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.penalty_registry: Dict[str, Dict[str, Any]] = {}
        if verify_ssl is None and "verify-ssl" in _grpo_ev:
            verify_ssl = bool(_grpo_ev["verify-ssl"])
        if verify_ssl is None:
            self.verify_ssl = os.environ.get("AI_API_VERIFY_SSL", "true").strip().lower() not in {"0", "false", "no"}
        else:
            self.verify_ssl = verify_ssl

        if not self.api_key:
            raise ValueError(
                "Missing API key. Set root `api-key` in fashion_config.yaml, AI_API_KEY, or pass api_key explicitly."
            )
        if not self.api_base:
            raise ValueError(
                "Missing API base. Set root `api-base` in fashion_config.yaml, AI_API_BASE, or pass api_base explicitly."
            )
        if not self.model:
            raise ValueError("Missing judge model. Set AI_API_MODEL/AI_MODEL or pass model explicitly.")

    def judge_module(
        self,
        text_description: str,
        module_name: str,
        metric_specs: List[Dict],
        axis_name: str,
        *,
        extra_guidance: str = "",
    ) -> Dict:
        user_prompt = self._build_user_prompt(
            text_description,
            module_name,
            metric_specs,
            axis_name,
            extra_guidance=extra_guidance,
        )
        temperature, top_p, seed = self._sampling_for_module(module_name)
        parsed = self._parse_json_with_retry(
            lambda: self._request_completion(
                system_prompt=self.DEFAULT_SYSTEM_PROMPT,
                user_content=user_prompt,
                response_format={"type": "json_object"},
                temperature=temperature,
                top_p=top_p,
                seed=seed,
            ),
            label=f"judge_module[{module_name}]",
        )
        return self._normalize_module_result(module_name, metric_specs, parsed, axis_name)

    def _sampling_for_module(self, module_name: str):
        if module_name == "DesignMerit":
            return (
                self.design_merit_temperature,
                self.design_merit_top_p,
                self.design_merit_seed,
            )
        return (self.temperature, self.top_p, None)

    def judge_quality_penalties(self, text_description: str) -> Dict:
        user_prompt = (
            f"Text to evaluate:\n{text_description}\n\n"
            "Judge local penalty items for this fashion description as a generation prompt.\n"
            "Focus on generation_content_penalty (non-imaging content: model pose/stance, redundant repeated facts, abstract editorial dilution, and any request for a collage, flat lay, product shot, extra view, Look number, or an off-body garment—not the standard single-frame line or the old T2I preamble), "
            "formula_template_penalty (cruise formula, brand-symbol-only, mood/essay dilution of visible design facts—content semantics only, not layout), "
            "trunk-level consistency, styling coordination, and rationality under realistic material and wearing conditions.\n"
            "For formula_template_penalty: score holistically by overall formula severity—formula trunk, brand-symbol-only, mood/essay dilution, interchangeability across looks—not by counting paragraph titles or bullets.\n"
            "UNIFIED RULE for consistency_penalty and coordination_penalty (asymmetry-related): be STRICT when inconsistency sits on trunk garments—outerwear, inner/base tops (shirts, tees, inner knit layers), bottoms, footwear; inner and outer upper-body layers are both trunk when each is a described garment. "
            "When explicitly described, outerwear lining and trouser inner lining (including lining visible through slits) count as trunk together with shell fabric—they must not read as two unrelated garment identities unless clearly separated as under-layer vs outer. "
            "Trunk left-right or same-garment conflicting identities must be penalized while those facts remain in the text. Fluent prose, the word cohesive, or a shared color does not lower the score. "
            "HARD FLOOR: one remaining trunk left-right identity split (different sleeve grammar, different leg garment, or different shoe type) means consistency_penalty and coordination_penalty are each at least 0.75; scores 0, 0.25, and 0.5 are forbidden while that split remains. Two or more of those zones still present means each penalty is 1.0. "
            "Same-element contradiction (one garment given two incompatible necklines, sleeve states, lengths, closures, or shell materials, including 'available in two styles' or 'transitions from A to B') means consistency_penalty at least 0.75; two or more conflicting bindings on the same garment means 1.0. "
            "A second theme or concept's garments still present (as an inner layer, a second subject, or a claimed cohesive contrast) means coordination_penalty at least 0.75 until those garments are gone. "
            "Chinese wording, a claim of symmetry, or the word cohesive does not lower these scores. Score 0 only after the conflicting branch is actually absent. "
            "Do NOT raise these two penalties for small, accessory-only bilateral differences when all trunk coat/inner/pants/shoes are already one identity.\n"
            "Apply coordination_penalty and consistency_penalty strictly when a single upper garment combines incompatible styling languages on left vs right "
            "(e.g., half tailored suit vs half cold-shoulder bishop silk) without one coherent design grammar; also when one coat stacks incompatible collar/military/armor codes without layering rationale.\n"
            "Raise coordination_penalty when leg harnesses conflict with very wide loose trousers without explainable attachment, or waist/hip has multiple belt-harness systems with unclear order; "
            "raise rationality_penalty when harness+trouser construction is physically implausible as ordinary wear.\n"
            "HARD FLOOR for generation_content_penalty: if the paragraph still contains a Look number or look title, a collage, a flat lay, a product shot, a second view, or an off-body catalog clause (if removed, its own garment, complete the look, finish the look), the score is at least 0.75. Two or more of those, or an explicit collage/flat-lay/product-shot request, means 1.0. The official first line that says no collage and no flat lay is boilerplate and does not raise this penalty. Scores 0, 0.25, and 0.5 are forbidden while those facts remain in the paragraph.\n"
            "Each penalty score must be one of its allowed discrete values (typically 0, 0.25, 0.5, 0.75, 1.0), "
            "where higher means a worse issue, analogous to inverted quality rubric levels.\n"
            "Return JSON only."
        )
        parsed = self._parse_json_with_retry(
            lambda: self._generate(self._build_quality_penalty_system_prompt(), user_prompt),
            label="judge_quality_penalties",
        )
        return self._normalize_quality_penalties(parsed)

    def _get_penalty_registry(self) -> Dict[str, Dict[str, Any]]:
        if self.penalty_registry:
            return self.penalty_registry
        return {
            "generation_content_penalty": {
                "allowed_scores": [0.0, 0.25, 0.5, 0.75, 1.0],
                "judge_guidance": "按**生图内容价值**分档。**0~0.25**：可见服装事实占主导；允许段末 1 句 palette/mood。**官方单帧开场白**（One photograph of one woman… / No collage, no flat lay）和旧开场白（Please generate female models and the matching clothing for them. / 请生成女模…）**不计罚、不升档**，评测管线通常会预先剥离。**硬下限**：正文仍有 Look 编号或标题、拼贴、平铺、产品图、第二机位，或离身货品句（if removed、its own garment、complete the look、finish the look）时，本惩罚 ≥ 0.75，禁止打 0、0.25、0.5；两类同时在，或明确要求 collage/flat lay/product shot，打 1.0。**≥0.5** 非成像内容占相当比重：(1) 模特姿态/走位/心理（stance should / forward step / poised / 模特应…）；(2) 同一可见事实多处重复无新增像素；(3) 抽象场域/身份/奢华评论明显多于可见锚点。**≥0.75**：上述叠加且可见事实稀疏。",
            },
            "consistency_penalty": {
                "allowed_scores": [0.0, 0.25, 0.5, 0.75, 1.0],
                "judge_guidance": "Trunk left-right identity splits and same-element contradictions must be scored while the conflicting facts remain. One zone (sleeve, leg, or shoe) still split: consistency_penalty ≥ 0.75, and 0, 0.25, and 0.5 are forbidden. Two or more zones: 1.0. Same garment with two incompatible necklines, sleeve states, lengths, closures, or shell materials, including 'available in two styles': ≥ 0.75; two or more conflicting bindings: 1.0. Fluent or Chinese wording does not justify 0. Score 0 only when one binding remains. Do not raise for mild accessory-only differences when the trunk is already one identity.",
            },
            "coordination_penalty": {
                "allowed_scores": [0.0, 0.25, 0.5, 0.75, 1.0],
                "judge_guidance": "Trunk left-right identity splits use the same floor as consistency_penalty: one zone ≥ 0.75 (0, 0.25, and 0.5 are forbidden), two or more zones = 1.0. Garments from a different theme or concept that are still in the text (kept as an inner layer, a second subject, or a cohesive contrast) mean coordination_penalty ≥ 0.75 until they are gone. Fluent or Chinese wording does not justify 0. Do not raise for mild accessory-only asymmetry when the trunk is already one identity.",
            },
            "rationality_penalty": {
                "allowed_scores": [0.0, 0.25, 0.5, 0.75, 1.0],
                "judge_guidance": "Raise this when the text describes garment facts that violate objective physical logic, realistic material conditions, or basic wearing feasibility. Also when leg harnesses/straps are described as tightly binding over extremely loose pant legs with no plausible routing or anchor points stated as ordinary wear facts.",
            },
            "formula_template_penalty": {
                "allowed_scores": [0.0, 0.25, 0.5, 0.75, 1.0],
                "judge_guidance": "Content-only formula penalty—never for section/bullet layout alone. Weigh: cruise/resort interchangeable trunk, brand-symbol-only, abstract mood/identity dilution vs visible craft facts, swappable-by-material-word. Concrete trim/appliqué/pattern/proportion anchors → 0~0.25 even if cruise trunk is mild.",
            },
        }

    def _build_quality_penalty_system_prompt(self) -> str:
        penalty_registry = self._get_penalty_registry()
        rules = [
            f"{idx}. {penalty_key} must be one of {cfg.get('allowed_scores', [0.0])}"
            for idx, (penalty_key, cfg) in enumerate(penalty_registry.items(), start=1)
        ]
        guidance_lines = [
            f"- {penalty_key}: {cfg.get('judge_guidance', '')}"
            for penalty_key, cfg in penalty_registry.items()
            if cfg.get("judge_guidance")
        ]
        return (
            "You are Design_text_Evaluator.\n\n"
            "Your task is to judge local quality penalties for a fashion text_description.\n\n"
            "Penalty rules:\n"
            + "\n".join(rules)
            + "\n"
            + f"{len(rules) + 1}. Every penalty item must provide local evidence from the text whenever possible.\n"
            + f"{len(rules) + 2}. Output strict JSON only.\n\n"
            + "Penalty guidance:\n"
            + "\n".join(guidance_lines)
            + "\n\nReturn format:\n"
            + "{\n"
            + '  "items": [\n'
            + "    {\n"
            + '      "penalty_key": "generation_content_penalty",\n'
            + '      "score": 0.25,\n'
            + '      "evidence": ["short evidence phrase 1", "short evidence phrase 2"],\n'
            + '      "reason": "short explanation"\n'
            + "    }\n"
            + "  ]\n"
            + "}\n"
        )

    def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        return self._request_completion(
            system_prompt=system_prompt,
            user_content=user_prompt,
            response_format=None,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    def generate_multimodal(
        self,
        system_prompt: str,
        user_content: List[Dict[str, Any]],
        *,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        OpenAI-style chat with multimodal ``user`` message: ``content`` is a list of
        ``{"type":"text","text":...}`` and ``{"type":"image_url","image_url":{"url":...}}`` parts.
        """
        return self._request_completion(
            system_prompt=system_prompt,
            user_content=user_content,
            response_format=response_format,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    def _build_user_prompt(
        self,
        text_description: str,
        module_name: str,
        metric_specs: List[Dict],
        axis_name: str,
        *,
        extra_guidance: str = "",
    ) -> str:
        serialized_specs = json.dumps(metric_specs, ensure_ascii=False, indent=2)
        if axis_name == "quality_score":
            if module_name == "DesignMerit":
                scale_rules = DESIGN_MERIT_JUDGE_GUIDE + "\n"
            else:
                scale_rules = (
                    "Scoring scale for each quality metric:\n"
                    "- Use the metric-specific five-level rubric in quality_scoring_rubric as the first reference.\n"
                    "- Also obey explicit score caps in each metric's rule field when present.\n"
                    "- 1.0 = near-perfect for that metric and quality dimension\n"
                    "- 0.75 = strong with only minor issues for that metric\n"
                    "- 0.5 = partially good but with clear room for improvement for that metric\n"
                    "- 0.25 = weak or inefficient for that metric\n"
                    "- 0.0 = missing, wrong, unusable, or seriously poor for that metric\n"
                    "Do not give 1.0 unless the metric is satisfied at a near-perfect prompt level under its own rubric.\n"
                )
            if module_name == "InformationDensity":
                scale_rules += (
                    "\nInformationDensity — facts per clause, not length:\n"
                    "- 1.0 only when identifying anchors remain (craft path, recognizable surface, layering) and almost every sentence adds a new imageable fact.\n"
                    "- Do not reward brevity. A short text that drops those anchors stays at most 0.5.\n"
                    "- Do not penalize length while new imageable facts are still being added.\n"
                    "- Restating the same fact, or a near-copy of the source, is not a new fact.\n"
                    "- One closing palette/mood sentence does not lower the score.\n"
                    "- Two identities or a same-element contradiction still in the text: at most 0.5.\n"
                )
            elif module_name in ("ConcisenessAndDensity", "GenerationReadiness", "StructuralClarity"):
                scale_rules += (
                    f"\n{module_name} module — T2I content priority (ignore layout):\n"
                    "- High: sentences map to visible pixels (garment form, material, color, trim path, layering, accessory placement).\n"
                    "- generation_readiness stays at most 0.25 while a same-element contradiction or a second theme's garments remain. Specific visible facts do not raise it.\n"
                    "- generation_readiness and visibility_priority stay at most 0.25 while the paragraph still has a Look number, a collage, a flat lay, a product shot, a second view, or an off-body catalog clause (if removed, its own garment, complete the look). The official single-frame first line does not count.\n"
                    "- Low: model stance/pose, abstract salon/promenade/identity essay dominating over visible facts.\n"
                    "- IGNORE the official single-frame line and the old T2I preamble: Please generate female models and the matching clothing for them.\n"
                    "- Do NOT penalize numbered sections or bullet lists if content is imaging-rich and semantically ordered.\n"
                )
            elif module_name == "ConceptBonus":
                scale_rules += (
                    "\nConceptBonus module — optional bonus only; do not inflate main quality scores.\n"
                    "- Infer applicability from text; compact captions may have zero applicable bonus metrics.\n"
                )
        else:
            scale_rules = (
                "Scoring scale for each metric:\n"
                "- score must be 1 if the applicable metric is clearly covered by the text\n"
                "- score must be 0 if the applicable metric is not clearly covered\n"
            )
        if module_name == "DesignMerit":
            requirements = (
                "Requirements:\n"
                "1. Judge applicability first; if applicable, score 1.0 / 0.75 / 0.5 / 0.25 / 0.0.\n"
                "2. Semantic judging, not keyword matching. Return JSON only.\n\n"
            )
        else:
            requirements = (
                "Requirements:\n"
                "1. Judge applicability first.\n"
                "2. If applicable=true, return a numeric score.\n"
                "3. Scoring must be semantic, not surface keyword matching.\n"
                "4. evidence should quote short phrases from the original text when possible.\n"
                "5. For quality metrics, be strict about prompt usefulness, precision, structure, concision, spatial imageability, and internal visual coherence.\n"
                "6. Return JSON only.\n\n"
            )
        if any(isinstance(spec, dict) and spec.get("few_shot") for spec in metric_specs):
            scale_rules += (
                "\nFew-shot template:\n"
                "- Items under few_shot are calibration examples. Do not score them as the text under evaluation.\n"
                "- Match the example with the same pattern, then use that score.\n"
                "- Do not score above an example that shows the same defect.\n"
                "- A shorter paragraph is not by itself a higher score.\n"
            )
        extra = f"{extra_guidance.strip()}\n\n" if extra_guidance and extra_guidance.strip() else ""
        return (
            f"Text to evaluate:\n{text_description}\n\n"
            f"Current module: {module_name}\n\n"
            f"Axis: {axis_name}\n\n"
            f"Metrics to judge:\n{serialized_specs}\n\n"
            f"{requirements}"
            f"{scale_rules}"
            f"{extra}"
        )

    def _generate(self, system_prompt: str, user_prompt: str) -> str:
        return self._request_completion(
            system_prompt=system_prompt,
            user_content=user_prompt,
            response_format={"type": "json_object"},
            repetition_penalty=JUDGE_REPETITION_PENALTY,
        )

    def _request_completion(
        self,
        system_prompt: str,
        user_content: Union[str, List[Dict[str, Any]]],
        response_format: Optional[Dict[str, Any]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        seed: Optional[int] = None,
        repetition_penalty: Optional[float] = None,
    ) -> str:
        if isinstance(user_content, str):
            user_message: Dict[str, Any] = {"role": "user", "content": user_content}
        else:
            user_message = {"role": "user", "content": user_content}
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                user_message,
            ],
            "temperature": self.temperature if temperature is None else temperature,
            "top_p": self.top_p if top_p is None else top_p,
            "max_completion_tokens": self.max_tokens if max_tokens is None else max_tokens,
        }
        if seed is not None:
            payload["seed"] = seed
        if repetition_penalty is not None:
            payload["repetition_penalty"] = repetition_penalty
        if response_format is not None:
            payload["response_format"] = response_format

        max_retries = 3
        last_error: str = ""
        for attempt in range(max_retries + 1):
            errors = []
            for url in self._candidate_chat_urls():
                request = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}",
                        "User-Agent": "Mozilla/5.0",
                        "Accept": "application/json",
                    },
                    method="POST",
                )
                try:
                    ssl_context = None
                    if not self.verify_ssl:
                        ssl_context = ssl._create_unverified_context()
                    with urllib.request.urlopen(request, timeout=self.timeout, context=ssl_context) as response:
                        body = response.read().decode("utf-8")
                    parsed = json.loads(body)
                    return parsed["choices"][0]["message"]["content"]
                except urllib.error.HTTPError as exc:
                    retry_after = exc.headers.get("Retry-After")
                    delay: Optional[float] = None
                    if retry_after:
                        try:
                            delay = float(retry_after)
                        except ValueError:
                            pass
                    if exc.code == 401 or exc.code == 403:
                        error_body = exc.read().decode("utf-8", errors="replace")
                        self.logger.error("API auth error %s — aborting retries: %s", exc.code, error_body)
                        raise RuntimeError(f"API authentication error ({exc.code}), aborting: {error_body}") from exc
                    if exc.code == 429:
                        if delay is None:
                            delay = (2 ** attempt) * 1.5
                        self.logger.warning("Rate-limited (429) on %s, waiting %.1fs before retry %d/%d",
                                            url, delay, attempt + 1, max_retries + 1)
                        if attempt < max_retries:
                            import time
                            time.sleep(delay)
                            continue
                        else:
                            errors.append(f"{url} -> 429 after all retries")
                            continue
                    if 500 <= exc.code < 600:
                        error_body = exc.read().decode("utf-8", errors="replace")
                        errors.append(f"{url} -> HTTP {exc.code}: {error_body}")
                        if attempt < max_retries:
                            continue
                        else:
                            continue
                    error_body = exc.read().decode("utf-8", errors="replace")
                    errors.append(f"{url} -> HTTP {exc.code}: {error_body}")
                except urllib.error.URLError as exc:
                    errors.append(f"{url} -> URLError: {exc}")
                except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
                    errors.append(f"{url} -> unexpected response format: {exc}")

            last_error = "\n".join(errors)
            if errors and all(is_connection_failure(item) for item in errors):
                raise JudgeConnectionError(
                    f"Judge API connection failed:\n{last_error}"
                )
            if attempt < max_retries:
                backoff = (2 ** attempt) * 2.0
                self.logger.warning("All URLs failed on attempt %d/%d, backing off %.1fs: %s",
                                    attempt + 1, max_retries + 1, backoff, last_error)
                import time
                time.sleep(backoff)
            else:
                break

        if is_connection_failure(last_error):
            raise JudgeConnectionError(
                f"Judge API connection failed after {max_retries + 1} attempt(s):\n{last_error}"
            )
        raise RuntimeError(
            f"Judge API request failed after {max_retries + 1} attempt(s):\n{last_error}"
        )

    def _candidate_chat_urls(self) -> List[str]:
        base = self.api_base.rstrip("/")
        parsed = urlparse(base)
        path = parsed.path.rstrip("/")
        urls = [f"{base}/chat/completions"]
        if path == "":
            urls.append(f"{base}/v1/chat/completions")
        elif path != "/v1" and not path.endswith("/v1"):
            urls.append(f"{base}/v1/chat/completions")
        deduped = []
        for url in urls:
            if url not in deduped:
                deduped.append(url)
        return deduped

    def _parse_json(self, raw_output: str) -> Dict:
        cleaned = self._clean_output(raw_output)
        collapsed = _collapse_repeated_json_strings(cleaned)
        try:
            return json.loads(self._extract_first_json_object(collapsed))
        except (ValueError, json.JSONDecodeError):
            repaired = _close_truncated_json(collapsed)
            try:
                return json.loads(repaired)
            except json.JSONDecodeError as exc:
                snippet = collapsed[:400]
                raise ValueError(f"LLM judge did not return valid JSON:\n{snippet}") from exc

    def _parse_json_with_retry(
        self,
        raw_factory,
        *,
        label: str,
        attempts: int = JUDGE_JSON_PARSE_ATTEMPTS,
    ) -> Dict:
        """Parse judge JSON; retry then fall back to {} so one truncated reply cannot abort evaluate."""
        last_exc: Optional[BaseException] = None
        n = max(1, int(attempts))
        for i in range(n):
            raw = raw_factory()
            try:
                return self._parse_json(raw)
            except ValueError as exc:
                last_exc = exc
                self.logger.warning(
                    "%s JSON parse failed (%s/%s): %s",
                    label,
                    i + 1,
                    n,
                    str(exc).split("\n", 1)[0][:240],
                )
        self.logger.warning(
            "%s giving up after %s parse error(s); treating output as empty",
            label,
            n,
        )
        if last_exc is not None:
            self.logger.debug("%s last parse error", label, exc_info=last_exc)
        return {}

    def _clean_output(self, text: str) -> str:
        text = re.sub(r"<think>[\s\S]*?</think>", "", text).strip()
        answer_match = re.search(r"<answer>([\s\S]*?)</answer>", text)
        if answer_match:
            text = answer_match.group(1).strip()
        text = re.sub(r"^```json\s*", "", text)
        text = re.sub(r"^```\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        return text.strip()

    def _extract_first_json_object(self, text: str) -> str:
        start = text.find("{")
        if start == -1:
            raise ValueError(f"LLM judge returned no JSON:\n{text}")
        depth = 0
        in_string = False
        escape = False
        for idx in range(start, len(text)):
            ch = text[idx]
            if in_string:
                if escape:
                    escape = False
                elif ch == "\\":
                    escape = True
                elif ch == '"':
                    in_string = False
                continue
            if ch == '"':
                in_string = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return text[start : idx + 1]
        raise ValueError(f"LLM judge returned incomplete JSON:\n{text}")

    def _normalize_module_result(self, module_name: str, metric_specs: List[Dict], parsed: Dict, axis_name: str) -> Dict:
        requested_metrics = {item["metric"] for item in metric_specs}
        normalized = {"module": module_name, "results": []}
        result_map = {}
        parsed = parsed if isinstance(parsed, dict) else {}
        for item in coerce_judge_result_items(parsed.get("results")):
            metric = item.get("metric")
            if metric in requested_metrics:
                result_map[metric] = item

        for spec in metric_specs:
            metric_name = spec["metric"]
            item = result_map.get(metric_name, {})
            applicable = bool(item.get("applicable", False))
            score_value = item.get("score", None if not applicable else 0)
            if applicable:
                score_value = self._normalize_score(score_value, axis_name)
                hit = 1 if score_value >= (QUALITY_FULL_HIT_THRESHOLD if axis_name == "quality_score" else 1.0) else 0
            else:
                score_value = None
                hit = None
            evidence = item.get("evidence", [])
            if evidence is None:
                evidence = []
            if isinstance(evidence, str):
                evidence = [evidence]
            reason = item.get("reason", "LLM returned no reason") or "LLM returned no reason"
            normalized["results"].append(
                {
                    "metric": metric_name,
                    "applicable": applicable,
                    "score": score_value,
                    "hit": hit,
                    "evidence": evidence[:6],
                    "reason": reason,
                }
            )
        return normalized

    def _normalize_score(self, raw_score: object, axis_name: str) -> float:
        try:
            numeric = float(raw_score)
        except (TypeError, ValueError):
            numeric = 0.0
        if axis_name == "quality_score":
            return min(QUALITY_ALLOWED_SCORES, key=lambda item: abs(item - numeric))
        return 1.0 if numeric >= 0.5 else 0.0

    def _normalize_quality_penalties(self, parsed: Dict) -> Dict:
        penalty_registry = self._get_penalty_registry()
        penalty_options = {
            key: cfg.get("allowed_scores", [0.0]) for key, cfg in penalty_registry.items()
        }
        raw_items = parsed.get("items", []) if isinstance(parsed, dict) else []
        items = raw_items if isinstance(raw_items, list) else []
        item_map = {}
        for item in items:
            if not isinstance(item, dict):
                continue
            penalty_key = item.get("penalty_key")
            if penalty_key in penalty_options:
                item_map[penalty_key] = item

        normalized = {"items": {}, "reasons": {}}
        for key, allowed in penalty_options.items():
            item = item_map.get(key, {})
            try:
                raw_value = float(item.get("score", 0.0))
            except (TypeError, ValueError):
                raw_value = 0.0
            normalized_score = min(allowed, key=lambda option: abs(option - raw_value))
            evidence = item.get("evidence", [])
            if evidence is None:
                evidence = []
            if isinstance(evidence, str):
                evidence = [evidence]
            reason = item.get("reason", "") or ""
            normalized[key] = normalized_score
            normalized["reasons"][key] = reason
            normalized["items"][key] = {
                "score": normalized_score,
                "evidence": evidence[:6],
                "reason": reason,
            }
        penalty_keys = list(penalty_options.keys())
        penalty_sum = sum(normalized[key] for key in penalty_keys)
        # 各 penalty 为 0~1 五档时，求和会远大于 quality 轴（质量分为各指标均值）；与 quality 轴对齐采用算术平均作为综合扣分
        normalized["total_penalty"] = round(penalty_sum / len(penalty_keys), 4) if penalty_keys else 0.0
        return normalized


class DesignTextEvaluator:
    """Evaluate fashion text descriptions with an API-based LLM judge."""

    def __init__(
        self,
        spec_path: Optional[str] = None,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.0,
        top_p: float = 1.0,
        max_new_tokens: int = 1600,
        timeout: int = 120,
        verify_ssl: Optional[bool] = None,
        rewriter_temperature: Optional[float] = None,
    ) -> None:
        del rewriter_temperature  # 保留参数仅为向后兼容；本模块不再进行多轮改写优化。
        if not logging.getLogger(__name__).handlers:
            logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        base_dir = Path(__file__).resolve().parent
        self.base_dir = base_dir
        self.spec_path = Path(spec_path) if spec_path else base_dir / "fashion_prompt_optimizer_spec.json"
        self.optimizer_prompt_path = base_dir / "fashion_sys_prompt.txt"
        with self.spec_path.open("r", encoding="utf-8") as f:
            self.spec = json.load(f)
        self.penalty_registry = self.spec.get("penalty_registry", {})
        self.optimizer_system_prompt = self.optimizer_prompt_path.read_text(encoding="utf-8").strip()
        _grpo_ev = grpo_design_text_evaluator_config()
        api_key = api_key or _yaml_opt_str(_grpo_ev.get("api-key"))
        api_base = api_base or _yaml_opt_str(_grpo_ev.get("api-base"))
        model = model or _yaml_opt_str(_grpo_ev.get("model"))
        if _grpo_ev.get("max-tokens") is not None:
            max_new_tokens = int(_grpo_ev["max-tokens"])
        if _grpo_ev.get("timeout") is not None:
            timeout = int(_grpo_ev["timeout"])
        if "temperature" in _grpo_ev:
            temperature = float(_grpo_ev["temperature"])
        if verify_ssl is None and "verify-ssl" in _grpo_ev:
            verify_ssl = bool(_grpo_ev["verify-ssl"])
        _llm_cfg = self.spec.get("llm") or {}
        _spec_default_model = str(_llm_cfg.get("default_model", "gpt-5.4-mini"))
        _resolved_model = (
            model
            or os.environ.get("AI_API_MODEL")
            or os.environ.get("AI_MODEL")
            or _yaml_opt_str(FASHION_CONFIG.get("llm-backend"))
            or _spec_default_model
        )

        self.judge = ApiLLMJudge(
            api_key=api_key,
            api_base=api_base,
            model=_resolved_model,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_new_tokens,
            timeout=timeout,
            verify_ssl=verify_ssl,
        )
        self.judge.penalty_registry = self.penalty_registry

    def _resolve_optimization_gate_config(self, gate_config: Optional[Dict[str, Any]] = None) -> Dict[str, float]:
        spec_gates = self.spec.get("optimization_gates", {}) or {}
        score_gate_min = float(spec_gates.get("score_gate_min", 0.8))
        penalty_gate_max = float(spec_gates.get("penalty_gate_max", 0.25))
        if gate_config:
            if gate_config.get("score_gate_min") is not None:
                score_gate_min = float(gate_config["score_gate_min"])
            if gate_config.get("penalty_gate_max") is not None:
                penalty_gate_max = float(gate_config["penalty_gate_max"])
        return {"score_gate_min": score_gate_min, "penalty_gate_max": penalty_gate_max}

    def _compute_gates(
        self,
        *,
        score_gate_value: float,
        coverage_axis_score: float,
        quality_effective: float,
        weights: Dict[str, float],
        total_cap: float,
        total_penalty: float,
        gate_config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        cfg = self._resolve_optimization_gate_config(gate_config)
        score_gate_value = round(min(float(score_gate_value), float(total_cap)), 4)
        tp = round(float(total_penalty), 4)
        score_passed = score_gate_value >= cfg["score_gate_min"] - 1e-9
        penalty_passed = tp <= cfg["penalty_gate_max"] + 1e-9
        return {
            "score_gate": {
                "name": "score_gate",
                "description": "内容主分 s_fp_base（quality 用 weighted base_score；不含 penalty，长度不进总分）",
                "value": score_gate_value,
                "threshold": cfg["score_gate_min"],
                "passed": score_passed,
                "weights": dict(weights),
                "components": {
                    "coverage_axis_score": round(float(coverage_axis_score), 4),
                    "quality_effective": round(float(quality_effective), 4),
                },
                "total_cap_applied": round(float(total_cap), 4),
            },
            "penalty_gate": {
                "name": "penalty_gate",
                "description": "仅依据 penalties.total_penalty（各 penalty 分值的算术平均）；不参与 S_fp / R_content 扣减",
                "total_penalty": tp,
                "threshold": cfg["penalty_gate_max"],
                "passed": penalty_passed,
            },
            "both_passed": score_passed and penalty_passed,
        }

    @staticmethod
    def _gates_both_pass(result: Dict) -> bool:
        gates = result.get("gates") or {}
        return bool(gates.get("score_gate", {}).get("passed")) and bool(gates.get("penalty_gate", {}).get("passed"))

    @staticmethod
    def _gates_passed_count(result: Dict) -> int:
        gates = result.get("gates") or {}
        n = 0
        if gates.get("score_gate", {}).get("passed"):
            n += 1
        if gates.get("penalty_gate", {}).get("passed"):
            n += 1
        return n

    def evaluate_text(
        self,
        text_description: str,
        source_name: str = "inline_text",
        gate_config: Optional[Dict[str, Any]] = None,
    ) -> Dict:
        raw_text = (text_description or "").strip()
        eval_prose = strip_eval_boilerplate(raw_text)
        text_for_judge = eval_prose if len(eval_prose) >= self.MIN_VALIDATED_TEXT_LENGTH else raw_text

        metric_results = {}
        raw_module_outputs = {}

        for module_group in ("coverage_modules", "quality_modules", "bonus_modules"):
            axis_name = {
                "coverage_modules": "coverage_score",
                "quality_modules": "quality_score",
                "bonus_modules": "bonus_score",
            }[module_group]
            for module in self.spec[module_group]:
                metric_specs = self._build_metric_specs(module["metrics"])
                module_output = self.judge.judge_module(
                    text_for_judge,
                    module["name"],
                    metric_specs,
                    axis_name,
                )
                if module["name"] == "DesignMerit":
                    # Use raw text so series titles/shared wardrobe lines are not stripped first.
                    module_output = apply_design_merit_auxiliary_caps(raw_text, module_output)
                raw_module_outputs[module["name"]] = module_output
                for result in module_output["results"]:
                    metric_name = result["metric"]
                    metric_cfg = self.spec["metric_registry"][metric_name]
                    quality_dimension_key = metric_cfg.get("quality_dimension")
                    quality_dimension_cfg = self.spec.get("quality_dimension_registry", {}).get(quality_dimension_key, {})
                    metric_results[metric_name] = {
                        "axis": metric_cfg["axis"],
                        "rule": metric_cfg["rule"],
                        "source_keypoints": metric_cfg["source_keypoints"],
                        "applicability_code": metric_cfg["applicability"],
                        "applicability_hint": APPLICABILITY_HINTS.get(
                            metric_cfg["applicability"],
                            f"Applicability code: {metric_cfg['applicability']}",
                        ),
                        "applicable": result["applicable"],
                        "score_value": result["score"],
                        "hit": result["hit"],
                        "matched_terms": result["evidence"],
                        "reason": result["reason"],
                        "quality_dimension": quality_dimension_key,
                        "quality_dimension_zh": quality_dimension_cfg.get("zh_name"),
                    }

        quality_penalties = self.judge.judge_quality_penalties(text_for_judge)
        conflicts = detect_consistency_conflicts(raw_text)
        layout = detect_layout_board(raw_text)
        quality_penalties = apply_consistency_penalty_floor(quality_penalties, conflicts)
        quality_penalties = apply_layout_board_penalty_floor(quality_penalties, layout)
        apply_conflict_quality_caps(metric_results, conflicts)
        apply_layout_board_quality_caps(metric_results, layout)
        module_scores = self._aggregate_module_scores(metric_results)
        axis_scores = self._aggregate_axis_scores(metric_results)
        quality_axis_score = axis_scores["quality_score"]["score"]
        quality_weighted = self._aggregate_weighted_quality_score(module_scores)

        char_len = len(eval_prose) if eval_prose else len(raw_text)

        quality_cap = 1.0
        if module_scores.get("BindingAccuracy", {}).get("score", 1.0) < 0.5:
            quality_cap = min(quality_cap, 0.6)
        addition_cap = conflict_quality_cap(conflicts)
        if addition_cap is not None:
            quality_cap = min(quality_cap, addition_cap)
        if layout.get("active"):
            quality_cap = min(quality_cap, CONFLICT_QUALITY_CAP)
        # penalties 不参与 S_fp / R_content；仅用于 penalty_gate（见 spec score_composition）。
        quality_effective = round(min(quality_weighted, quality_cap), 4)

        axes_cfg = self.spec.get("score_axes") or {}
        weights = {
            "coverage": float((axes_cfg.get("coverage_score") or {}).get("weight", 0.30)),
            "quality": float((axes_cfg.get("quality_score") or {}).get("weight", 0.70)),
        }
        coverage_score = axis_scores["coverage_score"]["score"]
        s_fp_base = round(
            coverage_score * weights["coverage"] + quality_effective * weights["quality"],
            4,
        )
        total_cap = 1.0

        rcfg = self.spec.get("r_content_for_rl") or {}
        hold_cfg = rcfg.get("holdout_regression") or {}
        length_disentangle = apply_length_disentangle(s_fp_base, char_len, hold_cfg)
        fashion_prompt_score = (
            length_disentangle["adjusted_score"]
            if length_disentangle.get("applied")
            else s_fp_base
        )
        total_defined_metrics = len(self.spec["metric_registry"])
        total_applicable_metrics = sum(1 for item in metric_results.values() if item["applicable"])
        total_hit_metrics = sum(1 for item in metric_results.values() if item["applicable"] and item["hit"] == 1)
        score_band = self._score_band(fashion_prompt_score)
        skipped_metrics = self._build_skipped_metrics(metric_results)

        gates = self._compute_gates(
            score_gate_value=fashion_prompt_score,
            coverage_axis_score=coverage_score,
            quality_effective=quality_effective,
            weights=weights,
            total_cap=total_cap,
            total_penalty=quality_penalties["total_penalty"],
            gate_config=gate_config,
        )

        out = {
            "name": self.spec["name"],
            "version": self.spec["version"],
            "source_name": source_name,
            "input_type": self.spec["input_type"],
            "judge_backend": "openai_compatible_api",
            "judge_model": self.judge.model,
            "judge_api_base": self.judge.api_base,
            "text_description": raw_text,
            "eval_prose": eval_prose,
            "total_score": fashion_prompt_score,
            "gates": gates,
            "score_band": score_band,
            "metric_totals": {
                "total_defined_metrics": total_defined_metrics,
                "total_applicable_metrics": total_applicable_metrics,
                "total_hit_metrics": total_hit_metrics,
                "total_skipped_metrics": len(skipped_metrics),
            },
            "skipped_metrics": skipped_metrics,
            "scores": {
                "coverage_score": axis_scores["coverage_score"],
                "quality_score": {
                    **axis_scores["quality_score"],
                    "base_score": quality_weighted,
                    "axis_score_unweighted": quality_axis_score,
                    "penalized_score": quality_effective,
                    "penalties": quality_penalties,
                    "cap": quality_cap,
                },
                "bonus_score": axis_scores["bonus_score"],
                "fashion_prompt_score": fashion_prompt_score,
                "s_fp_base": s_fp_base,
                "consistency_conflicts": conflicts,
                "length_disentangle": length_disentangle,
                "weights": weights,
                "total_cap": total_cap,
                "module_scores": module_scores,
            },
            "diagnosis": self._build_diagnosis(metric_results),
            "metric_results": metric_results,
            "context_summary": {
                "evaluated_modules": list(raw_module_outputs.keys()),
                "semantic_judging_enabled": True,
                "quality_penalties_enabled": True,
                "skipped_metrics_enabled": True,
                "optimization_gates_enabled": True,
            },
            "raw_module_outputs": raw_module_outputs,
        }
        rcfg = dict(rcfg)
        rcfg["length_already_applied"] = bool(length_disentangle.get("applied"))
        out["r_content"] = build_r_content_payload(
            eval_prose or raw_text,
            s_fp_base if not length_disentangle.get("applied") else fashion_prompt_score,
            quality_penalties["total_penalty"],
            rcfg,
            z_len=None,
        )
        out["score_formula"] = build_score_formula_breakdown(
            spec=self.spec,
            coverage_score=coverage_score,
            quality_axis_unweighted=quality_axis_score,
            quality_weighted=quality_weighted,
            quality_effective=quality_effective,
            quality_cap=quality_cap,
            total_penalty=float(quality_penalties["total_penalty"] or 0.0),
            weights=weights,
            s_fp_base=s_fp_base,
            total_cap=total_cap,
            char_len=char_len,
            length_disentangle=length_disentangle,
            fashion_prompt_score=fashion_prompt_score,
            r_content=out["r_content"],
            module_scores=module_scores,
        )
        return out

    def evaluate_txt_file(
        self,
        txt_path: str | Path,
        *,
        gate_config: Optional[Dict[str, float]] = None,
    ) -> Dict:
        path = Path(txt_path)
        with path.open("r", encoding="utf-8") as f:
            text_description = f.read().strip()
        return self.evaluate_text(
            text_description,
            source_name=path.name,
            gate_config=gate_config,
        )

    def evaluate_txt_directory(self, directory_path: str | Path) -> Dict[str, Dict]:
        directory = Path(directory_path)
        results = {}
        for txt_file in sorted(directory.glob("*.txt")):
            results[txt_file.name] = self.evaluate_txt_file(txt_file)
        return results

    MIN_VALIDATED_TEXT_LENGTH = 20

    CORE_GARMENT_KEYWORDS = [
        # Outerwear and one-piece. Substring match, so plurals and compounds count.
        "coat", "jacket", "blazer", "suit", "trench", "parka", "anorak", "bomber",
        "blouson", "gilet", "cape", "cloak", "robe", "gown", "dress", "frock",
        "jumpsuit", "playsuit", "romper", "bodysuit", "overalls", "dungaree",
        "cheongsam", "qipao",
        # Tops, including knit as the garment name.
        "shirt", "blouse", "top", "sweater", "cardigan", "pullover", "jumper",
        "knit", "knitwear", "hoodie", "sweatshirt", "tunic", "vest", "bodice",
        "bustier", "corset", "camisole", "halter", "polo",
        # Bottoms.
        "skirt", "trousers", "pants", "pant", "jeans", "shorts", "culotte",
        "legging", "palazzo", "kilt", "mini",
        # Footwear. These name the worn shoe, not a second garment system.
        "shoe", "pump", "mule", "sandal", "boot", "heel", "loafer", "oxford",
        "sneaker", "trainer", "stiletto", "slingback", "espadrille", "brogue",
        # Chinese category names and near-synonyms.
        "西装", "外套", "大衣", "风衣", "夹克", "衬衫", "连衣裙", "裙子", "裤",
        "毛衣", "毛衫", "开衫", "针织", "卫衣", "运动服", "套装", "旗袍", "马甲",
        "斗篷", "披肩", "上衣", "吊带", "背心", "罩衫", "短裙", "半裙", "长裙",
        "短裤", "西裤", "礼服", "连体", "皮鞋", "高跟", "凉鞋", "靴子", "短靴",
        "穆勒", "运动鞋",
    ]

    def _validate_optimized_text(self, optimized_text: str, original_text: str) -> str:
        """
        Sanity-check rewriter output: length floor, garbled chars, and core garment presence.
        Returns the validated (or fallback) text.
        """
        text = (optimized_text or "").strip()
        if not text:
            self.logger.warning("Rewriter returned empty output; falling back to original.")
            return original_text

        if len(text) < self.MIN_VALIDATED_TEXT_LENGTH:
            self.logger.warning(
                "Rewriter output too short (%d chars, min %d); falling back to original.",
                len(text), self.MIN_VALIDATED_TEXT_LENGTH,
            )
            return original_text

        # Check for garbled/machine characters (very low-ratio of meaningful characters).
        meaningful_chars = sum(1 for c in text if c.isalnum() or c in " .,;:!?-'\"（）《》「」‘’“”–—…")
        if meaningful_chars / len(text) < 0.6:
            self.logger.warning(
                "Rewriter output looks garbled (%.0f%% meaningful chars); falling back to original.",
                meaningful_chars / len(text) * 100,
            )
            return original_text

        # Core garment presence check: at least one keyword from the catalog must appear.
        text_lower = text.lower()
        found_core = any(kw.lower() in text_lower for kw in self.CORE_GARMENT_KEYWORDS)
        if not found_core:
            self.logger.warning(
                "Rewriter output contains no core garment keyword; falling back to original."
            )
            return original_text

        return text

    def _normalize_optimized_text(self, text: str) -> str:
        cleaned = self.judge._clean_output(text)
        cleaned = re.sub(r"\s*\n+\s*", " ", cleaned).strip()
        return cleaned

    def _build_metric_specs(self, metric_names: List[str]) -> List[Dict]:
        metric_specs = []
        for metric_name in metric_names:
            metric_cfg = self.spec["metric_registry"][metric_name]
            metric_spec = {
                "metric": metric_name,
                "axis": metric_cfg["axis"],
                "rule": metric_cfg["rule"],
                "source_keypoints": metric_cfg["source_keypoints"],
                "applicability_code": metric_cfg["applicability"],
                "applicability_hint": APPLICABILITY_HINTS.get(
                    metric_cfg["applicability"],
                    f"Applicability code: {metric_cfg['applicability']}",
                ),
            }
            if metric_cfg["axis"] == "quality_score":
                dimension_key = metric_cfg.get("quality_dimension")
                dimension_cfg = self.spec.get("quality_dimension_registry", {}).get(dimension_key, {})
                metric_spec.update(
                    {
                        "quality_dimension": dimension_key,
                        "quality_dimension_zh": dimension_cfg.get("zh_name", dimension_key),
                        "quality_dimension_description": dimension_cfg.get("description", ""),
                    }
                )
                # DesignMerit: module prompt only — dumping five-level rubric / soft_rules makes the 7B copy 0.75 lines.
                if dimension_key not in DESIGN_MERIT_DIMENSIONS:
                    metric_spec["quality_scoring_rubric"] = dimension_cfg.get("scoring_rubric", {})
                    soft_rules = dimension_cfg.get("soft_rules")
                    if soft_rules:
                        metric_spec["soft_rules"] = soft_rules
                    reference_corpus = dimension_cfg.get("reference_corpus")
                    if reference_corpus:
                        metric_spec["reference_corpus"] = reference_corpus
            few_shot = metric_cfg.get("few_shot")
            if few_shot:
                metric_spec["few_shot"] = few_shot
            metric_specs.append(metric_spec)
        return metric_specs

    def _aggregate_module_scores(self, metric_results: Dict) -> Dict:
        module_scores = {}
        for module_group in ("coverage_modules", "quality_modules", "bonus_modules"):
            for module in self.spec[module_group]:
                hits = 0
                applicable = 0
                score_sum = 0.0
                for metric_name in module["metrics"]:
                    result = metric_results[metric_name]
                    if result["applicable"]:
                        applicable += 1
                        hits += int(result["hit"])
                        score_sum += float(result["score_value"])
                module_scores[module["name"]] = {
                    "applicable_metrics": applicable,
                    "hit_metrics": hits,
                    "score_sum": round(score_sum, 4),
                    "score": round(score_sum / applicable, 4) if applicable else 0.0,
                }
        return module_scores

    def _aggregate_weighted_quality_score(self, module_scores: Dict) -> float:
        weights_cfg = self.spec.get("quality_module_weights") or {}
        default_weight = float((self.spec.get("score_composition") or {}).get("default_module_weight", 1.0))
        weighted_sum = 0.0
        weight_total = 0.0
        for module in self.spec.get("quality_modules") or []:
            name = module["name"]
            ms = module_scores.get(name) or {}
            if not ms.get("applicable_metrics"):
                continue
            w = float(weights_cfg.get(name, default_weight))
            weighted_sum += float(ms.get("score", 0.0)) * w
            weight_total += w
        if weight_total <= 0:
            return 0.0
        return round(weighted_sum / weight_total, 4)

    def _aggregate_axis_scores(self, metric_results: Dict) -> Dict:
        axis_scores = {}
        for axis_name in ("coverage_score", "quality_score", "bonus_score"):
            hits = 0
            applicable = 0
            score_sum = 0.0
            for result in metric_results.values():
                if result["axis"] == axis_name and result["applicable"]:
                    applicable += 1
                    hits += int(result["hit"])
                    score_sum += float(result["score_value"])
            axis_scores[axis_name] = {
                "applicable_metrics": applicable,
                "hit_metrics": hits,
                "score_sum": round(score_sum, 4),
                "score": round(score_sum / applicable, 4) if applicable else 0.0,
            }
        return axis_scores

    def _build_diagnosis(self, metric_results: Dict) -> Dict:
        missing_information = []
        quality_issues = []
        bonus_opportunities = []
        for metric_name, result in metric_results.items():
            if not result["applicable"] or result["hit"] is None:
                continue
            item = {
                "metric": metric_name,
                "rule": result["rule"],
                "score_value": result["score_value"],
                "matched_terms": result["matched_terms"],
                "reason": result["reason"],
            }
            if result["axis"] == "coverage_score" and result["score_value"] == 0:
                missing_information.append(item)
            elif result["axis"] == "quality_score" and float(result["score_value"]) < QUALITY_FULL_HIT_THRESHOLD:
                quality_issues.append(item)
            elif result["axis"] == "bonus_score" and float(result["score_value"]) < 1.0:
                bonus_opportunities.append(item)
        return {
            "missing_information": missing_information,
            "quality_issues": quality_issues,
            "bonus_opportunities": bonus_opportunities,
        }

    def _build_skipped_metrics(self, metric_results: Dict) -> List[Dict]:
        skipped = []
        for metric_name, result in metric_results.items():
            if result["applicable"]:
                continue
            skipped.append(
                {
                    "metric": metric_name,
                    "axis": result["axis"],
                    "rule": result["rule"],
                    "applicability_code": result["applicability_code"],
                    "applicability_hint": result["applicability_hint"],
                    "reason": result["reason"],
                }
            )
        return skipped

    def _score_band(self, score: float) -> str:
        for threshold, label in TOTAL_SCORE_BANDS:
            if score >= threshold:
                return label
        return "Poor"


def load_default_evaluator(
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
    model: Optional[str] = None,
    verify_ssl: Optional[bool] = None,
) -> DesignTextEvaluator:
    from ..local_llm import build_parallel_k_evaluator

    if api_key is None and api_base is None and model is None and verify_ssl is None:
        return build_parallel_k_evaluator()
    return DesignTextEvaluator(api_key=api_key, api_base=api_base, model=model, verify_ssl=verify_ssl)
