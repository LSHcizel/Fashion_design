"""K 路采样：同一提示词，同一温度。"""

from __future__ import annotations

import unittest

from plugins.parallel_k_rewrite.k_candidate_generator import (
    _one_rewrite,
    shared_rewrite_temperature,
)


class SharedTemperatureTests(unittest.TestCase):
    def test_config_temperature_is_shared(self) -> None:
        self.assertEqual(shared_rewrite_temperature(), 0.9)
        self.assertEqual(shared_rewrite_temperature({"temperature": 1.4}), 1.0)
        self.assertEqual(shared_rewrite_temperature({"temperature": -1}), 0.0)
        self.assertEqual(shared_rewrite_temperature({}), 0.9)

    def test_one_rewrite_sends_only_temperature(self) -> None:
        seen = {}

        class _Judge:
            max_tokens = 32

            def generate_text(self, **kwargs):
                seen.update(kwargs)
                return "A navy coat and black shoes."

        class _Ev:
            optimizer_system_prompt = "sys"
            judge = _Judge()

            def _validate_optimized_text(self, raw, _src):
                return raw

            def _normalize_optimized_text(self, text):
                return text

        row = _one_rewrite(
            _Ev(),
            "src",
            k=8,
            candidate_index=6,
            extra_context="",
            temperature_floor=0.9,
            temperature_step=0.0,
            temperature_cap=0.9,
        )
        self.assertEqual(seen["temperature"], 0.9)
        self.assertNotIn("top_p", seen)
        self.assertNotIn("presence_penalty", seen)
        self.assertNotIn("repetition_penalty", seen)
        self.assertNotIn("frequency_penalty", seen)
        self.assertEqual(row["temperature"], 0.9)
        self.assertIn("one sampling temperature", seen["user_prompt"])
        self.assertEqual(
            _one_rewrite(
                _Ev(),
                "src",
                k=8,
                candidate_index=0,
                extra_context="",
                temperature_floor=0.9,
                temperature_step=0.0,
                temperature_cap=0.9,
            )["temperature"],
            row["temperature"],
        )


if __name__ == "__main__":
    unittest.main()
