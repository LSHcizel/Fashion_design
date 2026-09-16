"""改写 user prompt：K 路共用抽主题/概念再重构要素，差异靠温度。"""

from __future__ import annotations

import unittest

from pathlib import Path

from plugins.parallel_k_rewrite.k_candidate_generator import (
    REWRITE_ELEMENT_RECONSTRUCTION,
    REWRITE_STYLE_CONCEPT_LOCK,
    build_rewrite_user_prompt,
)

SYS_PROMPT = (
    Path(__file__).resolve().parents[1]
    / "text_description_evaluator"
    / "fashion_sys_prompt.txt"
)

SPEC_JSON = (
    Path(__file__).resolve().parents[1]
    / "text_description_evaluator"
    / "fashion_prompt_optimizer_spec.json"
)

_COMBO_PHRASES = (
    "cropped jacket + shirt + short",
    "cropped-jacket + shirt + short",
    "短夹克+衬衫+短裤",
    "短夹克 + 衬衫 + 短裤",
)


class RewritePromptPolicyTests(unittest.TestCase):
    def test_user_prompt_extracts_theme_then_reconstructs(self) -> None:
        prompt = build_rewrite_user_prompt(
            "A cropped navy jacket over a white shirt and beige shorts with a self-belt.",
            k=10,
            candidate_index=2,
            extra_context="Chapter: salon-to-beach",
        )
        self.assertIn("rewrite candidate #3 of 10", prompt)
        self.assertIn("SOURCE TEXT TO REWRITE:", prompt)
        self.assertIn("Chapter: salon-to-beach", prompt)
        self.assertIn("THEME AND CONCEPT LOCK", prompt)
        self.assertIn("ELEMENT RECONSTRUCTION", prompt)
        self.assertIn("different temperatures", prompt)
        self.assertIn("Extract theme and concept from SOURCE only", prompt)
        self.assertNotIn("THIS CANDIDATE'S TASK", prompt)
        self.assertNotIn("strategy=", prompt)
        for phrase in _COMBO_PHRASES:
            self.assertNotIn(phrase, prompt)

    def test_all_k_share_the_same_strategy_text(self) -> None:
        prompts = [build_rewrite_user_prompt("source look.", k=10, candidate_index=i) for i in range(10)]
        bodies = []
        for i, prompt in enumerate(prompts):
            marker = f"rewrite candidate #{i + 1} of 10"
            self.assertIn(marker, prompt)
            bodies.append(prompt.replace(marker, "rewrite candidate #N of 10"))
        self.assertEqual(len(set(bodies)), 1)

    def test_policy_constants_lock_theme_and_allow_reconstruction(self) -> None:
        self.assertIn("extract the theme and the design concept", REWRITE_STYLE_CONCEPT_LOCK)
        self.assertIn("redesign the look's elements", REWRITE_ELEMENT_RECONSTRUCTION)
        self.assertIn("raise DesignMerit", REWRITE_ELEMENT_RECONSTRUCTION)

    def test_optimizer_system_prompt_matches_policy(self) -> None:
        prompt = SYS_PROMPT.read_text(encoding="utf-8")
        self.assertIn("Extract the theme and the design concept", prompt)
        self.assertIn("Element reconstruction pass", prompt)
        self.assertIn("collection-shared, interchangeable trunk-garment formula", prompt)
        for phrase in _COMBO_PHRASES:
            self.assertNotIn(phrase, prompt)

    def test_spec_and_judge_guide_use_generic_formula_wording(self) -> None:
        spec = SPEC_JSON.read_text(encoding="utf-8")
        for phrase in _COMBO_PHRASES:
            self.assertNotIn(phrase, spec)
        self.assertIn("公式化组合", spec)
        from plugins.text_description_evaluator.design_text_evaluator_api import (
            DESIGN_MERIT_JUDGE_GUIDE,
        )

        for phrase in _COMBO_PHRASES:
            self.assertNotIn(phrase, DESIGN_MERIT_JUDGE_GUIDE)
        self.assertIn("interchangeable trunk-garment formula", DESIGN_MERIT_JUDGE_GUIDE)


if __name__ == "__main__":
    unittest.main()
