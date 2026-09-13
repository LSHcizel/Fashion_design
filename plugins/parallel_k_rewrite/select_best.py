"""K 路候选与原文评估的排序 / 是否采纳（不依赖 GPU）。"""

from __future__ import annotations

from typing import Any, Dict, Iterable, Optional, Tuple


def _gates_both_passed(evaluation: Dict[str, Any]) -> bool:
    gates = evaluation.get("gates") or {}
    if "both_passed" in gates:
        return bool(gates["both_passed"])
    return bool((gates.get("score_gate") or {}).get("passed")) and bool(
        (gates.get("penalty_gate") or {}).get("passed")
    )


def _s_fp(evaluation: Dict[str, Any]) -> float:
    s = evaluation.get("total_score")
    if s is None:
        s = (evaluation.get("scores_compact") or {}).get("S_fp")
    if s is None:
        sg = (evaluation.get("gates") or {}).get("score_gate") or {}
        s = sg.get("value")
    return float(s or 0.0)


def _total_penalty(evaluation: Dict[str, Any]) -> float:
    pt = (
        (evaluation.get("scores") or {})
        .get("quality_score", {})
        .get("penalties", {})
        .get("total_penalty")
    )
    if pt is None:
        pt = ((evaluation.get("gates") or {}).get("penalty_gate") or {}).get("total_penalty")
    return float(pt or 0.0)


def rank_key(evaluation: Optional[Dict[str, Any]]) -> Tuple[int, float, float]:
    """越大越好：双门限通过、S_fp 高、惩罚低。"""
    if not isinstance(evaluation, dict):
        return (0, -1.0, 0.0)
    return (
        1 if _gates_both_passed(evaluation) else 0,
        _s_fp(evaluation),
        -_total_penalty(evaluation),
    )


def is_strictly_better(
    evaluation: Optional[Dict[str, Any]],
    baseline: Optional[Dict[str, Any]],
) -> bool:
    return rank_key(evaluation) > rank_key(baseline)


def candidate_eligible(cand: Dict[str, Any]) -> bool:
    if cand.get("dedupe_kept") is False:
        return False
    if cand.get("error"):
        return False
    ev = cand.get("evaluation")
    return isinstance(ev, dict)


def pick_best_candidate(candidates: Iterable[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    eligible = [c for c in candidates if candidate_eligible(c)]
    if not eligible:
        return None
    return max(eligible, key=lambda c: rank_key(c.get("evaluation")))


def pick_rewrite_if_better(
    *,
    baseline_evaluation: Optional[Dict[str, Any]],
    candidates: Iterable[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    """
    从 K 路里选评估最好的一条；仅当严格优于原文评估时返回该候选，否则 None（留原文）。
    """
    best = pick_best_candidate(candidates)
    if best is None:
        return None
    if not is_strictly_better(best.get("evaluation"), baseline_evaluation):
        return None
    return best
