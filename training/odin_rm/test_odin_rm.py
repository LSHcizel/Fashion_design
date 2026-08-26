"""ODIN 档 3：偏好对与损失的离线单测（不加载 7B）。"""

from __future__ import annotations

import math
import unittest

from training.grpo_compute import pick_reward_scalar
from training.odin_rm.data import apply_r_q_to_record, teacher_score
from training.odin_rm.pairs import assign_splits, pairs_from_group


def _rec(gid: str, idx: int, score: float, text: str, r_content: float | None = None) -> dict:
    return {
        "group_id": gid,
        "candidate_index": idx,
        "completion": text,
        "char_len": len(text),
        "S_fp": score,
        "R_content": r_content if r_content is not None else score,
        "scores_compact": {"S_fp": score, "R_content": r_content if r_content is not None else score},
        "r_content": {
            "enabled": True,
            "S_fp": score,
            "R_content": r_content if r_content is not None else score,
            "log_len": math.log1p(len(text)),
        },
        "training_filter": {"include_in_training": True},
        "context": {"shared_source_text": "src", "business_context": ""},
    }


class PairBuildingTests(unittest.TestCase):
    def test_higher_teacher_wins_and_ties_drop(self) -> None:
        recs = [
            _rec("g", 0, 0.9, "long " * 20, r_content=0.4),
            _rec("g", 1, 0.5, "short", r_content=0.7),
            _rec("g", 2, 0.9, "also long", r_content=0.9),
        ]
        pairs = pairs_from_group(recs)
        self.assertEqual(len(pairs), 2)
        for p in pairs:
            self.assertGreater(
                p["chosen"]["teacher_score"], p["rejected"]["teacher_score"]
            )
            self.assertEqual(p["chosen"]["teacher_score"], 0.9)

    def test_teacher_score_ignores_z_len_r_content(self) -> None:
        rec = _rec("g", 0, 0.82, "hello", r_content=0.11)
        self.assertEqual(teacher_score(rec), 0.82)

    def test_split_keeps_group_together(self) -> None:
        pairs = []
        for gid in ("a", "b", "c", "d"):
            pairs.extend(
                pairs_from_group(
                    [_rec(gid, 0, 0.8, "aa"), _rec(gid, 1, 0.2, "bb")]
                )
            )
        assign_splits(pairs, holdout_frac=0.25)
        by_g = {}
        for p in pairs:
            by_g.setdefault(p["group_id"], set()).add(p["split"])
        for splits in by_g.values():
            self.assertEqual(len(splits), 1)


class RewardWritebackTests(unittest.TestCase):
    def test_r_q_becomes_grpo_scalar(self) -> None:
        rec = _rec("g", 0, 0.7, "text")
        apply_r_q_to_record(rec, r_q=-1.25, r_l=3.0, backbone="x")
        self.assertEqual(rec["R_content"], -1.25)
        self.assertEqual(pick_reward_scalar(rec), -1.25)
        self.assertEqual(rec["S_fp"], 0.7)
        self.assertEqual(rec["r_content"]["odin_stage"], 3)
        self.assertIsNone(rec["r_content"]["z_len"])


class OdinLossTests(unittest.TestCase):
    def test_rank_and_pearson_shapes(self) -> None:
        try:
            import torch
        except ImportError:
            self.skipTest("torch not installed")
        from training.odin_rm.modeling import DualHeadRewardModel, last_token_hidden, odin_rm_loss

        hidden = torch.zeros(2, 4, 8)
        hidden[0, 1] = 1.0
        hidden[1, 2] = 2.0
        mask = torch.tensor([[1, 1, 0, 0], [1, 1, 1, 0]])
        pooled = last_token_hidden(hidden, mask)
        self.assertEqual(tuple(pooled.shape), (2, 8))
        self.assertEqual(float(pooled[0].sum()), 8.0)
        self.assertEqual(float(pooled[1].sum()), 16.0)

        class Tiny(torch.nn.Module):
            def __init__(self) -> None:
                super().__init__()
                self.config = type("c", (), {"hidden_size": 8})()

            def forward(self, **kwargs):
                raise AssertionError("should use scores_from_hidden")

        rm = DualHeadRewardModel(Tiny(), hidden_size=8)
        h_w = torch.randn(3, 8)
        h_l = torch.randn(3, 8)
        rqw, rlw = rm.scores_from_hidden(h_w)
        rql, rll = rm.scores_from_hidden(h_l)
        llw = torch.tensor([1.0, 2.0, 3.0])
        lll = torch.tensor([1.1, 2.2, 3.3])
        loss, stats = odin_rm_loss(
            rqw, rlw, rql, rll, llw, lll,
            head_q=rm.head_q, head_l=rm.head_l,
        )
        self.assertTrue(torch.isfinite(loss))
        self.assertIn("acc_sum", stats)
        loss.backward()
        self.assertIsNotNone(next(rm.head_q.parameters()).grad)


if __name__ == "__main__":
    unittest.main()
