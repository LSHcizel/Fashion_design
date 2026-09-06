"""ODIN 双头 RM 共用：读 JSONL、裁判标签、对话模板、把 r_Q 写回样本。"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional, Union

JsonPath = Union[str, Path]


def read_jsonl(path: JsonPath) -> Iterator[Dict[str, Any]]:
    with Path(path).open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def write_jsonl(path: JsonPath, rows: Iterable[Dict[str, Any]]) -> int:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with out.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            n += 1
    return n


def include_in_training(rec: Dict[str, Any]) -> bool:
    return bool((rec.get("training_filter") or {}).get("include_in_training", True))


def teacher_score(rec: Dict[str, Any]) -> Optional[float]:
    """
    裁判内容主分 s_fp_base（0～1）。

    不用 ``R_content``：档 1 组内可能已减 β·z_len，不能当 RM 老师。
    """
    sc = rec.get("scores_compact") or {}
    for key in ("S_fp", "fashion_prompt_score"):
        val = sc.get(key)
        if val is not None:
            return float(val)
    for key in ("S_fp", "fashion_prompt_score"):
        val = rec.get(key)
        if val is not None:
            return float(val)
    rc = rec.get("r_content") or {}
    if rc.get("S_fp") is not None:
        return float(rc["S_fp"])
    return None


def log_len_of(rec: Dict[str, Any]) -> float:
    rc = rec.get("r_content") or {}
    ll = rc.get("log_len")
    if ll is not None:
        return float(ll)
    n = rec.get("char_len")
    if n is None:
        n = len(str(rec.get("completion") or "").strip())
    return math.log1p(float(max(0, int(n))))


def candidate_key(rec: Dict[str, Any]) -> str:
    return f"{rec.get('group_id')}#{rec.get('candidate_index')}"


def messages_from_record(rec: Dict[str, Any], *, system_prompt: str = "") -> List[Dict[str, str]]:
    """与 GRPO phase_b 相同的 user/assistant 拼法，RM 看「原文+改写」。"""
    from ..hf_grpo.data import messages_from_phase_b_row

    return messages_from_phase_b_row(rec, system_prompt=system_prompt)


def apply_r_q_to_record(
    rec: Dict[str, Any],
    *,
    r_q: float,
    r_l: float,
    backbone: str = "",
) -> Dict[str, Any]:
    """把内容头写进 GRPO 奖励入口；S_fp / 门限仍是裁判 0～1。"""
    rq = float(r_q)
    rl = float(r_l)
    rec["R_content"] = rq
    grpo = dict(rec.get("grpo") or {})
    grpo["reward_scalar"] = rq
    grpo["group_id"] = rec.get("group_id")
    rec["grpo"] = grpo

    rc = dict(rec.get("r_content") or {})
    rc["enabled"] = True
    rc["odin_stage"] = 3
    rc["r_Q"] = round(rq, 6)
    rc["r_L"] = round(rl, 6)
    rc["r_sum"] = round(rq + rl, 6)
    rc["R_content"] = round(rq, 6)
    rc.pop("z_len", None)
    rc.pop("beta_z_len", None)
    rc.pop("gamma_penalty", None)
    rc.pop("holdout_length_prediction", None)
    rc.pop("length_mixed_into_score", None)
    rc.pop("r_after_length_residual", None)
    rc.pop("r_after_soft_penalty", None)
    rc.pop("penalty_merge", None)
    rc.pop("odin_reference", None)
    rc.pop("interpretation_zh", None)
    rec["r_content"] = rc

    sc = dict(rec.get("scores_compact") or {})
    sc["R_content"] = round(rq, 6)
    sc.pop("fashion_prompt_score", None)
    rec["scores_compact"] = sc

    rec["odin_rm"] = {
        "r_Q": round(rq, 6),
        "r_L": round(rl, 6),
        "r_sum": round(rq + rl, 6),
        "backbone": backbone,
    }
    rec.pop("hyperparameters", None)
    rec.pop("fashion_prompt_score", None)
    rec.pop("est_tokens_char_div_4", None)
    return rec
