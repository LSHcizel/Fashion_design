"""把 Trainer.on_log 里的优化指标写入 metrics.jsonl，并在结束时写首尾差。"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from transformers import TrainerCallback

from training.step_metrics import append_metrics, numeric_logs, progress_summary


class JsonlMetricsCallback(TrainerCallback):
    def __init__(self, path: Path, *, stage: str, summary_keys: tuple[str, ...]) -> None:
        self.path = Path(path)
        self.stage = stage
        self.summary_keys = summary_keys
        self._first: Optional[Dict[str, float]] = None
        self._last: Optional[Dict[str, float]] = None

    def on_log(self, args, state, control, logs=None, **kwargs):  # type: ignore[no-untyped-def]
        numbers = numeric_logs(logs)
        if not numbers:
            return control
        step = int(getattr(state, "global_step", 0) or 0)
        append_metrics(
            self.path,
            {"stage": self.stage, "event": "step", "global_step": step, **numbers},
        )
        if self._first is None:
            self._first = dict(numbers)
        self._last = dict(numbers)
        return control

    def on_train_end(self, args, state, control, **kwargs):  # type: ignore[no-untyped-def]
        if not self._first or not self._last:
            return control
        step = int(getattr(state, "global_step", 0) or 0)
        summary = progress_summary(
            stage=self.stage,
            global_step=step,
            first=self._first,
            last=self._last,
            keys=self.summary_keys,
        )
        if len(summary) > 3:
            append_metrics(self.path, summary)
        return control
