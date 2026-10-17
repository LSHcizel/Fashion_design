"""K 路 vs 原文：总分上升且惩罚不超门限后，取得分最高的一条。"""

from __future__ import annotations

import unittest

from plugins.parallel_k_rewrite.select_best import (
    DEFAULT_PENALTY_GATE_MAX,
    adoptable_rewrite,
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
            "penalty_gate": {
                "passed": penalty <= DEFAULT_PENALTY_GATE_MAX,
                "total_penalty": penalty,
            },
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

    def test_score_up_inside_gate_is_adoptable_even_if_penalty_rises(self) -> None:
        baseline = _ev(s_fp=0.40, penalty=0.05)
        self.assertTrue(adoptable_rewrite(_ev(s_fp=0.71, penalty=0.2), baseline))
        self.assertTrue(is_strictly_better(_ev(s_fp=0.71, penalty=0.0), baseline))
        self.assertFalse(adoptable_rewrite(_ev(s_fp=0.71, penalty=0.25), baseline))
        self.assertFalse(adoptable_rewrite(_ev(s_fp=0.40, penalty=0.0), baseline))
        self.assertFalse(adoptable_rewrite(_ev(s_fp=0.30, penalty=0.1), baseline))

    def test_score_up_over_gate_keeps_original(self) -> None:
        baseline = _ev(s_fp=0.39, penalty=0.6)
        higher_over_gate = _cand(0, _ev(s_fp=0.71, penalty=0.25))
        self.assertIsNone(
            pick_rewrite_if_better(
                baseline_evaluation=baseline,
                candidates=[higher_over_gate],
            )
        )

    def test_score_up_penalty_not_lower_is_adoptable_inside_gate(self) -> None:
        baseline = _ev(s_fp=0.39, penalty=0.05)
        higher_same_band = _cand(0, _ev(s_fp=0.71, penalty=0.2))
        chosen = pick_rewrite_if_better(
            baseline_evaluation=baseline,
            candidates=[higher_same_band],
        )
        self.assertIsNotNone(chosen)
        self.assertEqual(chosen["candidate_index"], 0)

    def test_not_better_keeps_original(self) -> None:
        baseline = _ev(s_fp=0.72, penalty=0.2)
        worse = _cand(0, _ev(s_fp=0.70, penalty=0.1))
        same = _cand(1, _ev(s_fp=0.72, penalty=0.0))
        self.assertIsNone(
            pick_rewrite_if_better(baseline_evaluation=baseline, candidates=[worse, same])
        )

    def test_better_rewrite_accepted_below_absolute_score_gate(self) -> None:
        baseline = _ev(s_fp=0.39, penalty=0.6)
        better = _cand(2, _ev(s_fp=0.71, penalty=0.0))
        chosen = pick_rewrite_if_better(baseline_evaluation=baseline, candidates=[better])
        self.assertIsNotNone(chosen)
        self.assertEqual(chosen["candidate_index"], 2)

    def test_best_effect_is_highest_score_among_adoptable(self) -> None:
        baseline = _ev(s_fp=0.40, penalty=0.6)
        lower_score = _cand(0, _ev(s_fp=0.71, penalty=0.0))
        higher_score = _cand(1, _ev(s_fp=0.84, penalty=0.2))
        over_gate = _cand(2, _ev(s_fp=0.95, penalty=0.25))
        chosen = pick_best_candidate(
            [lower_score, higher_score, over_gate],
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

    def test_custom_gate_can_exclude_boundary(self) -> None:
        baseline = _ev(s_fp=0.4, penalty=0.5)
        at_default_gate = _cand(0, _ev(s_fp=0.8, penalty=0.2))
        self.assertIsNotNone(
            pick_rewrite_if_better(
                baseline_evaluation=baseline,
                candidates=[at_default_gate],
            )
        )
        self.assertIsNone(
            pick_rewrite_if_better(
                baseline_evaluation=baseline,
                candidates=[at_default_gate],
                penalty_gate_max=0.15,
            )
        )


if __name__ == "__main__":
    unittest.main()
