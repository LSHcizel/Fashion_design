"""改写器配置切换：只动 rewriter-llm，不动 KL 锚点。"""

from __future__ import annotations

import unittest

from pathlib import Path

from training.hf_grpo.manage_rewriter import CONFIG_PATH, patch_rewriter_llm_fields

SAMPLE = """grpo:
  rewriter-llm:
    enabled: true
    model: "Qwen2.5-7B-Rewriter"
    model-path: "models/Qwen2.5-7B-Rewriter"
    timeout: 300
  hf-local-training:
    model: "models/Qwen2.5-7B-Rewriter"
    ref-model: "models/Qwen2.5-7B-Rewriter"
"""


class ManageRewriterTest(unittest.TestCase):
    def test_patch_only_rewriter_llm(self) -> None:
        out = patch_rewriter_llm_fields(
            SAMPLE,
            model="Qwen2.5-7B-Rewriter-grpo-v2",
            model_path="models/Qwen2.5-7B-Rewriter-grpo-v2",
        )
        self.assertIn('model: "Qwen2.5-7B-Rewriter-grpo-v2"', out)
        self.assertIn('model-path: "models/Qwen2.5-7B-Rewriter-grpo-v2"', out)
        self.assertIn(
            '  hf-local-training:\n    model: "models/Qwen2.5-7B-Rewriter"\n'
            '    ref-model: "models/Qwen2.5-7B-Rewriter"',
            out,
        )

    def test_real_config_roundtrip(self) -> None:
        text = Path(CONFIG_PATH).read_text(encoding="utf-8")
        mid = patch_rewriter_llm_fields(
            text,
            model="Qwen2.5-7B-Rewriter-grpo-v2",
            model_path="models/Qwen2.5-7B-Rewriter-grpo-v2",
        )
        self.assertIn('model-path: "models/Qwen2.5-7B-Rewriter-grpo-v2"', mid)
        self.assertIn('ref-model: "models/Qwen2.5-7B-Rewriter"', mid)
        back = patch_rewriter_llm_fields(
            mid,
            model="Qwen2.5-7B-Rewriter",
            model_path="models/Qwen2.5-7B-Rewriter",
        )
        self.assertEqual(back, text)

    def test_restore_roundtrip(self) -> None:
        mid = patch_rewriter_llm_fields(
            SAMPLE,
            model="tmp",
            model_path="models/tmp",
        )
        back = patch_rewriter_llm_fields(
            mid,
            model="Qwen2.5-7B-Rewriter",
            model_path="models/Qwen2.5-7B-Rewriter",
        )
        self.assertEqual(back, SAMPLE)


if __name__ == "__main__":
    unittest.main()
