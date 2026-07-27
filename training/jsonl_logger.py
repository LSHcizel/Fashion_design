"""将训练样本按行写入 JSONL，并维护运行目录下的轻量清单。"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .record_builder import SCHEMA_VERSION, iter_records_from_parallel_result


def default_runs_root() -> Path:
    """``grpo.training-data.runs-dir``（相对仓库根），默认 ``training/runs``。"""
    try:
        from plugins.text_description_evaluator.design_text_evaluator_api import (
            grpo_training_data_config,
        )
    except Exception:
        grpo_training_data_config = lambda: {}  # type: ignore[assignment, misc]
    td = grpo_training_data_config()
    rel = td.get("runs-dir") or "training/runs"
    if not isinstance(rel, str) or not rel.strip():
        rel = "training/runs"
    project = Path(__file__).resolve().parents[1]
    return (project / rel.strip()).resolve()


class TrainingRunLogger:
    """
    默认基础目录见 ``default_runs_root()``（``fashion_config.yaml`` 的 ``grpo.training-data.runs-dir``）。

    - 使用 ``.jsonl`` 扩展名，避免仓库根 ``.gitignore`` 对 ``*.json`` 的忽略。
    - 线程安全：若多线程写入请外层加锁或每线程独立文件。
    """

    def __init__(
        self,
        run_id: str,
        *,
        base_dir: Optional[Path] = None,
        filename: str = "samples.jsonl",
    ) -> None:
        self.run_id = run_id
        base = base_dir if base_dir is not None else default_runs_root()
        self.run_dir = base / run_id
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.jsonl_path = self.run_dir / filename
        self._manifest_path = self.run_dir / "run_manifest.txt"
        self._append_count = 0
        if not self._manifest_path.exists():
            self._manifest_path.write_text(
                f"run_id={run_id}\nschema_version={SCHEMA_VERSION}\n"
                f"created_utc={datetime.now(timezone.utc).isoformat()}\n",
                encoding="utf-8",
            )

    def append_record(self, record: Dict[str, Any]) -> None:
        line = json.dumps(record, ensure_ascii=False, default=str) + "\n"
        with self.jsonl_path.open("a", encoding="utf-8") as f:
            f.write(line)
        self._append_count += 1

    def append_parallel_result(
        self,
        parallel_result: Dict[str, Any],
        *,
        context: Dict[str, Any],
        group_round: int = 0,
        system_prompt_sha256: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """展开并行 K 结果并逐行追加，返回已写入的 dict 列表。"""
        written: List[Dict[str, Any]] = []
        for rec in iter_records_from_parallel_result(
            parallel_result,
            context=context,
            run_id=self.run_id,
            group_round=group_round,
            system_prompt_sha256=system_prompt_sha256,
        ):
            self.append_record(rec)
            written.append(rec)
        return written

    def path(self) -> Path:
        return self.jsonl_path

