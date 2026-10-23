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
            _rec("g", 0, 0.9, "also-long", r_content=0.4),
            _rec("g", 1, 0.5, "short", r_content=0.7),
            _rec("g", 2, 0.9, "also long", r_content=0.9),
        ]
        pairs = pairs_from_group(recs)
        self.assertEqual(len(pairs), 2)
        for p in pairs:
            self.assertGreater(p["teacher_margin"], 0.1)
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

    def test_pairs_stay_inside_one_group(self) -> None:
        recs = [
            _rec("a", 0, 0.9, "a high"),
            _rec("a", 1, 0.2, "a low"),
            _rec("b", 0, 0.1, "b low"),
            _rec("b", 1, 0.8, "b high"),
        ]
        pairs = pairs_from_group(recs)
        self.assertEqual(len(pairs), 2)
        seen = set()
        for p in pairs:
            self.assertEqual(p["group_id"], p["chosen"]["group_id"])
            self.assertEqual(p["group_id"], p["rejected"]["group_id"])
            seen.add(p["group_id"])
            self.assertGreater(p["chosen"]["teacher_score"], p["rejected"]["teacher_score"])
        self.assertEqual(seen, {"a", "b"})

    def test_margin_must_be_strictly_above_threshold(self) -> None:
        tied = pairs_from_group([_rec("g", 0, 0.70, "aa"), _rec("g", 1, 0.70, "bb")])
        self.assertEqual(tied, [])
        exact = pairs_from_group([_rec("g", 0, 0.80, "aa"), _rec("g", 1, 0.70, "bb")])
        self.assertEqual(exact, [])
        opened = pairs_from_group([_rec("g", 0, 0.81, "aa"), _rec("g", 1, 0.70, "bb")])
        self.assertEqual(len(opened), 1)
        self.assertEqual(opened[0]["pair_kind"], "score")
        self.assertEqual(opened[0]["chosen"]["candidate_index"], 0)

    def _original(self, gid: str, score: float, text: str = "the original draft") -> dict:
        rec = _rec(gid, -1, score, text)
        rec["training_filter"] = {
            "include_in_training": False,
            "exclude_reasons": ["baseline_reference"],
        }
        rec["parallel_sampling"] = {
            "injected_original": True,
            "reference_only": True,
            "dedupe_kept": True,
        }
        return rec

    def test_original_and_rewrite_form_a_pair(self) -> None:
        original = self._original("g", 0.40)
        high = _rec("g", 0, 0.90, "rewritten high")
        close = _rec("g", 1, 0.45, "rewritten close")
        pairs = pairs_from_group([original, high, close])
        sides = {
            (p["chosen"]["candidate_index"], p["rejected"]["candidate_index"])
            for p in pairs
        }
        self.assertEqual(sides, {(0, -1), (0, 1)})
        original_pair = next(p for p in pairs if -1 in (
            p["chosen"]["candidate_index"], p["rejected"]["candidate_index"],
        ))
        self.assertEqual(original_pair["chosen"]["candidate_index"], 0)
        self.assertEqual(original_pair["rejected"]["candidate_index"], -1)
        self.assertGreater(original_pair["teacher_margin"], 0.1)

    def test_original_can_be_the_higher_scoring_side(self) -> None:
        original = self._original("g", 0.80)
        low = _rec("g", 0, 0.20, "worse rewrite")
        pairs = pairs_from_group([original, low])
        self.assertEqual(len(pairs), 1)
        self.assertEqual(pairs[0]["chosen"]["candidate_index"], -1)
        self.assertEqual(pairs[0]["rejected"]["candidate_index"], 0)

    def test_original_with_another_exclude_reason_stays_out(self) -> None:
        original = self._original("g", 0.80)
        original["training_filter"]["exclude_reasons"].append("empty_completion")
        low = _rec("g", 0, 0.20, "worse rewrite")
        self.assertEqual(pairs_from_group([original, low]), [])


class RewardWritebackTests(unittest.TestCase):
    def test_r_q_becomes_grpo_scalar(self) -> None:
        rec = _rec("g", 0, 0.7, "text")
        apply_r_q_to_record(rec, r_q=-1.25, r_l=3.0, backbone="x")
        self.assertEqual(rec["R_content"], -1.25)
        self.assertEqual(pick_reward_scalar(rec), -1.25)
        self.assertEqual(pick_reward_scalar(rec, prefer="S_fp"), 0.7)
        self.assertEqual(rec["S_fp"], 0.7)
        self.assertEqual(rec["r_content"]["odin_stage"], 3)
        self.assertEqual(rec["r_content"]["r_Q"], -1.25)
        self.assertEqual(rec["r_content"]["r_L"], 3.0)
        self.assertNotIn("z_len", rec["r_content"])
        self.assertNotIn("beta_z_len", rec["r_content"])
        self.assertNotIn("hyperparameters", rec)


class TrainingRecordSlimTests(unittest.TestCase):
    def test_collect_record_drops_length_legacy(self) -> None:
        from training.record_builder import build_training_record

        rec = build_training_record(
            group_id="g",
            group_round=0,
            candidate_index=0,
            context={"shared_source_text": "src"},
            completion_text="a wool coat",
            evaluation={
                "total_score": 0.8,
                "scores": {
                    "s_fp_base": 0.8,
                    "quality_score": {"penalties": {"total_penalty": 0.1}},
                },
                "gates": {"both_passed": True},
                "r_content": {
                    "enabled": True,
                    "S_fp": 0.8,
                    "R_content": 0.8,
                    "char_len": 11,
                    "log_len": 2.48,
                    "z_len": 0.3,
                    "beta_z_len": 0.02,
                    "gamma_penalty": 0.0,
                    "holdout_length_prediction": 0.1,
                    "r_after_length_residual": 0.8,
                },
            },
            r_content_block={
                "enabled": True,
                "S_fp": 0.8,
                "R_content": 0.8,
                "char_len": 11,
                "log_len": 2.48,
                "z_len": 0.3,
                "beta_z_len": 0.02,
                "gamma_penalty": 0.0,
                "holdout_length_prediction": 0.1,
                "r_after_length_residual": 0.8,
            },
        )
        self.assertEqual(rec["S_fp"], 0.8)
        self.assertEqual(rec["char_len"], 11)
        self.assertEqual(rec["r_content"]["log_len"], 2.48)
        self.assertNotIn("z_len", rec["r_content"])
        self.assertNotIn("beta_z_len", rec["r_content"])
        self.assertNotIn("fashion_prompt_score", rec)
        self.assertNotIn("hyperparameters", rec)
        self.assertNotIn("est_tokens_char_div_4", rec)


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
        tw = torch.tensor([0.9, 0.8, 0.7])
        tl = torch.tensor([0.2, 0.3, 0.4])
        loss, stats = odin_rm_loss(
            rqw, rlw, rql, rll, llw, lll, tw, tl,
            head_q=rm.head_q, head_l=rm.head_l,
        )
        self.assertTrue(torch.isfinite(loss))
        self.assertIn("L_R", stats)
        self.assertIn("L_gap", stats)
        self.assertIn("L_L", stats)
        self.assertIn("L_O", stats)
        loss.backward()
        self.assertIsNotNone(next(rm.head_q.parameters()).grad)
        self.assertIsNotNone(next(rm.head_l.parameters()).grad)
        self.assertTrue(torch.all(rqw > 0).item())
        self.assertTrue(torch.all(rlw > 0).item())
        wide = torch.randn(32, 8) * 8
        q_wide, l_wide = rm.scores_from_hidden(wide)
        self.assertTrue(torch.all(q_wide > 0).item())
        self.assertTrue(torch.all(l_wide > 0).item())

    def test_ranking_and_gap_stay_on_quality_head(self) -> None:
        try:
            import torch
            import torch.nn.functional as F
        except ImportError:
            self.skipTest("torch not installed")
        from training.odin_rm.modeling import DualHeadRewardModel, odin_rm_loss

        class Tiny(torch.nn.Module):
            def __init__(self) -> None:
                super().__init__()
                self.config = type("c", (), {"hidden_size": 4})()

        rm = DualHeadRewardModel(Tiny(), hidden_size=4)
        lengths = torch.tensor([10.0, 20.0, 30.0, 40.0])
        high = torch.full((4,), 3.0)
        zero = torch.zeros(4)
        s_w = torch.full((4,), 0.8)
        s_l = torch.full((4,), 0.2)
        kwargs = dict(
            head_q=rm.head_q, head_l=rm.head_l,
            lambda_l=0.0, lambda_o=0.0, lambda_gap=0.0,
        )
        _, ranked = odin_rm_loss(high, zero, zero, zero, lengths, lengths, s_w, s_l, **kwargs)
        expected = float(-F.logsigmoid(torch.tensor(3.0)))
        self.assertAlmostEqual(ranked["L_R"], expected, places=5)
        self.assertEqual(ranked["acc_q"], 1.0)
        _, via_length = odin_rm_loss(zero, high, zero, zero, lengths, lengths, s_w, s_l, **kwargs)
        self.assertAlmostEqual(via_length["L_R"], float(-F.logsigmoid(torch.tensor(0.0))), places=5)
        self.assertGreater(via_length["L_R"], ranked["L_R"])
        _, flipped = odin_rm_loss(zero, zero, high, zero, lengths, lengths, s_w, s_l, **kwargs)
        self.assertGreater(flipped["L_R"], ranked["L_R"])
        self.assertEqual(flipped["acc_q"], 0.0)

        q_w = torch.full((4,), 0.8)
        q_l = torch.full((4,), 0.2)
        _, matched = odin_rm_loss(
            q_w, zero, q_l, zero, lengths, lengths, q_w, q_l,
            head_q=rm.head_q, head_l=rm.head_l, lambda_l=0.0, lambda_o=0.0, lambda_gap=10.0,
        )
        self.assertAlmostEqual(matched["L_gap"], 0.0, places=6)
        _, missed = odin_rm_loss(
            zero, zero, zero, zero, lengths, lengths, q_w, q_l,
            head_q=rm.head_q, head_l=rm.head_l, lambda_l=0.0, lambda_o=0.0, lambda_gap=10.0,
        )
        self.assertAlmostEqual(missed["L_gap"], 0.6 ** 2, places=5)
        self.assertGreater(missed["loss"] - missed["L_R"], matched["loss"] - matched["L_R"])

    def test_length_loss_is_pairwise_softplus_on_both_sides(self) -> None:
        try:
            import torch
        except ImportError:
            self.skipTest("torch not installed")
        from training.odin_rm.modeling import DualHeadRewardModel, length_correlation_loss, odin_rm_loss

        class Tiny(torch.nn.Module):
            def __init__(self) -> None:
                super().__init__()
                self.config = type("c", (), {"hidden_size": 4})()

        rm = DualHeadRewardModel(Tiny(), hidden_size=4)
        lengths = torch.tensor([10.0, 20.0, 30.0, 40.0])
        r_l = lengths.clone()
        r_q = torch.tensor([1.0, 0.0, 1.0, 0.0])
        one, rho_q, rho_l = length_correlation_loss(r_q, r_l, lengths)
        self.assertAlmostEqual(float(rho_l), 1.0, places=5)
        self.assertGreater(float(rho_q.abs()), 0.0)
        zeros = torch.zeros(4)
        _, stats = odin_rm_loss(
            r_q, r_l, r_q, r_l, lengths, lengths, zeros, zeros,
            head_q=rm.head_q, head_l=rm.head_l, lambda_l=1.0, lambda_o=0.0, lambda_gap=0.0,
        )
        self.assertAlmostEqual(stats["L_L"], float(one + one), places=5)
        followed, _, _ = length_correlation_loss(lengths, torch.zeros(4), lengths)
        opposed, _, _ = length_correlation_loss(-lengths, torch.zeros(4), lengths)
        flat, _, _ = length_correlation_loss(torch.tensor([0.2, 0.2, 0.2, 0.2]), torch.zeros(4), lengths)
        self.assertGreater(float(followed), float(opposed))
        self.assertLess(float(flat), float(followed))
        same_len, _, _ = length_correlation_loss(lengths, lengths, torch.ones(4))
        self.assertEqual(float(same_len), 0.0)

        q = torch.zeros(2, requires_grad=True)
        ell = torch.zeros(2, requires_grad=True)
        pair, _, _ = length_correlation_loss(q, ell, torch.tensor([10.0, 30.0]))
        pair.backward()
        self.assertLess(float(ell.grad[1]), 0.0)
        self.assertGreater(float(ell.grad[0]), 0.0)
        self.assertGreater(float(q.grad[1]), 0.0)
        self.assertLess(float(q.grad[0]), 0.0)

    def test_holdout_rho_uses_the_whole_set(self) -> None:
        try:
            import torch
        except ImportError:
            self.skipTest("torch not installed")
        from training.odin_rm.modeling import batch_pearson
        from training.odin_rm.train_rm import write_full_set_rho

        sides = {
            "a#0": (0.0, 10.0, 10.0),
            "a#1": (0.0, 20.0, 20.0),
            "a#2": (1.0, 30.0, 30.0),
            "a#3": (1.0, 40.0, 40.0),
        }
        stats = {"rho_q": 1.0, "rho_l": -1.0}
        write_full_set_rho(stats, sides)
        length = torch.tensor([10.0, 20.0, 30.0, 40.0])
        self.assertAlmostEqual(stats["rho_l"], float(batch_pearson(length, length)), places=5)
        self.assertLess(abs(stats["rho_q"]), abs(stats["rho_l"]))

    def test_orthogonality_is_absolute_weight_dot(self) -> None:
        try:
            import torch
        except ImportError:
            self.skipTest("torch not installed")
        from training.odin_rm.modeling import DualHeadRewardModel, odin_rm_loss, orthogonality_loss

        class Tiny(torch.nn.Module):
            def __init__(self) -> None:
                super().__init__()
                self.config = type("c", (), {"hidden_size": 4})()

        def set_direction(head, vec) -> None:
            direction = torch.tensor(vec, dtype=torch.float32).view(1, -1)
            with torch.no_grad():
                head.parametrizations.weight.original1.copy_(direction)

        rm = DualHeadRewardModel(Tiny(), hidden_size=4)
        set_direction(rm.head_q, [1.0, 0.0, 0.0, 0.0])
        set_direction(rm.head_l, [0.0, 1.0, 0.0, 0.0])
        self.assertAlmostEqual(float(orthogonality_loss(rm.head_q, rm.head_l).detach()), 0.0, places=5)
        set_direction(rm.head_l, [1.0, 0.0, 0.0, 0.0])
        dot = float(torch.dot(rm.head_q.weight.detach().reshape(-1), rm.head_l.weight.detach().reshape(-1)).abs())
        self.assertAlmostEqual(float(orthogonality_loss(rm.head_q, rm.head_l).detach()), dot, places=5)
        self.assertGreater(dot, 0.0)
        lengths = torch.tensor([10.0, 20.0, 30.0])
        zeros = torch.zeros(3)
        _, stats = odin_rm_loss(
            zeros, zeros, zeros, zeros, lengths, lengths, zeros, zeros,
            head_q=rm.head_q, head_l=rm.head_l, lambda_l=0.0, lambda_o=1.0, lambda_gap=0.0,
        )
        self.assertAlmostEqual(stats["L_O"], dot, places=5)
        self.assertAlmostEqual(stats["loss"], stats["L_R"] + dot, places=4)

    def test_old_same_score_length_pairs_are_dropped(self) -> None:
        from training.odin_rm.pairs import pair_in_rm_training

        self.assertFalse(pair_in_rm_training({"pair_kind": "same_score_length", "teacher_margin": 0.0}))
        self.assertFalse(pair_in_rm_training({"pair_kind": "score", "teacher_margin": 0.1}))
        self.assertTrue(pair_in_rm_training({"pair_kind": "score", "teacher_margin": 0.11}))

    def test_residual_correlation_drops_when_r_q_copies_sfp(self) -> None:
        from training.odin_rm.score import summarize_rm_scores

        rows = []
        for i, (score, ell) in enumerate(((0.2, 1.0), (0.5, 2.0), (0.8, 3.0))):
            rec = _rec("g", i, score, "x")
            rec["r_content"]["log_len"] = ell
            rec["odin_rm"] = {"r_Q": score, "r_L": ell}
            rows.append(rec)
        summary = summarize_rm_scores(rows)
        self.assertIsNone(summary["pearson_r_Q_residual_vs_log_len"])
        self.assertGreater(summary["pearson_r_L_vs_log_len"], 0.9)


class SuffixTrainTests(unittest.TestCase):
    def test_unfreeze_opens_only_the_last_layers_and_norm(self) -> None:
        from torch import nn

        from training.odin_rm.modeling import unfreeze_last_layers

        class Inner(nn.Module):
            def __init__(self) -> None:
                super().__init__()
                self.layers = nn.ModuleList([nn.Linear(3, 3) for _ in range(5)])
                self.norm = nn.LayerNorm(3)

        class Backbone(nn.Module):
            def __init__(self) -> None:
                super().__init__()
                self.model = Inner()
                self.extra = nn.Linear(3, 3)

        backbone = Backbone()
        opened = unfreeze_last_layers(backbone, 2)
        self.assertEqual(opened, 2)
        trainable = {name for name, param in backbone.named_parameters() if param.requires_grad}
        self.assertTrue(any(name.startswith("model.layers.3.") for name in trainable))
        self.assertTrue(any(name.startswith("model.layers.4.") for name in trainable))
        self.assertTrue(any(name.startswith("model.norm.") for name in trainable))
        self.assertFalse(any(name.startswith("model.layers.2.") for name in trainable))
        self.assertFalse(any(name.startswith("extra.") for name in trainable))

    def test_backward_stops_before_the_trainable_suffix(self) -> None:
        import torch
        from torch import nn

        from training.odin_rm.modeling import DualHeadRewardModel, last_token_from_inner, unfreeze_last_layers

        class Inner(nn.Module):
            def __init__(self) -> None:
                super().__init__()
                self.layers = nn.ModuleList([nn.Linear(4, 4) for _ in range(4)])
                self.norm = nn.Identity()

            def forward(self, input_ids=None, attention_mask=None, use_cache=False, **kwargs):
                hidden = input_ids.float().unsqueeze(-1).expand(-1, -1, 4).contiguous()
                for layer in self.layers:
                    hidden = layer(hidden)
                return type("Out", (), {"last_hidden_state": self.norm(hidden)})()

        class Backbone(nn.Module):
            def __init__(self) -> None:
                super().__init__()
                self.model = Inner()

        backbone = Backbone()
        unfreeze_last_layers(backbone, 1)
        for param in backbone.model.layers[0].parameters():
            param.requires_grad_(True)
        rm = DualHeadRewardModel(backbone, hidden_size=4)
        ids = torch.tensor([[1, 2, 3], [4, 5, 0]])
        mask = torch.tensor([[1, 1, 1], [1, 1, 0]])
        hidden = last_token_from_inner(rm, ids, mask, 1)
        hidden.sum().backward()
        self.assertIsNotNone(backbone.model.layers[-1].weight.grad)
        self.assertIsNone(backbone.model.layers[0].weight.grad)

    def test_adamw_stores_moments_in_bf16(self) -> None:
        import torch

        from training.odin_rm.train_rm import AdamWBf16State

        torch.manual_seed(0)
        base = torch.randn(16, 8)
        grad = torch.randn(16, 8)
        ref = torch.nn.Parameter(base.clone())
        got = torch.nn.Parameter(base.clone())
        ref.grad = grad.clone()
        got.grad = grad.clone()
        torch.optim.AdamW([ref], lr=1e-2, weight_decay=0.0).step()
        opt = AdamWBf16State([got], lr=1e-2, weight_decay=0.0)
        opt.step()
        state = opt.state[got]
        self.assertEqual(state["exp_avg"].dtype, torch.bfloat16)
        self.assertEqual(state["exp_avg_sq"].dtype, torch.bfloat16)
        self.assertEqual(state["exp_avg"].element_size(), 2)
        self.assertTrue(torch.allclose(got.detach(), ref.detach(), rtol=1e-5, atol=1e-5))

    def test_one_epoch_then_fifteen_step_watch(self) -> None:
        from training.odin_rm.train_rm import rm_step_budget

        scheduled, min_step, total = rm_step_budget(11324, 4, 1.0, 1.0, 15)
        self.assertEqual(scheduled, 2831)
        self.assertEqual(min_step, 2831)
        self.assertEqual(total, 2846)

    def test_holdout_watch_stops_only_after_the_minimum_step(self) -> None:
        from training.odin_rm.train_rm import update_holdout_watch

        best, stale, stop, improved = update_holdout_watch(
            0.70, None, 0, step=10, min_step=100, patience=2,
        )
        self.assertTrue(improved)
        self.assertFalse(stop)
        best, stale, stop, improved = update_holdout_watch(
            0.60, best, stale, step=20, min_step=100, patience=2,
        )
        self.assertFalse(improved)
        self.assertFalse(stop)
        best, stale, stop, improved = update_holdout_watch(
            0.60, best, stale, step=120, min_step=100, patience=2,
        )
        self.assertTrue(stop)
        self.assertEqual(best, 0.70)
        best, stale, stop, _ = update_holdout_watch(
            None, best, 0, step=200, min_step=100, patience=1,
        )
        self.assertFalse(stop)
        self.assertEqual(best, 0.70)


if __name__ == "__main__":
    unittest.main()
