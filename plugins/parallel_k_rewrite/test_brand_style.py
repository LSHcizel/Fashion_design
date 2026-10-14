"""品牌习惯卡已经离开第一改写器。这里核对目录读取，以及第二改写器的三段调用。"""

from __future__ import annotations

import re
import unittest

from plugins.brand_tone_rewriter.brand_card import (
    brand_preference_items,
    format_existing_designs,
    iter_style_houses,
    resolve_brand,
)
from plugins.brand_tone_rewriter.rewriter import rewrite_generated_description
from plugins.parallel_k_rewrite.k_candidate_generator import build_rewrite_user_prompt


class BrandCardCatalogTests(unittest.TestCase):
    def test_every_indexed_house_has_habit_sections(self) -> None:
        houses = list(iter_style_houses())
        self.assertGreaterEqual(len(houses), 30)
        for house in houses:
            resolved, items = brand_preference_items(explicit=house)
            self.assertEqual(resolved, house)
            self.assertTrue(items)
            self.assertTrue(any(item["section"] == "Silhouette" for item in items))
            blob = format_existing_designs(house, items)
            self.assertIn(f"House: {house}", blob)
            self.assertNotIn("BRAND STYLE CARD", blob)
            self.assertNotIn("Heritage & provenance", blob)
            self.assertNotIn("Show / location context", blob)
            self.assertNotIn("Creative director intent", blob)
            for item in items:
                line = item["text"]
                if re.search(r"\b(logo|monogram|interlocking)\b", line, re.IGNORECASE):
                    self.assertRegex(line, r"\b(not|without|no)\b")

    def test_explicit_brand_wins_over_another_house_in_the_text(self) -> None:
        self.assertEqual(
            resolve_brand(explicit="Gucci", texts=["a Prada crystal skirt"]),
            "Gucci",
        )
        house, items = brand_preference_items(
            explicit="gucci_ss27",
            texts=["a Prada crystal skirt"],
        )
        self.assertEqual(house, "Gucci")
        self.assertTrue(items)

    def test_aliases_resolve(self) -> None:
        self.assertEqual(resolve_brand(explicit="Hermes"), "Hermès")
        self.assertEqual(resolve_brand(explicit="YSL"), "Saint Laurent")
        self.assertEqual(resolve_brand(explicit="Chloé"), "Chloé")
        self.assertEqual(
            resolve_brand(texts=["Design a Bottega Veneta collection.", "a navy coat"]),
            "Bottega Veneta",
        )

    def test_ordinary_row_of_is_not_the_house(self) -> None:
        self.assertIsNone(resolve_brand(texts=["the row of buttons on a navy coat"]))
        self.assertEqual(resolve_brand(explicit="The Row"), "The Row")
        _house, items = brand_preference_items(explicit="Gucci")
        crafts = [item["text"] for item in items if item["section"] == "Craft"]
        self.assertGreaterEqual(len(crafts), 1)
        self.assertNotIn("enlarged Trench", " ".join(crafts))

    def test_unknown_brand_has_no_habits(self) -> None:
        self.assertIsNone(resolve_brand(explicit="Acme Atelier", texts=["a navy trench"]))
        house, items = brand_preference_items(texts=["a cropped navy jacket and beige shorts"])
        self.assertEqual(house, "")
        self.assertEqual(items, [])


class FirstRewriterHasNoBrandCardTests(unittest.TestCase):
    def test_user_prompt_does_not_carry_a_brand_card(self) -> None:
        prompt = build_rewrite_user_prompt(
            "A smile-line clutch and matching pumps.",
            k=2,
            candidate_index=0,
            extra_context="Chapter: Smile\nExtract the theme from SOURCE.",
        )
        self.assertNotIn("BRAND STYLE CARD", prompt)
        self.assertNotIn("REWRITE DIRECTION", prompt)
        self.assertLess(prompt.index("Chapter: Smile"), prompt.index("THEME AND CONCEPT LOCK"))

    def test_workflow_extra_context_has_no_brand_card(self) -> None:
        from fashion_workflow import FashionWorkflow

        wf = FashionWorkflow.__new__(FashionWorkflow)
        wf.brand = "Moschino"
        wf.design_target_prompt = "Design a Moschino collection"
        wf._current_sub_theme_name = "Smile"
        ctx = wf._rewrite_extra_context(
            None,
            source_text="A smile-line clutch.",
            generate_text=lambda **_kwargs: '{"keep": [1]}',
        )
        self.assertNotIn("BRAND STYLE CARD", ctx)
        self.assertNotIn("REWRITE DIRECTION", ctx)
        self.assertLess(ctx.index("Chapter: Smile"), ctx.index("THEME AND CONCEPT LOCK"))


class SecondRewriterTests(unittest.TestCase):
    def test_three_calls_then_a_new_description(self) -> None:
        seen = []

        def generate_text(**kwargs):
            seen.append(kwargs["system_prompt"])
            self.assertEqual(kwargs["temperature"], 0)
            if len(seen) == 1:
                self.assertIn("BRAND: Chanel", kwargs["user_prompt"])
                self.assertIn("THEME: salon released toward the shore", kwargs["user_prompt"])
                self.assertIn("Existing designs on file", kwargs["user_prompt"])
                self.assertIn("serious conflicting inconsistency", kwargs["user_prompt"])
                return (
                    '{"feature_points": ["soft tailoring"], '
                    '"signature_points": ["chain-weighted hem"], '
                    '"similar_designs": ["a fluid day suit"]}'
                )
            if len(seen) == 2:
                self.assertIn("brand and theme fit", kwargs["user_prompt"])
                self.assertIn("replace a garment type", kwargs["user_prompt"])
                self.assertNotIn("ELEMENT RECONSTRUCTION", kwargs["user_prompt"])
                self.assertIn("chain-weighted hem", kwargs["user_prompt"])
                return '{"suggestions": [{"edit": "weight the jacket hem with a chain", "where": "hem"}]}'
            self.assertIn("fits this house's tone", kwargs["user_prompt"])
            return (
                '{"kept": ["weight the jacket hem with a chain"], "dropped": [], '
                '"reflection": "The chain hem is Chanel and still a day suit.", '
                '"description": "A muted grey Chanel day suit with a chain along the jacket hem."}'
            )

        result = rewrite_generated_description(
            brand="Chanel",
            theme="salon released toward the shore",
            description="A muted grey tailored suit with pale shoes.",
            generate_text=generate_text,
        )
        self.assertEqual(len(seen), 3)
        self.assertEqual(result["model"], "gpt-5.4-mini")
        self.assertEqual(
            result["description"],
            "A muted grey Chanel day suit with a chain along the jacket hem.",
        )
        self.assertEqual(result["kept"], ["weight the jacket hem with a chain"])

    def test_missing_brand_theme_or_text_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            rewrite_generated_description(brand="", theme="shore", description="A coat.")

    def test_unknown_brand_keeps_the_description(self) -> None:
        def generate_text(**_kwargs):
            raise AssertionError("the model should not be called")

        result = rewrite_generated_description(
            brand="Acme Atelier",
            theme="shore",
            description="A navy coat.",
            generate_text=generate_text,
        )
        self.assertEqual(result["description"], "A navy coat.")
        self.assertEqual(result["skipped"], "no habit card for this brand")


if __name__ == "__main__":
    unittest.main()
