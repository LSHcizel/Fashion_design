"""Reverse-parse fashion images into detailed ``text_description`` documents."""

from __future__ import annotations

import base64
import http.client
import json
import mimetypes
import os
import re
import ssl
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Sequence, Union
from urllib.parse import urlparse

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO_ROOT / "fashion_config.yaml"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "outputs" / "image_inverse_parser"
IMAGE_MODEL_ENV = "IMAGE_INVERSE_MODEL"


SYSTEM_PROMPT = """You are a senior fashion image reverse parser.

Your job is to inspect the attached fashion image and reconstruct it as a detailed, image-faithful text_description document.

Core requirements:
1. Describe only what is visually supported by the image. Do not invent hidden closures, unseen back views, materials, brand names, or construction details.
2. Prioritize the worn look: silhouette, garment categories, proportions, neckline/collar, shoulders, sleeves, waist, hem/length, layering, color palette, visible surface/material cues, pattern/print, construction details, accessories, bag, footwear, styling, and overall mood.
3. Preserve spatial relationships: which garment is over/under, where details sit on the body, how top and bottom proportions relate, and whether the look is full-length, cropped, close-cut, oversized, sheer, structured, fluid, etc.
4. If something is uncertain, use careful visible-language such as "appears", "suggests", or omit it. Avoid vague filler.
5. Write in the same practical logic as a professional fashion text_description: one coherent paragraph, dense but readable, suitable for later image generation or fashion design analysis.
6. Do not describe the website UI, filename, watermark, or irrelevant background unless it changes the fashion reading.

Return strict JSON only with exactly these keys:
{
  "text_description": "one detailed paragraph",
  "key_elements": ["short visible element 1", "short visible element 2"],
  "uncertainty_notes": ["short note, or empty array"]
}"""


@dataclass
class ImageInverseConfig:
    api_key: str
    api_base: str
    model: str
    temperature: float = 1.0
    top_p: float = 1.0
    max_tokens: int = 2200
    timeout: int = 120
    verify_ssl: bool = True
    output_dir: Path = DEFAULT_OUTPUT_DIR
    language: str = "English"


@dataclass
class ImageInverseResult:
    image_path: str
    text_description: str
    key_elements: list[str]
    uncertainty_notes: list[str]
    raw_model_output: str
    model: str


def _load_fashion_config() -> Dict[str, Any]:
    if not CONFIG_PATH.exists():
        return {}
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _opt_str(value: Any) -> Optional[str]:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def load_image_inverse_config(**overrides: Any) -> ImageInverseConfig:
    """Load ``fashion_config.yaml`` → ``image-inverse-parser`` with root fallbacks."""
    root = _load_fashion_config()
    cfg = dict(root.get("image-inverse-parser") or {})

    api_key = (
        overrides.get("api_key")
        or os.environ.get("IMAGE_INVERSE_API_KEY")
        or _opt_str(cfg.get("api-key"))
        or _opt_str(root.get("api-key"))
        or _opt_str(root.get("openai-api-key"))
    )
    api_base = (
        overrides.get("api_base")
        or os.environ.get("IMAGE_INVERSE_API_BASE")
        or _opt_str(cfg.get("api-base"))
        or _opt_str(root.get("api-base"))
        or _opt_str(root.get("openai-api-base"))
    )
    model = (
        overrides.get("model")
        or os.environ.get(IMAGE_MODEL_ENV)
        or _opt_str(cfg.get("model"))
        or _opt_str((root.get("grpo") or {}).get("design-text-evaluator", {}).get("vision-model"))
        or _opt_str(root.get("llm-backend"))
        or "gpt-5.5"
    )

    if not api_key:
        raise ValueError("Missing image inverse API key. Set image-inverse-parser.api-key or root api-key.")
    if not api_base:
        raise ValueError("Missing image inverse API base. Set image-inverse-parser.api-base or root api-base.")

    output_dir = Path(overrides.get("output_dir") or cfg.get("output-dir") or DEFAULT_OUTPUT_DIR)
    if not output_dir.is_absolute():
        output_dir = REPO_ROOT / output_dir

    return ImageInverseConfig(
        api_key=str(api_key),
        api_base=str(api_base).rstrip("/"),
        model=str(model),
        temperature=float(overrides.get("temperature", cfg.get("temperature", 1.0))),
        top_p=float(overrides.get("top_p", cfg.get("top-p", 1.0))),
        max_tokens=int(overrides.get("max_tokens", cfg.get("max-tokens", 2200))),
        timeout=int(overrides.get("timeout", cfg.get("timeout", 120))),
        verify_ssl=bool(overrides.get("verify_ssl", cfg.get("verify-ssl", True))),
        output_dir=output_dir,
        language=str(overrides.get("language") or cfg.get("language") or "English"),
    )


def image_path_to_part(path: Union[str, Path]) -> Dict[str, Any]:
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"Image not found: {p}")
    mime, _ = mimetypes.guess_type(str(p))
    mime = mime or "image/jpeg"
    encoded = base64.standard_b64encode(p.read_bytes()).decode("ascii")
    return {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{encoded}"}}


def _clean_model_output(text: str) -> str:
    text = re.sub(r"<think>[\s\S]*?</think>", "", text).strip()
    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _extract_json(text: str) -> Dict[str, Any]:
    cleaned = _clean_model_output(text)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", cleaned)
        if not match:
            raise ValueError(f"Model did not return JSON: {cleaned[:500]}")
        return json.loads(match.group(0))


class ImageInverseParser:
    """OpenAI-compatible multimodal parser for fashion image reverse description."""

    def __init__(self, config: Optional[ImageInverseConfig] = None, **overrides: Any) -> None:
        self.config = config or load_image_inverse_config(**overrides)

    def parse_image(
        self,
        image_path: Union[str, Path],
        *,
        business_context: str = "",
        extra_instruction: str = "",
    ) -> ImageInverseResult:
        user_text = self._build_user_text(business_context, extra_instruction)
        raw = self._request_multimodal(user_text, image_path)
        parsed = _extract_json(raw)

        text_description = str(parsed.get("text_description", "")).strip()
        if not text_description:
            raise ValueError(f"Model output missing text_description: {parsed!r}")
        key_elements = [str(item).strip() for item in parsed.get("key_elements", []) if str(item).strip()]
        uncertainty_notes = [
            str(item).strip()
            for item in parsed.get("uncertainty_notes", [])
            if str(item).strip()
        ]
        return ImageInverseResult(
            image_path=str(Path(image_path)),
            text_description=text_description,
            key_elements=key_elements,
            uncertainty_notes=uncertainty_notes,
            raw_model_output=raw,
            model=self.config.model,
        )

    def write_text_description_document(
        self,
        result: ImageInverseResult,
        output_path: Optional[Union[str, Path]] = None,
    ) -> Path:
        image_stem = Path(result.image_path).stem
        target = Path(output_path) if output_path else self.config.output_dir / f"{image_stem}_text_description.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        body = [
            f"# {image_stem} text_description",
            "",
            "## text_description",
            "",
            result.text_description,
            "",
        ]
        if result.key_elements:
            body.extend(["## key_elements", ""])
            body.extend(f"- {item}" for item in result.key_elements)
            body.append("")
        if result.uncertainty_notes:
            body.extend(["## uncertainty_notes", ""])
            body.extend(f"- {item}" for item in result.uncertainty_notes)
            body.append("")
        target.write_text("\n".join(body), encoding="utf-8")

        json_path = target.with_suffix(".json")
        json_path.write_text(
            json.dumps(asdict(result), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return target

    def _build_user_text(self, business_context: str, extra_instruction: str) -> str:
        blocks = [
            f"Output language: {self.config.language}.",
            "Reverse-parse the attached fashion image into a faithful text_description document.",
        ]
        if business_context.strip():
            blocks.append(f"Business/design context:\n{business_context.strip()}")
        if extra_instruction.strip():
            blocks.append(f"Additional instruction:\n{extra_instruction.strip()}")
        return "\n\n".join(blocks)

    def _request_multimodal(self, user_text: str, image_path: Union[str, Path]) -> str:
        payload = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_text},
                        image_path_to_part(image_path),
                    ],
                },
            ],
            "temperature": self.config.temperature,
            "top_p": self.config.top_p,
            "max_completion_tokens": self.config.max_tokens,
            "response_format": {"type": "json_object"},
        }
        request_body = json.dumps(payload).encode("utf-8")

        max_rounds = 5
        backoff_cap_s = 45.0
        ssl_context_none = ssl._create_unverified_context()

        for round_idx in range(max_rounds):
            if round_idx:
                delay = min(backoff_cap_s, 2.0**round_idx)
                time.sleep(delay)

            transient = False
            permanent = False
            errors: list[str] = []

            for url in self._candidate_chat_urls():
                request = urllib.request.Request(
                    url,
                    data=request_body,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.config.api_key}",
                        "User-Agent": "Mozilla/5.0",
                        "Accept": "application/json",
                    },
                    method="POST",
                )
                ssl_context = ssl_context_none if not self.config.verify_ssl else None
                try:
                    with urllib.request.urlopen(
                        request, timeout=self.config.timeout, context=ssl_context
                    ) as response:
                        body = response.read().decode("utf-8")
                    parsed = json.loads(body)
                    return parsed["choices"][0]["message"]["content"]

                except urllib.error.HTTPError as exc:
                    error_body = exc.read().decode("utf-8", errors="replace")
                    errors.append(f"{url} -> HTTP {exc.code}: {error_body}")
                    lb = error_body.lower()
                    if exc.code == 408 or exc.code == 429 or exc.code >= 500:
                        transient = True
                    elif exc.code in (401, 403, 404):
                        permanent = True
                    elif exc.code == 400 and ("invalid_request_error" in lb or "invalid_request" in lb):
                        permanent = True

                except urllib.error.URLError as exc:
                    errors.append(f"{url} -> URLError: {exc}")
                    transient = True

                except (ssl.SSLError, ConnectionError, TimeoutError, OSError, http.client.HTTPException) as exc:
                    errors.append(f"{url} -> {type(exc).__name__}: {exc}")
                    transient = True

                except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
                    errors.append(f"{url} -> unexpected response format: {exc}")

            merged = "\n".join(errors)
            if permanent:
                raise RuntimeError("Image inverse API request failed (no retry):\n" + merged) from None
            if transient and round_idx + 1 < max_rounds:
                continue

            raise RuntimeError("Image inverse API request failed:\n" + merged) from None

    def _candidate_chat_urls(self) -> list[str]:
        base = self.config.api_base.rstrip("/")
        parsed = urlparse(base)
        path = parsed.path.rstrip("/")
        urls = [f"{base}/chat/completions"]
        if path == "":
            urls.append(f"{base}/v1/chat/completions")
        elif path != "/v1" and not path.endswith("/v1"):
            urls.append(f"{base}/v1/chat/completions")
        return list(dict.fromkeys(urls))


def parse_image_to_text_description(
    image_path: Union[str, Path],
    *,
    output_path: Optional[Union[str, Path]] = None,
    business_context: str = "",
    extra_instruction: str = "",
    **config_overrides: Any,
) -> ImageInverseResult:
    parser = ImageInverseParser(**config_overrides)
    result = parser.parse_image(
        image_path,
        business_context=business_context,
        extra_instruction=extra_instruction,
    )
    parser.write_text_description_document(result, output_path)
    return result
