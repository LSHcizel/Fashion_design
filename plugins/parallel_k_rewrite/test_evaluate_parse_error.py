"""Incomplete judge JSON must skip a candidate, not abort the K-path group."""

from __future__ import annotations

import unittest
from unittest.mock import Mock

from plugins.parallel_k_rewrite.k_candidate_generator import _evaluate_candidates_with_spec
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
