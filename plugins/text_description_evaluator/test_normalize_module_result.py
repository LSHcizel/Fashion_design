"""Local 7B judge sometimes returns non-dict ``results`` items."""

from __future__ import annotations

import unittest

from plugins.text_description_evaluator.design_text_evaluator_api import (
    ApiLLMJudge,
    coerce_judge_result_items,
)


class CoerceJudgeResultsTests(unittest.TestCase):
    def test_skips_bare_strings_and_keeps_dicts(self) -> None:
        items = coerce_judge_result_items(
            ["silhouette_clarity", {"metric": "color_logic", "applicable": True, "score": 1}]
        )
        self.assertEqual(items[0]["metric"], "silhouette_clarity")
        self.assertEqual(items[1]["metric"], "color_logic")
        self.assertEqual(items[1]["score"], 1)

    def test_metric_keyed_dict(self) -> None:
        items = coerce_judge_result_items({"belt": {"applicable": False, "score": None}})
        self.assertEqual(items[0]["metric"], "belt")
        self.assertFalse(items[0]["applicable"])

    def test_normalize_does_not_crash_on_string_results(self) -> None:
        judge = ApiLLMJudge(api_key="local", api_base="http://127.0.0.1:8000/v1", model="dummy")
        specs = [{"metric": "silhouette_clarity"}, {"metric": "color_logic"}]
        out = judge._normalize_module_result(
            "Coverage",
            specs,
            {"results": ["silhouette_clarity", "not-a-dict"]},
            "coverage_score",
        )
        self.assertEqual(len(out["results"]), 2)
        self.assertEqual(out["results"][0]["metric"], "silhouette_clarity")
        self.assertFalse(out["results"][0]["applicable"])


if __name__ == "__main__":
    unittest.main()
