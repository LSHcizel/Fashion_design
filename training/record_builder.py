"""
《改进方案》第 4 步：训练 JSONL 单条记录结构（与 GRPO 组、ODIN/R_content 字段对齐）。

每条样本一行 JSON：同一 ``group_id`` 下 K 条 completion 各写一行，共享 ``context`` 语义字段。
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, Iterator, List, Optional


SCHEMA_VERSION = "grpo_training_v2"


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _est_tokens(char_len: int) -> float:
    return round(max(0, int(char_len)) / 4.0, 4)


def _compact_gates(evaluation: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not evaluation:
        return None
    g = evaluation.get("gates") or {}
    sg = g.get("score_gate") or {}
    pg = g.get("penalty_gate") or {}
    return {
        "score_gate_passed": sg.get("passed"),
        "score_gate_value": sg.get("value"),
        "score_gate_threshold": sg.get("threshold"),
        "penalty_gate_passed": pg.get("passed"),
        "penalty_gate_total_penalty": pg.get("total_penalty"),
        "penalty_gate_threshold": pg.get("threshold"),
        "both_passed": g.get("both_passed"),
    }


def _compact_scores_for_training(evaluation: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not evaluation:
        return None
    sc = evaluation.get("scores") or {}
    cov = sc.get("coverage_score") or {}
    q = sc.get("quality_score") or {}
    pen = q.get("penalties") or {}
    fp = sc.get("fashion_prompt_score", evaluation.get("total_score"))
    rc_block = evaluation.get("r_content")
    r_enabled = isinstance(rc_block, dict) and rc_block.get("enabled", True)
    sfp_val = float(rc_block["S_fp"]) if r_enabled and isinstance(rc_block, dict) and rc_block.get("S_fp") is not None else fp
    r_scalar = (
        float(rc_block["R_content"])
        if r_enabled and isinstance(rc_block, dict) and rc_block.get("R_content") is not None
        else None
    )
    return {
        "S_fp": sfp_val,
        "R_content": r_scalar,
        "fashion_prompt_score": fp,
        "coverage_axis_score": (cov.get("score") if isinstance(cov, dict) else None),
        "quality_penalized_score": q.get("penalized_score"),
        "quality_base_score": q.get("base_score"),
        "total_penalty": pen.get("total_penalty"),
        "weights": sc.get("weights"),
    }


def build_training_record(
    *,
    group_id: str,
    group_round: int,
    candidate_index: int,
    context: Dict[str, Any],
    completion_text: str,
    evaluation: Optional[Dict[str, Any]],
    r_content_block: Optional[Dict[str, Any]],
    parallel_meta: Optional[Dict[str, Any]] = None,
    run_id: str = "default",
    record_type: str = "rewrite_candidate",
    system_prompt_sha256: Optional[str] = None,
) -> Dict[str, Any]:
    """
    构造一行训练 JSONL 对象（第 4 步完整字段）。

    Parameters
    ----------
    context :
        须含模型改写时可见的语义信息，建议键：
        ``shared_source_text``（原文）、``business_context``（业务约束）、
        ``instruction_summary``（对用户任务的一句话摘要）、
        可选 ``system_prompt_label``（如 ``fashion_sys_prompt.txt``）。
    evaluation :
        单次 ``evaluate_text`` 完整返回；若无评判则为 None。
    r_content_block :
        建议使用 ``evaluation["r_content"]``（已含 γ、β、z_len、R_content 等）。
    parallel_meta :
        可选：temperature、dedupe_kept、rewrite_error 等并行采样元数据。
    system_prompt_sha256 :
        可选：当前 rewriter 系统提示的 hash，便于复现实验。
    """
    char_len = len((completion_text or "").strip())
    rcfg = dict(r_content_block) if isinstance(r_content_block, dict) else {}
    rc_enabled = rcfg.get("enabled", True)
    R = float(rcfg["R_content"]) if rc_enabled and rcfg.get("R_content") is not None else None
    S_fp = float(evaluation.get("total_score", 0.0) or 0.0) if evaluation else None

    training_filter: Dict[str, Any] = {
        "non_empty_completion": char_len > 0,
        "evaluation_present": evaluation is not None,
        "dedupe_kept": (parallel_meta or {}).get("dedupe_kept", True),
        "rewrite_error": (parallel_meta or {}).get("rewrite_error"),
        "include_in_training": True,
        "exclude_reasons": [],
    }

    if not training_filter["non_empty_completion"]:
        training_filter["include_in_training"] = False
        training_filter["exclude_reasons"].append("empty_completion")
    if evaluation is None:
        training_filter["include_in_training"] = False
        training_filter["exclude_reasons"].append("missing_evaluation")
    elif not training_filter["dedupe_kept"]:
        training_filter["include_in_training"] = False
        training_filter["exclude_reasons"].append("dedupe_dropped")
    if training_filter["rewrite_error"]:
        training_filter["include_in_training"] = False
        training_filter["exclude_reasons"].append("rewrite_exception")

    if evaluation is not None:
        gates_block = evaluation.get("gates") or {}
        if not gates_block.get("both_passed"):
            training_filter["include_in_training"] = False
            training_filter["exclude_reasons"].append("gates_not_both_passed")

    eval_for_compact = evaluation
    if evaluation is not None and isinstance(r_content_block, dict) and not evaluation.get("r_content"):
        eval_for_compact = dict(evaluation)
        eval_for_compact["r_content"] = r_content_block

    return {
        "schema_version": SCHEMA_VERSION,
        "record_type": record_type,
        "run_id": run_id,
        "timestamp_utc": _iso_now(),
        "group_id": group_id,
        "group_round": int(group_round),
        "candidate_index": int(candidate_index),
        "context": {
            **context,
            "system_prompt_sha256": system_prompt_sha256,
        },
        "completion": completion_text,
        "char_len": char_len,
        "est_tokens_char_div_4": _est_tokens(char_len),
        "S_fp": S_fp,
        "R_content": R,
        "fashion_prompt_score": S_fp,
        "scores_compact": _compact_scores_for_training(eval_for_compact),
        "gates_compact": _compact_gates(evaluation),
        "penalties": (
            evaluation.get("scores", {}).get("quality_score", {}).get("penalties") if evaluation else None
        ),
        "r_content": rcfg,
        "hyperparameters": {
            "gamma_penalty": rcfg.get("gamma_penalty"),
            "beta_z_len": rcfg.get("beta_z_len"),
            "r_content_formula": rcfg.get("formula"),
            "length_use_log": None,
        },
        "grpo": {
            "reward_scalar": R,
            "S_fp": S_fp,
            "R_content": R,
            "group_id": group_id,
            "note": "RL/GRPO 主标量建议使用顶栏 R_content 或 grpo.reward_scalar（与 r_content.R_content 一致）；S_fp 为 fashion_prompt_score / total_score。",
        },
        "parallel_sampling": parallel_meta or {},
        "training_filter": training_filter,
    }


def iter_records_from_parallel_result(
    parallel_result: Dict[str, Any],
    *,
    context: Dict[str, Any],
    run_id: str,
    group_round: Optional[int] = None,
    system_prompt_sha256: Optional[str] = None,
) -> Iterator[Dict[str, Any]]:
    """
    从 ``generate_k_parallel_rewrites`` 的返回体展开为多条训练记录。
    """
    gid = str(parallel_result.get("group_id") or "")
    rnd = int(group_round if group_round is not None else 0)
    src = parallel_result.get("source_text") or ""
    biz = parallel_result.get("extra_context") or ""
    ctx = {
        **context,
        "shared_source_text": context.get("shared_source_text", src),
        "business_context": context.get("business_context", biz),
    }
    for c in parallel_result.get("candidates") or []:
        ev = c.get("evaluation")
        rc = ev.get("r_content") if isinstance(ev, dict) else None
        meta = {
            "temperature": c.get("temperature"),
            "dedupe_kept": c.get("dedupe_kept", True),
            "dedupe_reason": c.get("dedupe_reason"),
            "rewrite_error": c.get("error"),
            "evaluation_skipped": c.get("evaluation_skipped"),
        }
        yield build_training_record(
            group_id=gid,
            group_round=rnd,
            candidate_index=int(c.get("candidate_index", -1)),
            context=ctx,
            completion_text=str(c.get("text") or ""),
            evaluation=ev if isinstance(ev, dict) else None,
            r_content_block=rc if isinstance(rc, dict) else None,
            parallel_meta=meta,
            run_id=run_id,
            system_prompt_sha256=system_prompt_sha256,
        )


def sha256_text(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def summarize_jsonl_file(path: str, *, max_lines: int = 100_000) -> Dict[str, Any]:
    """对样本 JSONL 做简易离线汇总（条数、include_in_training、平均 R_content、门限通过率）。"""
    import json
    from pathlib import Path

    p = Path(path)
    if not p.is_file():
        return {"error": "file_not_found", "path": str(p)}

    total = 0
    included = 0
    rs: List[float] = []
    sfs: List[float] = []
    gate_ok = 0
    lines_read = 0

    with p.open("r", encoding="utf-8") as f:
        for line in f:
            lines_read += 1
            if lines_read > max_lines:
                break
            line = line.strip()
            if not line:
                continue
            try:
                o = json.loads(line)
            except json.JSONDecodeError:
                continue
            total += 1
            if (o.get("training_filter") or {}).get("include_in_training"):
                included += 1
            r = (o.get("grpo") or {}).get("reward_scalar")
            if r is None:
                r = o.get("R_content")
            if r is not None:
                rs.append(float(r))
            sf = o.get("S_fp")
            if sf is None:
                sf = (o.get("scores_compact") or {}).get("S_fp")
            if sf is not None:
                sfs.append(float(sf))
            g = o.get("gates_compact") or {}
            if g.get("both_passed") is True:
                gate_ok += 1

    return {
        "path": str(p),
        "lines_json": total,
        "included_for_training": included,
        "mean_S_fp": round(sum(sfs) / len(sfs), 6) if sfs else None,
        "mean_R_content": round(sum(rs) / len(rs), 6) if rs else None,
        "count_with_R_content": len(rs),
        "both_gates_passed_count": gate_ok,
    }
