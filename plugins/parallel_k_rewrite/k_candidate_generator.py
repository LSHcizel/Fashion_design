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
    grpo_parallel_k_rewrite_config,
    is_connection_failure,
)
from ..text_description_evaluator.r_content_reward import apply_group_z_len_r_content

if TYPE_CHECKING:
    from ..text_description_evaluator.design_text_evaluator_api import DesignTextEvaluator


REWRITE_STYLE_CONCEPT_LOCK = (
    "THEME AND CONCEPT LOCK: First extract the theme and the design concept already present "
    "in SOURCE (collection story, dualities, aesthetic register, and design intent). "
    "Keep those consistent. Do not switch to a different theme or a different concept "
    "(no workwear→eveningwear unless SOURCE already is that register)."
)

REWRITE_WHOLE_LOOK_SCOPE = (
    "WHOLE-LOOK CHANGE (allowed, inside theme/concept): You MAY change the overall clothing "
    "so the rewrite is a new realization of the SAME extracted theme and concept — including "
    "color and palette, garment pairing and categories (what is worn with what), silhouette "
    "and layering, and detail design (trim, surface, construction, local craft, accessories). "
    "A color restyle or a different pairing that still reads as that theme/concept is in-scope. "
    "Do not keep SOURCE's current SKU just to be faithful. "
    "Out of scope: leaving the theme or design concept, or jumping to a competing register."
)

REWRITE_ELEMENT_RECONSTRUCTION = (
    "ELEMENT RECONSTRUCTION: After extracting theme and concept, redesign the look's elements "
    "to raise DesignMerit: recompose color, pairing, silhouette, layering, surface, edge "
    "treatment, volume, local construction, and detail design while the theme and concept "
    "still read as the same. Acceptable reconstruction may replace or restack garments and "
    "details. It must not abandon the extracted theme/concept, and must not treat a "
    "collection-shared interchangeable garment formula as the identity."
)

REWRITE_DESIGN_MERIT = (
    "DESIGN MERIT GOAL: Optimize for a higher DesignMerit score (identifying idea, not completeness). "
    "Give this rewrite exactly one dominant visual idea, grounded on parts and layers. "
    "Examples of idea kinds (a menu, not an assignment to this candidate): allover surface field; "
    "trim/appliqué path along neckline, front, hem, or cuff; open outer over an inner that would "
    "still read alone; trunk volume/surface collision; or another equally specific visible idea. "
    "Do not merely paraphrase SOURCE, retighten wording, or only change pose/background. "
    "If SOURCE already has an idea, you may strengthen, relocate/rescale, or replace it with a "
    "different idea that still belongs to the extracted theme and concept — including new color, "
    "pairing, and detail design — so the generated image can diverge from a clone of SOURCE's "
    "current SKU. "
    "If SOURCE is only formulaic wardrobe grammar, create one identifying idea inside that theme. "
    "Do not treat factory finishing (topstitching, hidden placket), ordinary dressing "
    "(tucked shirt), brand hardware as identity, or theme dualities as the identity. "
    "Compress promenade/salon/stance commentary."
)

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

REWRITE_SHARED_STRATEGY = (
    "SHARED STRATEGY (theme/concept lock + logo lock; whole-look change inside that lock): "
    "1) Extract theme and concept from SOURCE only — there is no separate chapter brief. "
    "2) You may change colors, garment pairing, and detail design — the whole look — so this "
    "sample is not a wording-only clone of SOURCE; a generated image should be able to diverge. "
    "Stay inside the extracted theme and concept. Identifying-idea kinds are a menu, not a "
    "per-candidate assignment. "
    "3) Keep any original house logo/monogram as the same brand mark (placement/scale may change). "
    "4) Output one coherent English paragraph."
)

# Backward-compatible name used by workflow extra_context.
REWRITE_LOCAL_EDITS_ALLOWED = REWRITE_ELEMENT_RECONSTRUCTION


def build_rewrite_user_prompt(
    source_text: str,
    k: int,
    candidate_index: int,
    extra_context: str = "",
) -> str:
    """K 路改写 user prompt：可改整体造型（颜色/搭配/细节），主题与概念、品牌 logo 加锁。"""
    user = (
        f"PARALLEL REWRITE TASK\n"
        f"You are producing rewrite candidate #{candidate_index + 1} of {k} for the SAME source. "
        f"This is an independent sample: choose one identifying idea yourself "
        "(do not wait for a kind to be assigned). "
        "You may change the overall clothing (color, pairing, detail design) as long as the "
        "extracted theme and concept stay the same. "
        "Candidates are sampled separately at different temperatures.\n\n"
        f"{REWRITE_SHARED_STRATEGY}\n"
        f"{REWRITE_STYLE_CONCEPT_LOCK}\n"
        f"{REWRITE_WHOLE_LOOK_SCOPE}\n"
        f"{REWRITE_BRAND_LOGO_LOCK}\n"
        f"{REWRITE_ELEMENT_RECONSTRUCTION}\n"
        f"{REWRITE_DESIGN_MERIT}\n\n"
        f"SOURCE TEXT TO REWRITE:\n{source_text.strip()}\n\n"
    )
    if extra_context.strip():
        user += (
            f"BUSINESS CONTEXT / CONSTRAINTS (shared across all {k} candidates):\n"
            f"{extra_context.strip()}\n\n"
        )
    user += (
        "OUTPUT RULES:\n"
        "1. Output exactly one coherent English paragraph: the optimized fashion image prompt only.\n"
        "2. No markdown fences, no numbering, no preamble or commentary.\n"
        "3. Lead with the identifying idea you chose, then outer-to-inner visual order.\n"
        "4. Whole-look change is allowed (color, pairing, details) only inside SOURCE's theme and concept.\n"
        "5. If SOURCE or business context has a house logo/monogram, keep that same brand mark "
        "(placement and size may change; never another house).\n"
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
        候选条数；为 ``None`` 时使用 ``fashion_config.yaml`` → ``grpo.parallel-k-rewrite.k``（缺省 **10**）。
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
        传入 `evaluate_text` 的门限覆盖，例如 ``{"score_gate_min": 0.8, "penalty_gate_max": 0.5}``；
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
        k = int(_pk.get("k", 10))
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
