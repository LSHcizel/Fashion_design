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


class JudgeJsonRetryTests(unittest.TestCase):
    INCOMPLETE = (
        '{\n'
        '  "module": "LanguageClarity",\n'
        '  "results": [\n'
        '    {\n'
        '      "metric": "quantity_accuracy",\n'
        '      "applicable": true,\n'
        '      "score": 1.0,\n'
        '      "evidence": ["light aqua-blue", "relaxed oversized"],\n'
        '      "reason": "'
    )

    def _judge(self) -> ApiLLMJudge:
        return ApiLLMJudge(api_key="local", api_base="http://127.0.0.1:8000/v1", model="dummy")

    def test_extract_raises_on_truncated_json(self) -> None:
        judge = self._judge()
        with self.assertRaises(ValueError) as ctx:
            judge._parse_json(self.INCOMPLETE)
        self.assertIn("incomplete JSON", str(ctx.exception))

    def test_retry_then_empty_fallback(self) -> None:
        judge = self._judge()
        calls = {"n": 0}

        def raw_factory() -> str:
            calls["n"] += 1
            return self.INCOMPLETE

        parsed = judge._parse_json_with_retry(raw_factory, label="test", attempts=3)
        self.assertEqual(parsed, {})
        self.assertEqual(calls["n"], 3)

    def test_retry_succeeds_on_later_attempt(self) -> None:
        judge = self._judge()
        replies = [
            self.INCOMPLETE,
            '{"module": "LanguageClarity", "results": [{"metric": "quantity_accuracy", "applicable": true, "score": 1.0}]}',
        ]

        parsed = judge._parse_json_with_retry(lambda: replies.pop(0), label="test", attempts=3)
        self.assertEqual(parsed["module"], "LanguageClarity")
        self.assertEqual(parsed["results"][0]["score"], 1.0)

    def test_judge_module_does_not_raise_on_truncated_json(self) -> None:
        judge = self._judge()
        judge._request_completion = lambda **kwargs: self.INCOMPLETE  # type: ignore[method-assign]
        out = judge.judge_module(
            "a light aqua-blue oversized shirt",
            "LanguageClarity",
            [{"metric": "quantity_accuracy"}],
            "coverage_score",
        )
        self.assertEqual(out["results"][0]["metric"], "quantity_accuracy")
        self.assertFalse(out["results"][0]["applicable"])


if __name__ == "__main__":
    unittest.main()
