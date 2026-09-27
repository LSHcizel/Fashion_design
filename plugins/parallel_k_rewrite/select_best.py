"""K 路候选与原文评估的排序 / 是否采纳（不依赖 GPU）。"""

from __future__ import annotations

from typing import Any, Dict, Iterable, Optional, Tuple


def _s_fp(evaluation: Dict[str, Any]) -> float:
    s = evaluation.get("total_score")
    if s is None:
        s = (evaluation.get("scores_compact") or {}).get("S_fp")
    if s is None:
        sg = (evaluation.get("gates") or {}).get("score_gate") or {}
        s = sg.get("value")
    return float(s or 0.0)


def _penalty(evaluation: Dict[str, Any]) -> Optional[float]:
    penalties = (
        (evaluation.get("scores") or {}).get("quality_score") or {}
    ).get("penalties") or {}
    if penalties.get("total_penalty") is not None:
        return float(penalties["total_penalty"])
    pg = (evaluation.get("gates") or {}).get("penalty_gate") or {}
    if pg.get("total_penalty") is not None:
        return float(pg["total_penalty"])
    return None


def rank_key(evaluation: Optional[Dict[str, Any]]) -> Tuple[float, float]:
    """越大越好：先总分，总分相同再看更低的惩罚。"""
    if not isinstance(evaluation, dict):
        return (-1.0, -1.0)
    penalty = _penalty(evaluation)
    return (
        _s_fp(evaluation),
        0.0 if penalty is None else -penalty,
    )


def improves_score_and_penalty(
    evaluation: Optional[Dict[str, Any]],
    baseline: Optional[Dict[str, Any]],
) -> bool:
    """总分严格提高，并且惩罚严格降低。缺惩罚分视为做不到。"""
    if not isinstance(evaluation, dict) or not isinstance(baseline, dict):
        return False
    new_penalty = _penalty(evaluation)
    base_penalty = _penalty(baseline)
    if new_penalty is None or base_penalty is None:
        return False
    return _s_fp(evaluation) > _s_fp(baseline) and new_penalty < base_penalty


def is_strictly_better(
    evaluation: Optional[Dict[str, Any]],
    baseline: Optional[Dict[str, Any]],
) -> bool:
    return improves_score_and_penalty(evaluation, baseline)


def candidate_eligible(cand: Dict[str, Any]) -> bool:
    if cand.get("dedupe_kept") is False:
        return False
    if cand.get("error"):
        return False
    ev = cand.get("evaluation")
    return isinstance(ev, dict)


def pick_best_candidate(
    candidates: Iterable[Dict[str, Any]],
    *,
    baseline_evaluation: Optional[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    """同时提高总分并降低惩罚的候选里，取效果最好的一条。"""
    eligible = [
        c
        for c in candidates
        if candidate_eligible(c)
        and improves_score_and_penalty(c.get("evaluation"), baseline_evaluation)
    ]
    if not eligible:
        return None
    return max(eligible, key=lambda c: rank_key(c.get("evaluation")))


def pick_rewrite_if_better(
    *,
    baseline_evaluation: Optional[Dict[str, Any]],
    candidates: Iterable[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    """
    只采纳同时比原文总分更高、惩罚更低的改写，并在其中取总分最高的一条。
    总分相同则取惩罚更低的一条。没有同时做到这两点的改写不替换原文。
    """
    return pick_best_candidate(candidates, baseline_evaluation=baseline_evaluation)
