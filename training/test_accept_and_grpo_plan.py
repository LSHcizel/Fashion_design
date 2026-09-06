"""冷启动一次 + 多轮短 GRPO：验收摘要与轮次编号（不加载 7B）。"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from training.accept_report import build_round_accept, summarize_rows
from training.hf_grpo.run_recommended_training import (
    grpo_round_dir,
    load_latest,
    resolve_grpo_start,
    write_latest,
)


class AcceptReportTests(unittest.TestCase):
    def test_summarize_gates_and_rewards(self) -> None:
        rows = [
            {
                "group_id": "g1",
                "R_content": 1.2,
                "S_fp": 0.8,
                "char_len": 100,
                "advantage": 0.5,
                "penalties": {"total_penalty": 0.1},
                "gates_compact": {
                    "both_passed": True,
                    "score_gate_passed": True,
                    "penalty_gate_passed": True,
                },
                "training_filter": {"include_in_training": True},
            },
            {
                "group_id": "g1",
                "R_content": 0.2,
                "S_fp": 0.4,
                "char_len": 200,
                "advantage": -0.5,
                "penalties": {"total_penalty": 0.3},
                "gates_compact": {
                    "both_passed": False,
                    "score_gate_passed": False,
                    "penalty_gate_passed": True,
                },
            },
        ]
        s = summarize_rows(rows)
        self.assertEqual(s["rows"], 2)
        self.assertEqual(s["groups"], 1)
        self.assertEqual(s["mean_R_content"], 0.7)
        self.assertEqual(s["mean_S_fp"], 0.6)
        self.assertEqual(s["mean_char_len"], 150.0)
        self.assertEqual(s["score_gate_pass_rate"], 0.5)
        self.assertEqual(s["penalty_gate_pass_rate"], 1.0)
        self.assertEqual(s["both_gates_pass_rate"], 0.5)
        self.assertEqual(s["advantage_positive_rate"], 0.5)

    def test_round_accept_marks_cold_start_contract(self) -> None:
        blob = build_round_accept(
            round_idx=2,
            policy_dir=Path("."),
            ref_dir="models/Qwen2.5-7B-Rewriter",
            epochs=0.25,
            data_summary={"rows": 1},
        )
        self.assertEqual(blob["cold_start"]["sft"], "once")
        self.assertEqual(blob["cold_start"]["dual_head_rm"], "once")
        self.assertEqual(blob["cold_start"]["grpo"], "short_rounds")
        self.assertEqual(blob["epochs_this_round"], 0.25)


class GrpoRoundPlanTests(unittest.TestCase):
    def test_cold_start_begins_at_sft_round_one(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            work = Path(td)
            sft = work / "sft"
            sft.mkdir()
            policy, start = resolve_grpo_start(
                skip_sft=False,
                sft_out=sft,
                grpo_root=work / "grpo",
                grpo_policy="",
                round_start=0,
            )
            self.assertEqual(policy, sft)
            self.assertEqual(start, 1)
            self.assertEqual(grpo_round_dir(work / "grpo", 1).name, "round_01")

    def test_continue_uses_latest_and_increments_round(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            work = Path(td)
            sft = work / "sft"
            sft.mkdir()
            grpo = work / "grpo"
            r4 = grpo / "round_04"
            r4.mkdir(parents=True)
            write_latest(grpo, round_idx=4, policy_dir=r4, ref_dir="ref")
            latest = load_latest(grpo)
            self.assertEqual(latest["round"], 4)
            policy, start = resolve_grpo_start(
                skip_sft=True,
                sft_out=sft,
                grpo_root=grpo,
                grpo_policy="",
                round_start=0,
            )
            self.assertEqual(policy.resolve(), r4.resolve())
            self.assertEqual(start, 5)

    def test_skip_sft_without_checkpoint_fails(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            work = Path(td)
            with self.assertRaises(SystemExit):
                resolve_grpo_start(
                    skip_sft=True,
                    sft_out=work / "sft",
                    grpo_root=work / "grpo",
                    grpo_policy="",
                    round_start=0,
                )


if __name__ == "__main__":
    unittest.main()
