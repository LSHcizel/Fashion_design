"""一致性负例语料：18 条已出图描述，供远程 K 路采集读取。"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from training.build_grpo_source_corpus import (
    DEFAULT_CONSISTENCY_DIR,
    build_consistency_corpus,
    iter_consistency_defect_sources,
)


class ConsistencyCorpusTests(unittest.TestCase):
    def test_eighteen_negative_sources_match_txt(self) -> None:
        rows = list(iter_consistency_defect_sources(DEFAULT_CONSISTENCY_DIR))
        self.assertEqual(len(rows), 18)
        ids = [r["source_id"] for r in rows]
        self.assertEqual(len(set(ids)), 18)
        for row in rows:
            self.assertEqual(row["role"], "negative")
            self.assertIn("different theme or concept", row["business_context"])
            self.assertIn("Write the rewrite in English", row["business_context"])
            self.assertNotIn("Stated theme:", row["business_context"])
            src = Path(row["path"])
            text = (DEFAULT_CONSISTENCY_DIR.parents[1] / src).read_text(encoding="utf-8").strip()
            self.assertEqual(row["text"], text)

    def test_writer_emits_jsonl(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "source_corpus.jsonl"
            stats = build_consistency_corpus(DEFAULT_CONSISTENCY_DIR, out)
            self.assertEqual(stats["n_total"], 18)
            lines = [ln for ln in out.read_text(encoding="utf-8").splitlines() if ln.strip()]
            self.assertEqual(len(lines), 18)
            self.assertEqual(json.loads(lines[0])["source_id"], "consistency_01_asymmetry")


if __name__ == "__main__":
    unittest.main()
