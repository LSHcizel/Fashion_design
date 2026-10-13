"""组过滤、按组取样，以及策略项不再按单句长度归一。不加载 7B。"""

from __future__ import annotations

import unittest

import torch

from training.hf_grpo.data import select_grpo_rows
from training.hf_grpo.modeling import grpo_loss, token_kl_k3_sum
from training.hf_grpo.train_grpo import GroupBatchSampler


class SelectGrpoRowsTests(unittest.TestCase):
    def test_drops_group_whose_reward_barely_moves(self) -> None:
        rows = [
            {"group_id": "flat", "advantage": 1.0, "group_stats": {"std_r_for_advantage": 0.001}},
            {"group_id": "flat", "advantage": -1.0, "group_stats": {"std_r_for_advantage": 0.001}},
            {"group_id": "gap", "advantage": 0.7, "R_content": 1.0},
            {"group_id": "gap", "advantage": -0.7, "R_content": -1.0},
        ]
        kept, summary = select_grpo_rows(rows, min_reward_std=0.05)
        self.assertEqual([row["group_id"] for row in kept], ["gap", "gap"])
        self.assertEqual(summary["groups_dropped_small_gap"], 1)
        self.assertEqual(summary["groups_kept"], 1)
        self.assertEqual(summary["rows_kept"], 2)

    def test_drops_singleton_and_zero_advantage(self) -> None:
        rows = [
            {"group_id": "one", "advantage": 0.0, "R_content": 1.0},
            {"group_id": "zero", "advantage": 0.0, "R_content": 3.0},
            {"group_id": "zero", "advantage": 0.0, "R_content": 1.0},
        ]
        kept, summary = select_grpo_rows(rows, min_reward_std=0.05)
        self.assertEqual(kept, [])
        self.assertEqual(summary["groups_dropped_too_small"], 1)
        self.assertEqual(summary["groups_dropped_flat_advantage"], 1)

    def test_low_meaningful_completion_does_not_stay_in_the_group(self) -> None:
        english = "a navy wool coat with a belted waist and black boots"
        rows = [
            {"group_id": "g", "advantage": 1.0, "R_content": 1.0, "completion": english},
            {"group_id": "g", "advantage": 0.0, "R_content": 0.2, "completion": english + " lined"},
            {
                "group_id": "g",
                "advantage": -1.0,
                "R_content": 0.0,
                "completion": "@@@@####$$$$%%%%&&&&",
            },
        ]
        kept, summary = select_grpo_rows(rows, min_reward_std=0.05)
        self.assertEqual(len(kept), 2)
        self.assertEqual(summary["rows_dropped_low_meaningful"], 1)
        self.assertEqual(summary["groups_kept"], 1)
        self.assertTrue(all("@" not in str(row["completion"]) for row in kept))

    def test_symbol_only_group_is_dropped(self) -> None:
        rows = [
            {"group_id": "g", "advantage": 1.0, "R_content": 1.0, "completion": "@@@@####$$$$%%%%&&&&"},
            {"group_id": "g", "advantage": -1.0, "R_content": 0.0, "completion": "~~~~^^^^****====!!!!"},
        ]
        kept, summary = select_grpo_rows(rows, min_reward_std=0.05)
        self.assertEqual(kept, [])
        self.assertEqual(summary["groups_dropped_low_meaningful"], 1)


class GroupBatchSamplerTests(unittest.TestCase):
    def test_each_batch_is_one_source(self) -> None:
        sampler = GroupBatchSampler(["b", "a", "b", "a"], seed=0)
        batches = list(sampler)
        self.assertEqual(len(batches), 2)
        self.assertCountEqual(batches, [[1, 3], [0, 2]])
        self.assertEqual(sorted(i for batch in batches for i in batch), [0, 1, 2, 3])


class GrpoLossScaleTests(unittest.TestCase):
    def test_policy_term_uses_token_sum_not_per_sequence_mean(self) -> None:
        # 短句 2 token、长句 6 token，优势相同。按句平均会让长句每个 token 的梯度更小。
        advantage = torch.tensor([1.0, 1.0])
        sum_logp = torch.tensor([-2.0, -6.0])
        token_count = torch.tensor([2.0, 6.0])
        mean_logp = sum_logp / token_count
        ref = torch.zeros(2)
        loss, pol, kl = grpo_loss(
            mean_logp,
            ref,
            advantage,
            beta_kl=0.0,
            sum_logp_policy=sum_logp,
            token_count=token_count,
        )
        # -sum(A * sum_logp) / sum(T) = -(-2 + -6) / 8 = 1
        self.assertAlmostEqual(float(pol), 1.0, places=5)
        self.assertAlmostEqual(float(loss), 1.0, places=5)
        per_sequence_mean = float((-(advantage * mean_logp).mean()))
        self.assertAlmostEqual(per_sequence_mean, 1.0, places=5)
        # 长句贡献 6/8 的策略项，而不是和短句各占一半。
        long_share = float((advantage[1] * sum_logp[1]).abs() / token_count.sum())
        short_share = float((advantage[0] * sum_logp[0]).abs() / token_count.sum())
        self.assertGreater(long_share, short_share)
        self.assertAlmostEqual(float(kl), 0.0, places=5)

    def test_token_kl_matches_schulman_k3(self) -> None:
        import math

        logp_policy = torch.tensor([-1.0, -1.0])
        logp_ref = torch.tensor([-1.1, -1.1])
        mask = torch.tensor([True, True])
        total = token_kl_k3_sum(logp_policy, logp_ref, mask)
        one = math.exp(-0.1) + 0.1 - 1.0
        self.assertAlmostEqual(float(total), 2.0 * one, places=5)
        _loss, _pol, kl = grpo_loss(
            torch.tensor([-2.0]),
            torch.tensor([-2.2]),
            torch.tensor([1.0]),
            beta_kl=10.0,
            sum_logp_policy=torch.tensor([-2.0]),
            token_count=torch.tensor([2.0]),
            token_kl_sum=total,
        )
        self.assertAlmostEqual(float(kl), one, places=5)


if __name__ == "__main__":
    unittest.main()
