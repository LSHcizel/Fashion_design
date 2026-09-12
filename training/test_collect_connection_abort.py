"""连接失败时中止采集、删除异常记录，且训练不导入这些行。"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from plugins.text_description_evaluator.design_text_evaluator_api import (
    JudgeConnectionError,
    is_connection_failure,
)
from training.collect_k_rewrite_samples import (
    _bootstrap_completed,
    _connection_failed_group_ids,
    _purge_groups,
)
from training.grpo_pipeline import default_include_for_training
from training.record_builder import record_include_in_training


CONN_ERR = (
    "Judge API request failed after 4 attempt(s):\n"
    "http://127.0.0.1:8001/v1/chat/completions -> URLError: "
    "<urlopen error [Errno 111] Connection refused>"
)


def _rec(gid: str, *, error=None, include: bool = True) -> dict:
    return {
        "group_id": gid,
        "candidate_index": 0,
        "completion": "" if error else "ok",
        "parallel_sampling": {"rewrite_error": error},
        "training_filter": {
            "include_in_training": include and not error,
            "rewrite_error": error,
            "exclude_reasons": ["rewrite_exception"] if error else [],
        },
    }


class ConnectionFailureDetectTests(unittest.TestCase):
    def test_markers_and_exception_type(self) -> None:
        self.assertTrue(is_connection_failure(CONN_ERR))
        self.assertTrue(is_connection_failure(JudgeConnectionError(CONN_ERR)))
        self.assertFalse(is_connection_failure("JSON parse error"))
        self.assertFalse(is_connection_failure(None))


class PurgeAndBootstrapTests(unittest.TestCase):
    def test_purge_drops_jsonl_and_completed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            jsonl = run / "samples.jsonl"
            completed = run / "completed_groups.txt"
            rows = [_rec("good"), _rec("bad", error=CONN_ERR), _rec("good2")]
            jsonl.write_text(
                "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n",
                encoding="utf-8",
            )
            completed.write_text("good\nbad\ngood2\n", encoding="utf-8")
            dropped = _purge_groups(jsonl, completed, {"bad"})
            self.assertEqual(dropped, 1)
            kept = [json.loads(ln)["group_id"] for ln in jsonl.read_text(encoding="utf-8").splitlines() if ln]
            self.assertEqual(kept, ["good", "good2"])
            self.assertEqual(completed.read_text(encoding="utf-8").splitlines(), ["good", "good2"])

    def test_bootstrap_purges_connection_failed_groups(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            jsonl = run / "samples.jsonl"
            completed = run / "completed_groups.txt"
            rows = [_rec("pos_058"), _rec("pos_059", error=CONN_ERR)]
            jsonl.write_text(
                "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n",
                encoding="utf-8",
            )
            completed.write_text("pos_058\npos_059\n", encoding="utf-8")
            done = _bootstrap_completed(jsonl, completed)
            self.assertEqual(done, {"pos_058"})
            self.assertEqual(_connection_failed_group_ids(jsonl), set())
            gids = [json.loads(ln)["group_id"] for ln in jsonl.read_text(encoding="utf-8").splitlines() if ln]
            self.assertEqual(gids, ["pos_058"])


class TrainingImportFilterTests(unittest.TestCase):
    def test_connection_failed_records_are_not_imported(self) -> None:
        bad = _rec("pos_059", error=CONN_ERR)
        good = _rec("pos_001")
        self.assertFalse(record_include_in_training(bad))
        self.assertFalse(default_include_for_training(bad))
        self.assertTrue(record_include_in_training(good))
        self.assertTrue(default_include_for_training(good))


class OneRewriteAbortTests(unittest.TestCase):
    def test_one_rewrite_reraises_connection_failure(self) -> None:
        from plugins.parallel_k_rewrite.k_candidate_generator import _one_rewrite

        class _Judge:
            max_tokens = 16

            def generate_text(self, **_kwargs):
                raise JudgeConnectionError(CONN_ERR)

        class _Ev:
            optimizer_system_prompt = "sys"
            judge = _Judge()

            def _validate_optimized_text(self, raw, _src):
                return raw

            def _normalize_optimized_text(self, text):
                return text

        with self.assertRaises(JudgeConnectionError):
            _one_rewrite(_Ev(), "src", k=2, candidate_index=0, extra_context="", temperature_floor=0.1, temperature_step=0.05, temperature_cap=0.5)

    def test_generate_k_aborts_on_connection_failure(self) -> None:
        from plugins.parallel_k_rewrite.k_candidate_generator import generate_k_parallel_rewrites

        def _boom(*_a, **_k):
            raise JudgeConnectionError(CONN_ERR)

        with patch(
            "plugins.parallel_k_rewrite.k_candidate_generator._one_rewrite",
            side_effect=_boom,
        ):
            with self.assertRaises(JudgeConnectionError):
                generate_k_parallel_rewrites("src", k=2, evaluator=object(), evaluate_candidates=False)


if __name__ == "__main__":
    unittest.main()
