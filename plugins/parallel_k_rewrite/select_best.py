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


def rank_key(evaluation: Optional[Dict[str, Any]]) -> Tuple[int, float]:
    """越大越好：双门限通过，然后总分高。惩罚不参与排序。"""
    if not isinstance(evaluation, dict):
        return (0, -1.0)
    return (
        1 if _gates_both_passed(evaluation) else 0,
        _s_fp(evaluation),
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
    """双门限都过的候选里，取总分最高的一条。没有过门的候选则不选。"""
    eligible = [
        c
        for c in candidates
        if candidate_eligible(c) and _gates_both_passed(c.get("evaluation") or {})
    ]
    if not eligible:
        return None
    return max(eligible, key=lambda c: _s_fp(c.get("evaluation") or {}))


def pick_rewrite_if_better(
    *,
    baseline_evaluation: Optional[Dict[str, Any]],
    candidates: Iterable[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    """
    只在总分门和惩罚门都通过的改写里取 S_fp 最高的一条。
    它高于原文时才替换；没有过门的改写不替换原文。
    """
    best = pick_best_candidate(candidates)
    if best is None:
        return None
    if not is_strictly_better(best.get("evaluation"), baseline_evaluation):
        return None
    return best
