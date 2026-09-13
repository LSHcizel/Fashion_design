"""工作流门限失败改写：yaml 开关（不导入 fashion_workflow，避免本地缺 anthropic）。"""

from __future__ import annotations

import unittest
from pathlib import Path

import yaml


class WorkflowGateRewriteConfigTests(unittest.TestCase):
    def test_yaml_enables_rewrite_on_gate_fail(self) -> None:
        cfg = yaml.safe_load(Path("fashion_config.yaml").read_text(encoding="utf-8")) or {}
        ev = cfg.get("text-evaluator") or {}
        self.assertTrue(ev.get("rewrite-on-gate-fail"))
        self.assertEqual(ev.get("score-gate-min"), 0.8)


if __name__ == "__main__":
    unittest.main()
