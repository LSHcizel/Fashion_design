"""Incomplete judge JSON must skip a candidate, not abort the K-path group."""

from __future__ import annotations

import threading
import unittest
from unittest.mock import Mock, patch

from plugins.parallel_k_rewrite.k_candidate_generator import (
    _evaluate_candidates_with_spec,
    generate_k_parallel_rewrites,
)
from plugins.text_description_evaluator.design_text_evaluator_api import JudgeConnectionError


class EvaluateParseErrorTests(unittest.TestCase):
    def test_truncated_json_marks_skipped_and_continues(self) -> None:
        evaluator = Mock()
        evaluator.evaluate_text.side_effect = ValueError(
            "LLM judge returned incomplete JSON:\n{ \"module\": \"LanguageClarity\""
        )
        evaluator.spec = {"r_content_for_rl": {}}
        cands = [
            {
                "candidate_index": 0,
                "text": "look a",
                "dedupe_kept": True,
                "error": None,
            },
            {
                "candidate_index": 1,
                "text": "look b",
                "dedupe_kept": True,
                "error": None,
            },
        ]
        group_evals = _evaluate_candidates_with_spec(
            evaluator,
            cands,
            gate_config=None,
            eval_source_prefix="g",
            eval_max_workers=2,
        )
        self.assertEqual(group_evals, [])
        for c in cands:
            self.assertIsNone(c["evaluation"])
            self.assertEqual(c["evaluation_skipped"], "judge_eval_error")
            self.assertIn("incomplete JSON", c["evaluation_error"])
        self.assertEqual(evaluator.evaluate_text.call_count, 2)

    def test_score_starts_while_other_rewrites_still_run(self) -> None:
        eval_started = threading.Event()

        def fake_rewrite(*args, **kwargs):
            idx = args[3]
            if idx == 1:
                self.assertTrue(eval_started.wait(3), "score did not start before the second rewrite finished")
            return {
                "candidate_index": idx,
                "text": f"look {idx}",
                "char_len": 6,
                "temperature": 0.2,
                "error": None,
            }

        def fake_score(evaluator, idx, cand, **kwargs):
            eval_started.set()
            return idx, None, "skip"

        evaluator = Mock()
        evaluator.spec = {"r_content_for_rl": {}}
        with patch(
            "plugins.parallel_k_rewrite.k_candidate_generator._one_rewrite",
            side_effect=fake_rewrite,
        ), patch(
            "plugins.parallel_k_rewrite.k_candidate_generator._score_one_candidate",
            side_effect=fake_score,
        ):
            result = generate_k_parallel_rewrites(
                "source look",
                k=2,
                evaluator=evaluator,
                max_workers=2,
                eval_max_workers=2,
                evaluate_candidates=True,
            )
        self.assertEqual(result["k_returned"], 2)
        self.assertTrue(eval_started.is_set())

    def test_connection_error_still_raises(self) -> None:
        evaluator = Mock()
        evaluator.evaluate_text.side_effect = JudgeConnectionError("connection refused")
        cands = [
            {
                "candidate_index": 0,
                "text": "look a",
                "dedupe_kept": True,
                "error": None,
            }
        ]
        with self.assertRaises(JudgeConnectionError):
            _evaluate_candidates_with_spec(
                evaluator,
                cands,
                gate_config=None,
                eval_source_prefix="g",
                eval_max_workers=1,
            )


if __name__ == "__main__":
    unittest.main()
