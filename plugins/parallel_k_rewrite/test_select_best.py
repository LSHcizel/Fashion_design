"""K 路 vs 原文：过门优先、同分比惩罚、不优于则退回。"""

from __future__ import annotations

import unittest

from plugins.parallel_k_rewrite.select_best import (
    is_strictly_better,
    pick_best_candidate,
    pick_rewrite_if_better,
    rank_key,
)


def _ev(*, passed: bool, s_fp: float, penalty: float) -> dict:
    return {
        "total_score": s_fp,
        "gates": {
            "both_passed": passed,
            "score_gate": {"passed": passed, "value": s_fp},
            "penalty_gate": {"passed": passed or penalty <= 0.5, "total_penalty": penalty},
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
    def test_gate_pass_ranks_above_fail(self) -> None:
        self.assertGreater(
            rank_key(_ev(passed=True, s_fp=0.81, penalty=0.1)),
            rank_key(_ev(passed=False, s_fp=0.99, penalty=0.0)),
        )

    def test_same_gate_prefers_lower_penalty(self) -> None:
        high_pen = _ev(passed=False, s_fp=0.75, penalty=0.4)
        low_pen = _ev(passed=False, s_fp=0.75, penalty=0.1)
        self.assertTrue(is_strictly_better(low_pen, high_pen))

    def test_not_better_keeps_original(self) -> None:
        baseline = _ev(passed=False, s_fp=0.72, penalty=0.2)
        worse = _cand(0, _ev(passed=False, s_fp=0.70, penalty=0.3))
        same = _cand(1, _ev(passed=False, s_fp=0.72, penalty=0.2))
        self.assertIsNone(pick_rewrite_if_better(baseline_evaluation=baseline, candidates=[worse, same]))

    def test_better_rewrite_accepted(self) -> None:
        baseline = _ev(passed=False, s_fp=0.72, penalty=0.2)
        better = _cand(2, _ev(passed=True, s_fp=0.85, penalty=0.1))
        chosen = pick_rewrite_if_better(baseline_evaluation=baseline, candidates=[better])
        self.assertIsNotNone(chosen)
        self.assertEqual(chosen["candidate_index"], 2)

    def test_skips_dupes_and_errors(self) -> None:
        good = _cand(1, _ev(passed=True, s_fp=0.9, penalty=0.0))
        dup = _cand(0, _ev(passed=True, s_fp=0.99, penalty=0.0), dedupe_kept=False)
        err = _cand(2, _ev(passed=True, s_fp=0.99, penalty=0.0), error="boom")
        self.assertEqual(pick_best_candidate([dup, err, good])["candidate_index"], 1)


if __name__ == "__main__":
    unittest.main()
