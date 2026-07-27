"""
阶段 A — 图像逆解析：多模态 API（带图）→ 文本摘要 + 完整 prompt → ``evaluate_text`` 评测 →
写出与 ``build_sft_record_for_group`` 相同字段的 SFT 记录（可并入 ``phase_a_sft.jsonl``）。

- **User 消息**：仅 ``[Business context]``（可选）与 ``[Image-derived summary]``，不含原文 rewrite 槽位。
- **Assistant**：逆解析得到的 ``fashion_image_prompt``（经规范化）；监督侧与并行 K 路导出的 SFT 行分列存储（两条样本）。
"""

from __future__ import annotations

import base64
import json
import mimetypes
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Sequence, Tuple, Union

from plugins.text_description_evaluator.design_text_evaluator_api import (
    ApiLLMJudge,
    DesignTextEvaluator,
    grpo_design_text_evaluator_config,
)

from .grpo_compute import pick_reward_scalar
from .grpo_pipeline import DEFAULT_SFT_SCHEMA, build_sft_record_for_group

IMAGE_INVERSE_SOURCE_SCHEMA = "phase_a_image_inverse_v1"

IMAGE_INVERSE_MODEL_ENV = "AI_API_MODEL_VISION"

INVERSE_PARSE_SYSTEM_PROMPT = """You are a senior fashion design analyst with access to the attached image(s).

You must output one JSON object only (no markdown fences, no commentary). The JSON must have exactly these keys:
- "image_derived_summary": string in English. Condensed visual grounding only: silhouette, palette, key garments, materials where visible, styling cues. Max about 120 words. This text will later be the sole image-derived conditioning given to a text-only model — stay factual to the image, no fluff.
- "fashion_image_prompt": string in English. Exactly one coherent paragraph: a direct fashion image generation prompt describing the same look, suitable for text-to-image models. Same style as professional runway / lookbook prompt writing (not analytic essay prose).

Do not invent garments or colors not supported by the image. If uncertain, omit rather than guess."""


def image_path_to_url_part(path: Union[str, Path]) -> Dict[str, Any]:
    """Local file → OpenAI-style ``image_url`` part (data URI)."""
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"Image not found: {p}")
    mime, _ = mimetypes.guess_type(str(p))
    mime = mime or "image/jpeg"
    b64 = base64.standard_b64encode(p.read_bytes()).decode("ascii")
    return {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}}


def build_multimodal_user_content(
    instruction_text: str,
    image_paths: Sequence[Union[str, Path]],
) -> List[Dict[str, Any]]:
    parts: List[Dict[str, Any]] = [{"type": "text", "text": instruction_text.strip()}]
    for raw in image_paths:
        parts.append(image_path_to_url_part(raw))
    return parts


def _inverse_instruction(business_context: str) -> str:
    blocks: List[str] = []
    biz = (business_context or "").strip()
    if biz:
        blocks.append(f"Shared business context / constraints:\n{biz}")
    blocks.append(
        "Follow the system instructions and return the JSON object with "
        '"image_derived_summary" and "fashion_image_prompt" for these image(s).'
    )
    return "\n\n".join(blocks)


def _parse_inverse_json(raw: str, vision_judge: ApiLLMJudge) -> Dict[str, str]:
    cleaned = vision_judge._clean_output(raw)
    try:
        obj = json.loads(cleaned)
    except json.JSONDecodeError:
        m = re.search(r"\{[\s\S]*\}", cleaned)
        if not m:
            raise ValueError(f"inverse_parse: no JSON in model output: {cleaned[:500]}")
        obj = json.loads(m.group(0))
    summary = str(obj.get("image_derived_summary", "")).strip()
    prompt = str(obj.get("fashion_image_prompt", "")).strip()
    if not summary or not prompt:
        raise ValueError(f"inverse_parse: missing keys in JSON: {obj!r}")
    return {"image_derived_summary": summary, "fashion_image_prompt": prompt}


@dataclass
class ImageInverseOutcome:
    image_derived_summary: str
    fashion_image_prompt: str
    evaluation: Dict[str, Any]
    raw_model_output: str


def run_image_inverse_multimodal(
    vision_judge: ApiLLMJudge,
    *,
    image_paths: Sequence[Union[str, Path]],
    business_context: str = "",
    temperature: float = 1.0,
    max_tokens: Optional[int] = None,
) -> ImageInverseOutcome:
    """
    调用带图 API，解析 JSON，并对 ``fashion_image_prompt`` 执行 ``DesignTextEvaluator.evaluate_text``。

    Parameters
    ----------
    vision_judge :
        具备多模态能力的 ``ApiLLMJudge``（通常单独设 ``AI_API_MODEL_VISION``，与评测模型可不同）。
    """
    if not image_paths:
        raise ValueError("run_image_inverse_multimodal requires at least one image path")
    instructor = _inverse_instruction(business_context)
    user_parts = build_multimodal_user_content(instructor, image_paths)

    fmt: Optional[Dict[str, str]] = {"type": "json_object"}
    raw: str
    try:
        raw = vision_judge.generate_multimodal(
            INVERSE_PARSE_SYSTEM_PROMPT,
            user_parts,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=fmt,
        )
    except RuntimeError:
        raw = vision_judge.generate_multimodal(
            INVERSE_PARSE_SYSTEM_PROMPT,
            user_parts,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=None,
        )

    parsed = _parse_inverse_json(raw, vision_judge)
    ev_obj = DesignTextEvaluator()
    prompt = parsed["fashion_image_prompt"]
    prompt = ev_obj._normalize_optimized_text(prompt)
    prompt = ev_obj._validate_optimized_text(prompt, parsed["image_derived_summary"])
    src = f"image_inverse.{Path(image_paths[0]).stem}"
    evaluation = ev_obj.evaluate_text(prompt, source_name=src, gate_config=None)
    return ImageInverseOutcome(
        image_derived_summary=parsed["image_derived_summary"].strip(),
        fashion_image_prompt=prompt.strip(),
        evaluation=evaluation,
        raw_model_output=raw,
    )


def build_phase_a_sft_record_image_inverse(
    outcome: ImageInverseOutcome,
    *,
    group_id: str,
    group_round: int = 0,
    system_prompt_text: str = "",
    business_context: str = "",
    reward_key: Literal["R_content", "total_score"] = "R_content",
) -> Dict[str, Any]:
    """
    与 ``build_sft_record_for_group`` 相同顶层字段，便于与同目录下文本组导出的 SFT 行合并。

    ``chosen_candidate_index`` 固定为 ``-1`` 表示图像逆解析行（与 K 路候选 index 区分）。
    """
    pseudo_rec = {
        "grpo": {"reward_scalar": (outcome.evaluation.get("r_content") or {}).get("R_content")},
        "r_content": outcome.evaluation.get("r_content"),
        "S_fp": outcome.evaluation.get("total_score"),
        "R_content": (outcome.evaluation.get("r_content") or {}).get("R_content")
        if (outcome.evaluation.get("r_content") or {}).get("enabled", True)
        else None,
        "fashion_prompt_score": outcome.evaluation.get("total_score"),
        "scores_compact": {"fashion_prompt_score": outcome.evaluation.get("total_score")},
    }
    reward_best = round(pick_reward_scalar(pseudo_rec, prefer=reward_key), 8)

    user_parts_msg: List[str] = []
    biz = (business_context or "").strip()
    if biz:
        user_parts_msg.append(f"[Business context]\n{biz}")
    user_parts_msg.append(f"[Image-derived summary]\n{outcome.image_derived_summary}")
    user_content = "\n\n".join(user_parts_msg).strip()
    assistant = outcome.fashion_image_prompt.strip()

    messages: List[Dict[str, str]] = []
    if system_prompt_text.strip():
        messages.append({"role": "system", "content": system_prompt_text.strip()})
    messages.append({"role": "user", "content": user_content})
    messages.append({"role": "assistant", "content": assistant})

    return {
        "schema_version": DEFAULT_SFT_SCHEMA,
        "phase": "A_SFT",
        "group_id": group_id,
        "group_round": int(group_round),
        "chosen_candidate_index": -1,
        "S_fp": outcome.evaluation.get("total_score"),
        "R_content": (outcome.evaluation.get("r_content") or {}).get("R_content")
        if (outcome.evaluation.get("r_content") or {}).get("enabled", True)
        else None,
        "reward_best": reward_best,
        "reward_key": reward_key,
        "source_samples_schema": IMAGE_INVERSE_SOURCE_SCHEMA,
        "messages": messages,
    }


def make_vision_judge(base_judge: Optional[ApiLLMJudge] = None, **kwargs: Any) -> ApiLLMJudge:
    """
    基于现有 ``ApiLLMJudge`` 的配置克隆一个用于多模态的 judge。

    默认优先 ``fashion_config.yaml`` → ``grpo.design-text-evaluator.vision-model``，
    其次环境变量 ``AI_API_MODEL_VISION``，最后 ``base_judge.model``。
    """
    y = grpo_design_text_evaluator_config()
    vm = (y.get("vision-model") or "").strip() or None
    if base_judge is not None:
        model = vm or os.environ.get(IMAGE_INVERSE_MODEL_ENV) or base_judge.model
        return ApiLLMJudge(
            api_key=base_judge.api_key,
            api_base=base_judge.api_base,
            model=model,
            temperature=kwargs.get("temperature", base_judge.temperature),
            top_p=kwargs.get("top_p", base_judge.top_p),
            max_tokens=kwargs.get("max_tokens", base_judge.max_tokens),
            timeout=kwargs.get("timeout", base_judge.timeout),
            verify_ssl=kwargs.get("verify_ssl", base_judge.verify_ssl),
        )
    return ApiLLMJudge(**kwargs)


def build_pair_phase_a_records(
    vision_judge: ApiLLMJudge,
    *,
    image_paths: Sequence[Union[str, Path]],
    group_id: str,
    group_records: List[Dict[str, Any]],
    group_round: int = 0,
    business_context: str = "",
    system_prompt_text: str = "",
    reward_key: Literal["R_content", "total_score"] = "R_content",
    inverse_temperature: float = 1.0,
) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
    """
    一次生成两条阶段 A 记录：图像逆解析 SFT + （若 ``group_records`` 非空）K 路组内最优 SFT。
    ``group_records`` 须为同一 ``group_id`` 的 ``samples.jsonl`` 行字典列表（与 ``load_samples_by_group`` 一致）。
    """
    outcome = run_image_inverse_multimodal(
        vision_judge,
        image_paths=image_paths,
        business_context=business_context,
        temperature=inverse_temperature,
    )
    image_rec = build_phase_a_sft_record_image_inverse(
        outcome,
        group_id=group_id,
        group_round=group_round,
        system_prompt_text=system_prompt_text,
        business_context=business_context,
        reward_key=reward_key,
    )
    rewrite_rec: Optional[Dict[str, Any]] = None
    if group_records:
        rewrite_rec = build_sft_record_for_group(
            group_records,
            reward_key=reward_key,
            system_prompt_text=system_prompt_text,
        )
    return image_rec, rewrite_rec


def append_phase_a_sft_jsonl(path: Union[str, Path], record: Dict[str, Any]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def append_two_phase_a_lines_for_group(
    path: Union[str, Path],
    *,
    image_record: Dict[str, Any],
    rewrite_record: Optional[Dict[str, Any]],
) -> None:
    """
    同一 ``group_id`` 写两条 stage-A 样本：先逆解析行，再（若存在）K 路组内最高分重写行。
    """
    append_phase_a_sft_jsonl(path, image_record)
    if rewrite_record is not None:
        append_phase_a_sft_jsonl(path, rewrite_record)
