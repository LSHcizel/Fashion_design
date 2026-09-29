"""把各训练阶段真正用于更新参数的指标追加到 metrics.jsonl。"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping, Optional


def append_metrics(path: Path, record: Mapping[str, Any]) -> None:
    """追加一行 JSON。``path`` 的父目录不存在时会创建。"""
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    row = {"utc": datetime.now(timezone.utc).isoformat(), **dict(record)}
    with out.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def numeric_logs(logs: Optional[Mapping[str, Any]]) -> Dict[str, float]:
    """只保留可比较的数值，丢掉 Trainer 日志里的字符串。"""
    if not logs:
        return {}
    kept: Dict[str, float] = {}
    for key, value in logs.items():
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)):
            kept[str(key)] = float(value)
    return kept


class WindowMeanMetrics:
    """一个 logging 窗口内，对 compute_loss 返回的标量取均值。"""

    def __init__(self) -> None:
        self._sums: Dict[str, float] = {}
        self._n = 0

    def add(self, **values: float) -> None:
        for key, value in values.items():
            self._sums[key] = self._sums.get(key, 0.0) + float(value)
        self._n += 1

    def flush(self) -> Dict[str, float]:
        if self._n <= 0:
            return {}
        out = {key: total / self._n for key, total in self._sums.items()}
        self._sums.clear()
        self._n = 0
        return out


def progress_summary(
    *,
    stage: str,
    global_step: int,
    first: Mapping[str, float],
    last: Mapping[str, float],
    keys: tuple[str, ...],
) -> Dict[str, Any]:
    """首尾差值。loss 类指标变小、acc 类指标变大，表示这一步参数更新有收益。"""
    summary: Dict[str, Any] = {
        "stage": stage,
        "event": "summary",
        "global_step": int(global_step),
    }
    for key in keys:
        if key not in first or key not in last:
            continue
        a = float(first[key])
        b = float(last[key])
        summary[f"first_{key}"] = a
        summary[f"last_{key}"] = b
        summary[f"delta_{key}"] = b - a
    return summary
