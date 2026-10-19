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
        self.assertIn("L_rec", stats)
        self.assertIn("L_gap", stats)
        self.assertIn("L_rl", stats)
        self.assertIn("acc_q", stats)
        loss.backward()
        self.assertIsNotNone(next(rm.head_q.parameters()).grad)
        self.assertIsNotNone(next(rm.head_l.parameters()).grad)

    def test_close_length_restores_sfp_gap(self) -> None:
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
        z = torch.zeros(1)
        s_hi = torch.tensor([0.90])
        s_lo = torch.tensor([0.60])
        kwargs = dict(head_q=rm.head_q, head_l=rm.head_l)
        # 句长相同，r_Q 抄上 S_fp 分差，r_L 为 0：还原项和分差项都是 0。
        _, matched = odin_rm_loss(
            s_hi, z, s_lo, z, z, z, s_hi, s_lo, **kwargs,
        )
        self.assertAlmostEqual(matched["L_rec"], 0.0, places=6)
        self.assertAlmostEqual(matched["L_gap"], 0.0, places=6)
        self.assertAlmostEqual(matched["gap_sfp_mae"], 0.0, places=6)
        # 分差被收小：分差项为正。幅度按平方计，不是只看符号。
        _, shrunk = odin_rm_loss(
            s_hi, z, torch.tensor([0.80]), z, z, z, s_hi, s_lo, **kwargs,
        )
        self.assertAlmostEqual(shrunk["L_gap"], 0.20 ** 2, places=4)
        # 分差被拉得比 S_fp 更大，同样要付出分差项。
        _, wider = odin_rm_loss(
            torch.tensor([0.95]), z, torch.tensor([0.55]), z, z, z, s_hi, s_lo, **kwargs,
        )
        self.assertAlmostEqual(wider["L_gap"], 0.10 ** 2, places=4)
        # r_Q 分差对了，但 r_L 没有补成 S_fp：还原项为正。
        _, unsplit = odin_rm_loss(
            s_hi, torch.tensor([0.20]), s_lo, z, z, z, s_hi, s_lo, **kwargs,
        )
        self.assertAlmostEqual(unsplit["L_gap"], 0.0, places=6)
        self.assertGreater(unsplit["L_rec"], 0.0)
        # 两边 r_L 一样大、和 S_fp 也能加回去：分差项是 0，但 r_L 占比过大。
        shift = torch.tensor([0.40])
        _, bulky = odin_rm_loss(
            s_hi - 0.40, shift, s_lo - 0.40, shift, z, z, s_hi, s_lo, **kwargs,
        )
        self.assertAlmostEqual(bulky["L_gap"], 0.0, places=6)
        self.assertAlmostEqual(bulky["L_rec"], 0.0, places=6)
        self.assertGreater(bulky["L_rl"], matched["L_rl"])

    def test_dull_pairs_drop_out(self) -> None:
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
        z = torch.zeros(1)
        kwargs = dict(head_q=rm.head_q, head_l=rm.head_l)
        s_hi = torch.tensor([0.80])
        s_lo = torch.tensor([0.78])
        _, copied = odin_rm_loss(s_hi, z, s_lo, z, z, z, s_hi, s_lo, **kwargs)
        _, blown = odin_rm_loss(
            torch.tensor([0.90]), z, torch.tensor([0.70]), z, z, z, s_hi, s_lo, **kwargs,
        )
        self.assertEqual(copied["effect_frac"], 0.0)
        self.assertAlmostEqual(copied["loss"], 0.0, places=6)
        self.assertAlmostEqual(blown["loss"], 0.0, places=6)

    def test_long_side_quality_drops_when_score_is_close(self) -> None:
        try:
            import torch
        except ImportError:
            self.skipTest("torch not installed")
        from training.odin_rm.modeling import GAP_FULL, LENGTH_FAR_NAT, DualHeadRewardModel, odin_rm_loss

        class Tiny(torch.nn.Module):
            def __init__(self) -> None:
                super().__init__()
                self.config = type("c", (), {"hidden_size": 4})()

        rm = DualHeadRewardModel(Tiny(), hidden_size=4)
        z = torch.zeros(1)
        far = z + LENGTH_FAR_NAT
        kwargs = dict(head_q=rm.head_q, head_l=rm.head_l)
        s_hi = torch.tensor([0.55])
        s_lo = torch.tensor([0.50])
        # 原始分接近、高分一侧长到一倍：r_L 仍是 0 时，长度项为正。
        _, copied = odin_rm_loss(
            s_hi, z, s_lo, z, far, z, s_hi, s_lo, **kwargs,
        )
        self.assertGreater(copied["L_rl"], 0.0)
        self.assertEqual(copied["effect_frac"], 1.0)
        # 长侧 r_L 取 0.20，r_Q 相应少 0.20，加总仍是 S_fp。短侧 r_L 保持 0。
        _, split = odin_rm_loss(
            s_hi - GAP_FULL, torch.tensor([GAP_FULL]), s_lo, z, far, z, s_hi, s_lo, **kwargs,
        )
        self.assertAlmostEqual(split["L_rl"], 0.0, places=6)
        self.assertAlmostEqual(split["L_rec"], 0.0, places=6)
        # 把这 0.20 扣到短的一侧：长度项回升。
        _, wrong = odin_rm_loss(
            s_hi, z, s_lo - GAP_FULL, torch.tensor([GAP_FULL]), far, z, s_hi, s_lo, **kwargs,
        )
        self.assertGreater(wrong["L_rl"], split["L_rl"])
        # 句长只差 0.05 nat，而且原始分差也不大：整对不进损失。
        _, tiny_len = odin_rm_loss(
            s_hi, z, s_lo, z, z + 0.05, z, s_hi, s_lo, **kwargs,
        )
        self.assertEqual(tiny_len["effect_frac"], 0.0)
        self.assertAlmostEqual(tiny_len["loss"], 0.0, places=6)

    def test_long_winner_shrinks_sfp_gap(self) -> None:
        try:
            import torch
        except ImportError:
            self.skipTest("torch not installed")
        from training.odin_rm.modeling import GAP_FULL, LENGTH_FAR_NAT, DualHeadRewardModel, odin_rm_loss

        class Tiny(torch.nn.Module):
            def __init__(self) -> None:
                super().__init__()
                self.config = type("c", (), {"hidden_size": 4})()

        rm = DualHeadRewardModel(Tiny(), hidden_size=4)
        z = torch.zeros(1)
        far = z + LENGTH_FAR_NAT
        kwargs = dict(head_q=rm.head_q, head_l=rm.head_l)
        s_hi = torch.tensor([0.90])
        s_lo = torch.tensor([0.60])
        # 高分一侧长到一倍：原样保住 0.30 的分差算损失。目标分差是 0.10。
        _, full = odin_rm_loss(
            s_hi, z, s_lo, z, far, z, s_hi, s_lo, **kwargs,
        )
        self.assertAlmostEqual(full["L_gap"], 0.20 ** 2, places=4)
        # 分差缩小 0.20，长侧 r_L 拿走这 0.20：分差项和还原项都是 0。
        _, shrunk = odin_rm_loss(
            s_hi - GAP_FULL, torch.tensor([GAP_FULL]), s_lo, z, far, z, s_hi, s_lo, **kwargs,
        )
        self.assertAlmostEqual(shrunk["L_gap"], 0.0, places=6)
        self.assertAlmostEqual(shrunk["L_rec"], 0.0, places=6)
        self.assertAlmostEqual(shrunk["L_rl"], 0.0, places=6)
        # 缩得超过 0.20：相对缩小后的目标又偏小，分差项为正。
        _, over = odin_rm_loss(
            s_lo, torch.tensor([0.30]), s_lo, z, far, z, s_hi, s_lo, **kwargs,
        )
        self.assertAlmostEqual(over["L_gap"], (GAP_FULL - 0.30) ** 2, places=4)
        # 高分一侧更短，r_L 仍接近：不缩小，原分差对齐时分差项为 0。
        _, short_hi = odin_rm_loss(
            s_hi, z, s_lo, z, z, far, s_hi, s_lo, **kwargs,
        )
        self.assertAlmostEqual(short_hi["L_gap"], 0.0, places=6)
        _, short_hi_cut = odin_rm_loss(
            s_hi - GAP_FULL, z, s_lo, z, z, far, s_hi, s_lo, **kwargs,
        )
        self.assertGreater(short_hi_cut["L_gap"], short_hi["L_gap"])

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
