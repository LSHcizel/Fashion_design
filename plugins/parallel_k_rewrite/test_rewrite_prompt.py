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
        self.assertLess(prompt.index("SOURCE TEXT TO REWRITE:"), prompt.index("THEME AND CONCEPT"))
        self.assertLess(prompt.index("Chapter: salon-to-beach"), prompt.index("THEME AND CONCEPT"))
        self.assertIn("A cropped navy jacket", prompt[: prompt.index("THEME AND CONCEPT")])
        self.assertIn("Chapter: salon-to-beach", prompt)
        self.assertIn("THEME AND CONCEPT", prompt)
        self.assertIn("ONE OUTFIT", prompt)
        self.assertIn("VISIBLE FACTS", prompt)
        self.assertIn("BRAND LOGO LOCK", prompt)
        self.assertNotIn("BRAND STYLE CARD", prompt)
        self.assertNotIn("REWRITE DIRECTION", prompt)
        self.assertIn("MUST NOT replace it with another brand", prompt)
        self.assertIn("Choose the resolution yourself", prompt)
        self.assertIn("Do not write Chinese", prompt)
        self.assertIn("head to shoes", prompt)
        self.assertIn("one sampling temperature", prompt)
        self.assertIn("does not assign one legal edit", prompt)
        self.assertIn("SINGLE FRAME", prompt)
        self.assertIn("CLOTHED RUNWAY", prompt)
        self.assertIn("bare chest", prompt)
        self.assertIn("one camera in front of her face", prompt)
        self.assertIn("Front view only, not from behind", prompt)
        self.assertIn("Look number", prompt)
        self.assertIn("different theme or concept", prompt)
        self.assertIn("garment pairing", prompt)
        self.assertIn("add or delete", prompt)
        self.assertIn("expand the description", prompt)
        self.assertIn("moderate new element", prompt)
        self.assertNotIn("below is complete", prompt)
        self.assertNotIn("another show", prompt)
        self.assertNotIn("An inner layer stays visible", prompt)
        self.assertNotIn("business note to preserve", prompt)
        self.assertNotIn("moderately rebuild", prompt)
        self.assertNotIn("paraphrase of SOURCE", prompt)
        self.assertNotIn("Do not restate SOURCE", prompt)
        self.assertNotIn("InformationDensity", prompt)
        self.assertNotIn("quality-axis dimension", prompt)
        self.assertNotIn("LEFT-RIGHT EXAMPLE", prompt)
        self.assertNotIn("SAME-ELEMENT EXAMPLE", prompt)
        self.assertNotIn("copy that edit", prompt)
        self.assertNotIn("KEEP THIS SIDE", prompt)
        self.assertNotIn("Keep every other garment already in SOURCE", prompt)
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
        self.assertIn("one sampling temperature", prompts[0])
        self.assertIn("The rewrite rules stay the same", prompts[0])

    def test_policy_constants_lock_theme_logo_and_allow_whole_look_change(self) -> None:
        self.assertIn("Extract the theme and the design concept", REWRITE_STYLE_CONCEPT_LOCK)
        self.assertIn("camera can photograph", REWRITE_ELEMENT_RECONSTRUCTION)
        self.assertNotIn("raise DesignMerit", REWRITE_ELEMENT_RECONSTRUCTION)
        self.assertIn("garment pairing", REWRITE_WHOLE_LOOK_SCOPE)
        self.assertIn("Choose the resolution yourself", REWRITE_WHOLE_LOOK_SCOPE)
        self.assertIn("different theme or concept", REWRITE_STYLE_CONCEPT_LOCK)
        self.assertIn("SAME house", REWRITE_BRAND_LOGO_LOCK)
        self.assertIn("MUST NOT replace it with another brand", REWRITE_BRAND_LOGO_LOCK)
        self.assertIn("Keep that theme", REWRITE_STYLE_CONCEPT_LOCK)
        self.assertIn("identifying features", REWRITE_STYLE_CONCEPT_LOCK)
        self.assertIn("add or delete", REWRITE_WHOLE_LOOK_SCOPE)
        self.assertIn("expand the description", REWRITE_WHOLE_LOOK_SCOPE)
        self.assertNotIn("BRAND STYLE CARD", REWRITE_STYLE_CONCEPT_LOCK)

    def test_optimizer_system_prompt_matches_policy(self) -> None:
        prompt = SYS_PROMPT.read_text(encoding="utf-8")
        self.assertIn("Keep the theme and design concept already in the source", prompt)
        self.assertIn("add or delete", prompt)
        self.assertIn("expand the description", prompt)
        self.assertIn("moderate new element", prompt)
        self.assertNotIn("another show's clothes", prompt)
        self.assertNotIn("business note says to preserve", prompt)
        self.assertNotIn("moderately rebuild", prompt)
        self.assertNotIn("paraphrase of the source", prompt)
        self.assertNotIn("Do not paraphrase SOURCE", prompt)
        self.assertIn("Choose the resolution yourself", prompt)
        self.assertIn("another house's logo", prompt)
        self.assertNotIn("BRAND STYLE CARD", prompt)
        self.assertNotIn("quality-axis dimension", prompt)
        self.assertNotIn("BindingAccuracy", prompt)
        self.assertIn("or Chinese", prompt)
        self.assertIn("Front view, full figure from head to shoes", prompt)
        self.assertIn("Look number", prompt)
        self.assertIn("does not assign one legal edit", prompt)
        self.assertIn("one pair of shoes", prompt)
        self.assertIn("Exposed skin does not raise", prompt)
        self.assertNotIn("LEFT-RIGHT EXAMPLE", prompt)
        self.assertNotIn("SAME-ELEMENT EXAMPLE", prompt)
        self.assertNotIn("copy that edit", prompt)
        self.assertNotIn("DELETE list", prompt)
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
        self.assertIn("标志性风格卡", spec)
        self.assertIn("与主题冲突时以原文主题为准", spec)
        self.assertIn("\"penalty_gate_max\": 0.2", spec)
        self.assertIn("必须删除另一套衣服并严格统一成一套", spec)
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
        self.assertNotIn("bilateral_coherence", brief)
        self.assertIn("consistency_penalty", brief)
        self.assertNotIn("spatial_coherence", brief)
        self.assertIn("EXPOSED PENALTY DEDUCTIONS", brief)
        self.assertIn("do not assign one legal edit", brief)
        self.assertIn("coordination_penalty", brief)
        deducted = format_exposed_repair_brief(
            {
                "scores": {
                    "quality_score": {
                        "negative_k": 2,
                        "negative_slots": ["sleeve", "bottom"],
                        "penalties": {"items": {}},
                    }
                }
            }
        )
        self.assertIn("QUALITY DEDUCTION: k=2", deducted)
        self.assertIn("two sleeve grammars", deducted)
        self.assertIn("two bottoms", deducted)
        self.assertNotIn("formula_template_penalty", brief)
        self.assertNotIn("KEEP THIS SIDE", brief)
        self.assertNotIn("LEFT-RIGHT EXAMPLE", brief)
        self.assertEqual(format_exposed_repair_brief({}), "")
        self.assertEqual(format_exposed_repair_brief(None), "")
        self.assertEqual(
            format_exposed_repair_brief(
                None,
                source_text="The left sleeve is matte wool. The right sleeve is silk.",
            ),
            "",
        )
        scored = format_exposed_repair_brief(
            {
                "metric_results": {
                    "spatial_coherence": {
                        "applicable": True,
                        "score_value": 0.25,
                        "reason": "虽然左右是两套衣服，但每边只写了一种材质。",
                    }
                },
                "scores": {"quality_score": {"penalties": {"items": {}}}},
            },
            source_text="The left sleeve is matte wool. The right sleeve is silk.",
        )
        self.assertIn("spatial_coherence", scored)
        self.assertNotIn("虽然左右", scored)
        self.assertNotIn("KEEP THIS SIDE", scored)
        self.assertNotIn("DELETE THESE GARMENTS", scored)
        self.assertNotIn("LEFT-RIGHT EXAMPLE", scored)


if __name__ == "__main__":
    unittest.main()
