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
    "when_craft_or_embellishment_is_salient": "Only applicable when the text mentions or clearly implies craft, embellishment, trim, appliqué, braid, quilting, embroidery, deconstruction, patch decoration, or similar salient construction/detail—not mere generic hardware or finish words.",
}

QUALITY_ALLOWED_SCORES = [0.0, 0.25, 0.5, 0.75, 1.0]
QUALITY_FULL_HIT_THRESHOLD = 0.75
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
_SECTION_HEADER_RE = re.compile(r"^\s*\d+\.\s+The\s+", re.IGNORECASE)
_LOOK_TITLE_RE = re.compile(r"^Look\s+\d+\s*:", re.IGNORECASE)


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
        if _is_t2i_preamble(stripped):
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
5. evidence should quote short spans from the original text whenever possible.
6. When bilateral differences exist, distinguish trunk from accessories. Trunk = all clothing that defines the worn look: outerwear, inner/base tops (shirts, tees, knit base layers, dress bodices when described as a garment layer), bottoms, and footwear—inner and outer layers each count as trunk when described as separate garments. When the text explicitly describes them, trunk also includes outerwear/jacket/coat lining and trouser/pant inner lining or in-seam revealed lining as part of the same garment’s coherent structure (shell vs lining must read as one grammar unless clearly layered). On trunk garments, large left-right differences in style, material, or garment identity should score poorly unless clearly grounded in one coherent grammar; **stacking several** trunk-level left-right contrasts at once (e.g. sleeve presence mismatch + different pant-leg materials/identities + mismatched footwear families + gloved vs bare hand as extra trunk contrast) is especially hostile to image generation—penalize accordingly even if the text calls it “deconstructed.” Mild left-right differences on accessories alone (belt, gloves, jewelry, bag) should be scored leniently and must not drive the same strictness as trunk splits when all trunk garments read unified.
7. When spatial relations exist, judge whether layering, inside-outside, front-back, and attachment positions remain visually coherent and imageable.
8. For visibility priority, reward texts that emphasize visible, image-dominant details over hidden interior or low-visibility details.
9. For quality_score metrics, use the provided quality_dimension and quality_scoring_rubric as the primary grading standard, not only the generic scale.
10. For DesignMerit, score the LOOK's design idea, not specification completeness (coverage already does that). High: a non-substitutable visible move (craft type+path, unusual proportion, trunk combination that would collapse if one piece were swapped). Low: an interchangeable kit whose identity is brand hardware, setting/mood talk, or a theme sentence. Ignore layout and T2I preamble.
11. For ConcisenessAndDensity (visibility_priority), prioritize **visible, image-dominant garment facts** over hidden details, model pose/stance/psychology, and abstract field/identity commentary. The standard T2I preamble line ("Please generate female models and the matching clothing for them." or Chinese equivalent) is fixed boilerplate—ignore it; never penalize it.
12. For StructuralClarity and GenerationReadiness, judge whether garment information is semantically ordered and **directly usable for T2I**; do NOT lower scores solely because the text uses numbered sections or bullet lists if the underlying content is imaging-rich.
13. For coverage_score metrics, follow each metric's rule field strictly: when a rule requires compound coverage (e.g. construction_technique needs named craft plus approximate body/garment zone; bag or footwear need at least two of three listed facets when applicable; color_relationship_logic needs a color relationship such as dominance, contrast, or tonal layering—not merely listing hue names), hit=1 only if those facets are clearly satisfied in the text. For belt: applicable only when an actual belt/sash/waist-strap/harness accessory is present or described; structural waist emphasis from garment cut alone (defined waist, peplum, seaming, proportion) does not make belt applicable and must not be scored as a belt miss.
14. Output strict JSON only. Do not output markdown fences or extra commentary.

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
        raw_output = self._generate(self.DEFAULT_SYSTEM_PROMPT, user_prompt)
        parsed = self._parse_json(raw_output)
        return self._normalize_module_result(module_name, metric_specs, parsed, axis_name)

    def judge_quality_penalties(self, text_description: str) -> Dict:
        user_prompt = (
            f"Text to evaluate:\n{text_description}\n\n"
            "Judge local penalty items for this fashion description as a generation prompt.\n"
            "Focus on generation_content_penalty (non-imaging content: model pose/stance, redundant repeated facts, abstract editorial dilution—not the standard T2I preamble line), "
            "formula_template_penalty (cruise formula, brand-symbol-only, mood/essay dilution of visible design facts—content semantics only, not layout), "
            "trunk-level consistency, styling coordination, and rationality under realistic material and wearing conditions.\n"
            "For formula_template_penalty: score holistically by overall formula severity—formula trunk, brand-symbol-only, mood/essay dilution, interchangeability across looks—not by counting paragraph titles or bullets.\n"
            "UNIFIED RULE for consistency_penalty and coordination_penalty (asymmetry-related): be STRICT when inconsistency sits on trunk garments—outerwear, inner/base tops (shirts, tees, inner knit layers), bottoms, footwear; inner and outer upper-body layers are both trunk when each is a described garment. "
            "When explicitly described, outerwear lining and trouser inner lining (including lining visible through slits) count as trunk together with shell fabric—they must not read as two unrelated garment identities unless clearly separated as under-layer vs outer. "
            "Trunk left-right or same-garment conflicting identities should be penalized strongly; the intended fix is align to one side’s design language or remove the conflicting branch. "
            "If the text simultaneously lists **multiple** trunk-scale left-right splits (e.g. asymmetric sleeves on the coat + different materials or garment types on left vs right pant legs + mismatched shoe types on left vs right feet), treat as severe for image prompts: **do not** reduce consistency/coordination to mild (0.25) solely because the prose says “intentional deconstruction”—use at least **0.5** until the narrative clearly converges to one dominant silhouette/material/shoe grammar or omits weaker branches. "
            "Do NOT raise these two penalties for small, accessory-only bilateral differences (e.g., one glove vs other, off-center belt, single-sided earring) when all trunk coat/inner/pants/shoes read as one coherent look.\n"
            "Apply coordination_penalty and consistency_penalty strictly when a single upper garment combines incompatible styling languages on left vs right "
            "(e.g., half tailored suit vs half cold-shoulder bishop silk) without one coherent design grammar; also when one coat stacks incompatible collar/military/armor codes without layering rationale.\n"
            "Raise coordination_penalty when leg harnesses conflict with very wide loose trousers without explainable attachment, or waist/hip has multiple belt-harness systems with unclear order; "
            "raise rationality_penalty when harness+trouser construction is physically implausible as ordinary wear.\n"
            "Each penalty score must be one of its allowed discrete values (typically 0, 0.25, 0.5, 0.75, 1.0), "
            "where higher means a worse issue, analogous to inverted quality rubric levels.\n"
            "Return JSON only."
        )
        raw_output = self._generate(self._build_quality_penalty_system_prompt(), user_prompt)
        parsed = self._parse_json(raw_output)
        return self._normalize_quality_penalties(parsed)

    def _get_penalty_registry(self) -> Dict[str, Dict[str, Any]]:
        if self.penalty_registry:
            return self.penalty_registry
        return {
            "generation_content_penalty": {
                "allowed_scores": [0.0, 0.25, 0.5, 0.75, 1.0],
                "judge_guidance": "Score by imaging content value. IGNORE standard T2I preamble (Please generate female models and the matching clothing for them. / 请生成女模…)—never raise penalty for it alone. ≥0.5 for: model stance/pose/psychology, repeated facts without new pixels, abstract salon/promenade/identity essay outweighing visible anchors. ≥0.75 if non-imaging layers stack and visible facts are sparse.",
            },
            "consistency_penalty": {
                "allowed_scores": [0.0, 0.25, 0.5, 0.75, 1.0],
                "judge_guidance": "Raise only for trunk-level conflicts: outerwear, inner/base tops, bottoms, footwear splitting into conflicting left-right or mutually exclusive garment identities; be strict (align-to-one-side or delete-branch). Penalize **stacked** multi-zone trunk L/R enumeration (upper sleeve asymmetry + split pant legs + mismatched shoe families, etc.) at **≥0.5** unless clearly merged to one readable trunk or weaker side omitted—do not excuse with “coherent split system” alone down to 0.25. When the text describes outerwear lining or trouser inner lining, treat shell+lining as one trunk narrative—penalize shell vs lining or left-right lining clashes that split identity. Do not raise for mild bilateral differences confined to accessories when all trunk layers stay coherent. Same strict rules for one coat stacking incompatible collar/military/armor codes without split layers.",
            },
            "coordination_penalty": {
                "allowed_scores": [0.0, 0.25, 0.5, 0.75, 1.0],
                "judge_guidance": "Raise when trunk elements clash in mood/volume/material (outerwear vs inner top vs bottoms vs shoes; and described outerwear lining or trouser inner lining vs shell when they fight as unrelated fields). If upper/lower trunk already clash **and** left vs right feet use incompatible shoe moods (e.g. formal Oxford vs strappy sandal), coordination should be **≥0.5** unless one shoe narrative is dropped or unified. Do not raise for minor accessory-only asymmetry if outer/inner/pants/shoes read unified. Also raise for harness/trouser attachment chaos, stacked waist systems, detached lining vs shell as before.",
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
            cap_line = (
                "- Also obey explicit score caps in each metric's rule field when present.\n"
                if module_name != "DesignMerit"
                else ""
            )
            scale_rules = (
                "Scoring scale for each quality metric:\n"
                "- Use the metric-specific five-level rubric in quality_scoring_rubric as the first reference.\n"
                f"{cap_line}"
                "- 1.0 = near-perfect for that metric and quality dimension\n"
                "- 0.75 = strong with only minor issues for that metric\n"
                "- 0.5 = partially good but with clear room for improvement for that metric\n"
                "- 0.25 = weak or inefficient for that metric\n"
                "- 0.0 = missing, wrong, unusable, or seriously poor for that metric\n"
                "Do not give 1.0 unless the metric is satisfied at a near-perfect prompt level under its own rubric.\n"
            )
            if module_name == "DesignMerit":
                scale_rules += (
                    "\nDesignMerit — judge the look's design idea, not how completely it is specified:\n"
                    "- Completeness, length, and tidy garment lists are not high DesignMerit by themselves.\n"
                    "- High: a visible move that identifies this look (craft type+path, unusual proportion, "
                    "or a trunk combination that would collapse if one piece were swapped).\n"
                    "- Low: interchangeable kit (same silhouette family with swapped color/fabric/brand words), "
                    "brand-named hardware/finish as the signature, or mood/identity/pose commentary in place of a visual move.\n"
                )
            elif module_name in ("ConcisenessAndDensity", "GenerationReadiness", "StructuralClarity"):
                scale_rules += (
                    f"\n{module_name} module — T2I content priority (ignore layout):\n"
                    "- High: sentences map to visible pixels (garment form, material, color, trim path, layering, accessory placement).\n"
                    "- Low: model stance/pose, abstract salon/promenade/identity essay dominating over visible facts.\n"
                    "- IGNORE standard T2I preamble: Please generate female models and the matching clothing for them.\n"
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
        return (
            f"Text to evaluate:\n{text_description}\n\n"
            f"Current module: {module_name}\n\n"
            f"Axis: {axis_name}\n\n"
            f"Metrics to judge:\n{serialized_specs}\n\n"
            "Requirements:\n"
            "1. Judge applicability first.\n"
            "2. If applicable=true, return a numeric score.\n"
            "3. Scoring must be semantic, not surface keyword matching.\n"
            "4. evidence should quote short phrases from the original text when possible.\n"
            "5. For quality metrics, be strict about prompt usefulness, precision, structure, concision, spatial imageability, and internal visual coherence.\n"
            "6. Return JSON only.\n\n"
            f"{scale_rules}"
        )

    def _generate(self, system_prompt: str, user_prompt: str) -> str:
        return self._request_completion(
            system_prompt=system_prompt,
            user_content=user_prompt,
            response_format={"type": "json_object"},
        )

    def _request_completion(
        self,
        system_prompt: str,
        user_content: Union[str, List[Dict[str, Any]]],
        response_format: Optional[Dict[str, Any]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        if isinstance(user_content, str):
            user_message: Dict[str, Any] = {"role": "user", "content": user_content}
        else:
            user_message = {"role": "user", "content": user_content}
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                user_message,
            ],
            "temperature": self.temperature if temperature is None else temperature,
            "top_p": self.top_p,
            "max_completion_tokens": self.max_tokens if max_tokens is None else max_tokens,
        }
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
            if attempt < max_retries:
                backoff = (2 ** attempt) * 2.0
                self.logger.warning("All URLs failed on attempt %d/%d, backing off %.1fs: %s",
                                    attempt + 1, max_retries + 1, backoff, last_error)
                import time
                time.sleep(backoff)
            else:
                break

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
        json_block = self._extract_first_json_object(cleaned)
        try:
            return json.loads(json_block)
        except json.JSONDecodeError as exc:
            raise ValueError(f"LLM judge did not return valid JSON:\n{cleaned}") from exc

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
        for item in parsed.get("results", []):
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
        items = parsed.get("items", []) if isinstance(parsed.get("items", []), list) else []
        item_map = {}
        for item in items:
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
        score_gate_min = float(spec_gates.get("score_gate_min", 0.7))
        penalty_gate_max = float(spec_gates.get("penalty_gate_max", 0.5))
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
                "description": "最终 S_fp（quality 用 weighted base_score，不含 penalty 扣减；已做 holdout 长度去相关）",
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
        module_scores = self._aggregate_module_scores(metric_results)
        axis_scores = self._aggregate_axis_scores(metric_results)
        quality_axis_score = axis_scores["quality_score"]["score"]
        quality_weighted = self._aggregate_weighted_quality_score(module_scores)

        char_len = len(eval_prose) if eval_prose else len(raw_text)

        quality_cap = 1.0
        if module_scores.get("BindingAccuracy", {}).get("score", 1.0) < 0.5:
            quality_cap = min(quality_cap, 0.6)
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
        fashion_prompt_score = length_disentangle["adjusted_score"]
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
            fashion_prompt_score,
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
        "coat", "jacket", "blazer", "suit", "dress", "skirt", "trousers", "pants",
        "pant", "jeans", "shirt", "blouse", "top", "sweater", "cardigan", "vest",
        "gown", "robe", "cape", "cloak", "tunic", "bodysuit", "jumpsuit", "romper",
        "西装", "外套", "大衣", "风衣", "夹克", "衬衫", "连衣裙", "裙子", "裤",
        "毛衣", "针织", "卫衣", "运动服", "套装", "旗袍", "马甲", "斗篷",
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
                        "quality_scoring_rubric": dimension_cfg.get("scoring_rubric", {}),
                    }
                )
                # DesignMerit: style preference lives in module prompt + rubric; omit soft_rules/corpus noise.
                if dimension_key not in (
                    "DesignDistinctiveness",
                    "VisualGrounding",
                    "CraftSalience",
                    "CombinationOriginality",
                    "DesignSignalPurity",
                ):
                    soft_rules = dimension_cfg.get("soft_rules")
                    if soft_rules:
                        metric_spec["soft_rules"] = soft_rules
                    reference_corpus = dimension_cfg.get("reference_corpus")
                    if reference_corpus:
                        metric_spec["reference_corpus"] = reference_corpus
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
