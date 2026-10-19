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
        self.assertEqual(len(pairs), 3)
        opened = [p for p in pairs if p["teacher_margin"] >= 0.10]
        self.assertEqual(len(opened), 2)
        for p in opened:
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
        self.assertIn("L_gap", stats)
        self.assertIn("L_len", stats)
        self.assertNotIn("L_ord", stats)
        loss.backward()
        self.assertIsNotNone(next(rm.head_q.parameters()).grad)
        self.assertIsNotNone(next(rm.head_l.parameters()).grad)

    def test_length_head_reports_excess_over_source(self) -> None:
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
        src = torch.tensor([5.0])
        s_hi = torch.tensor([0.90])
        s_lo = torch.tensor([0.60])
        kwargs = dict(
            head_q=rm.head_q,
            head_l=rm.head_l,
            lambda_corr=0.0,
            source_log_win=src,
            source_log_lose=src,
        )
        # 与原文一样长，r_L 报 0，r_Q 分差对齐 S_fp：长度和分差都是 0。
        _, matched = odin_rm_loss(
            s_hi, torch.zeros(1), s_lo, torch.zeros(1), src, src, s_hi, s_lo, **kwargs,
        )
        self.assertAlmostEqual(matched["L_len"], 0.0, places=6)
        self.assertAlmostEqual(matched["L_gap"], 0.0, places=6)
        # 短于原文仍报 0：不因偏短加损失。
        _, shorter = odin_rm_loss(
            s_hi, torch.zeros(1), s_lo, torch.zeros(1), src - 0.4, src - 0.2, s_hi, s_lo, **kwargs,
        )
        self.assertAlmostEqual(shorter["L_len"], 0.0, places=6)
        # 长到一倍却报 0：长度项等于超长幅度的平方。
        far = src + torch.log(torch.tensor([2.0]))
        _, too_long = odin_rm_loss(
            s_hi, torch.zeros(1), s_lo, torch.zeros(1), far, src, s_hi, s_lo, **kwargs,
        )
        self.assertAlmostEqual(too_long["L_len"], 0.5 * torch.log(torch.tensor(2.0)).square().item(), places=4)
        # 长侧如实报出超长幅度：长度项为 0。
        excess = torch.log(torch.tensor([2.0]))
        _, reported = odin_rm_loss(
            s_hi, excess, s_lo, torch.zeros(1), far, src, s_hi, s_lo, **kwargs,
        )
        self.assertAlmostEqual(reported["L_len"], 0.0, places=5)

    def test_close_excess_keeps_sfp_gap(self) -> None:
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
        src = torch.tensor([5.0])
        s_hi = torch.tensor([0.90])
        s_lo = torch.tensor([0.60])
        kwargs = dict(
            head_q=rm.head_q,
            head_l=rm.head_l,
            lambda_corr=0.0,
            lambda_orth=0.0,
            source_log_win=src,
            source_log_lose=src,
        )
        # 超长幅度都是 0：分差被收小要付出分差项。头自己把 r_L 拉开，不能借此逃避。
        _, shrunk = odin_rm_loss(
            torch.tensor([0.70]), torch.zeros(1), s_lo, torch.zeros(1), src, src, s_hi, s_lo, **kwargs,
        )
        self.assertAlmostEqual(shrunk["L_gap"], 0.20 ** 2, places=4)
        far_rl = torch.log(torch.tensor([2.0]))
        _, shrunk_but_head_split = odin_rm_loss(
            torch.tensor([0.70]), far_rl, s_lo, torch.zeros(1), src, src, s_hi, s_lo, **kwargs,
        )
        self.assertAlmostEqual(shrunk_but_head_split["L_gap"], shrunk["L_gap"], places=4)
        # 分差对调：对齐项按整段分差计，名次随之错开。
        _, flipped = odin_rm_loss(
            s_lo, torch.zeros(1), s_hi, torch.zeros(1), src, src, s_hi, s_lo, **kwargs,
        )
        self.assertAlmostEqual(flipped["L_gap"], 0.60 ** 2, places=4)
        self.assertEqual(flipped["acc_q"], 0.0)
        # 一侧长到一倍：r_Q 仍守住 S_fp 分差，不按超长扣减。
        far = src + torch.log(torch.tensor([2.0]))
        excess = torch.log(torch.tensor([2.0]))
        _, copied = odin_rm_loss(
            s_hi, excess, s_lo, torch.zeros(1), far, src, s_hi, s_lo, **kwargs,
        )
        self.assertAlmostEqual(copied["L_gap"], 0.0, places=4)
        _, deducted = odin_rm_loss(
            s_hi - excess, excess, s_lo, torch.zeros(1), far, src, s_hi, s_lo, **kwargs,
        )
        self.assertAlmostEqual(deducted["L_gap"], excess.square().item(), places=4)

    def test_same_score_keeps_r_q_gap_at_zero(self) -> None:
        try:
            import torch
        except ImportError:
            self.skipTest("torch not installed")
        from training.odin_rm.modeling import DualHeadRewardModel, odin_rm_loss
        from training.odin_rm.pairs import pairs_from_group

        class Tiny(torch.nn.Module):
            def __init__(self) -> None:
                super().__init__()
                self.config = type("c", (), {"hidden_size": 4})()

        rm = DualHeadRewardModel(Tiny(), hidden_size=4)
        src = torch.tensor([5.0])
        score = torch.tensor([0.70])
        excess = torch.log(torch.tensor([2.0]))
        far = src + excess
        kwargs = dict(
            head_q=rm.head_q,
            head_l=rm.head_l,
            lambda_corr=0.0,
            lambda_orth=0.0,
            source_log_win=src,
            source_log_lose=src,
        )
        # 同分、B 长到一倍：两边 r_Q 相同，分差项为 0。字数差不进内容头。
        _, tied = odin_rm_loss(
            score, torch.zeros(1), score, excess, src, far, score, score, **kwargs,
        )
        self.assertAlmostEqual(tied["L_gap"], 0.0, places=4)
        self.assertEqual(tied["same_score_frac"], 1.0)
        # 把长的 r_Q 压低：分差项等于压低量的平方。
        _, separated = odin_rm_loss(
            score, torch.zeros(1), score - excess, excess, src, far, score, score, **kwargs,
        )
        self.assertAlmostEqual(separated["L_gap"], excess.square().item(), places=4)
        pairs = pairs_from_group(
            [_rec("g", 0, 0.70, "a" * 10), _rec("g", 1, 0.70, "b" * 1000)]
        )
        self.assertEqual(len(pairs), 1)
        self.assertEqual(pairs[0]["pair_kind"], "same_score_length")
        self.assertEqual(pairs[0]["chosen"]["candidate_index"], 0)
        self.assertLess(pairs[0]["chosen"]["log_len"], pairs[0]["rejected"]["log_len"])

    def test_small_score_gap_still_trains_content_head(self) -> None:
        try:
            import torch
        except ImportError:
            self.skipTest("torch not installed")
        from training.odin_rm.modeling import MIN_SCORE_GAP, DualHeadRewardModel, odin_rm_loss
        from training.odin_rm.pairs import pairs_from_group

        class Tiny(torch.nn.Module):
            def __init__(self) -> None:
                super().__init__()
                self.config = type("c", (), {"hidden_size": 4})()

        rm = DualHeadRewardModel(Tiny(), hidden_size=4)
        src = torch.tensor([5.0])
        s_hi = torch.tensor([0.55])
        s_lo = torch.tensor([0.50])
        self.assertLess(float(s_hi - s_lo), MIN_SCORE_GAP)
        kwargs = dict(
            head_q=rm.head_q,
            head_l=rm.head_l,
            lambda_orth=0.0,
            source_log_win=src,
            source_log_lose=src,
        )
        _, matched = odin_rm_loss(
            s_hi, torch.zeros(1), s_lo, torch.zeros(1), src, src, s_hi, s_lo, **kwargs,
        )
        self.assertAlmostEqual(matched["L_gap"], 0.0, places=6)
        self.assertEqual(matched["usable_frac"], 1.0)
        _, reversed_gap = odin_rm_loss(
            s_lo, torch.zeros(1), s_hi, torch.zeros(1), src, src, s_hi, s_lo, **kwargs,
        )
        self.assertAlmostEqual(reversed_gap["L_gap"], 0.10 ** 2, places=4)
        pairs = pairs_from_group(
            [_rec("g", 0, 0.55, "aa"), _rec("g", 1, 0.50, "bb")]
        )
        self.assertEqual(len(pairs), 1)
        self.assertEqual(pairs[0]["pair_kind"], "score")

    def test_aligned_gap_keeps_correlation_out_of_loss(self) -> None:
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
        ell = torch.tensor([1.0, 2.0, 3.0])
        src = torch.full((3,), 2.0)
        s_w = torch.tensor([0.30, 0.60, 0.90])
        s_l = torch.tensor([0.10, 0.40, 0.70])
        kwargs = dict(
            head_q=rm.head_q,
            head_l=rm.head_l,
            lambda_orth=0.0,
            source_log_win=src,
            source_log_lose=src,
        )
        _, aligned = odin_rm_loss(
            s_w, torch.zeros(3), s_l, torch.zeros(3), ell, ell, s_w, s_l,
            lambda_corr=1.0, **kwargs,
        )
        self.assertAlmostEqual(aligned["L_gap"], 0.0, places=5)
        self.assertGreater(abs(aligned["rho_q"]), 0.9)
        self.assertAlmostEqual(aligned["loss"], 0.0, places=5)
        self.assertGreater(aligned["L_orth"], 0.5)

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
