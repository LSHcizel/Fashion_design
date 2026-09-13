"""LoRA / 24G 加载约定（不加载 7B）。"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from training.hf_grpo.model_load import (
    is_peft_adapter_dir,
    lora_cli_args,
    same_model_path,
    should_use_lora,
)


class ModelLoadHelpersTest(unittest.TestCase):
    def test_adapter_dir_needs_config(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.assertFalse(is_peft_adapter_dir(root))
            (root / "adapter_config.json").write_text("{}", encoding="utf-8")
            self.assertTrue(is_peft_adapter_dir(root))

    def test_lora_on_by_default(self) -> None:
        self.assertTrue(should_use_lora(full_finetune=False, lora_r=16))
        self.assertFalse(should_use_lora(full_finetune=True, lora_r=16))
        self.assertFalse(should_use_lora(full_finetune=False, lora_r=0))

    def test_lora_cli_default_and_full(self) -> None:
        self.assertEqual(
            lora_cli_args(lora_r=16, lora_alpha=32, full_finetune=False),
            ["--lora-r", "16", "--lora-alpha", "32"],
        )
        self.assertEqual(
            lora_cli_args(lora_r=16, lora_alpha=32, full_finetune=True),
            ["--full-finetune"],
        )

    def test_same_model_path_relative(self) -> None:
        self.assertTrue(same_model_path("models/Qwen2.5-7B-Rewriter", "models/Qwen2.5-7B-Rewriter"))
        with tempfile.TemporaryDirectory() as td:
            a = Path(td) / "m"
            a.mkdir()
            self.assertTrue(same_model_path(a, Path(td) / "m"))


if __name__ == "__main__":
    unittest.main()
