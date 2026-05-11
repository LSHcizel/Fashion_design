"""
API-based LLM-as-a-judge DesignTextEvaluator for fashion text descriptions.
"""

from __future__ import annotations

import json
import logging
import os
import re
import ssl
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urlparse

import yaml


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


APPLICABILITY_HINTS = {
    "always": "Always judge this metric.",
    "when_shape_is_salient": "Only applicable when the text clearly mentions silhouette, shape, or structural contour.",
    "when_length_or_hem_is_salient": "Only applicable when the text mentions length, hemline, slit, or garment length.",
    "when_exposure_is_salient": "Only applicable when the text mentions exposure, coverage, cutout, or body reveal.",
    "when_material_is_inferable": "Only applicable when the text provides enough information about the main material.",
    "when_surface_trait_is_salient": "Only applicable when the text mentions gloss, matte, drape, stiffness, pleats, or surface traits.",
    "when_secondary_color_is_salient": "Only applicable when the text clearly includes secondary color or color relationship information.",
    "when_pattern_exists": "Only applicable when the text describes pattern or print information.",
    "when_closure_is_salient": "Only applicable when the text mentions button, zipper, tie, buckle, or closure details.",
    "when_functional_detail_is_salient": "Only applicable when the text mentions pockets, straps, utility parts, or functional details.",
    "when_deconstruction_exists": "Only applicable when the text mentions deconstruction, splicing, displacement, or reconstruction.",
    "when_hardware_is_salient": "Only applicable when the text mentions chains, studs, metal rings, crystals, or similar embellishment.",
    "when_full_look_and_bag_exists": "Only applicable when the text describes a full look and the bag is an important part of it.",
    "when_full_look_and_footwear_exists": "Only applicable when the text describes a full look and footwear is an important part of it.",
    "when_jewelry_is_salient": "Only applicable when jewelry or body ornament is explicitly present.",
    "when_belt_or_waist_accent_exists": "Only applicable when a belt or strong waist emphasis is present.",
    "when_layering_exists": "Only applicable when the text describes layering or multi-layer garment relations.",
    "when_proportion_is_salient": "Only applicable when the text describes top-bottom proportion, waist position, or visual balance.",
    "when_asymmetry_exists": "Only applicable when the text describes asymmetry, one-shoulder, single sleeve, or uneven structure.",
    "when_bilateral_difference_exists": "Only applicable when the text explicitly distinguishes left/right sides or other bilateral elements such as shoes, sleeves, legs, or shoulders.",
    "when_spatial_relation_exists": "Only applicable when the text describes layering, front/back, inside/outside, attached position, crossing paths, or other explicit spatial relations.",
    "when_multiple_garments_exist": "Only applicable when the text includes multiple garments or multi-item relations.",
    "when_quantity_is_used": "Only applicable when the text includes numbers, counts, or explicit quantity relations.",
    "when_style_goal_is_explicit": "Only applicable when the text explicitly expresses aesthetic or style vocabulary.",
    "when_reference_is_grounded": "Only applicable when the text explicitly provides cultural, historical, or brand grounding.",
    "when_gender_expression_is_relevant": "Only applicable when the text explicitly mentions gender expression or androgyny.",
    "when_series_theme_is_known": "Only applicable when the text clearly mentions a theme or conceptual narrative.",
    "when_brand_goal_is_explicit": "Only applicable when the text explicitly targets brand language or brand identity.",
    "when_absence_is_important": "Only applicable when absence or exclusion of an element matters in the text.",
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
10. Output strict JSON only. Do not output markdown fences or extra commentary.

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

        config_api_key = FASHION_CONFIG.get("api-key") or FASHION_CONFIG.get("openai-api-key")
        config_api_base = FASHION_CONFIG.get("api-base") or FASHION_CONFIG.get("openai-api-base")

        self.api_key = api_key or os.environ.get("AI_API_KEY") or config_api_key
        self.api_base = (
            api_base
            or os.environ.get("AI_API_BASE")
            or config_api_base
            or "https://api.ohmygpt.com/v1"
        ).rstrip("/")
        self.model = model or os.environ.get("AI_API_MODEL") or os.environ.get("AI_MODEL") or "gpt-5.4-mini"
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.penalty_registry: Dict[str, Dict[str, Any]] = {}
        if verify_ssl is None:
            self.verify_ssl = os.environ.get("AI_API_VERIFY_SSL", "true").strip().lower() not in {"0", "false", "no"}
        else:
            self.verify_ssl = verify_ssl

        if not self.api_key:
            raise ValueError("Missing API key. Set AI_API_KEY or pass api_key explicitly.")
        if not self.api_base:
            raise ValueError("Missing API base. Set AI_API_BASE or pass api_base explicitly.")
        if not self.model:
            raise ValueError("Missing judge model. Set AI_API_MODEL/AI_MODEL or pass model explicitly.")

    def judge_module(self, text_description: str, module_name: str, metric_specs: List[Dict], axis_name: str) -> Dict:
        user_prompt = self._build_user_prompt(text_description, module_name, metric_specs, axis_name)
        raw_output = self._generate(self.DEFAULT_SYSTEM_PROMPT, user_prompt)
        parsed = self._parse_json(raw_output)
        return self._normalize_module_result(module_name, metric_specs, parsed, axis_name)

    def judge_quality_penalties(self, text_description: str) -> Dict:
        user_prompt = (
            f"Text to evaluate:\n{text_description}\n\n"
            "Judge local penalty items for this fashion description as a generation prompt.\n"
            "Focus on generation_content_penalty (redundant, irrelevant, analytical or conceptual prose that hurts prompt efficiency; also long lists of style symbols without a clear imaging trunk), "
            "trunk-level consistency, styling coordination, and rationality under realistic material and wearing conditions.\n"
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
                "judge_guidance": "Raise this when redundancy, irrelevant or low-imaging-value detail, or analytical/conceptual/runway-essay prose materially hurts prompt efficiency; also when many conflicting style symbols are listed without a clear silhouette/layering trunk so the prompt cannot focus. Pick one discrete level by overall severity.",
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
            user_prompt=user_prompt,
            response_format=None,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    def _build_user_prompt(self, text_description: str, module_name: str, metric_specs: List[Dict], axis_name: str) -> str:
        serialized_specs = json.dumps(metric_specs, ensure_ascii=False, indent=2)
        if axis_name == "quality_score":
            scale_rules = (
                "Scoring scale for each quality metric:\n"
                "- Use the metric-specific five-level rubric in quality_scoring_rubric as the first reference.\n"
                "- 1.0 = near-perfect for that metric and quality dimension\n"
                "- 0.75 = strong with only minor issues for that metric\n"
                "- 0.5 = partially good but with clear room for improvement for that metric\n"
                "- 0.25 = weak or inefficient for that metric\n"
                "- 0.0 = missing, wrong, unusable, or seriously poor for that metric\n"
                "Do not give 1.0 unless the metric is satisfied at a near-perfect prompt level under its own rubric.\n"
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
            user_prompt=user_prompt,
            response_format={"type": "json_object"},
        )

    def _request_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: Optional[Dict[str, Any]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
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
        base_dir = Path(__file__).resolve().parent
        self.base_dir = base_dir
        self.spec_path = Path(spec_path) if spec_path else base_dir / "fashion_prompt_optimizer_spec.json"
        self.optimizer_prompt_path = base_dir / "fashion_sys_prompt.txt"
        self.optimization_inputs_dir = base_dir / "optimization_reports" / "inputs"
        self.optimization_outputs_dir = base_dir / "optimization_reports" / "outputs"
        with self.spec_path.open("r", encoding="utf-8") as f:
            self.spec = json.load(f)
        self.penalty_registry = self.spec.get("penalty_registry", {})
        self.optimizer_system_prompt = self.optimizer_prompt_path.read_text(encoding="utf-8").strip()
        _llm_cfg = self.spec.get("llm") or {}
        _spec_default_model = str(_llm_cfg.get("default_model", "gpt-5.4-mini"))
        self._optimization_compact_summary = bool(_llm_cfg.get("optimization_compact_summary", True))
        _resolved_model = (
            model
            or os.environ.get("AI_API_MODEL")
            or os.environ.get("AI_MODEL")
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
        _rw = self.spec.get("rewriter", {}) or {}
        self.optimizer_rewriter_temperature = float(
            rewriter_temperature if rewriter_temperature is not None else float(_rw.get("temperature", 0.1))
        )
        self._optimize_candidate_eval_cfg = self.spec.get("optimize_candidate_evaluation") or {}

    def _optimize_candidate_eval_enabled(self) -> bool:
        cfg = self._optimize_candidate_eval_cfg
        return bool(cfg.get("enabled", False))

    def _blend_optimize_candidate_metrics(self, metric_results: Dict, baseline_result: Dict) -> None:
        """多轮 optimize 再评估：非 always 的 coverage 可沿用 baseline 命中。"""
        cfg = self._optimize_candidate_eval_cfg
        if not cfg.get("enabled", False):
            return
        baseline = baseline_result.get("metric_results") or {}
        if cfg.get("carry_forward_non_always_coverage_hits", True):
            for name, res in metric_results.items():
                if res.get("axis") != "coverage_score":
                    continue
                if (res.get("applicability_code") or "") == "always":
                    continue
                b = baseline.get(name)
                if not b or not b.get("applicable"):
                    continue
                if int(b.get("hit") or 0) != 1:
                    continue
                if not res.get("applicable"):
                    continue
                if int(res.get("hit") or 0) == 1:
                    continue
                res["score_value"] = b["score_value"]
                res["hit"] = b["hit"]
                res["reason"] = b.get("reason", res.get("reason", ""))
                res["matched_terms"] = list(b.get("matched_terms") or [])

    def _build_rewrite_basis_evidence_lines(self, evaluation_result: Dict) -> str:
        """最高分稿上的 penalty 证据摘要，供 rewriter 对照针对性修改。"""
        lines: List[str] = []
        items = (evaluation_result.get("scores") or {}).get("quality_score", {}).get("penalties", {}).get("items") or {}
        for key in self._get_penalty_keys():
            entry = items.get(key) or {}
            try:
                sc = float(entry.get("score", 0.0) or 0.0)
            except (TypeError, ValueError):
                sc = 0.0
            if sc <= 0:
                continue
            ev = entry.get("evidence") or []
            if isinstance(ev, str):
                ev = [ev]
            evs = "; ".join(str(x).strip() for x in ev[:6] if str(x).strip())
            reason = (entry.get("reason") or "").strip()
            chunk = f"- [{key}] score={sc}"
            if reason:
                chunk += f" | reason: {reason[:320]}{'…' if len(reason) > 320 else ''}"
            if evs:
                chunk += f" | evidence: {evs[:400]}{'…' if len(evs) > 400 else ''}"
            lines.append(chunk)
        if not lines:
            return ""
        return "PEAK-SCORE DRAFT — penalty evidence to fix (target these spans; stay grounded):\n" + "\n".join(lines) + "\n\n"

    def _resolve_optimization_gate_config(self, gate_config: Optional[Dict[str, Any]] = None) -> Dict[str, float]:
        spec_gates = self.spec.get("optimization_gates", {}) or {}
        score_gate_min = float(spec_gates.get("score_gate_min", 0.75))
        penalty_gate_max = float(spec_gates.get("penalty_gate_max", 0.1))
        if gate_config:
            if gate_config.get("score_gate_min") is not None:
                score_gate_min = float(gate_config["score_gate_min"])
            if gate_config.get("penalty_gate_max") is not None:
                penalty_gate_max = float(gate_config["penalty_gate_max"])
        return {"score_gate_min": score_gate_min, "penalty_gate_max": penalty_gate_max}

    def _compute_gates(
        self,
        *,
        coverage_axis_score: float,
        quality_base_score: float,
        weights: Dict[str, float],
        total_cap: float,
        total_penalty: float,
        gate_config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        cfg = self._resolve_optimization_gate_config(gate_config)
        raw_combined = float(coverage_axis_score) * float(weights["coverage"]) + float(quality_base_score) * float(
            weights["quality"]
        )
        score_gate_value = round(min(raw_combined, float(total_cap)), 4)
        tp = round(float(total_penalty), 4)
        score_passed = score_gate_value >= cfg["score_gate_min"] - 1e-9
        penalty_passed = tp <= cfg["penalty_gate_max"] + 1e-9
        return {
            "score_gate": {
                "name": "score_gate",
                "description": "coverage_score 与 quality_score 轴均值的加权和（quality 使用 base_score，不含 penalty 扣减）",
                "value": score_gate_value,
                "threshold": cfg["score_gate_min"],
                "passed": score_passed,
                "weights": dict(weights),
                "components": {
                    "coverage_axis_score": round(float(coverage_axis_score), 4),
                    "quality_base_score": round(float(quality_base_score), 4),
                },
                "total_cap_applied": round(float(total_cap), 4),
            },
            "penalty_gate": {
                "name": "penalty_gate",
                "description": "仅依据 penalties.total_penalty（各 penalty 分值的算术平均）",
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

    def _gate_failure_target_lines(self, evaluation_result: Dict) -> List[str]:
        lines: List[str] = []
        gates = evaluation_result.get("gates") or {}
        sg = gates.get("score_gate") or {}
        pg = gates.get("penalty_gate") or {}
        if not sg.get("passed"):
            lines.append(
                f"【得分门限未通过】加权得分 {sg.get('value')} 低于阈值 {sg.get('threshold')}（coverage×{sg.get('weights', {}).get('coverage', '?')} "
                f"+ quality_base×{sg.get('weights', {}).get('quality', '?')}，且受 total_cap 限制）。请针对下列低分指标的原因与证据改写文本，优先补齐覆盖与质量 rubric 要求。"
            )
            for metric_name, result in evaluation_result.get("metric_results", {}).items():
                if result.get("axis") not in ("coverage_score", "quality_score"):
                    continue
                if not result.get("applicable"):
                    continue
                sv = float(result.get("score_value", 0.0) or 0.0)
                if sv >= QUALITY_FULL_HIT_THRESHOLD:
                    continue
                ev = result.get("matched_terms") or []
                reason = result.get("reason") or ""
                lines.append(
                    f"  - 指标 `{metric_name}`（{result.get('axis')}）得分 {sv}：{reason}；证据片段：{self._format_terms(ev)}"
                )
        if not pg.get("passed"):
            lines.append(
                f"【惩罚门限未通过】综合惩罚 total_penalty={pg.get('total_penalty')} 高于阈值 {pg.get('threshold')}。"
                f"请按各 penalty 的原因与证据压缩冗余/无关/分析性表述，并修复一致性、协调性、合理性等问题。"
            )
            penalty_items = evaluation_result["scores"]["quality_score"]["penalties"].get("items", {})
            for key in self._get_penalty_keys():
                item = penalty_items.get(key, {})
                score = float(item.get("score", 0.0) or 0.0)
                if score <= 0:
                    continue
                reason = item.get("reason", "") or ""
                evidence = item.get("evidence", []) or []
                lines.append(
                    f"  - 惩罚 `{key}` 分值 {score}：{reason}；证据：{self._format_terms(evidence)}"
                )
        return lines

    def evaluate_text(
        self,
        text_description: str,
        source_name: str = "inline_text",
        gate_config: Optional[Dict[str, Any]] = None,
        *,
        optimize_round_baseline: Optional[Dict] = None,
    ) -> Dict:
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
                module_output = self.judge.judge_module(text_description, module["name"], metric_specs, axis_name)
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

        quality_penalties = self.judge.judge_quality_penalties(text_description)
        if optimize_round_baseline is not None and self._optimize_candidate_eval_enabled():
            self._blend_optimize_candidate_metrics(metric_results, optimize_round_baseline)
        module_scores = self._aggregate_module_scores(metric_results)
        axis_scores = self._aggregate_axis_scores(metric_results)
        quality_base_score = axis_scores["quality_score"]["score"]
        quality_cap = 1.0
        if module_scores.get("BindingAccuracy", {}).get("score", 1.0) < 0.5:
            quality_cap = min(quality_cap, 0.6)
        # 总分与 penalized_score 不再扣减 penalties；penalties 仅用于惩罚门与清单。
        quality_effective = round(min(quality_base_score, quality_cap), 4)

        weights = {"coverage": 0.4, "quality": 0.6}
        coverage_score = axis_scores["coverage_score"]["score"]
        fashion_prompt_score = round(
            coverage_score * weights["coverage"] + quality_effective * weights["quality"],
            4,
        )
        total_cap = 1.0
        if module_scores.get("GarmentCore", {}).get("score", 1.0) < 0.5 or module_scores.get("MaterialColor", {}).get("score", 1.0) < 0.4:
            total_cap = min(total_cap, 0.7)
        fashion_prompt_score = round(min(fashion_prompt_score, total_cap), 4)
        score_band = self._score_band(fashion_prompt_score)
        total_defined_metrics = len(self.spec["metric_registry"])
        total_applicable_metrics = sum(1 for item in metric_results.values() if item["applicable"])
        total_hit_metrics = sum(1 for item in metric_results.values() if item["applicable"] and item["hit"] == 1)
        skipped_metrics = self._build_skipped_metrics(metric_results)

        gates = self._compute_gates(
            coverage_axis_score=coverage_score,
            quality_base_score=quality_base_score,
            weights=weights,
            total_cap=total_cap,
            total_penalty=quality_penalties["total_penalty"],
            gate_config=gate_config,
        )

        return {
            "name": self.spec["name"],
            "version": self.spec["version"],
            "source_name": source_name,
            "input_type": self.spec["input_type"],
            "judge_backend": "openai_compatible_api",
            "judge_model": self.judge.model,
            "judge_api_base": self.judge.api_base,
            "text_description": text_description,
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
                    "base_score": quality_base_score,
                    "penalized_score": quality_effective,
                    "penalties": quality_penalties,
                    "cap": quality_cap,
                },
                "bonus_score": axis_scores["bonus_score"],
                "fashion_prompt_score": fashion_prompt_score,
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
                "optimize_candidate_leniency_applied": bool(
                    optimize_round_baseline is not None and self._optimize_candidate_eval_enabled()
                ),
            },
            "raw_module_outputs": raw_module_outputs,
        }

    def evaluate_txt_file(self, txt_path: str | Path) -> Dict:
        path = Path(txt_path)
        with path.open("r", encoding="utf-8") as f:
            text_description = f.read().strip()
        return self.evaluate_text(text_description, source_name=path.name)

    def evaluate_txt_directory(self, directory_path: str | Path) -> Dict[str, Dict]:
        directory = Path(directory_path)
        results = {}
        for txt_file in sorted(directory.glob("*.txt")):
            results[txt_file.name] = self.evaluate_txt_file(txt_file)
        return results

    def optimize_text_description(
        self,
        text_description: str,
        source_name: str = "inline_text",
        report_dir: Optional[str | Path] = None,
        save_report: bool = True,
        max_rounds: int = 5,
        min_score_improvement: float = 0.02,
        min_quality_improvement: float = 0.05,
        score_gate_min: Optional[float] = None,
        penalty_gate_max: Optional[float] = None,
    ) -> Dict:
        gate_cfg: Dict[str, Any] = {}
        if score_gate_min is not None:
            gate_cfg["score_gate_min"] = score_gate_min
        if penalty_gate_max is not None:
            gate_cfg["penalty_gate_max"] = penalty_gate_max
        gate_cfg_arg = gate_cfg if gate_cfg else None

        original_result = self.evaluate_text(text_description, source_name=source_name, gate_config=gate_cfg_arg)
        report_path: Optional[Path] = None

        if self._gates_both_pass(original_result):
            optimized_text = text_description
            optimized_result = original_result
            if save_report:
                report_path = self.write_optimization_report(
                    source_name=source_name,
                    original_text=text_description,
                    optimized_text=optimized_text,
                    original_result=original_result,
                    optimized_result=optimized_result,
                    report_dir=report_dir,
                    round_records=[],
                )
            return {
                "source_name": source_name,
                "original_text": text_description,
                "optimized_text": optimized_text,
                "original_result": original_result,
                "optimized_result": optimized_result,
                "score_delta": 0.0,
                "quality_delta": 0.0,
                "both_gates_satisfied": True,
                "gates_satisfied_initially": True,
                "rounds": [],
                "rounds_executed": 0,
                "best_round_index": None,
                "report_path": str(report_path) if report_path else None,
            }

        best_text = text_description
        best_result = original_result
        current_text = text_description
        current_result = original_result
        round_records: List[Dict] = []
        best_round_index: Optional[int] = None

        total_rounds = max(1, int(max_rounds))
        for round_index in range(1, total_rounds + 1):
            per_key_rewrite_counts = self._aggregate_per_key_rewrite_counts(round_records)
            strategy = self._build_round_strategy(
                current_result=current_result,
                previous_result=round_records[-1]["input_result"] if round_records else None,
                round_history=round_records,
                round_index=round_index,
                min_score_improvement=min_score_improvement,
                min_quality_improvement=min_quality_improvement,
                per_key_rewrite_counts=per_key_rewrite_counts,
            )
            candidate_text = self._rewrite_text_description(current_text, current_result, strategy)
            candidate_result = self.evaluate_text(
                candidate_text,
                source_name=f"{source_name}.round{round_index}",
                gate_config=gate_cfg_arg,
                optimize_round_baseline=best_result,
            )
            round_record = self._build_round_record(
                round_index=round_index,
                input_text=current_text,
                input_result=current_result,
                output_text=candidate_text,
                output_result=candidate_result,
                strategy=strategy,
            )
            round_records.append(round_record)

            if self._is_better_result(candidate_result, best_result):
                best_text = candidate_text
                best_result = candidate_result
                best_round_index = round_index

            current_text = best_text
            current_result = best_result

            if self._should_stop_optimization(
                round_records=round_records,
                current_result=current_result,
                round_index=round_index,
                max_rounds=total_rounds,
                min_score_improvement=min_score_improvement,
                min_quality_improvement=min_quality_improvement,
            ):
                break

        optimized_text = best_text
        optimized_result = best_result

        if save_report:
            report_path = self.write_optimization_report(
                source_name=source_name,
                original_text=text_description,
                optimized_text=optimized_text,
                original_result=original_result,
                optimized_result=optimized_result,
                report_dir=report_dir,
                round_records=round_records,
            )

        return {
            "source_name": source_name,
            "original_text": text_description,
            "optimized_text": optimized_text,
            "original_result": original_result,
            "optimized_result": optimized_result,
            "score_delta": round(optimized_result["total_score"] - original_result["total_score"], 4),
            "quality_delta": round(
                optimized_result["scores"]["quality_score"]["penalized_score"]
                - original_result["scores"]["quality_score"]["penalized_score"],
                4,
            ),
            "both_gates_satisfied": self._gates_both_pass(optimized_result),
            "gates_satisfied_initially": False,
            "rounds": round_records,
            "rounds_executed": len(round_records),
            "best_round_index": best_round_index,
            "report_path": str(report_path) if report_path else None,
        }

    def optimize_txt_file(
        self,
        txt_path: str | Path,
        report_dir: Optional[str | Path] = None,
        save_report: bool = True,
        max_rounds: int = 5,
        min_score_improvement: float = 0.02,
        min_quality_improvement: float = 0.05,
        score_gate_min: Optional[float] = None,
        penalty_gate_max: Optional[float] = None,
    ) -> Dict:
        path = Path(txt_path)
        text_description = path.read_text(encoding="utf-8").strip()
        return self.optimize_text_description(
            text_description=text_description,
            source_name=path.name,
            report_dir=report_dir,
            save_report=save_report,
            max_rounds=max_rounds,
            min_score_improvement=min_score_improvement,
            min_quality_improvement=min_quality_improvement,
            score_gate_min=score_gate_min,
            penalty_gate_max=penalty_gate_max,
        )

    def optimize_txt_directory(
        self,
        directory_path: str | Path,
        report_dir: Optional[str | Path] = None,
        save_report: bool = True,
        max_rounds: int = 5,
        min_score_improvement: float = 0.02,
        min_quality_improvement: float = 0.05,
        score_gate_min: Optional[float] = None,
        penalty_gate_max: Optional[float] = None,
    ) -> Dict[str, Dict]:
        directory = Path(directory_path)
        results = {}
        for txt_file in sorted(directory.glob("*.txt")):
            results[txt_file.name] = self.optimize_txt_file(
                txt_path=txt_file,
                report_dir=report_dir,
                save_report=save_report,
                max_rounds=max_rounds,
                min_score_improvement=min_score_improvement,
                min_quality_improvement=min_quality_improvement,
                score_gate_min=score_gate_min,
                penalty_gate_max=penalty_gate_max,
            )
        return results

    def write_optimization_report(
        self,
        source_name: str,
        original_text: str,
        optimized_text: str,
        original_result: Dict,
        optimized_result: Dict,
        report_dir: Optional[str | Path] = None,
        round_records: Optional[List[Dict]] = None,
    ) -> Path:
        output_dir = Path(report_dir) if report_dir else self.optimization_outputs_dir
        output_dir.mkdir(parents=True, exist_ok=True)

        file_stem = self._safe_file_stem(source_name)
        report_path = output_dir / f"{file_stem}_optimization_report.md"
        report_content = self._build_optimization_report(
            source_name=source_name,
            original_text=original_text,
            optimized_text=optimized_text,
            original_result=original_result,
            optimized_result=optimized_result,
            round_records=round_records or [],
        )
        report_path.write_text(report_content, encoding="utf-8")
        return report_path

    def _rewrite_text_description(
        self,
        text_description: str,
        evaluation_result: Dict,
        strategy: Optional[Dict] = None,
    ) -> str:
        optimization_prompt = self._build_optimization_prompt(text_description, evaluation_result, strategy)
        optimized_text = self.judge.generate_text(
            system_prompt=self.optimizer_system_prompt,
            user_prompt=optimization_prompt,
            temperature=self.optimizer_rewriter_temperature,
            max_tokens=self.judge.max_tokens,
        )
        validated = self._validate_optimized_text(optimized_text, text_description)
        return self._normalize_optimized_text(validated)

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

    def _build_penalty_repair_checklist_section(self, evaluation_result: Dict) -> str:
        """逐条列出当前非零 penalty 的 reason/evidence，供 rewriter 按项消除（不编造）。"""
        penalties = evaluation_result["scores"]["quality_score"]["penalties"]
        items: Dict[str, Any] = penalties.get("items") or {}
        lines: List[str] = [
            "PENALTY REPAIR CHECKLIST — address EVERY item with score > 0:",
            "These reasons and evidence come from the evaluator’s judgment of the CURRENT text (before your rewrite).",
            "THREE-STEP POLICY (applies to ALL penalty items in every optimization round):",
            "  Step 1 — REWRITE: rephrase, merge redundancy, fix entity binding, resolve contradictions, and keep grounded design where possible.",
            "  Step 2 — REWRITE AGAIN: if a penalty is still likely, rewrite the same evidence span again with stronger convergence and clearer garment grammar.",
            "  Step 3 — DELETE: only if two rewrite passes still cannot remove the trigger; omit the minimal harmful span.",
            "  For consistency/coordination driven by **stacked** trunk left-right splits (upper + pant legs + mismatched shoes, etc.): one full rewrite pass must try to unify; if the same stacked pattern would still trigger the penalty, **DELETE whole weaker branches** (one leg’s alt material, one shoe type, one sleeve extreme, etc.) until one coherent trunk remains—do not keep all opposites for “authentic deconstruction.”",
            "Do not invent new garment facts.",
            "",
        ]
        n = 0
        for key in self._get_penalty_keys():
            entry = items.get(key) or {}
            raw_score = entry.get("score")
            if raw_score is None:
                raw_score = penalties.get(key, 0.0)
            score = float(raw_score or 0.0)
            if score <= 0:
                continue
            n += 1
            reason = (entry.get("reason") or "").strip()
            evidence = entry.get("evidence") or []
            if isinstance(evidence, str):
                evidence = [evidence]
            lines.append(f"{n}. [{key}] penalty score = {score}")
            if reason:
                lines.append(f"   Judge reason: {reason}")
            if evidence:
                lines.append("   Judge evidence (phrases from the evaluated text):")
                for ev in evidence[:10]:
                    evs = str(ev).strip()
                    if evs:
                        lines.append(f"   - {evs}")
            lines.append(
                "   Required fix (three steps): (1) REWRITE the triggering evidence into coherent fashion language and binding. "
                "(2) REWRITE AGAIN with stronger convergence if the first rewrite may still trigger the same penalty. "
                "(3) DELETE/omit only if two rewrites still leave the issue; prefer the shortest deletion that fixes the judge’s concern. "
                "Never add new facts."
            )
            lines.append("")
        if n == 0:
            lines.append("(No non-zero penalties on the current text.)")
        return "\n".join(lines)

    def _compact_optimizer_summary_payload(self, summary_payload: Dict[str, Any], strategy: Optional[Dict]) -> Dict[str, Any]:
        """压缩 optimize 改写中的 Evaluation summary 体积；保留分数、门限、penalty 全量与策略轮次信号。"""
        out: Dict[str, Any] = {
            "source_name": summary_payload.get("source_name"),
            "total_score": summary_payload.get("total_score"),
            "score_band": summary_payload.get("score_band"),
            "gates": summary_payload.get("gates"),
            "quality_penalized_score": summary_payload.get("quality_penalized_score"),
            "coverage_score": summary_payload.get("coverage_score"),
            "quality_base_score": summary_payload.get("quality_base_score"),
            "bonus_score": summary_payload.get("bonus_score"),
            "penalties": summary_payload.get("penalties"),
        }
        wm = summary_payload.get("weak_modules") or []
        out["weak_modules"] = [
            {"module": x.get("module"), "score": round(float(x.get("score", 0.0) or 0.0), 4)} for x in wm[:8]
        ]
        lqm = summary_payload.get("low_quality_metrics") or []
        out["low_quality_metrics"] = []
        for x in lqm[:10]:
            raw_reason = x.get("reason") or ""
            reason = raw_reason[:240] + ("…" if len(raw_reason) > 240 else "")
            out["low_quality_metrics"].append(
                {
                    "metric": x.get("metric"),
                    "score_value": x.get("score_value"),
                    "reason": reason,
                }
            )
        for key in ("missing_information", "quality_issues", "bonus_opportunities"):
            arr = summary_payload.get(key)
            if isinstance(arr, list):
                out[key] = arr[:6]
            else:
                out[key] = arr
        skipped = summary_payload.get("skipped_metrics")
        out["skipped_metrics"] = (skipped[:12] if isinstance(skipped, list) else skipped)
        st = strategy or {}
        ac = st.get("asymmetry_control") or {}
        out["adaptive_strategy"] = {
            "round_index": st.get("round_index"),
            "forced_consistency_bilateral_choice": st.get("forced_consistency_bilateral_choice"),
            "gates": st.get("gates"),
            "active_penalties": [
                {"penalty_key": x.get("penalty_key"), "score": x.get("score")}
                for x in (st.get("active_penalties") or [])[:5]
            ],
            "stubborn_penalties": [
                {"penalty_key": x.get("penalty_key"), "current_score": x.get("current_score")}
                for x in (st.get("stubborn_penalties") or [])[:5]
            ],
            "stubborn_metrics": [
                {"metric": x.get("metric"), "current_score": x.get("current_score")}
                for x in (st.get("stubborn_metrics") or [])[:6]
            ],
            "asymmetry_stage": ac.get("stage"),
            "asymmetry_core_rule": ac.get("core_rule"),
        }
        return out

    def _build_optimization_prompt(
        self,
        text_description: str,
        evaluation_result: Dict,
        strategy: Optional[Dict] = None,
    ) -> str:
        scores = evaluation_result["scores"]
        penalties = scores["quality_score"]["penalties"]
        penalty_items = penalties.get("items", {})
        weak_modules = self._select_weak_modules(scores.get("module_scores", {}))
        low_quality_metrics = self._select_low_quality_metrics(evaluation_result.get("metric_results", {}))
        improvement_targets = self._build_improvement_targets(evaluation_result)
        if strategy:
            improvement_targets.extend(strategy.get("additional_targets", []))

        summary_payload = {
            "source_name": evaluation_result.get("source_name"),
            "total_score": evaluation_result.get("total_score"),
            "score_band": evaluation_result.get("score_band"),
            "gates": evaluation_result.get("gates"),
            "quality_penalized_score": scores["quality_score"].get("penalized_score"),
            "coverage_score": scores["coverage_score"].get("score"),
            "quality_base_score": scores["quality_score"].get("base_score"),
            "bonus_score": scores["bonus_score"].get("score"),
            "penalties": {
                key: {
                    "score": value.get("score", 0.0),
                    "reason": value.get("reason", ""),
                    "evidence": value.get("evidence", []),
                }
                for key, value in penalty_items.items()
            },
            "weak_modules": weak_modules,
            "missing_information": evaluation_result.get("diagnosis", {}).get("missing_information", []),
            "quality_issues": evaluation_result.get("diagnosis", {}).get("quality_issues", []),
            "bonus_opportunities": evaluation_result.get("diagnosis", {}).get("bonus_opportunities", []),
            "low_quality_metrics": low_quality_metrics,
            "skipped_metrics": evaluation_result.get("skipped_metrics", []),
            "adaptive_strategy": strategy or {},
        }

        targets_text = "\n".join(f"- {item}" for item in improvement_targets)
        if getattr(self, "_optimization_compact_summary", True):
            summary_for_prompt = self._compact_optimizer_summary_payload(summary_payload, strategy)
            summary_text = json.dumps(summary_for_prompt, ensure_ascii=False, separators=(",", ":"))
        else:
            summary_text = json.dumps(summary_payload, ensure_ascii=False, indent=2)
        asymmetry_policy = self._render_asymmetry_policy_text(strategy)
        gates = evaluation_result.get("gates") or {}
        penalty_gate_failed = not bool((gates.get("penalty_gate") or {}).get("passed"))
        penalty_checklist = self._build_penalty_repair_checklist_section(evaluation_result)
        guard = (strategy or {}).get("penalty_rewrite_guard") or {}
        delete_enabled = bool(guard.get("delete_enabled", True))
        rewrite_pass_1_done = bool(guard.get("rewrite_pass_1_done", False))
        rewrite_pass_2_done = bool(guard.get("rewrite_pass_2_done", False))  # kept for backward compat, unused

        gate_priority_lines = [
            "Gate priority — three-step handling for ALL penalty items (every round):",
            "- Step 1 REWRITE: always try first—restructure sentences, fix binding, de-contradict, merge duplication, and replace vague prose with concrete garment terms.",
            "- Step 2 REWRITE AGAIN: if penalties may persist, rewrite the same harmful span again with stronger convergence and clearer visual grammar.",
            (
                "- Step 3 DELETE: enabled after one rewrite pass — remove spans that still trigger the same penalty. Prefer minimal deletion."
                if delete_enabled
                else f"- Step 3 DELETE: LOCKED this round (rewrite_pass_1_done={rewrite_pass_1_done})."
            ),
            "- Keep grounded secondary styling when Step 1/2 can state it clearly; do not jump to Step 3.",
            "- Do not invent fabrics, colors, hardware, garment pieces, or placements not present in the Original text. No brand or runway essay.",
            "- Macro work order: (1) strip conceptual/editorial prose via rewrite; (2) unify contradictions/implausible wear by rewriting into one coherent reading; "
            "(3) converge trunk silhouette and material mood through clearer phrasing; (4) only then trim duplicate or weak-imaging ornament by deletion if rewrite failed.",
            "- Trunk paired extremes (outerwear, inner/base top, bottoms, shoes, and when described, outerwear lining or trouser inner lining vs shell): when two grounded extremes clash (e.g. long scarf-like sleeve vs cropped opposite sleeve, dueling lapels), "
            "Step 1 — merge into ONE light asymmetric line or one unified sleeve/silhouette reading; Step 2 — rewrite the same conflicting span again for stronger convergence; Step 3 — only then omit the WEAKER grounded branch (minimal span).",
            "- **No stacked trunk L/R catalogs** in the final paragraph: if the text still lists multiple simultaneous trunk contrasts (jacket sleeve mismatch + different legs + different shoe families + gloved vs bare hand as extra trunk split), you MUST converge or delete enough branches to leave **one** dominant upper, bottom, and shoe grammar for image generation—preserving every opposite is forbidden when penalties flag it.",
        ]
        if penalty_gate_failed:
            gate_priority_lines.append(
                "- Penalty gate is NOT satisfied: enforce Step 1 + Step 2 on each active penalty item before any Step 3 deletion."
            )
        if not delete_enabled:
            gate_priority_lines.append(
                "- Hard guard active: do not output deletion-oriented edits this round; only rewrite and rewrite-again are allowed."
            )
        gate_priority_text = "\n".join(gate_priority_lines)

        late_round_escalation = ""
        ri = int((strategy or {}).get("round_index") or 1)
        soft_max = 1
        tight_round = 2
        late_escalation_start = 3
        stronger_start = 4
        final_round = 5
        trunk_round_block = (
            f"ROUND {ri} — TRUNK EXTREMES (escalates each optimization round; rewrite-rewrite before deleting one side):\n"
            "- Step 1: on trunk garments, merge paired opposites into ONE light asymmetric phrase or one unified sleeve/silhouette (stay grounded).\n"
            "- Step 2: rewrite the same flagged span again with stronger convergence and simpler visual grammar.\n"
            + (
                "- Step 3: omit the weaker grounded branch only after Steps 1-2 were applied; use minimal deletion.\n"
                if delete_enabled
                else "- Step 3: LOCKED this round by guard; do not omit branches yet.\n"
            )
        )
        if ri <= soft_max:
            late_round_escalation = trunk_round_block + (
                "- Round 1 emphasis: merge/soften/rephrase only; do not drop a whole-side extreme before a genuine rewrite on the conflicting spans.\n\n"
            )
        elif ri == tight_round:
            late_round_escalation = trunk_round_block + (
                (
                    "- Round 2: stronger merge on the same passages; if checklist still flags the same trunk clash after Steps 1-2, Step 3 is allowed—drop the weaker extreme cue.\n\n"
                    if delete_enabled
                    else "- Round 2: stronger merge on the same passages; Step 3 remains locked this round.\n\n"
                )
            )
        else:
            late_round_escalation = trunk_round_block + (
                "- Round 3+: merge exhaustively first on flagged spans; then allow stronger omission of remaining deconstruction symbols if penalties persist.\n\n"
            )
        if ri >= late_escalation_start:
            late_round_escalation += (
                "LATE-ROUND DECONSTRUCTION CONVERGENCE (optimization round >= 3):\n"
                "Still use THREE STEPS: (1) REWRITE—converge extreme left/right sleeve language, shorten or rephrase scarf-like tails, "
                "clarify slash openings and inner panels into one readable sentence, reduce lapel asymmetry in wording. "
                "(2) REWRITE AGAIN—apply a second-pass convergence on the same harmful evidence. "
                "(3) DELETE only if those passages still draw penalties after two rewrites. Lowering penalties matters more than keeping every avant-garde cue, "
                "but do not delete until Steps 1-2 are genuinely tried on the harmful spans.\n\n"
            )
        if ri >= stronger_start:
            late_round_escalation += (
                "STRONGER CONVERGENCE (round >= 4): Penalty minimization over maximal drama. After two exhaustive rewrite passes (Step 1-2), "
                "omit or flatten remaining experimental constructions (Step 3) only where they still trigger mild penalties.\n\n"
            )
        if ri >= final_round:
            late_round_escalation += (
                "FINAL ROUND (5): Push penalties toward zero. First pass: rewrite the whole prompt for coherence. Second pass: remove only "
                "what still harms scores; keep core categories, palette, materials; deconstruction one light phrase or removed only if rewrite cannot save it.\n\n"
            )

        forced_bc = bool((strategy or {}).get("forced_consistency_bilateral_choice"))
        forced_bilateral_block = ""
        if forced_bc:
            forced_bilateral_block = (
                "MANDATORY — After optimization round 2, the evaluated text still has consistency_penalty > 0 with asymmetry-related judge reasons. "
                "You MUST output a hard binary choice for every flagged trunk conflict (no paired opposing extremes on one garment):\n"
                "- For sleeves, lapels, shoulders, or shell vs described lining, pick EXACTLY ONE grounded outcome: unify into one symmetric or mild-asymmetric reading, "
                "or align entirely to one side’s grounded details, or delete the weaker branch—do NOT keep both extremes (e.g. scarf-like long sleeve AND cropped opposite sleeve; "
                "two competing lapels; lining vs shell as unrelated garment identities unless Original clearly separates layers).\n"
                "- If several trunk zones still enumerate left-vs-right splits (upper + pants + shoes), **delete** enough weaker lines (one full leg description, one shoe, one glove hand, etc.) so the prompt reads as **one** imageable subject—not a list of parallel opposites.\n"
                "- Outerwear lining and trouser inner lining are trunk when the text describes them: one coherent lining narrative with the shell.\n"
                "Stay grounded in the Original; do not invent facts.\n\n"
            )

        rewrite_basis_intro = (
            "REWRITE BASIS — current best draft (dual-gate-first selection):\n"
            "The paragraph under 'Original text' at the end IS the best candidate so far, chosen primarily to pass both score and penalty gates, "
            "then by lower total_penalty / higher score-gate value, then asymmetry penalties and total score.\n"
            "The evaluation summary, penalty checklist, and optimization targets below are from THAT draft’s evaluator output—use them for targeted fixes only.\n"
            "Address the judge’s stated reasons and quoted evidence; do not optimize for issues that only appeared on abandoned exploratory drafts.\n\n"
        )
        peak_penalty_evidence = self._build_rewrite_basis_evidence_lines(evaluation_result)

        return (
            "You are rewriting a fashion text description after it has already been scored by the evaluator.\n"
            "Use the evaluation feedback to perform targeted optimization.\n"
            "Work through the PENALTY REPAIR CHECKLIST item by item using the three-step policy: Step 1 rewrite, Step 2 rewrite again, Step 3 delete only if needed.\n"
            "Preserve grounded garment facts from the original text; remove non-visual essay prose, repetition, and noisy meta-instructions.\n"
            "When multiple garments exist, explicitly keep attributes bound to the correct garment.\n"
            "Treat silhouette-defining outerwear, inner/base top layer when present, bottom category, footwear family, primary palette, and main material family as the visual trunk of the look "
            "(trunk includes inner and outer upper-body garments plus pants/skirt and shoes; when described, outerwear lining and trouser inner lining count as trunk with their shell).\n"
            "Reject trunk asymmetry by default: do not keep left-right split identities on trunk garments.\n"
            "Force trunk convergence to one readable grammar across outerwear, inner/base top, bottoms, and footwear.\n"
            "If asymmetry remains after rewrite/rewrite-again, delete the weaker branch instead of preserving controlled asymmetry.\n"
            "Return only the optimized fashion prompt in one coherent paragraph.\n\n"
            f"{rewrite_basis_intro}"
            f"{peak_penalty_evidence}"
            f"{gate_priority_text}\n\n"
            f"{late_round_escalation}"
            f"{forced_bilateral_block}"
            f"{penalty_checklist}\n\n"
            f"Asymmetry control policy:\n{asymmetry_policy}\n\n"
            f"Optimization targets:\n{targets_text}\n\n"
            f"Evaluation summary:\n{summary_text}\n\n"
            f"Original text:\n{text_description}\n"
        )

    _ASYM_PENALTY_KEYS = frozenset({"consistency_penalty", "coordination_penalty"})

    @staticmethod
    def _consistency_penalty_reason_implies_bilateral_asymmetry(reason: str, evidence: Any) -> bool:
        """Judge reason/evidence 是否仍指向左右或同件不对称类 consistency 问题（用于第3轮起强制二选一，即第2轮结束后）。"""
        parts: List[str] = [reason or ""]
        if isinstance(evidence, str):
            parts.append(evidence)
        elif isinstance(evidence, list):
            parts.extend(str(x) for x in evidence)
        blob = " ".join(parts).lower()
        needles = (
            "asymmet",
            "left-right",
            "left and right",
            "left vs",
            "right vs",
            "left side",
            "right side",
            "bilateral",
            "one sleeve",
            "other sleeve",
            "opposite sleeve",
            "both sleeves",
            "scarf-like",
            "cropped",
            "lapel",
            "shoulder",
            "competing",
            " split ",
            "conflicting",
            "same-garment",
            "mismatched",
            "左右",
            "不对称",
            "双侧",
            "互斥",
            "割裂",
            "双袖",
            "一侧",
            "对侧",
        )
        return any(n in blob for n in needles)

    def _build_asymmetry_priority_targets(self, evaluation_result: Dict) -> List[str]:
        """左右/一致性/协调性相关目标：排在优化提示最前，优先于其它 penalty 与整体文笔。"""
        penalty_items = evaluation_result["scores"]["quality_score"]["penalties"].get("items", {})
        metric_results = evaluation_result.get("metric_results", {})
        cons = float(penalty_items.get("consistency_penalty", {}).get("score", 0.0) or 0.0)
        coord = float(penalty_items.get("coordination_penalty", {}).get("score", 0.0) or 0.0)
        bilateral_weak = self._is_low_quality_metric(metric_results, "bilateral_coherence")
        if cons <= 0 and coord <= 0 and not bilateral_weak:
            return []

        lines: List[str] = [
            "【优先】先处理不对称、左右绑定、主干一致性与造型协调（consistency / coordination / bilateral），"
            "再处理生成导向文案、信息密度与其它质量维度。",
            "【主干对撞】双袖/双驳领等极端对撞：先合并为一句轻描或统一廓形/袖线（改写），禁止未改写先删；仅当改写后仍触发上述惩罚时，再删较弱一侧极端（最小删除）。",
            "【多区左右分裂】若上装袖态、裤腿材质/裤型、双脚鞋型等多处同时左右对打，合并一轮后仍像多套主体，必须整支删除弱侧（删一整腿异料叙述、删一只异鞋、删多余手套线等），不得保留长串并列对撞。",
        ]
        penalty_target_map = self._get_penalty_target_map("optimizer_target")
        if bilateral_weak:
            lines.append("左右或双侧元素若存在差异，需要收束到同一设计语言中，并明确其设计意图。")
            lines.append("主干部分必须对称或同源，不保留局部结构和边缘细节中的主干不对称。")
        if cons > 0:
            t = penalty_target_map.get("consistency_penalty")
            if t:
                lines.append(t)
            lines.append("外穿与内搭上装、裤装、鞋等主干单品在左右关系上应尽量保持同源与稳定，不要让多处主干差异同时争夺视觉中心。")
            lines.append("避免同一物件被写成多个互斥状态或互相冲突的单品身份。")
            lines.append("外套、内搭、下装、鞋履的轮廓与主色系、主材质语气应保持统一衔接，主干不允许不对称分叉。")
        if coord > 0:
            t = penalty_target_map.get("coordination_penalty")
            if t:
                lines.append(t)
            lines.append("削弱与整体气质明显违和的搭配，让鞋履、配件和局部设计服务于同一造型氛围。")
            lines.append(
                "若上装为单件却左右呈现西装精裁与礼服化泡袖/露肩/强对撞材质等互斥语境，"
                "应收束为同一造型语气或改为外套与内搭分件描述，避免半件正装半件另一品类的极端违和。"
            )
        return lines

    def _build_improvement_targets(self, evaluation_result: Dict) -> List[str]:
        scores = evaluation_result["scores"]
        penalties = scores["quality_score"]["penalties"]
        penalty_items = penalties.get("items", {})
        targets: List[str] = []
        targets.extend(self._gate_failure_target_lines(evaluation_result))
        targets.extend(self._build_asymmetry_priority_targets(evaluation_result))

        penalty_target_map = self._get_penalty_target_map("optimizer_target")
        for penalty_key, target in penalty_target_map.items():
            if penalty_key in self._ASYM_PENALTY_KEYS:
                continue
            penalty_score = float(penalty_items.get(penalty_key, {}).get("score", 0.0))
            if penalty_score > 0:
                targets.append(target)

        diagnosis = evaluation_result.get("diagnosis", {})
        if diagnosis.get("missing_information"):
            targets.append("补齐原文中已经隐含但未被清晰组织的关键信息类别，不得编造新事实。")
        if diagnosis.get("quality_issues"):
            targets.append("针对低质量指标提高术语精确度、结构顺序和 prompt 可用性。")

        metric_results = evaluation_result.get("metric_results", {})
        if self._is_low_quality_metric(metric_results, "spatial_coherence"):
            targets.append("明确层次、内外、前后、上下和附着位置等空间关系，避免难以成像的空间冲突。")
        if self._is_low_quality_metric(metric_results, "visibility_priority"):
            targets.append("优先保留可见且决定成像结果的主体信息，压缩隐藏内里、内部结构和低可见度细节的篇幅。")

        if float(penalty_items.get("rationality_penalty", {}).get("score", 0.0) or 0.0) > 0:
            targets.append("删除或收束违反客观规律、现实材质条件或基本穿着常识的设定，只保留可成立的视觉事实。")

        if not targets:
            targets.append("在不新增未提供事实的前提下，提升简洁性、结构化程度和可直接生成图像的可用性。")
        return targets

    @staticmethod
    def _asymmetry_related_penalty_sum(result: Dict) -> float:
        """一致性 + 协调性惩罚分值之和，用于优化择优时优先于 total_penalty 与总分。"""
        items = (result.get("scores") or {}).get("quality_score", {}).get("penalties", {}).get("items", {})
        c = float((items.get("consistency_penalty") or {}).get("score", 0.0) or 0.0)
        coord = float((items.get("coordination_penalty") or {}).get("score", 0.0) or 0.0)
        return c + coord

    def _select_weak_modules(self, module_scores: Dict[str, Dict]) -> List[Dict]:
        weak_modules = []
        for module_name, module_result in module_scores.items():
            if float(module_result.get("score", 0.0)) >= 0.9999:
                continue
            weak_modules.append(
                {
                    "module": module_name,
                    "score": module_result.get("score", 0.0),
                    "applicable_metrics": module_result.get("applicable_metrics", 0),
                    "hit_metrics": module_result.get("hit_metrics", 0),
                }
            )
        weak_modules.sort(key=lambda item: item["score"])
        return weak_modules[:8]

    def _select_low_quality_metrics(self, metric_results: Dict[str, Dict]) -> List[Dict]:
        selected = []
        for metric_name, result in metric_results.items():
            if result.get("axis") != "quality_score" or not result.get("applicable"):
                continue
            score_value = float(result.get("score_value", 0.0) or 0.0)
            if score_value >= 1.0:
                continue
            selected.append(
                {
                    "metric": metric_name,
                    "quality_dimension": result.get("quality_dimension"),
                    "quality_dimension_zh": result.get("quality_dimension_zh"),
                    "score_value": score_value,
                    "rule": result.get("rule", ""),
                    "reason": result.get("reason", ""),
                    "matched_terms": result.get("matched_terms", []),
                }
            )
        selected.sort(key=lambda item: item["score_value"])
        return selected[:12]

    def _normalize_optimized_text(self, text: str) -> str:
        cleaned = self.judge._clean_output(text)
        cleaned = re.sub(r"\s*\n+\s*", " ", cleaned).strip()
        return cleaned

    def _get_penalty_keys(self) -> List[str]:
        return list(self.penalty_registry.keys())

    def _get_penalty_target_map(self, field_name: str) -> Dict[str, str]:
        return {
            penalty_key: cfg.get(field_name, "")
            for penalty_key, cfg in self.penalty_registry.items()
            if cfg.get(field_name)
        }

    def _get_unresolved_penalty_keys(self) -> List[str]:
        return [
            penalty_key
            for penalty_key, cfg in self.penalty_registry.items()
            if cfg.get("counts_for_unresolved_stop", False)
        ]

    def _safe_file_stem(self, source_name: str) -> str:
        raw_stem = Path(source_name).stem or "inline_text"
        safe_stem = re.sub(r"[^A-Za-z0-9._-]+", "_", raw_stem).strip("._")
        return safe_stem or "inline_text"

    def _build_asymmetry_control_policy(self, round_index: int) -> Dict[str, Any]:
        trunk = [
            "outerwear silhouette",
            "outerwear lining when described",
            "inner/base top layer",
            "bottom category",
            "trouser inner lining when described",
            "footwear family",
            "primary palette",
            "main material family",
        ]
        soft_max = 1
        tight_round = 2
        strong_round = 3
        if round_index <= soft_max:
            return {
                "stage": "soft_convergence",
                "core_rule": "主干部分必须保持对称或同源，拒绝主干不对称。",
                "trunk_extreme_merge_delete": "第1轮：双袖/双驳领等对撞以合并、轻描、重述为单一可读表述为主；原则上不在充分改写前删整侧极端。",
                "trunk_elements": trunk,
                "allowed_difference_zones": [],
                "disallowed_difference_zones": [
                    "multiple simultaneous trunk-level divergences",
                    "competing left-right garment identities",
                    "conflicting primary material families",
                ],
            }
        if round_index == tight_round:
            return {
                "stage": "tight_convergence",
                "core_rule": "收束阶段：主干必须稳定统一，不保留会打散主体识别的左右分叉；开始收敛明显解构（大开衩露内搭、双袖极端差异等）为更可读的表述。",
                "trunk_extreme_merge_delete": "第2轮：在上一轮合并基础上加强同一冲突的改写；若 checklist 仍指向同一主干对撞，允许在完整改写后删去较弱一侧极端（最小删除）。",
                "trunk_elements": trunk,
                "allowed_difference_zones": [],
                "disallowed_difference_zones": [
                    "multiple simultaneous trunk-level asymmetries",
                    "left-right divergence that splits the overall look identity",
                    "conflicting primary material families",
                    "scarf-like sleeve tail vs cropped opposite sleeve as competing trunk cues",
                ],
            }
        if round_index == strong_round:
            return {
                "stage": "strong_deconstruction_pullback",
                "core_rule": "强收敛：显著弱化非常规结构——左右袖长/袖型极端对撞、裤侧大开衩+第二裤型内露、超长拖袖尾等，改写为统一轮廓或仅保留一句轻描；优先可成像与 penalty 下降。",
                "trunk_extreme_merge_delete": "第3轮：必须先对 flagged 段落完成合并/轻描；仍触发 consistency/coordination 时，果断删较弱一侧极端或多余解构符号。",
                "trunk_elements": trunk,
                "allowed_difference_zones": [],
                "disallowed_difference_zones": [
                    "dual sleeve length extremes that read as two different garments",
                    "trouser slash reveals with a second inner bottom category",
                    "multiple simultaneous avant-garde construction cues on the trunk",
                ],
            }
        return {
            "stage": "penalty_first_max_convergence",
            "core_rule": "末段以压低惩罚优先：允许明显削弱原稿中的强解构符号（在仍有 grounded 前提下），收束为单一、稳态 look；复杂非常规结构可删或改为常规西装/裤装表述。",
            "trunk_extreme_merge_delete": f"第{round_index}轮：合并穷尽后，优先删仍拉高惩罚的主干解构符号，保留核心品类/色料/廓形。",
            "trunk_elements": trunk,
            "allowed_difference_zones": [],
            "disallowed_difference_zones": [
                "any remaining structure that still reads as experimental runway deconstruction on left-right or slash-inner-layer",
                "footwear or bottoms that fight a converged tailored trunk",
            ],
        }

    def _render_asymmetry_policy_text(self, strategy: Optional[Dict]) -> str:
        policy = strategy.get("asymmetry_control", {}) if strategy else {}
        lines = [
            f"- Stage: {policy.get('stage', 'soft_convergence')}",
            f"- Core rule: {policy.get('core_rule', 'Keep trunk elements stable and asymmetry controlled.')}",
        ]
        trunk_md = policy.get("trunk_extreme_merge_delete")
        if trunk_md:
            lines.append(f"- Trunk extremes (merge before delete, by round): {trunk_md}")
        trunk_elements = policy.get("trunk_elements", [])
        if trunk_elements:
            lines.append(f"- Trunk elements: {', '.join(trunk_elements)}")
        allowed_zones = policy.get("allowed_difference_zones", [])
        if allowed_zones:
            lines.append(f"- Allowed difference zones: {', '.join(allowed_zones)}")
        disallowed_zones = policy.get("disallowed_difference_zones", [])
        if disallowed_zones:
            lines.append(f"- Disallowed difference zones: {', '.join(disallowed_zones)}")
        return "\n".join(lines)

    def _build_round_strategy(
        self,
        current_result: Dict,
        previous_result: Optional[Dict],
        round_history: List[Dict],
        round_index: int,
        min_score_improvement: float,
        min_quality_improvement: float,
        per_key_rewrite_counts: Optional[Dict[str, int]] = None,
    ) -> Dict:
        current_penalties = current_result["scores"]["quality_score"]["penalties"]
        current_metrics = current_result.get("metric_results", {})
        current_modules = current_result["scores"].get("module_scores", {})

        stubborn_penalties = self._select_stubborn_penalties(current_result, previous_result)
        stubborn_metrics = self._select_stubborn_metrics(current_result, previous_result)
        weak_modules = self._select_weak_modules(current_modules)[:4]
        asymmetry_control = self._build_asymmetry_control_policy(round_index)
        strategy_notes = self._build_strategy_notes(
            current_result=current_result,
            round_history=round_history,
            round_index=round_index,
            min_score_improvement=min_score_improvement,
            min_quality_improvement=min_quality_improvement,
        )

        penalty_target_map = self._get_penalty_target_map("round_strategy_target")
        metric_target_map = {
            "generation_readiness": "把文本收束成可直接生成的 prompt 句式，减少说明性和编辑性表达。",
            "visibility_priority": "主体单品的可见廓形、材质、颜色和外部造型必须优先于隐藏内里和局部弱可见细节。",
            "spatial_coherence": "明确内外、上下、前后、叠搭和附着位置，避免空间关系模糊。",
            "bilateral_coherence": "如果保留左右差异，确保差异在材质、色调和造型语言上仍然可统一识别。",
            "attribute_entity_binding": "把属性和单品绑定写得更集中，避免一个句子跨多个实体切换。",
            "multi_garment_binding": "多单品描述时按单品分段组织，减少同一句里左右腿、左右脚、上装和配件混写。",
            "reference_clarity": "减少代词、省略和跳跃指代，直接点名对应单品和部位。",
            "quantity_accuracy": "保留关键数字，但避免过多并列尺寸细节影响主结构识别。",
            "information_ordering": "先主体，再结构，再材质颜色，再配饰，保持固定顺序。",
            "core_information_density": "减少次要配件和概念性补充，提升主体服装信息占比。",
        }
        active_penalties = self._select_active_penalties(current_penalties)
        active_penalty_keys = {item["penalty_key"] for item in active_penalties}
        rewrite_guard = self._build_penalty_rewrite_guard(active_penalty_keys, per_key_rewrite_counts)

        additional_targets = [
            "【多轮核心目标】以得分门与惩罚门同时通过为首要目的；择优时优先保留使任一门通过、或使 total_penalty 下降、或使得分门加权值上升的改写，不必以总分为唯一标准。",
            "多轮次·三步策略：对拉高 penalty、矛盾或难成像的表述，先改写、再重写同一证据片段；仅当两次改写后仍无法消除问题时再删除最小必要片段。",
        ]
        for item in stubborn_penalties:
            target = penalty_target_map.get(item["penalty_key"])
            if target:
                additional_targets.append(target)
        for item in stubborn_metrics:
            target = metric_target_map.get(item["metric"])
            if target:
                additional_targets.append(target)
        if "generation_content_penalty" in active_penalty_keys:
            additional_targets.append(
                "压缩重复与解释性表述：先改写为紧凑 prompt 句式；仍占篇幅且弱成像的再删除弱可见、无关与元指令类内容。"
            )
        if "consistency_penalty" in active_penalty_keys:
            additional_targets.append("主干拒绝不对称：外套、内搭、下装、鞋履必须左右同类同源。")
            additional_targets.append("若同一物件被描述成多个互斥状态，优先保留最稳定的一种绑定关系。")
            additional_targets.append("衣、裤、鞋作为主干必须对称与稳定，禁止主类别左右切换。")
            additional_targets.append("通过统一主色、主材质和主轮廓增强收束感，不保留主干不对称。")
            soft_max = 1
            tight_round = 2
            if round_index <= soft_max:
                additional_targets.append(
                    "【consistency·本轮】主干左右对撞（如双袖极端）：以合并为一句轻描、统一袖线/廓形为主，不优先删整侧极端。"
                )
            elif round_index == tight_round:
                additional_targets.append(
                    "【consistency·本轮】若合并后仍判主干互斥，在已充分改写 flagged 段落后，可删较弱一侧极端表述（最小删除）。"
                )
            else:
                additional_targets.append(
                    "【consistency·本轮】先穷尽合并/轻描 flagged 主干对撞，再删仍拉高惩罚的解构符号。"
                )
        if "coordination_penalty" in active_penalty_keys:
            additional_targets.append("清理与整体风格明显违和的搭配，确保鞋履、配件和主体服装在气质上互相衬托。")
            additional_targets.append("优先消除单件上装左右互斥的风格场域（精裁西装式半侧 vs 对侧泡袖露肩高光泽丝绸等），统一为可成像的单一上装语法或明确分层。")
            soft_max = 1
            tight_round = 2
            if round_index <= soft_max:
                additional_targets.append(
                    "【coordination·本轮】主干场域对撞先通过合并语气、过渡句、统一材质家族来收敛，不优先删一侧气质描写。"
                )
            elif round_index == tight_round:
                additional_targets.append(
                    "【coordination·本轮】加强合并后若仍违和，可删较弱一侧的极端场域描写（最小删除）。"
                )
            else:
                additional_targets.append(
                    "【coordination·本轮】合并优先；仍冲突时删较弱主干分支上的极端气质符号。"
                )
        if "rationality_penalty" in active_penalty_keys:
            additional_targets.append("去掉不符合现实材质条件或穿着逻辑的主体设定，避免模型生成不可成立的服装。")
        penalty_gate_failed = not bool((current_result.get("gates") or {}).get("penalty_gate", {}).get("passed"))
        penalty_tradeoff_start = 2
        late_escalation_start = 3
        stronger_start = 4
        final_round = 5
        if round_index >= penalty_tradeoff_start:
            additional_targets.append("本轮比上一轮更强调收束：若主干元素仍存在左右分叉，优先统一主干，再保留边缘层差异。")
        if round_index >= late_escalation_start:
            additional_targets.append(
                "后续轮次·强收敛解构：在不过度编造前提下，显著弱化左右袖/袖型极端对撞、裤腿开衩露内搭或第二裤型、单侧超长拖袖尾等非常规结构，改写为统一、易成像的轮廓。"
            )
        if round_index >= stronger_start:
            additional_targets.append(
                "本轮以压低惩罚优先：先改写以削弱强解构符号（scarf-like 长袖尾、大面积不对称驳领、开衩内露等），收束为单一可读 look；仅当改写后仍触发 mild penalty 时再删减该复杂结构。"
            )
        if round_index >= final_round:
            additional_targets.append(
                "末轮极限收束：优先使 penalty 逼近 0；仅保留输入中最核心的品类、色料与 silhouette，解构改为一句轻描或删除。"
            )
        if penalty_gate_failed and round_index >= penalty_tradeoff_start:
            additional_targets.append(
                "惩罚门仍未通过：在 grounded 范围内可牺牲部分 avant-garde 细节以换取更低 total_penalty，不必保留全部原始解构强度。"
            )
        if round_history:
            last_round = round_history[-1]
            score_stall = min_score_improvement
            quality_stall = min_quality_improvement
            if last_round["score_delta"] < score_stall:
                additional_targets.append("上一轮总分提升有限，本轮允许更激进地删除次要细节，优先换取更稳定的成像结果。")
            if last_round["quality_delta"] < quality_stall:
                additional_targets.append("上一轮质量提升有限，本轮优先解决仍未改善的低质量区域，而不是继续补充新信息。")

        forced_consistency_bilateral_choice = False
        forced_start = 3
        if round_index >= forced_start:
            penalties_block = (current_result.get("scores") or {}).get("quality_score", {}).get("penalties") or {}
            cons_item = (penalties_block.get("items") or {}).get("consistency_penalty") or {}
            try:
                cscore = float(cons_item.get("score", 0.0) or 0.0)
            except (TypeError, ValueError):
                cscore = 0.0
            if cscore <= 0:
                try:
                    cscore = float(penalties_block.get("consistency_penalty", 0.0) or 0.0)
                except (TypeError, ValueError):
                    cscore = 0.0
            if cscore > 0:
                reason = (cons_item.get("reason") or "").strip()
                evidence = cons_item.get("evidence") or []
                forced_consistency_bilateral_choice = self._consistency_penalty_reason_implies_bilateral_asymmetry(
                    reason, evidence
                )
        if forced_consistency_bilateral_choice:
            additional_targets.append(
                "【强制·consistency】第2轮结束后当前最优稿仍 consistency>0 且裁判原因含不对称：本轮必须二选一——同一主干（含外套里布/裤装内衬若原文已写）禁止并列互斥左右或壳衬对撞；统一为单一可读结构或删较弱 grounded 分支，不得同时保留对打的双袖/双驳领等。"
            )
        if not rewrite_guard.get("delete_enabled"):
            additional_targets = self._strip_delete_guidance_targets(
                additional_targets,
                rewrite_guard.get("per_key_delete_enabled"),
            )
            if rewrite_guard.get("has_active_penalties"):
                locked_keys = [
                    k for k, v in rewrite_guard.get("per_key_delete_enabled", {}).items() if not v
                ]
                additional_targets.append(
                    f"【删除闸门】以下 penalty keys 尚未完成两次 rewrite，不允许删除导向：{locked_keys}。"
                    " 本轮仅允许改写（rewrite）路径；重写（rewrite-again）后仍无法消除的 penalty 才可进入删除步骤。"
                )

        return {
            "round_index": round_index,
            "current_total_score": current_result.get("total_score"),
            "current_quality_score": current_result["scores"]["quality_score"].get("penalized_score"),
            "gates": current_result.get("gates"),
            "active_penalties": active_penalties,
            "stubborn_penalties": stubborn_penalties,
            "stubborn_metrics": stubborn_metrics,
            "weak_modules": weak_modules,
            "asymmetry_control": asymmetry_control,
            "strategy_notes": strategy_notes,
            "additional_targets": self._dedupe_preserve_order(additional_targets),
            "forced_consistency_bilateral_choice": forced_consistency_bilateral_choice,
            "penalty_rewrite_guard": rewrite_guard,
            "per_key_rewrite_counts": per_key_rewrite_counts or {},
        }

    @staticmethod
    def _build_penalty_rewrite_guard(
        active_penalty_keys: Set[str],
        per_key_rewrite_counts: Optional[Dict[str, int]] = None,
    ) -> Dict[str, Any]:
        """
        Per-key rewrite guard: delete_enabled per penalty key only after that key
        has been through at least 1 rewrite attempt.  Tracks progress for each
        active key independently rather than gating on global round number.
        """
        has_active = bool(active_penalty_keys)
        per_key_counts = per_key_rewrite_counts or {}
        per_key_guard: Dict[str, bool] = {}
        delete_enabled_overall = True

        for key in sorted(active_penalty_keys):
            count = per_key_counts.get(key, 0)
            enabled = count >= 1
            per_key_guard[key] = enabled
            if not enabled:
                delete_enabled_overall = False

        return {
            "has_active_penalties": has_active,
            "active_penalty_keys": sorted(active_penalty_keys),
            "per_key_rewrite_counts": dict(per_key_counts),
            "per_key_delete_enabled": per_key_guard,
            "delete_enabled": delete_enabled_overall,
            "rewrite_pass_1_done_per_key": {k: v >= 1 for k, v in per_key_counts.items()},
        }

    @staticmethod
    def _strip_delete_guidance_targets(
        targets: List[str],
        per_key_delete_enabled: Optional[Dict[str, bool]] = None,
    ) -> List[str]:
        """
        Strip delete guidance from targets unless the key's delete step is already unlocked.
        Operates per penalty key: only removes delete guidance for keys that haven't yet
        completed one rewrite pass.
        """
        zh_markers = ("删除", "删减", "删去", "删较弱", "删一", "删支")
        enabled_keys = {
            k for k, v in (per_key_delete_enabled or {}).items() if v
        }
        kept: List[str] = []
        for t in targets:
            # If ALL active penalty keys have delete enabled, keep everything.
            if per_key_delete_enabled and enabled_keys == set(per_key_delete_enabled.keys()) and enabled_keys:
                kept.append(t)
                continue
            low = t.lower()
            if any(k in t for k in zh_markers):
                continue
            if any(k in low for k in ("omit", "drop", "delete")):
                continue
            kept.append(t)
        return kept

    @staticmethod
    def _aggregate_per_key_rewrite_counts(round_history: List[Dict]) -> Dict[str, int]:
        """
        Aggregate rewrite attempt counts per penalty key across all completed rounds.
        A key is counted once per round if it appeared in that round's active_penalties,
        regardless of whether the rewrite actually eliminated the penalty.
        """
        counts: Dict[str, int] = {}
        for record in round_history:
            for key in record.get("attempted_penalty_keys", []):
                counts[key] = counts.get(key, 0) + 1
        return counts

    def _select_active_penalties(self, penalties: Dict) -> List[Dict]:
        active = []
        for key in self._get_penalty_keys():
            score = float(penalties.get(key, 0.0) or 0.0)
            if score <= 0:
                continue
            active.append(
                {
                    "penalty_key": key,
                    "score": score,
                    "reason": penalties.get("items", {}).get(key, {}).get("reason", ""),
                }
            )
        active.sort(key=lambda item: item["score"], reverse=True)
        return active

    def _select_stubborn_penalties(self, current_result: Dict, previous_result: Optional[Dict]) -> List[Dict]:
        current_penalties = current_result["scores"]["quality_score"]["penalties"]
        previous_penalties = previous_result["scores"]["quality_score"]["penalties"] if previous_result else {}
        stubborn = []
        for key in self._get_penalty_keys():
            current_score = float(current_penalties.get(key, 0.0) or 0.0)
            previous_score = float(previous_penalties.get(key, current_score) or 0.0)
            improved = round(previous_score - current_score, 4)
            if current_score <= 0:
                continue
            if previous_result is None or improved < 0.05:
                stubborn.append(
                    {
                        "penalty_key": key,
                        "current_score": current_score,
                        "previous_score": previous_score,
                        "improved": improved,
                        "reason": current_penalties.get("items", {}).get(key, {}).get("reason", ""),
                    }
                )
        stubborn.sort(key=lambda item: (item["improved"], -item["current_score"]))
        return stubborn[:5]

    def _select_stubborn_metrics(self, current_result: Dict, previous_result: Optional[Dict]) -> List[Dict]:
        current_metrics = current_result.get("metric_results", {})
        previous_metrics = previous_result.get("metric_results", {}) if previous_result else {}
        stubborn = []
        for metric_name, current_metric in current_metrics.items():
            if current_metric.get("axis") != "quality_score" or not current_metric.get("applicable"):
                continue
            current_score = float(current_metric.get("score_value", 0.0) or 0.0)
            previous_score = float(previous_metrics.get(metric_name, {}).get("score_value", current_score) or 0.0)
            improved = round(current_score - previous_score, 4)
            if current_score >= 0.75 and improved > 0:
                continue
            if previous_result is None or improved <= 0.0 or current_score < 0.75:
                stubborn.append(
                    {
                        "metric": metric_name,
                        "current_score": current_score,
                        "previous_score": previous_score,
                        "improved": improved,
                        "reason": current_metric.get("reason", ""),
                    }
                )
        stubborn.sort(key=lambda item: (item["current_score"], item["improved"]))
        return stubborn[:6]

    def _build_strategy_notes(
        self,
        current_result: Dict,
        round_history: List[Dict],
        round_index: int,
        min_score_improvement: float,
        min_quality_improvement: float,
    ) -> List[str]:
        notes = [f"当前为第 `{round_index}` 轮优化。"]
        penalties = current_result["scores"]["quality_score"]["penalties"]
        for penalty_key, cfg in self.penalty_registry.items():
            threshold = cfg.get("strategy_note_threshold")
            note = cfg.get("strategy_note")
            if threshold is None or not note:
                continue
            if float(penalties.get(penalty_key, 0.0) or 0.0) >= float(threshold):
                notes.append(note)
        if round_history:
            last_round = round_history[-1]
            score_stall = min_score_improvement
            quality_stall = min_quality_improvement
            if last_round["score_delta"] < score_stall:
                notes.append("上一轮总分提升有限，需要更激进的压缩与聚焦。")
            if last_round["quality_delta"] < quality_stall:
                notes.append("上一轮质量提升有限，本轮优先处理未改善的质量项。")
        return notes

    def _build_round_record(
        self,
        round_index: int,
        input_text: str,
        input_result: Dict,
        output_text: str,
        output_result: Dict,
        strategy: Dict,
    ) -> Dict:
        active_penalty_keys_in_round = {
            item["penalty_key"] for item in strategy.get("active_penalties", [])
        }
        return {
            "round_index": round_index,
            "input_text": input_text,
            "input_result": input_result,
            "output_text": output_text,
            "output_result": output_result,
            "score_delta": round(output_result["total_score"] - input_result["total_score"], 4),
            "quality_delta": round(
                output_result["scores"]["quality_score"]["penalized_score"]
                - input_result["scores"]["quality_score"]["penalized_score"],
                4,
            ),
            "attempted_penalty_keys": sorted(active_penalty_keys_in_round),
            "strategy": strategy,
        }

    def _is_better_result(self, candidate_result: Dict, reference_result: Dict) -> bool:
        """
        Ranking comparator for multi-round optimization candidate selection.

        Phase 1 — Gate resolution
            If one candidate passes both gates and the other does not,
            the one that passes both wins immediately.
            Special case: even if total_score is lower, a candidate that unblocks
            the penalty_gate (reference fails it) wins over one that does not.

        Phase 2 — Per-failed-gate dimension (only when gate not passed)
            score_gate    → higher score_gate value wins.
            penalty_gate  → lower total_penalty wins;
                            tie-break: lower (consistency_penalty + coordination_penalty).

        Phase 3 — Both gates passed (or neither unblocked)
            Prefer lower total_penalty.
            Tie-break: lower (consistency_penalty + coordination_penalty).
            Further tie-break: higher total_score.
        """
        c_both = self._gates_both_pass(candidate_result)
        r_both = self._gates_both_pass(reference_result)

        # ── Phase 1: Gate resolution ──────────────────────────────────────────
        if c_both and not r_both:
            return True
        if r_both and not c_both:
            return False

        # Both pass both gates, or both fail both gates — fall through.
        c_g = candidate_result.get("gates") or {}
        r_g = reference_result.get("gates") or {}
        c_pg_pass = bool((c_g.get("penalty_gate") or {}).get("passed"))
        r_pg_pass = bool((r_g.get("penalty_gate") or {}).get("passed"))
        c_sg_pass = bool((c_g.get("score_gate") or {}).get("passed"))
        r_sg_pass = bool((r_g.get("score_gate") or {}).get("passed"))

        # Special: candidate unblocks penalty_gate → accept it even if total is lower.
        if not r_pg_pass and c_pg_pass:
            return True

        # ── Phase 2: Per-failed-gate dimension ───────────────────────────────
        # score_gate not passed — compare score_gate value (higher is better).
        if not c_sg_pass and not r_sg_pass:
            c_sg_v = float((c_g.get("score_gate") or {}).get("value") or 0.0)
            r_sg_v = float((r_g.get("score_gate") or {}).get("value") or 0.0)
            if c_sg_v != r_sg_v:
                return c_sg_v > r_sg_v

        # penalty_gate not passed — compare total_penalty (lower is better).
        if not c_pg_pass and not r_pg_pass:
            c_pen = self._total_penalty(candidate_result)
            r_pen = self._total_penalty(reference_result)
            if c_pen != r_pen:
                return c_pen < r_pen
            # Tie-break: consistency + coordination (lower is better).
            c_asym = self._asymmetry_related_penalty_sum(candidate_result)
            r_asym = self._asymmetry_related_penalty_sum(reference_result)
            if c_asym != r_asym:
                return c_asym < r_asym

        # Only one fails score_gate → the other wins.
        if not c_sg_pass and r_sg_pass:
            return False
        if not r_sg_pass and c_sg_pass:
            return True

        # Only one fails penalty_gate → the one that passes wins (already covered above).
        # (Already handled: candidate passes → return True above; opposite handled here.)

        # ── Phase 3: Both candidates on same footing ───────────────────────────
        c_pen = self._total_penalty(candidate_result)
        r_pen = self._total_penalty(reference_result)
        if c_pen != r_pen:
            return c_pen < r_pen

        # Tie-break: consistency + coordination (lower is better).
        c_asym = self._asymmetry_related_penalty_sum(candidate_result)
        r_asym = self._asymmetry_related_penalty_sum(reference_result)
        if c_asym != r_asym:
            return c_asym < r_asym

        # Final tie-break: total_score (higher is better).
        c_total = float(candidate_result.get("total_score") or 0.0)
        r_total = float(reference_result.get("total_score") or 0.0)
        return c_total > r_total

    @staticmethod
    def _total_penalty(result: Dict) -> float:
        return round(
            float(
                result.get("scores", {})
                .get("quality_score", {})
                .get("penalties", {})
                .get("total_penalty", 0.0)
                or 0.0
            ),
            4,
        )

    def _should_stop_optimization(
        self,
        round_records: List[Dict],
        current_result: Dict,
        round_index: int,
        max_rounds: int,
        min_score_improvement: float,
        min_quality_improvement: float,
    ) -> bool:
        if not round_records:
            return True
        if self._gates_both_pass(current_result):
            return True
        if round_index >= max_rounds:
            return True
        last_round = round_records[-1]
        score_stall = min_score_improvement
        quality_stall = min_quality_improvement
        if (
            last_round["score_delta"] < score_stall
            and last_round["quality_delta"] < quality_stall
            and not last_round["strategy"].get("stubborn_penalties")
            and not last_round["strategy"].get("stubborn_metrics")
        ):
            return True
        return False

    def _dedupe_preserve_order(self, items: List[str]) -> List[str]:
        deduped = []
        for item in items:
            if item not in deduped:
                deduped.append(item)
        return deduped

    def _build_optimization_report(
        self,
        source_name: str,
        original_text: str,
        optimized_text: str,
        original_result: Dict,
        optimized_result: Dict,
        round_records: List[Dict],
    ) -> str:
        summary_lines = [
            f"- 来源文件：`{source_name}`",
            f"- 双门限同时满足：`{self._gates_both_pass(optimized_result)}`",
            f"- 原始总分：`{original_result['total_score']}`",
            f"- 优化后总分：`{optimized_result['total_score']}`",
            f"- 总分变化：`{round(optimized_result['total_score'] - original_result['total_score'], 4)}`",
            f"- 原始质量分：`{original_result['scores']['quality_score']['penalized_score']}`",
            f"- 优化后质量分：`{optimized_result['scores']['quality_score']['penalized_score']}`",
            f"- 原始分档：`{original_result['score_band']}`",
            f"- 优化后分档：`{optimized_result['score_band']}`",
        ]
        summary_lines.extend(self._format_gates_report_lines("原始", original_result.get("gates") or {}))
        summary_lines.extend(self._format_gates_report_lines("优化后", optimized_result.get("gates") or {}))

        penalty_lines = self._format_penalty_comparison(
            original_result["scores"]["quality_score"]["penalties"],
            optimized_result["scores"]["quality_score"]["penalties"],
        )
        penalty_detail_lines = self._format_penalty_details(
            original_result["scores"]["quality_score"]["penalties"],
            optimized_result["scores"]["quality_score"]["penalties"],
        )
        module_lines = self._format_module_comparison(
            original_result["scores"]["module_scores"],
            optimized_result["scores"]["module_scores"],
        )
        metric_lines = self._format_metric_comparison(
            original_result["metric_results"],
            optimized_result["metric_results"],
        )
        changed_metric_lines = self._format_changed_metric_details(
            original_result["metric_results"],
            optimized_result["metric_results"],
        )
        round_history_lines = self._format_round_history(round_records)
        round_text_lines = self._format_round_text_sections(round_records)

        summary_lines.append(f"- 已执行优化轮数：`{len(round_records)}`（默认最大 `max_rounds=5`，可能因双门限通过或停滞早停而提前结束）")

        return (
            "# Text Description Optimization Report\n\n"
            "## Summary\n"
            + "\n".join(summary_lines)
            + "\n\n## Penalty Comparison\n"
            + "\n".join(penalty_lines)
            + "\n\n## Penalty Repair Details\n"
            + "\n".join(penalty_detail_lines)
            + "\n\n## Round History\n"
            + "\n".join(round_history_lines)
            + "\n\n## Round Texts（各轮优化全文）\n"
            + "\n".join(round_text_lines)
            + "\n\n## Module Comparison\n"
            + "\n".join(module_lines)
            + "\n\n## Metric Comparison\n"
            + "\n".join(metric_lines)
            + "\n\n## Changed Metric Details\n"
            + "\n".join(changed_metric_lines)
            + "\n\n## Original Text\n\n"
            + original_text
            + "\n\n## Optimized Text\n\n"
            + optimized_text
            + "\n"
        )

    def _format_gates_report_lines(self, label: str, gates: Dict[str, Any]) -> List[str]:
        if not gates:
            return [f"- {label}门限：无 gates 数据（可能为旧版评估结果）"]
        sg = gates.get("score_gate") or {}
        pg = gates.get("penalty_gate") or {}
        return [
            f"- {label}·得分门限：加权值 `{sg.get('value')}` / 阈值 `{sg.get('threshold')}` / 通过 `{sg.get('passed')}`",
            f"- {label}·惩罚门限：total_penalty `{pg.get('total_penalty')}` / 阈值 `{pg.get('threshold')}` / 通过 `{pg.get('passed')}`",
        ]

    def _format_penalty_comparison(self, original_penalties: Dict, optimized_penalties: Dict) -> List[str]:
        lines = []
        keys = [*self._get_penalty_keys(), "total_penalty"]
        for key in keys:
            original_value = original_penalties.get(key, 0.0)
            optimized_value = optimized_penalties.get(key, 0.0)
            delta = round(float(optimized_value) - float(original_value), 4)
            lines.append(
                f"- `{key}`: `{original_value}` -> `{optimized_value}` (`{delta}`)"
            )
        return lines

    def _format_penalty_details(self, original_penalties: Dict, optimized_penalties: Dict) -> List[str]:
        lines = []
        keys = self._get_penalty_keys()
        for key in keys:
            before_item = original_penalties.get("items", {}).get(key, {})
            after_item = optimized_penalties.get("items", {}).get(key, {})
            before_score = float(original_penalties.get(key, 0.0) or 0.0)
            after_score = float(optimized_penalties.get(key, 0.0) or 0.0)
            lines.append(f"### `{key}`")
            lines.append(f"- 优化前分值：`{before_score}`")
            lines.append(f"- 优化后分值：`{after_score}`")
            lines.append(f"- 修复结果：{self._describe_penalty_repair(before_score, after_score)}")
            lines.append(f"- 优化前原因：{before_item.get('reason', '') or 'N/A'}")
            lines.append(f"- 优化后原因：{after_item.get('reason', '') or 'N/A'}")
            lines.append(f"- 优化前证据：{self._format_terms(before_item.get('evidence', []))}")
            lines.append(f"- 优化后证据：{self._format_terms(after_item.get('evidence', []))}")
            lines.append("")
        return lines

    def _describe_penalty_repair(self, before_score: float, after_score: float) -> str:
        if after_score < before_score:
            return f"已缓解，下降 `{round(before_score - after_score, 4)}`。"
        if after_score > before_score:
            return f"问题加重，上升 `{round(after_score - before_score, 4)}`。"
        if after_score == 0:
            return "无处罚，当前未发现该类问题。"
        return "未明显改善，仍需继续针对该问题优化。"

    def _format_round_history(self, round_records: List[Dict]) -> List[str]:
        if not round_records:
            return ["- 本次仅执行单轮结果对比，未记录中间回合。"]
        lines = []
        for round_record in round_records:
            strategy = round_record.get("strategy", {})
            lines.append(f"### Round `{round_record['round_index']}`")
            lines.append(
                f"- 分数变化：`{round_record['input_result']['total_score']}` -> "
                f"`{round_record['output_result']['total_score']}` "
                f"(`{round_record['score_delta']}`)"
            )
            lines.append(
                f"- 质量变化：`{round_record['input_result']['scores']['quality_score']['penalized_score']}` -> "
                f"`{round_record['output_result']['scores']['quality_score']['penalized_score']}` "
                f"(`{round_record['quality_delta']}`)"
            )
            lines.append(
                f"- 重点 penalty：{self._format_round_focus_items(strategy.get('stubborn_penalties', []), 'penalty_key')}"
            )
            lines.append(
                f"- 重点 metric：{self._format_round_focus_items(strategy.get('stubborn_metrics', []), 'metric')}"
            )
            lines.append(
                f"- 重点模块：{self._format_round_focus_items(strategy.get('weak_modules', []), 'module')}"
            )
            lines.append(
                f"- 策略备注：{'; '.join(strategy.get('strategy_notes', [])) or 'N/A'}"
            )
            lines.append(
                f"- 本轮附加修复目标：{'; '.join(strategy.get('additional_targets', [])) or 'N/A'}"
            )
            lines.append("")
        return lines

    def _format_round_text_sections(self, round_records: List[Dict]) -> List[str]:
        """各轮改写前输入与 LLM 输出全文，便于审阅优化过程。"""
        if not round_records:
            return [
                "- 未执行改写轮次（例如初始文本已满足双门限，或仅做评估未跑 optimize）。",
                "",
            ]
        lines: List[str] = []
        for round_record in round_records:
            idx = round_record.get("round_index", "?")
            inp = (round_record.get("input_text") or "").strip()
            out = (round_record.get("output_text") or "").strip()
            lines.append(f"### Round `{idx}` · 输入（本轮优化前）")
            lines.append("")
            lines.append("```")
            lines.append(inp or "—")
            lines.append("```")
            lines.append("")
            lines.append(f"### Round `{idx}` · 输出（本轮 LLM 改写）")
            lines.append("")
            lines.append("```")
            lines.append(out or "—")
            lines.append("```")
            lines.append("")
        return lines

    def _format_round_focus_items(self, items: List[Dict], key_name: str) -> str:
        if not items:
            return "N/A"
        return "; ".join(str(item.get(key_name, "")) for item in items if item.get(key_name))

    def _format_module_comparison(self, original_modules: Dict, optimized_modules: Dict) -> List[str]:
        lines = [
            "| Module | Before Score | After Score | Delta | Before Hits | After Hits | Before Applicable | After Applicable |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
        module_names = sorted(set(original_modules.keys()) | set(optimized_modules.keys()))
        for module_name in module_names:
            before = original_modules.get(module_name, {})
            after = optimized_modules.get(module_name, {})
            before_score = float(before.get("score", 0.0))
            after_score = float(after.get("score", 0.0))
            delta = round(after_score - before_score, 4)
            lines.append(
                f"| `{module_name}` | `{before_score}` | `{after_score}` | `{delta}` | "
                f"`{before.get('hit_metrics', 0)}` | `{after.get('hit_metrics', 0)}` | "
                f"`{before.get('applicable_metrics', 0)}` | `{after.get('applicable_metrics', 0)}` |"
            )
        return lines

    def _format_metric_comparison(self, original_metrics: Dict, optimized_metrics: Dict) -> List[str]:
        lines = [
            "| Metric | Axis | Before Applicable | After Applicable | Before Hit | After Hit | Before Score | After Score | Delta |",
            "|---|---|---|---|---|---|---:|---:|---:|",
        ]
        metric_names = sorted(set(original_metrics.keys()) | set(optimized_metrics.keys()))
        for metric_name in metric_names:
            before = original_metrics.get(metric_name, {})
            after = optimized_metrics.get(metric_name, {})
            before_score = self._format_metric_numeric(before.get("score_value"))
            after_score = self._format_metric_numeric(after.get("score_value"))
            delta = self._format_metric_delta(before.get("score_value"), after.get("score_value"))
            lines.append(
                f"| `{metric_name}` | `{before.get('axis', after.get('axis', ''))}` | "
                f"`{self._format_bool(before.get('applicable'))}` | `{self._format_bool(after.get('applicable'))}` | "
                f"`{self._format_hit(before.get('hit'))}` | `{self._format_hit(after.get('hit'))}` | "
                f"`{before_score}` | `{after_score}` | `{delta}` |"
            )
        return lines

    def _format_changed_metric_details(self, original_metrics: Dict, optimized_metrics: Dict) -> List[str]:
        lines = []
        metric_names = sorted(set(original_metrics.keys()) | set(optimized_metrics.keys()))
        for metric_name in metric_names:
            before = original_metrics.get(metric_name, {})
            after = optimized_metrics.get(metric_name, {})
            if not self._metric_changed(before, after):
                continue
            lines.append(f"### `{metric_name}`")
            lines.append(f"- 规则：`{before.get('rule', after.get('rule', ''))}`")
            lines.append(
                f"- 优化前：applicable=`{self._format_bool(before.get('applicable'))}`，"
                f"hit=`{self._format_hit(before.get('hit'))}`，"
                f"score=`{self._format_metric_numeric(before.get('score_value'))}`"
            )
            lines.append(
                f"- 优化后：applicable=`{self._format_bool(after.get('applicable'))}`，"
                f"hit=`{self._format_hit(after.get('hit'))}`，"
                f"score=`{self._format_metric_numeric(after.get('score_value'))}`"
            )
            lines.append(f"- 优化前原因：{before.get('reason', '') or 'N/A'}")
            lines.append(f"- 优化后原因：{after.get('reason', '') or 'N/A'}")
            lines.append(
                f"- 优化前命中证据：{self._format_terms(before.get('matched_terms', []))}"
            )
            lines.append(
                f"- 优化后命中证据：{self._format_terms(after.get('matched_terms', []))}"
            )
            lines.append("")
        if not lines:
            return ["- 无 metric 命中变化，主要变化体现在 penalty 与整体表达质量。"]
        return lines

    def _metric_changed(self, before: Dict, after: Dict) -> bool:
        comparable_keys = ("applicable", "hit", "score_value", "reason", "matched_terms")
        for key in comparable_keys:
            if before.get(key) != after.get(key):
                return True
        return False

    def _format_bool(self, value: Optional[bool]) -> str:
        if value is None:
            return "N/A"
        return "yes" if bool(value) else "no"

    def _format_hit(self, value: Optional[int]) -> str:
        if value is None:
            return "N/A"
        return str(value)

    def _format_metric_numeric(self, value: Optional[float]) -> str:
        if value is None:
            return "N/A"
        return str(round(float(value), 4))

    def _format_metric_delta(self, before: Optional[float], after: Optional[float]) -> str:
        if before is None or after is None:
            return "N/A"
        return str(round(float(after) - float(before), 4))

    def _format_terms(self, terms: List[str]) -> str:
        if not terms:
            return "N/A"
        return "; ".join(str(term) for term in terms[:8])

    def _is_low_quality_metric(self, metric_results: Dict[str, Dict], metric_name: str) -> bool:
        result = metric_results.get(metric_name, {})
        if not result or not result.get("applicable"):
            return False
        try:
            return float(result.get("score_value", 0.0) or 0.0) < QUALITY_FULL_HIT_THRESHOLD
        except (TypeError, ValueError):
            return False

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
    return DesignTextEvaluator(api_key=api_key, api_base=api_base, model=model, verify_ssl=verify_ssl)
