"""改写 user prompt：可见想法不限数量，须服务主题并处理已暴露的一致性与惩罚。"""

from __future__ import annotations

import unittest

from pathlib import Path

from plugins.parallel_k_rewrite.k_candidate_generator import (
    REWRITE_BRAND_LOGO_LOCK,
    REWRITE_ELEMENT_RECONSTRUCTION,
    REWRITE_STYLE_CONCEPT_LOCK,
    REWRITE_WHOLE_LOOK_SCOPE,
    build_rewrite_user_prompt,
    format_exposed_repair_brief,
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
    def test_user_prompt_asks_to_adjust_idea_without_assigning_kind(self) -> None:
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
        self.assertIn("WHOLE-LOOK CHANGE", prompt)
        self.assertIn("ELEMENT RECONSTRUCTION", prompt)
        self.assertIn("BRAND LOGO LOCK", prompt)
        self.assertIn("MUST NOT replace it with another brand", prompt)
        self.assertIn("not a quota", prompt)
        self.assertIn("count is not fixed", prompt)
        self.assertIn("serve the theme and concept extracted from SOURCE", prompt)
        self.assertIn("lower every listed penalty", prompt)
        self.assertIn("one footwear family", prompt)
        self.assertIn("contradictory binding", prompt)
        self.assertIn("different theme or concept", prompt)
        self.assertIn("failed rewrite", prompt)
        self.assertIn("Delete the other side", prompt)
        self.assertIn("color and palette", prompt)
        self.assertIn("garment pairing", prompt)
        self.assertIn("detail design", prompt)
        self.assertNotIn("THIS CANDIDATE'S TASK", prompt)
        self.assertNotIn("Assigned identifying-idea kind", prompt)
        self.assertNotIn("surface_field", prompt)
        self.assertNotIn("second_identity", prompt)
        for phrase in _COMBO_PHRASES:
            self.assertNotIn(phrase, prompt)

    def test_all_k_share_the_same_policy_text(self) -> None:
        prompts = [
            build_rewrite_user_prompt("source look.", k=10, candidate_index=i) for i in range(10)
        ]
        bodies = []
        for i, prompt in enumerate(prompts):
            marker = f"rewrite candidate #{i + 1} of 10"
            self.assertIn(marker, prompt)
            bodies.append(prompt.replace(marker, "rewrite candidate #N of 10"))
        self.assertEqual(len(set(bodies)), 1)
        self.assertIn("different temperatures", prompts[0])

    def test_policy_constants_lock_theme_logo_and_allow_whole_look_change(self) -> None:
        self.assertIn("extract the theme and the design concept", REWRITE_STYLE_CONCEPT_LOCK)
        self.assertIn("redesign the look's elements", REWRITE_ELEMENT_RECONSTRUCTION)
        self.assertIn("raise DesignMerit", REWRITE_ELEMENT_RECONSTRUCTION)
        self.assertIn("color and palette", REWRITE_WHOLE_LOOK_SCOPE)
        self.assertIn("garment pairing", REWRITE_WHOLE_LOOK_SCOPE)
        self.assertIn("detail design", REWRITE_WHOLE_LOOK_SCOPE)
        self.assertIn("SAME extracted theme and concept", REWRITE_WHOLE_LOOK_SCOPE)
        self.assertIn("different theme or concept", REWRITE_STYLE_CONCEPT_LOCK)
        self.assertIn("SAME house", REWRITE_BRAND_LOGO_LOCK)
        self.assertIn("MUST NOT replace it with another brand", REWRITE_BRAND_LOGO_LOCK)

    def test_optimizer_system_prompt_matches_policy(self) -> None:
        prompt = SYS_PROMPT.read_text(encoding="utf-8")
        self.assertIn("Extract the theme and the design concept", prompt)
        self.assertIn("Element reconstruction pass", prompt)
        self.assertIn("collection-shared, interchangeable trunk-garment formula", prompt)
        self.assertIn("Brand logo lock", prompt)
        self.assertIn("not a quota and not an assignment", prompt)
        self.assertIn("count is not fixed", prompt)
        self.assertIn("Repair pass", prompt)
        self.assertIn("one footwear family", prompt)
        self.assertIn("different theme or concept", prompt)
        self.assertIn("must not replace it with another brand", prompt)
        self.assertIn("color/palette, garment pairing", prompt)
        self.assertIn("does not require keeping SOURCE's original palette", prompt)
        self.assertNotIn("assigned a specific identifying-idea kind", prompt)
        for phrase in _COMBO_PHRASES:
            self.assertNotIn(phrase, prompt)

    def test_spec_and_judge_guide_use_generic_formula_wording(self) -> None:
        spec = SPEC_JSON.read_text(encoding="utf-8")
        for phrase in _COMBO_PHRASES:
            self.assertNotIn(phrase, spec)
        self.assertIn("公式化组合", spec)
        self.assertIn("不限固定数量", spec)
        self.assertIn("不预分配", spec)
        self.assertIn("一致性问题", spec)
        self.assertIn("惩罚扣分", spec)
        self.assertIn("不得因行文通顺打 0", spec)
        self.assertIn("两类及以上同时还在", spec)
        self.assertIn("本项 ≤ 0.25", spec)
        self.assertIn("允许改整体造型", spec)
        self.assertIn("禁止偏离原文主题与概念", spec)
        self.assertIn("禁止换成别的牌子", spec)
        from plugins.text_description_evaluator.design_text_evaluator_api import (
            DESIGN_MERIT_JUDGE_GUIDE,
        )

        for phrase in _COMBO_PHRASES:
            self.assertNotIn(phrase, DESIGN_MERIT_JUDGE_GUIDE)
        self.assertIn("interchangeable trunk-garment formula", DESIGN_MERIT_JUDGE_GUIDE)

    def test_repair_brief_lists_consistency_and_penalties(self) -> None:
        brief = format_exposed_repair_brief(
            {
                "metric_results": {
                    "bilateral_coherence": {
                        "applicable": True,
                        "score_value": 0.25,
                        "reason": "left sleeve and right sleeve are different garments",
                    },
                    "spatial_coherence": {
                        "applicable": True,
                        "score_value": 1.0,
                        "reason": "layering is clear",
                    },
                },
                "scores": {
                    "quality_score": {
                        "penalties": {
                            "items": {
                                "consistency_penalty": {
                                    "score": 0.5,
                                    "reason": "trunk left-right clash",
                                },
                                "formula_template_penalty": {
                                    "score": 0.0,
                                    "reason": "",
                                },
                                "coordination_penalty": {
                                    "score": 0.75,
                                    "reason": "oxford shoe against a sandal on the other foot",
                                },
                            }
                        }
                    }
                },
            }
        )
        self.assertIn("EXPOSED CONSISTENCY", brief)
        self.assertIn("bilateral_coherence", brief)
        self.assertIn("consistency_penalty", brief)
        self.assertNotIn("spatial_coherence", brief)
        self.assertIn("EXPOSED PENALTY DEDUCTIONS", brief)
        self.assertIn("one footwear family", brief)
        self.assertIn("contradictory binding", brief)
        self.assertIn("coordination_penalty", brief)
        self.assertNotIn("formula_template_penalty", brief)
        self.assertEqual(format_exposed_repair_brief({}), "")
        self.assertEqual(format_exposed_repair_brief(None), "")


if __name__ == "__main__":
    unittest.main()
