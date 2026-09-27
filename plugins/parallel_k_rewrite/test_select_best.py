"""K 路 vs 原文：同时提高总分并降低惩罚后，取效果最好的一条。"""

from __future__ import annotations

import unittest

from plugins.parallel_k_rewrite.select_best import (
    is_strictly_better,
    pick_best_candidate,
    pick_rewrite_if_better,
    rank_key,
)


def _ev(*, s_fp: float, penalty: float) -> dict:
    return {
        "total_score": s_fp,
        "gates": {
            "score_gate": {"passed": s_fp >= 0.8, "value": s_fp},
            "penalty_gate": {"passed": penalty <= 0.25, "total_penalty": penalty},
        },
        "scores": {"quality_score": {"penalties": {"total_penalty": penalty}}},
    }


def _cand(idx: int, ev: dict, **extra) -> dict:
    row = {
        "candidate_index": idx,
        "text": f"t{idx}",
        "temperature": 0.4,
        "dedupe_kept": True,
        "evaluation": ev,
    }
    row.update(extra)
    return row


class SelectBestTests(unittest.TestCase):
    def test_higher_score_ranks_first_then_lower_penalty(self) -> None:
        higher_score = _ev(s_fp=0.91, penalty=0.4)
        lower_score = _ev(s_fp=0.82, penalty=0.1)
        self.assertGreater(rank_key(higher_score), rank_key(lower_score))
        same_score_cleaner = _ev(s_fp=0.91, penalty=0.2)
        self.assertGreater(rank_key(same_score_cleaner), rank_key(higher_score))

    def test_both_improvements_required(self) -> None:
        baseline = _ev(s_fp=0.40, penalty=0.6)
        self.assertTrue(is_strictly_better(_ev(s_fp=0.71, penalty=0.0), baseline))
        self.assertFalse(is_strictly_better(_ev(s_fp=0.71, penalty=0.6), baseline))
        self.assertFalse(is_strictly_better(_ev(s_fp=0.40, penalty=0.0), baseline))
        self.assertFalse(is_strictly_better(_ev(s_fp=0.30, penalty=0.1), baseline))

    def test_score_up_penalty_not_down_keeps_original(self) -> None:
        baseline = _ev(s_fp=0.39, penalty=0.6)
        higher_same_penalty = _cand(0, _ev(s_fp=0.71, penalty=0.6))
        self.assertIsNone(
            pick_rewrite_if_better(
                baseline_evaluation=baseline,
                candidates=[higher_same_penalty],
            )
        )

    def test_not_better_keeps_original(self) -> None:
        baseline = _ev(s_fp=0.72, penalty=0.2)
        worse = _cand(0, _ev(s_fp=0.70, penalty=0.3))
        same = _cand(1, _ev(s_fp=0.72, penalty=0.2))
        self.assertIsNone(
            pick_rewrite_if_better(baseline_evaluation=baseline, candidates=[worse, same])
        )

    def test_better_rewrite_accepted_below_absolute_gate(self) -> None:
        baseline = _ev(s_fp=0.39, penalty=0.6)
        better = _cand(2, _ev(s_fp=0.71, penalty=0.0))
        chosen = pick_rewrite_if_better(baseline_evaluation=baseline, candidates=[better])
        self.assertIsNotNone(chosen)
        self.assertEqual(chosen["candidate_index"], 2)

    def test_best_effect_is_highest_score_among_improvers(self) -> None:
        baseline = _ev(s_fp=0.40, penalty=0.6)
        lower_score = _cand(0, _ev(s_fp=0.71, penalty=0.0))
        higher_score = _cand(1, _ev(s_fp=0.84, penalty=0.2))
        chosen = pick_best_candidate(
            [lower_score, higher_score],
            baseline_evaluation=baseline,
        )
        self.assertEqual(chosen["candidate_index"], 1)

    def test_lower_score_does_not_replace_higher_original(self) -> None:
        baseline = _ev(s_fp=0.96, penalty=0.2)
        lower = _cand(0, _ev(s_fp=0.84, penalty=0.0))
        self.assertIsNone(
            pick_rewrite_if_better(baseline_evaluation=baseline, candidates=[lower])
        )

    def test_skips_dupes_and_errors(self) -> None:
        baseline = _ev(s_fp=0.4, penalty=0.5)
        good = _cand(1, _ev(s_fp=0.9, penalty=0.0))
        dup = _cand(0, _ev(s_fp=0.99, penalty=0.0), dedupe_kept=False)
        err = _cand(2, _ev(s_fp=0.99, penalty=0.0), error="boom")
        chosen = pick_best_candidate(
            [dup, err, good],
            baseline_evaluation=baseline,
        )
        self.assertEqual(chosen["candidate_index"], 1)


if __name__ == "__main__":
    unittest.main()
