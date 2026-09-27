"""设计与冲突的划分，以及冲突对总分上限的影响。"""

from __future__ import annotations

import unittest
from pathlib import Path

from plugins.text_description_evaluator.design_text_evaluator_api import (
    apply_consistency_penalty_floor,
    compute_design_merit_metric_caps,
    conflict_quality_cap,
    detect_consistency_conflicts,
    list_design_identifying_signatures,
)

REPO = Path(__file__).resolve().parents[2]
DEFECTS = REPO / "fashion_research_dir" / "consistency_defect_cases"
INVERSE = REPO / "fashion_research_dir" / "wgsn_batch_image_inverse" / "20260524T044337Z"


def _prose(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if "## text_description" in text:
        body = text.split("## text_description", 1)[1]
        body = body.split("## key_elements", 1)[0]
        return body.strip()
    return text.strip()


class ConflictDefinitionTests(unittest.TestCase):
    def test_negative_cases_are_conflicts(self) -> None:
        for path in sorted(DEFECTS.glob("[0-9][0-9]_*.txt")):
            found = detect_consistency_conflicts(path.read_text(encoding="utf-8"))
            self.assertTrue(found["active"], path.name)

    def test_inverse_looks_stay_design(self) -> None:
        jacket = INVERSE / (
            "01_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__001_media_cha_biarritz_ps27_003_text_description.md"
        )
        tweed = INVERSE / (
            "09_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__009_media_cha_biarritz_ps27_028_text_description.md"
        )
        jacket_text = _prose(jacket)
        tweed_text = _prose(tweed)
        self.assertFalse(detect_consistency_conflicts(jacket_text)["active"])
        self.assertFalse(detect_consistency_conflicts(tweed_text)["active"])
        self.assertIn("edge_path", list_design_identifying_signatures(jacket_text))
        self.assertIn("second_identity", list_design_identifying_signatures(tweed_text))

    def test_placement_and_one_identity_finishing_are_not_conflicts(self) -> None:
        text = (
            "A narrow ink coat frames a parchment silk-crepe blouse and warm grey slim wool trousers. "
            "The coat closes with a concealed placket, an off-center slit, and a hem just past the calf. "
            "Smoke-grey topstitching stays on the matte wool."
        )
        found = detect_consistency_conflicts(text)
        self.assertFalse(found["active"])
        caps = compute_design_merit_metric_caps(text)["caps"]
        self.assertNotIn("design_distinctiveness", caps)

    def test_conflict_caps_design_even_when_an_edge_remains(self) -> None:
        text = (
            "Dense floral appliqué runs along the neckline and both front edges. "
            "The left half is matte black wool with a set-in sleeve. "
            "The right half is silk and sequin with a bishop sleeve."
        )
        found = detect_consistency_conflicts(text)
        self.assertTrue(found["active"])
        caps = compute_design_merit_metric_caps(text)["caps"]
        self.assertEqual(caps["design_distinctiveness"]["cap"], 0.25)
        self.assertEqual(caps["design_signal_purity"]["cap"], 0.25)

    def test_or_choice_one_shoulder_and_repair_voice_are_conflicts(self) -> None:
        skirt_or_trouser = (
            "Underneath, keep a slim matching floral pencil skirt or narrow column trouser "
            "only if visible at the hem."
        )
        flats_or_pumps = "Finish with simple black flats or low pumps."
        one_shoulder = (
            "A fitted knee-length pencil dress with a single long cream sleeve finished with "
            "a bold red cuff, while the other side is sleeveless for an asymmetric one-shoulder effect."
        )
        repair = (
            "Pair it with a tailored black trouser to replace the conflicting bottom "
            "and restore a coherent full look."
        )
        negated = "A blush tulle ballgown, no tailcoat, no top hat."
        self.assertIn("bottom", detect_consistency_conflicts(skirt_or_trouser)["alternative_slots"])
        self.assertIn("shoe", detect_consistency_conflicts(flats_or_pumps)["alternative_slots"])
        self.assertTrue(detect_consistency_conflicts(one_shoulder)["two_sleeve_states"])
        self.assertTrue(detect_consistency_conflicts(repair)["repair_voice"])
        self.assertTrue(detect_consistency_conflicts(negated)["foreign_terms"])
        for text in (skirt_or_trouser, flats_or_pumps, one_shoulder, repair, negated):
            self.assertTrue(detect_consistency_conflicts(text)["active"], text)

    def test_inverse_corpus_stays_design(self) -> None:
        flagged = []
        for path in sorted(INVERSE.glob("*_text_description.md")):
            found = detect_consistency_conflicts(_prose(path))
            if found["active"]:
                flagged.append(f"{path.name}: {found['reason']}")
        self.assertEqual(flagged, [])

    def test_material_or_and_layered_sleeveless_stay_design(self) -> None:
        material = "The surface reads as matte silk or fine crepe, with a concealed placket."
        layered = (
            "The jacket has long slim sleeves and an open front. "
            "Under it, a sleeveless striped top closes with gold-tone buttons."
        )
        self.assertFalse(detect_consistency_conflicts(material)["active"])
        self.assertFalse(detect_consistency_conflicts(layered)["active"])

    def test_dirty_rewrites_keep_asymmetry_and_contradictory_positions(self) -> None:
        dirty = {
            "sides": (
                "Black wool trousers with a crease on the left leg and a red silk culotte on the right. "
                "Closed black satin court pumps on the left foot and an open red silk evening sandal on the right."
            ),
            "sleeves": (
                "A cropped sleeve ending above the elbow opens over a navy short. "
                "Over the right half, the jacket has a floor-grazing liquid-black silk sleeve."
            ),
            "collar": "A black collarless jacket cropped to the hip features a wide notched lapel.",
            "neck_and_hem": (
                "A high stand-collar coat with a deep plunging V neckline. "
                "The straight hem just below the knee creates a floor-sweeping train."
            ),
            "shell": (
                "The coat is available in matte wool-gabardine, with a liquid mirror sequin version."
            ),
            "theme": "The inner layer features a harlequin bodice and a jeweled mask.",
        }
        for name, text in dirty.items():
            found = detect_consistency_conflicts(text)
            self.assertTrue(found["active"], name)
            self.assertEqual(conflict_quality_cap(found), 0.25)
        clear = conflict_quality_cap({"active": False})
        self.assertIsNone(clear)
        split_across_sentences = {
            "two bottoms": (
                "A black box jacket with a wide notched lapel, cropped to the hip, over fitted black shorts. "
                "The lower body consists of wide ivory wool trousers."
            ),
            "neck then hem": (
                "A high stand-collar knee coat with a straight hem just below the knee. "
                "The coat is sleeveless with a deep plunging V neck to the waist. "
                "The hem sweeps the floor in a luxurious train."
            ),
            "two closures": (
                "A narrow ink coat with a concealed button placket frames a silk blouse. "
                "The coat is a double-breasted style with six exposed buttons."
            ),
        }
        for name, text in split_across_sentences.items():
            found = detect_consistency_conflicts(text)
            self.assertTrue(found["active"], name)
            self.assertEqual(conflict_quality_cap(found), 0.25)

    def test_penalty_floor_does_not_enter_total_score(self) -> None:
        penalties = {
            "consistency_penalty": 0.0,
            "coordination_penalty": 0.0,
            "generation_content_penalty": 0.0,
            "rationality_penalty": 0.0,
            "formula_template_penalty": 0.0,
            "items": {
                "consistency_penalty": {"score": 0.0, "reason": "", "evidence": []},
                "coordination_penalty": {"score": 0.0, "reason": "", "evidence": []},
                "generation_content_penalty": {"score": 0.0, "reason": "", "evidence": []},
                "rationality_penalty": {"score": 0.0, "reason": "", "evidence": []},
                "formula_template_penalty": {"score": 0.0, "reason": "", "evidence": []},
            },
            "reasons": {},
        }
        text = Path(DEFECTS / "10_style_clash.txt").read_text(encoding="utf-8")
        found = detect_consistency_conflicts(text)
        self.assertTrue(found["foreign_terms"])
        apply_consistency_penalty_floor(penalties, found)
        self.assertGreaterEqual(penalties["consistency_penalty"], 0.75)
        self.assertGreaterEqual(penalties["coordination_penalty"], 0.75)


if __name__ == "__main__":
    unittest.main()
