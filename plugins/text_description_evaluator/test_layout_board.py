"""单帧：拼贴、平铺、Look 编号和离身货品抬高 generation_content_penalty。"""

from __future__ import annotations

import unittest

from plugins.text_description_evaluator.design_text_evaluator_api import (
    apply_layout_board_penalty_floor,
    detect_layout_board,
)


PREFIX = (
    "One photograph of one woman at one moment, from one camera. "
    "Show only what that camera sees on her body. "
    "No collage, no flat lay, no product shot, no extra views, no text."
)


class LayoutBoardTests(unittest.TestCase):
    def test_official_prefix_alone_is_not_a_board(self) -> None:
        text = PREFIX + "\n\nA long open coat in gold chevron wool, worn over a striped top."
        self.assertFalse(detect_layout_board(text)["active"])

    def test_look_title_and_off_body_clause_are_severe(self) -> None:
        text = (
            "Look 01: Open Coat\n\n"
            "The coat is worn open over a striped top that would still read as its own garment "
            "if the coat were removed. Large earrings finish the look."
        )
        found = detect_layout_board(text)
        self.assertTrue(found["active"])
        self.assertTrue(found["severe"])
        self.assertIn("look label", found["classes"])
        self.assertIn("off-body catalog", found["classes"])

    def test_penalty_floor_uses_generation_content_penalty(self) -> None:
        penalties = {
            "generation_content_penalty": 0.0,
            "consistency_penalty": 0.0,
            "items": {
                "generation_content_penalty": {"score": 0.0, "reason": ""},
                "consistency_penalty": {"score": 0.0, "reason": ""},
            },
        }
        updated = apply_layout_board_penalty_floor(
            penalties,
            {"active": True, "severe": True, "reason": "look label; off-body catalog"},
        )
        self.assertEqual(updated["generation_content_penalty"], 1.0)
        self.assertEqual(updated["items"]["generation_content_penalty"]["score"], 1.0)
        self.assertEqual(updated["consistency_penalty"], 0.0)


if __name__ == "__main__":
    unittest.main()
