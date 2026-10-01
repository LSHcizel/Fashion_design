"""冷启动一次 + 多轮短 GRPO：验收摘要与轮次编号（不加载 7B）。"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from training.accept_report import build_round_accept, summarize_rows, summarize_score_lift
from training.compare_best_rewrite import _groups_missing_original, pending_from_corpus, pending_originals
from training.source_corpus import default_corpus_path
from training.record_builder import build_training_record
from training.run_next_grpo_round import build_collect_cmd, build_grpo_cmd, import_latest_weights
from argparse import Namespace

from training.hf_grpo.run_recommended_training import (
    build_sft_cmd,
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
        self.assertIsNone(blob["score_lift"])

    def test_score_lift_pairs_rewrite_against_original_and_previous(self) -> None:
        rows = [
            {
                "group_id": "g1",
                "candidate_index": -1,
                "S_fp": 0.40,
                "scores_compact": {
                    "quality_base_score": 0.30,
                    "coverage_axis_score": 0.50,
                    "module_scores": {"DesignMerit": 0.20, "InformationDensity": 0.40},
                },
                "gates_compact": {
                    "score_gate_passed": False,
                    "penalty_gate_passed": True,
                    "both_passed": False,
                },
            },
            {
                "group_id": "g1",
                "candidate_index": 0,
                "S_fp": 0.80,
                "scores_compact": {
                    "quality_base_score": 0.70,
                    "coverage_axis_score": 0.90,
                    "module_scores": {"DesignMerit": 0.60, "InformationDensity": 0.80},
                },
                "gates_compact": {
                    "score_gate_passed": True,
                    "penalty_gate_passed": True,
                    "both_passed": True,
                },
            },
            {
                "group_id": "g1",
                "candidate_index": 1,
                "S_fp": 0.60,
                "scores_compact": {
                    "quality_base_score": 0.50,
                    "coverage_axis_score": 0.70,
                    "module_scores": {"DesignMerit": 0.40, "InformationDensity": 0.60},
                },
                "gates_compact": {
                    "score_gate_passed": False,
                    "penalty_gate_passed": True,
                    "both_passed": False,
                },
            },
        ]
        previous = {
            "mean_S_fp": 0.50,
            "mean_quality": 0.40,
            "mean_coverage": 0.60,
            "modules": {
                "DesignMerit": {"mean": 0.30},
                "InformationDensity": {"mean": 0.50},
            },
        }
        lift = summarize_score_lift(rows, previous_rewrites=previous)
        self.assertEqual(lift["rewrites"]["mean_S_fp"], 0.7)
        self.assertEqual(lift["rewrites"]["mean_quality"], 0.6)
        self.assertEqual(lift["lift_vs_original"]["groups"], 1)
        self.assertEqual(lift["lift_vs_original"]["S_fp"], 0.3)
        self.assertEqual(lift["lift_vs_original"]["quality"], 0.3)
        self.assertEqual(lift["lift_vs_original"]["modules"]["DesignMerit"], 0.3)
        self.assertEqual(lift["lift_vs_original"]["modules"]["InformationDensity"], 0.3)
        self.assertEqual(lift["best_rewrite_lift_vs_original"]["S_fp"], 0.4)
        self.assertEqual(lift["best_rewrite_lift_vs_original"]["groups_best_higher"], 1)
        self.assertEqual(lift["best_rewrite_lift_vs_original"]["groups_best_lower"], 0)
        self.assertEqual(lift["lift_vs_previous_round"]["S_fp"], 0.2)
        self.assertEqual(lift["lift_vs_previous_round"]["quality"], 0.2)
        self.assertEqual(lift["lift_vs_previous_round"]["modules"]["LanguageClarity"], None)

    def test_baseline_reference_is_kept_out_of_training(self) -> None:
        rec = build_training_record(
            group_id="g",
            group_round=0,
            candidate_index=-1,
            context={"shared_source_text": "原文"},
            completion_text="原文",
            evaluation={"total_score": 0.5, "scores": {}, "gates": {}},
            r_content_block=None,
            parallel_meta={"injected_original": True, "reference_only": True, "dedupe_kept": True},
        )
        self.assertFalse(rec["training_filter"]["include_in_training"])
        self.assertIn("baseline_reference", rec["training_filter"]["exclude_reasons"])

    def test_missing_original_is_the_source_text(self) -> None:
        rows = [
            {
                "group_id": "g1",
                "candidate_index": 0,
                "S_fp": 0.8,
                "context": {"shared_source_text": "原文甲"},
            },
            {
                "group_id": "g2",
                "candidate_index": -1,
                "S_fp": 0.4,
                "context": {"shared_source_text": "原文乙"},
            },
        ]
        missing = _groups_missing_original(rows)
        self.assertEqual(missing, {"g1": "原文甲"})
        self.assertEqual(pending_originals(rows, {"g1"}), {})
        self.assertEqual(pending_originals(rows, set()), {"g1": "原文甲"})
        corpus = [
            {"source_id": "g1", "text": "原文甲"},
            {"source_id": "g2", "text": "原文乙"},
        ]
        self.assertEqual(pending_from_corpus(corpus, {"g1"}), {"g2": "原文乙"})
        self.assertTrue(default_corpus_path().name == "source_corpus.jsonl")


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

    def test_sft_cmd_defaults_to_lora(self) -> None:
        args = Namespace(
            max_length=2048,
            sft_epochs=1.0,
            sft_lr=2e-5,
            batch=1,
            grad_accum=8,
            dtype="bf16",
            sft_logging_steps=10,
            sft_no_early_stop=True,
            lora_r=16,
            lora_alpha=32,
            full_finetune=False,
        )
        cmd = build_sft_cmd(
            py="python",
            phase_a=Path("a.jsonl"),
            model="m",
            sft_out=Path("out"),
            args=args,
        )
        self.assertIn("--lora-r", cmd)
        self.assertIn("16", cmd)
        self.assertNotIn("--full-finetune", cmd)

    def test_online_round_collects_then_one_grpo_without_sft(self) -> None:
        collect = build_collect_cmd(
            py="python",
            corpus=Path("corpus.jsonl"),
            collect_run_id="grpo_theme/online/round_05",
            system_prompt_file=None,
        )
        self.assertIn("training.collect_k_rewrite_samples", collect)
        self.assertIn("--no-resume", collect)
        self.assertIn("grpo_theme/online/round_05", collect)
        grpo = build_grpo_cmd(
            py="python",
            phase_b=Path("phase_b.jsonl"),
            train_work=Path("hf"),
            grpo_epochs=1.0,
            grpo_lr=1e-6,
            beta_kl=0.001,
            dtype="bf16",
            max_length=2048,
            batch=1,
            grad_accum=8,
            grpo_policy="",
            system_prompt_file=None,
            dry_run=True,
        )
        self.assertIn("--skip-sft", grpo)
        self.assertEqual(grpo[grpo.index("--grpo-rounds") + 1], "1")
        self.assertNotIn("--phase-a", grpo)
        self.assertIn("--dry-run", grpo)

    def test_skip_reimport_when_stamp_matches(self) -> None:
        from training.hf_grpo.manage_rewriter import write_applied_adapter

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            policy = root / "round_01"
            policy.mkdir()
            grpo = root / "hf" / "grpo"
            write_latest(grpo, round_idx=1, policy_dir=policy, ref_dir="ref")
            merged = root / "merged"
            merged.mkdir()
            write_applied_adapter(merged, policy)
            out = import_latest_weights(
                run_id="demo",
                train_work=root / "hf",
                dtype="bf16",
                vllm_gpu="1",
                restart=True,
                dry_run=False,
                skip_if_same=True,
                merged=merged,
            )
            self.assertEqual(out, merged)

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
