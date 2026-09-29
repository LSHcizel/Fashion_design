"""优化指标 JSONL：窗口均值、首尾差、Trainer 回调落盘。"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from training.hf_grpo.metrics_callback import JsonlMetricsCallback
from training.step_metrics import WindowMeanMetrics, append_metrics, progress_summary


class StepMetricsTests(unittest.TestCase):
    def test_window_mean_then_flush_resets(self) -> None:
        window = WindowMeanMetrics()
        window.add(policy_term=-1.0, kl_term=0.2)
        window.add(policy_term=-3.0, kl_term=0.4)
        got = window.flush()
        self.assertAlmostEqual(got["policy_term"], -2.0)
        self.assertAlmostEqual(got["kl_term"], 0.3)
        self.assertEqual(window.flush(), {})

    def test_progress_summary_records_delta(self) -> None:
        summary = progress_summary(
            stage="sft",
            global_step=20,
            first={"loss": 2.0, "loss_ema": 2.0},
            last={"loss": 1.5, "loss_ema": 1.6},
            keys=("loss", "loss_ema"),
        )
        self.assertEqual(summary["event"], "summary")
        self.assertAlmostEqual(summary["delta_loss"], -0.5)
        self.assertAlmostEqual(summary["delta_loss_ema"], -0.4)

    def test_callback_writes_step_and_summary(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "metrics.jsonl"
            cb = JsonlMetricsCallback(path, stage="grpo", summary_keys=("loss", "policy_term"))
            state = SimpleNamespace(global_step=10)
            cb.on_log(None, state, SimpleNamespace(), logs={"loss": 1.0, "policy_term": -0.2, "note": "skip"})
            state.global_step = 20
            cb.on_log(None, state, SimpleNamespace(), logs={"loss": 0.5, "policy_term": -0.8})
            cb.on_train_end(None, state, SimpleNamespace())
            rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
        self.assertEqual([r["event"] for r in rows], ["step", "step", "summary"])
        self.assertNotIn("note", rows[0])
        self.assertAlmostEqual(rows[-1]["delta_loss"], -0.5)
        self.assertAlmostEqual(rows[-1]["delta_policy_term"], -0.6)
        append_metrics(path, {"stage": "rm", "event": "step", "global_step": 1, "train_loss": 0.4})
        extra = json.loads(path.read_text(encoding="utf-8").splitlines()[-1])
        self.assertEqual(extra["stage"], "rm")
        self.assertIn("utc", extra)


if __name__ == "__main__":
    unittest.main()
