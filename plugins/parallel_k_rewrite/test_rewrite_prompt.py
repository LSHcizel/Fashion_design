"""改写 user prompt：锁住原风格概念，允许局部元素调整/替换。"""

from __future__ import annotations

import unittest

from pathlib import Path

from plugins.parallel_k_rewrite.k_candidate_generator import (
    REWRITE_LOCAL_EDITS_ALLOWED,
    REWRITE_STYLE_CONCEPT_LOCK,
    build_rewrite_user_prompt,
)

SYS_PROMPT = (
    Path(__file__).resolve().parents[1]
    / "text_description_evaluator"
    / "fashion_sys_prompt.txt"
)


class RewritePromptPolicyTests(unittest.TestCase):
    def test_user_prompt_locks_style_and_allows_local_edits(self) -> None:
        prompt = build_rewrite_user_prompt(
            "A cropped navy jacket over a white shirt and beige shorts with a self-belt.",
            k=10,
            candidate_index=2,
            extra_context="Chapter: salon-to-beach",
        )
        self.assertIn("rewrite candidate #3 of 10", prompt)
        self.assertIn("SOURCE TEXT TO REWRITE:", prompt)
        self.assertIn("Chapter: salon-to-beach", prompt)
        self.assertIn("STYLE CONCEPT LOCK", prompt)
        self.assertIn("LOCAL EDITS ALLOWED", prompt)
        self.assertIn("local element adjustments or replacements", prompt)
        self.assertNotIn("Do not invent new garments, surfaces, or trims.", prompt)
        self.assertNotIn("do not invent new facts", prompt)
        self.assertIn("Local replacements must serve that idea, not replace it.", prompt)

    def test_policy_constants_forbid_restyle(self) -> None:
        self.assertIn("Do not restyle the look into a different concept", REWRITE_STYLE_CONCEPT_LOCK)
        self.assertIn("Prefer replace/adjust over adding a new garment", REWRITE_LOCAL_EDITS_ALLOWED)

    def test_optimizer_system_prompt_matches_policy(self) -> None:
        prompt = SYS_PROMPT.read_text(encoding="utf-8")
        self.assertIn("Preserve the original style concept", prompt)
        self.assertIn("Local element pass", prompt)
        self.assertIn("local replacements must serve that idea", prompt.lower())
        self.assertNotIn(
            "Do not invent a new identifying idea, garment, surface, or trim that is not grounded in the source.",
            prompt,
        )


if __name__ == "__main__":
    unittest.main()
