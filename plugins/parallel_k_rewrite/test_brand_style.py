"""品牌风格卡：解析到品牌才附上，主题仍以原文为准。"""

from __future__ import annotations

import re
import unittest

from plugins.parallel_k_rewrite.brand_style import brand_style_block, iter_style_houses, resolve_brand
from plugins.parallel_k_rewrite.k_candidate_generator import build_rewrite_user_prompt


class BrandStyleCardTests(unittest.TestCase):
    def test_every_indexed_house_has_an_operational_card(self) -> None:
        houses = list(iter_style_houses())
        self.assertGreaterEqual(len(houses), 30)
        for house in houses:
            card = brand_style_block(explicit=house)
            self.assertIn(f"House: {house}", card)
            self.assertIn("Silhouette:", card)
            self.assertIn("does not replace that theme", card)
            self.assertNotIn("Heritage & provenance", card)
            self.assertNotIn("Show / location context", card)
            self.assertNotIn("Creative director intent", card)
            facts = "\n".join(
                line
                for line in card.splitlines()
                if line.startswith(("Silhouette:", "Craft:", "Palette:", "Construction:"))
            )
            for line in facts.splitlines():
                if re.search(r"\b(logo|monogram|interlocking)\b", line, re.IGNORECASE):
                    self.assertRegex(line, r"\b(not|without|no)\b")

    def test_explicit_brand_wins_over_another_house_in_the_text(self) -> None:
        self.assertEqual(
            resolve_brand(explicit="Gucci", texts=["a Prada crystal skirt"]),
            "Gucci",
        )
        card = brand_style_block(explicit="gucci_ss27", texts=["a Prada crystal skirt"])
        self.assertIn("House: Gucci", card)
        self.assertNotIn("House: Prada", card)

    def test_aliases_and_design_target_resolve_when_workflow_brand_is_absent(self) -> None:
        self.assertEqual(resolve_brand(explicit="Hermes"), "Hermès")
        self.assertEqual(resolve_brand(explicit="YSL"), "Saint Laurent")
        self.assertEqual(resolve_brand(explicit="Chloé"), "Chloé")
        found = resolve_brand(
            texts=["Design a Bottega Veneta collection.", "a navy coat with no house name"]
        )
        self.assertEqual(found, "Bottega Veneta")
        card = brand_style_block(texts=["the intrecciato is Bottega Veneta's craft"])
        self.assertIn("House: Bottega Veneta", card)
        self.assertIn("Craft:", card)

    def test_ordinary_row_of_is_not_the_house(self) -> None:
        self.assertIsNone(resolve_brand(texts=["the row of buttons on a navy coat"]))
        self.assertEqual(resolve_brand(explicit="The Row"), "The Row")
        gucci = brand_style_block(explicit="Gucci")
        self.assertIn("Craft:", gucci)
        self.assertIn(" | ", gucci)
        self.assertNotIn("enlarged Trench", gucci)

    def test_unknown_or_absent_brand_skips_the_card(self) -> None:
        self.assertIsNone(resolve_brand(explicit="Acme Atelier", texts=["a navy trench"]))
        self.assertEqual(brand_style_block(texts=["a cropped navy jacket and beige shorts"]), "")
        self.assertEqual(brand_style_block(explicit="", texts=[""]), "")

    def test_design_target_is_read_before_a_stray_brand_in_the_look(self) -> None:
        found = resolve_brand(
            texts=[
                "Design a Chanel Cruise collection.",
                "A stray Gucci bit is named inside the defective look.",
            ]
        )
        self.assertEqual(found, "Chanel")

    def test_style_card_is_business_context_before_the_theme_lock(self) -> None:
        card = brand_style_block(explicit="Moschino")
        prompt = build_rewrite_user_prompt(
            "A smile-line clutch and matching pumps.",
            k=2,
            candidate_index=0,
            extra_context=card + "\nExtract the theme from SOURCE.",
        )
        self.assertLess(prompt.index("BRAND STYLE CARD"), prompt.index("THEME AND CONCEPT LOCK"))
        self.assertLess(prompt.index("House: Moschino"), prompt.index("THEME AND CONCEPT LOCK"))
        self.assertIn("does not replace that theme", prompt)
        self.assertIn("BRAND LOGO LOCK", prompt)

    def test_workflow_extra_context_puts_the_card_before_the_theme_lock(self) -> None:
        from fashion_workflow import FashionWorkflow

        wf = FashionWorkflow.__new__(FashionWorkflow)
        wf.brand = "Moschino"
        wf.design_target_prompt = "Design a Moschino collection"
        wf._current_sub_theme_name = "Smile"
        ctx = wf._rewrite_extra_context(None, source_text="A smile-line clutch.")
        self.assertLess(ctx.index("House: Moschino"), ctx.index("Extract theme and design concept"))
        self.assertLess(ctx.index("BRAND STYLE CARD"), ctx.index("THEME AND CONCEPT LOCK"))
        self.assertIn("When the card conflicts with the theme, keep the theme.", ctx)

        wf.brand = None
        wf.design_target_prompt = "A quiet tailored story with no house name."
        plain = wf._rewrite_extra_context(None, source_text="A navy jacket over beige shorts.")
        self.assertNotIn("House:", plain)


if __name__ == "__main__":
    unittest.main()
