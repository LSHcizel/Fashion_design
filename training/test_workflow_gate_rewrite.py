"""工作流门限失败改写：yaml 开关，以及未被采纳时的废章判定。"""

from __future__ import annotations

import unittest
from pathlib import Path

import yaml

from workflow_subtheme_gate import (
    look_kept_for_reflect,
    look_rewrite_not_adopted,
    replace_sub_theme_heading,
    subtheme_discarded,
)


class WorkflowGateRewriteConfigTests(unittest.TestCase):
    def test_yaml_enables_rewrite_on_gate_fail(self) -> None:
        cfg = yaml.safe_load(Path("fashion_config.yaml").read_text(encoding="utf-8")) or {}
        ev = cfg.get("text-evaluator") or {}
        self.assertTrue(ev.get("rewrite-on-gate-fail"))
        self.assertEqual(ev.get("score-gate-min"), 0.8)

    def test_gate_pass_and_adopted_rewrite_keep_the_chapter(self) -> None:
        self.assertFalse(
            look_rewrite_not_adopted(
                {"mode": "evaluate_only", "passed": True, "both_gates_passed": True},
                evaluator_enabled=True,
            )
        )
        self.assertFalse(
            look_rewrite_not_adopted(
                {"mode": "k_rewrite", "passed": False, "both_gates_passed": False},
                evaluator_enabled=True,
            )
        )
        self.assertFalse(
            look_rewrite_not_adopted(
                {"mode": "passthrough", "passed": False},
                evaluator_enabled=False,
            )
        )

    def test_gate_pass_and_adopted_rewrites_enter_reflect(self) -> None:
        adopted = {"mode": "k_rewrite", "passed": False, "both_gates_passed": False}
        gate_pass = {"mode": "evaluate_only", "passed": True, "both_gates_passed": True}
        failed = {"mode": "evaluate_only", "passed": False, "both_gates_passed": False}
        self.assertTrue(look_kept_for_reflect(adopted, evaluator_enabled=True))
        self.assertTrue(look_kept_for_reflect(gate_pass, evaluator_enabled=True))
        self.assertFalse(look_kept_for_reflect(failed, evaluator_enabled=True))

    def test_subtheme_discarded_only_when_every_look_fails(self) -> None:
        failed = {"mode": "evaluate_only", "passed": False, "both_gates_passed": False}
        adopted = {"mode": "k_rewrite", "passed": True, "both_gates_passed": True}
        gate_pass = {"mode": "evaluate_only", "passed": True, "both_gates_passed": True}
        self.assertTrue(subtheme_discarded([failed, failed], evaluator_enabled=True))
        self.assertFalse(subtheme_discarded([failed, adopted], evaluator_enabled=True))
        self.assertFalse(subtheme_discarded([failed, gate_pass], evaluator_enabled=True))
        self.assertFalse(subtheme_discarded([], evaluator_enabled=True))

    def test_failed_rewrite_rejects_the_look(self) -> None:
        self.assertTrue(
            look_rewrite_not_adopted(
                {"mode": "evaluate_only", "passed": False, "both_gates_passed": False},
                evaluator_enabled=True,
            )
        )

    def test_replace_sub_theme_heading_by_name_and_index(self) -> None:
        text = (
            "**Theme:**\nOverview\n\n"
            "**Sub-themes for chapter development:**\n"
            "**First Tide:**\nA shore chapter.\n\n"
            "**Second Tide:**\nA night chapter.\n"
        )
        renamed = replace_sub_theme_heading(text, "First Tide", "New Tide")
        self.assertIn("**New Tide:**", renamed)
        self.assertNotIn("**First Tide:**", renamed)
        self.assertIn("**Second Tide:**", renamed)

        by_index = replace_sub_theme_heading(text, "missing", "Third Tide", chapter_index=2)
        self.assertIn("**Third Tide:**", by_index)
        self.assertNotIn("**Second Tide:**", by_index)


if __name__ == "__main__":
    unittest.main()
