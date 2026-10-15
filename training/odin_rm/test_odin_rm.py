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


class RewardWritebackTests(unittest.TestCase):
    def test_r_q_becomes_grpo_scalar(self) -> None:
        rec = _rec("g", 0, 0.7, "text")
        apply_r_q_to_record(rec, r_q=-1.25, r_l=3.0, backbone="x")
        self.assertEqual(rec["R_content"], -1.25)
        self.assertEqual(pick_reward_scalar(rec), -1.25)
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
        self.assertIn("L_fit", stats)
        self.assertIn("L_cmp", stats)
        self.assertIn("mean_verb", stats)
        self.assertIn("acc_q", stats)
        loss.backward()
        self.assertIsNotNone(next(rm.head_q.parameters()).grad)

    def test_fit_follows_teacher_and_ignores_length_head(self) -> None:
        try:
            import torch
        except ImportError:
            self.skipTest("torch not installed")
        from training.odin_rm.modeling import DualHeadRewardModel, odin_rm_loss

        class Tiny(torch.nn.Module):
            def __init__(self) -> None:
                super().__init__()
                self.config = type("c", (), {"hidden_size": 4})()

        rm = DualHeadRewardModel(Tiny(), hidden_size=4)
        tw = torch.tensor([0.9, 0.8, 0.7])
        tl = torch.tensor([0.2, 0.3, 0.1])
        matched_q_w = tw.clone().requires_grad_(True)
        matched_q_l = tl.clone().requires_grad_(True)
        swapped_q_w = tl.clone().requires_grad_(True)
        swapped_q_l = tw.clone().requires_grad_(True)
        long_w = torch.tensor([4.0, 5.0, 6.0])
        short_l = torch.tensor([0.1, 0.2, 0.3])
        llw = torch.tensor([1.0, 2.0, 3.0])
        lll = torch.tensor([1.2, 2.2, 3.2])
        kwargs = dict(head_q=rm.head_q, head_l=rm.head_l, lambda_corr=0.0, lambda_orth=0.0)
        fit_match, stats_match = odin_rm_loss(
            matched_q_w, long_w, matched_q_l, short_l, llw, lll, tw, tl, **kwargs
        )
        fit_swap, stats_swap = odin_rm_loss(
            swapped_q_w, long_w, swapped_q_l, short_l, llw, lll, tw, tl, **kwargs
        )
        fit_other_len, stats_other = odin_rm_loss(
            matched_q_w, short_l, matched_q_l, long_w, llw, lll, tw, tl, **kwargs
        )
        self.assertAlmostEqual(stats_match["L_cmp"], 0.0, places=6)
        self.assertAlmostEqual(stats_match["L_fit"], 0.0, places=6)
        self.assertGreater(stats_swap["L_cmp"], stats_match["L_cmp"])
        self.assertGreater(stats_swap["L_fit"], stats_match["L_fit"])
        self.assertAlmostEqual(stats_other["L_cmp"], stats_match["L_cmp"], places=6)
        self.assertAlmostEqual(stats_other["L_fit"], stats_match["L_fit"], places=6)
        self.assertEqual(stats_match["acc_q"], 1.0)
        self.assertEqual(stats_swap["acc_q"], 0.0)
        self.assertAlmostEqual(stats_match["mean_verb"], 0.0, places=6)

    def test_slightly_long_is_a_small_deduction_and_double_length_is_not(self) -> None:
        try:
            import torch
        except ImportError:
            self.skipTest("torch not installed")
        from training.odin_rm.modeling import DualHeadRewardModel, odin_rm_loss

        class Tiny(torch.nn.Module):
            def __init__(self) -> None:
                super().__init__()
                self.config = type("c", (), {"hidden_size": 4})()

        from training.odin_rm.modeling import (
            DOUBLE_SOURCE_NAT,
            MILD_OVER_NAT,
            MILD_PENALTY,
            WITHIN_GROUP_SFP_STD,
            verbosity_penalty,
        )

        rm = DualHeadRewardModel(Tiny(), hidden_size=4)
        shorter = verbosity_penalty(torch.tensor([-0.2]))
        mild = verbosity_penalty(torch.tensor([MILD_OVER_NAT]))
        doubled = verbosity_penalty(torch.tensor([DOUBLE_SOURCE_NAT]))
        self.assertAlmostEqual(float(shorter), 0.0, places=6)
        self.assertAlmostEqual(float(mild), MILD_PENALTY, places=4)
        self.assertAlmostEqual(float(doubled), WITHIN_GROUP_SFP_STD, places=4)
        self.assertLess(float(mild), 0.01)
        src = torch.tensor([2.0])
        # 分差 0.02：稍许偏长扣 0.005，高分仍是目标；长到两倍扣 0.053，目标倒向较短的那条。
        s_hi = torch.tensor([0.80])
        s_lo = torch.tensor([0.78])
        q_hi = torch.tensor([0.80])
        q_lo = torch.tensor([0.78])
        _, mild_stats = odin_rm_loss(
            q_hi, torch.zeros(1), q_lo, torch.zeros(1),
            src + MILD_OVER_NAT, src, s_hi, s_lo,
            head_q=rm.head_q, head_l=rm.head_l,
            source_log_win=src, source_log_lose=src,
        )
        self.assertEqual(mild_stats["acc_q"], 1.0)
        _, long_stats = odin_rm_loss(
            q_hi, torch.zeros(1), q_lo, torch.zeros(1),
            src + DOUBLE_SOURCE_NAT, src, s_hi, s_lo,
            head_q=rm.head_q, head_l=rm.head_l,
            source_log_win=src, source_log_lose=src,
        )
        self.assertEqual(long_stats["acc_q"], 0.0)
        self.assertGreater(long_stats["mean_verb"], mild_stats["mean_verb"])

    def test_gap_stays_with_sfp_and_length_is_the_only_shift(self) -> None:
        try:
            import torch
        except ImportError:
            self.skipTest("torch not installed")
        from training.odin_rm.modeling import (
            DOUBLE_SOURCE_NAT,
            GAP_MATCH_WEIGHT,
            WITHIN_GROUP_SFP_STD,
            DualHeadRewardModel,
            odin_rm_loss,
        )

        class Tiny(torch.nn.Module):
            def __init__(self) -> None:
                super().__init__()
                self.config = type("c", (), {"hidden_size": 4})()

        rm = DualHeadRewardModel(Tiny(), hidden_size=4)
        self.assertAlmostEqual(GAP_MATCH_WEIGHT, 1.0 / WITHIN_GROUP_SFP_STD, places=6)
        src = torch.tensor([2.0])
        s_hi = torch.tensor([0.80])
        s_lo = torch.tensor([0.78])
        kwargs = dict(head_q=rm.head_q, head_l=rm.head_l, source_log_win=src, source_log_lose=src)
        # 不长过原文：r_Q 抄 S_fp 时，分差与裁判一致，长度残差为 0。
        _, same = odin_rm_loss(
            s_hi, torch.zeros(1), s_lo, torch.zeros(1),
            src, src, s_hi, s_lo, **kwargs,
        )
        self.assertAlmostEqual(same["L_cmp"], 0.0, places=6)
        self.assertAlmostEqual(same["gap_sfp_mae"], 0.0, places=6)
        self.assertAlmostEqual(same["verb_resid_mae"], 0.0, places=6)
        # 高分那条长到原文两倍：仍抄 S_fp 时，分差没跟上扣分，长度残差就是这 0.053。
        _, copied = odin_rm_loss(
            s_hi, torch.zeros(1), s_lo, torch.zeros(1),
            src + DOUBLE_SOURCE_NAT, src, s_hi, s_lo, **kwargs,
        )
        self.assertAlmostEqual(copied["gap_sfp_mae"], 0.0, places=4)
        self.assertAlmostEqual(copied["verb_resid_mae"], WITHIN_GROUP_SFP_STD, places=4)
        # 漏掉一个组内标准差：加权后的分差损失等于 0.053，而不是 0.053²。
        self.assertAlmostEqual(copied["L_cmp"], WITHIN_GROUP_SFP_STD, places=3)
        # 把扣分写进 r_Q 之后，和 S_fp 的分差正好等于冗长扣分，长度残差回到 0。
        q_hi = s_hi - WITHIN_GROUP_SFP_STD
        _, shifted = odin_rm_loss(
            q_hi, torch.zeros(1), s_lo, torch.zeros(1),
            src + DOUBLE_SOURCE_NAT, src, s_hi, s_lo, **kwargs,
        )
        self.assertAlmostEqual(shifted["L_cmp"], 0.0, places=4)
        self.assertAlmostEqual(shifted["verb_resid_mae"], 0.0, places=4)
        self.assertAlmostEqual(shifted["gap_sfp_mae"], WITHIN_GROUP_SFP_STD, places=4)

    def test_anti_length_content_head_costs_more_than_uncorrelated(self) -> None:
        try:
            import torch
        except ImportError:
            self.skipTest("torch not installed")
        from training.odin_rm.modeling import length_disentangle_term

        rho_l = torch.tensor(0.94)
        flat = length_disentangle_term(torch.tensor(0.0), rho_l)
        anti = length_disentangle_term(torch.tensor(-0.94), rho_l)
        same_dir = length_disentangle_term(torch.tensor(0.94), rho_l)
        self.assertLess(float(flat), float(anti))
        self.assertLess(float(flat), float(same_dir))


if __name__ == "__main__":
    unittest.main()
