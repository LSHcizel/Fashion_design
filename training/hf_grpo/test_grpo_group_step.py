"""组过滤、按组取样，以及策略项不再按单句长度归一。不加载 7B。"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import torch

from training.hf_grpo.data import select_grpo_rows
from training.hf_grpo.modeling import grpo_loss, token_kl_k3_sum
from training.hf_grpo.train_grpo import (
    GroupBatchSampler,
    drop_kl_ref_keys,
    forward_frozen_kl_ref,
    kl_ref_kind_from_flags,
)


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


class _Out:
    def __init__(self, logits: torch.Tensor) -> None:
        self.logits = logits


class _Switchable(torch.nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.active_adapter = "default"
        self.scale = {"default": 2.0, "kl_ref": 5.0}

    def set_adapter(self, name: str) -> None:
        self.active_adapter = name

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> _Out:
        del attention_mask
        return _Out(input_ids * self.scale[self.active_adapter])


class FrozenKlRefTests(unittest.TestCase):
    def test_sft_adapter_is_frozen_ref_not_the_base(self) -> None:
        self.assertEqual(
            kl_ref_kind_from_flags(ref_is_adapter=True, policy_is_adapter=True, same_base=True),
            "frozen_adapter",
        )
        with self.assertRaises(SystemExit):
            kl_ref_kind_from_flags(ref_is_adapter=True, policy_is_adapter=True, same_base=False)

    def test_base_path_still_disables_adapter(self) -> None:
        self.assertEqual(
            kl_ref_kind_from_flags(ref_is_adapter=False, policy_is_adapter=True, same_base=True),
            "disable_base",
        )

    def test_forward_uses_kl_ref_then_restores_trainable_adapter(self) -> None:
        model = _Switchable()
        model.train()
        logits = forward_frozen_kl_ref(model, torch.ones(1, 2), torch.ones(1, 2))
        self.assertTrue(torch.equal(logits, torch.full((1, 2), 5.0)))
        self.assertEqual(model.active_adapter, "default")
        self.assertTrue(model.training)

    def test_checkpoint_state_drops_frozen_adapter(self) -> None:
        kept = drop_kl_ref_keys(
            {
                "layers.0.lora_A.default.weight": torch.tensor(1.0),
                "layers.0.lora_A.kl_ref.weight": torch.tensor(2.0),
            }
        )
        self.assertIsNotNone(kept)
        assert kept is not None
        self.assertEqual(list(kept), ["layers.0.lora_A.default.weight"])

    def test_loaded_sft_adapter_stays_put_when_policy_moves(self) -> None:
        from peft import LoraConfig, get_peft_model

        from training.hf_grpo.model_load import attach_frozen_kl_ref

        class Tiny(torch.nn.Module):
            def __init__(self) -> None:
                super().__init__()
                self.q_proj = torch.nn.Linear(4, 4, bias=False)

            def forward(self, x: torch.Tensor) -> torch.Tensor:
                return self.q_proj(x)

        torch.manual_seed(0)
        policy = get_peft_model(
            Tiny(),
            LoraConfig(r=2, lora_alpha=4, target_modules=["q_proj"], bias="none"),
        )
        with tempfile.TemporaryDirectory() as td:
            sft = Path(td) / "sft"
            policy.save_pretrained(sft)
            for _name, param in policy.named_parameters():
                if param.requires_grad:
                    param.data.add_(1.0)
            attach_frozen_kl_ref(policy, sft)
            x = torch.ones(1, 4)
            policy.set_adapter("default")
            moved = policy(x).detach()
            policy.set_adapter("kl_ref")
            frozen = policy(x).detach()
            policy.set_adapter("default")
            self.assertFalse(torch.allclose(moved, frozen))
            for name, param in policy.named_parameters():
                if ".kl_ref." in name:
                    self.assertFalse(param.requires_grad)
            out = Path(td) / "round"
            policy.save_pretrained(out, selected_adapters=["default"])
            self.assertTrue((out / "adapter_config.json").is_file())
            self.assertFalse((out / "kl_ref").exists())


if __name__ == "__main__":
    unittest.main()
