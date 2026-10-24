"""品牌习惯卡不进入基于评分的质量改写。这里核对目录读取，以及品牌调性改写要先校验再改。"""

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
from plugins.brand_tone_rewriter.web_search import (
    collection_url,
    extract_review_snippet,
    interval_sample,
    is_vogue_url,
    look_image_urls,
    mentions_brand,
    parse_vogue_search_html,
    prefer_theme,
    select_brand_hits,
    vogue_query,
)
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
        self.assertLess(prompt.index("Chapter: Smile"), prompt.index("THEME AND CONCEPT"))

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
        self.assertLess(ctx.index("Chapter: Smile"), ctx.index("THEME AND CONCEPT"))


class SecondRewriterTests(unittest.TestCase):
    def test_both_conflicts_then_a_new_description(self) -> None:
        seen = []

        def generate_text(**kwargs):
            seen.append(kwargs["system_prompt"])
            self.assertEqual(kwargs["temperature"], 0)
            if len(seen) == 1:
                self.assertIn("opposite direction", kwargs["system_prompt"])
                self.assertIn("A muted grey tailored suit with pale shoes.", kwargs["user_prompt"])
                self.assertIn("soften the hem into a chain-weighted line", kwargs["user_prompt"])
                self.assertIn("a light cloth that moves", kwargs["user_prompt"])
                self.assertNotIn("concrete edit points", kwargs["system_prompt"])
                return (
                    '{"checks": ['
                    '{"source": "review", "stance": "soften the hem into a chain-weighted line", '
                    '"axis": "structure", "quote": "tailored suit", "status": "conflict"},'
                    '{"source": "image", "stance": "a light cloth that moves", '
                    '"axis": "surface", "quote": "pale shoes", "status": "conflict"}'
                    ']}'
                )
            if len(seen) == 2:
                self.assertIn("concrete edit points", kwargs["system_prompt"])
                self.assertIn("paired", kwargs["system_prompt"])
                self.assertIn("drop", kwargs["system_prompt"])
                self.assertIn("tailored suit", kwargs["user_prompt"])
                self.assertIn("pale shoes", kwargs["user_prompt"])
                self.assertIn("CONFIRMED CONFLICTS", kwargs["user_prompt"])
                return (
                    '{"points": ['
                    '{"edit": "weight the jacket hem with a chain", "pair": "a pale day shoe", "drop": "the plain hem"},'
                    '{"edit": "add a second evening gown", "pair": "bare shoulders", "drop": "the day suit"}'
                    ']}'
                )
            if len(seen) == 3:
                self.assertIn("abstract score", kwargs["system_prompt"])
                self.assertIn("ids 1, 2", kwargs["user_prompt"])
                self.assertNotIn("Write the description", kwargs["user_prompt"])
                return '{"scores": [{"ids": [1, 2], "score": 0.2}, {"ids": [2], "score": 0.3}, {"ids": [1], "score": 0.9}]}'
            self.assertIn("selected combination", kwargs["system_prompt"])
            self.assertIn("weight the jacket hem with a chain", kwargs["user_prompt"])
            self.assertNotIn("add a second evening gown", kwargs["user_prompt"])
            return '{"description": "A muted grey Chanel day suit with a chain along the jacket hem."}'

        result = rewrite_generated_description(
            brand="Chanel",
            theme="salon released toward the shore",
            description="A muted grey tailored suit with pale shoes.",
            generate_text=generate_text,
            habit_card=(
                "House: Chanel\nTheme: salon released toward the shore\n"
                "Review stances:\n- soften the hem into a chain-weighted line\n"
                "Image style:\n- a light cloth that moves"
            ),
        )
        self.assertEqual(len(seen), 4)
        self.assertEqual(result["model"], "gpt-5.4-mini")
        self.assertEqual(result["selected_ids"], [1])
        self.assertEqual(result["selected_score"], 0.9)
        self.assertEqual(
            result["description"],
            "A muted grey Chanel day suit with a chain along the jacket hem.",
        )
        self.assertEqual(result["kept"], ["weight the jacket hem with a chain"])
        self.assertEqual(result["dropped"], ["the plain hem"])
        self.assertEqual(result["card_source"], "provided")
        self.assertEqual(len(result["conflicts"]), 2)

    def test_missing_brand_theme_or_text_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            rewrite_generated_description(brand="", theme="shore", description="A coat.")

    def test_review_without_images_does_not_rewrite(self) -> None:
        def search_fn(brand, theme):
            self.assertEqual(brand, "Dior")
            self.assertEqual(theme, "a walk in the garden")
            return [
                {
                    "title": "Dior Bar jacket",
                    "url": "https://example.com/dior",
                    "snippet": "Dior shows a fitted navy wool Bar jacket with a peplum over a narrow skirt.",
                }
            ]

        def generate_text(**kwargs):
            self.assertIn("You read one show review", kwargs["system_prompt"])
            self.assertIn("Bar jacket", kwargs["user_prompt"])
            self.assertNotIn("A grey coat.", kwargs["user_prompt"])
            self.assertNotIn("Heritage & provenance", kwargs["user_prompt"])
            return '{"stances": ["soften tailoring into a promenade line"]}'

        result = rewrite_generated_description(
            brand="Dior",
            theme="a walk in the garden",
            description="A grey coat.",
            generate_text=generate_text,
            search_fn=search_fn,
        )
        self.assertEqual(result["card_source"], "web")
        self.assertIn("soften tailoring into a promenade line", result["habit_card"])
        self.assertNotIn("A grey coat.", result["habit_card"])
        self.assertEqual(result["retrieved"][0]["url"], "https://example.com/dior")
        self.assertEqual(result["description"], "A grey coat.")
        self.assertEqual(result["skipped"], "no reference")
        self.assertEqual(result["conflicts"], [])

    def test_empty_search_keeps_the_description(self) -> None:
        def generate_text(**_kwargs):
            raise AssertionError("empty search must not invent a tone card")

        result = rewrite_generated_description(
            brand="Acme Atelier",
            theme="shore",
            description="A navy coat.",
            generate_text=generate_text,
            search_fn=lambda _brand, _theme: [],
        )
        self.assertEqual(result["card_source"], "")
        self.assertEqual(result["habit_card"], "")
        self.assertEqual(result["retrieved"], [])
        self.assertEqual(result["description"], "A navy coat.")
        self.assertEqual(result["skipped"], "no reference")

    def test_both_conflicts_from_review_and_images_rewrite(self) -> None:
        images = [
            "https://assets.vogue.com/photos/aaaaaaaaaaaaaaaaaaaaaaaa/master/w_640,c_limit/1.jpg",
            "https://assets.vogue.com/photos/bbbbbbbbbbbbbbbbbbbbbbbb/master/w_640,c_limit/2.jpg",
        ]
        description = "A grey coat with a straight hem."

        def search_fn(brand, theme):
            self.assertEqual(brand, "Dior")
            return [
                {
                    "title": "Christian Dior",
                    "url": "https://www.vogue.com/fashion-shows/fall-2026-ready-to-wear/christian-dior",
                    "snippet": "Dior shows a fitted navy wool Bar jacket with a peplum over a narrow skirt.",
                    "images": images,
                }
            ]

        def generate_multimodal(**kwargs):
            self.assertEqual(kwargs["temperature"], 0)
            self.assertIn("evenly spaced runway photographs", kwargs["system_prompt"])
            text = kwargs["user_content"][0]["text"]
            self.assertNotIn("Bar jacket", text)
            self.assertIn("evenly spaced looks", text)
            self.assertNotIn(description, text)
            self.assertEqual(
                [part["image_url"]["url"] for part in kwargs["user_content"][1:]],
                images,
            )
            return '{"styles": ["let the hem trail while the cloth stays light"]}'

        def generate_text(**kwargs):
            system = kwargs["system_prompt"]
            if "You read one show review" in system:
                self.assertIn("Bar jacket", kwargs["user_prompt"])
                self.assertNotIn(description, kwargs["user_prompt"])
                return '{"stances": ["soften tailoring into a promenade line"]}'
            if "You compare one generated description" in system:
                self.assertIn(description, kwargs["user_prompt"])
                self.assertIn("soften tailoring into a promenade line", kwargs["user_prompt"])
                self.assertIn("let the hem trail while the cloth stays light", kwargs["user_prompt"])
                return (
                    '{"checks": ['
                    '{"source": "review", "stance": "soften tailoring into a promenade line", '
                    '"axis": "structure", "quote": "straight hem", "status": "conflict"},'
                    '{"source": "image", "stance": "let the hem trail while the cloth stays light", '
                    '"axis": "volume", "quote": "grey coat", "status": "conflict"}'
                    ']}'
                )
            if "concrete edit points" in system:
                self.assertIn("straight hem", kwargs["user_prompt"])
                self.assertIn("let the hem trail", kwargs["user_prompt"])
                self.assertIn(description, kwargs["user_prompt"])
                return (
                    '{"points": [{"edit": "trail the hem", '
                    '"pair": "a light cloth", "drop": "the straight hem"}]}'
                )
            if "abstract score" in system:
                return '{"scores": [{"ids": [1], "score": 0.9}]}'
            return '{"description": "A light coat with a trailing hem."}'

        result = rewrite_generated_description(
            brand="Dior",
            theme="a walk in the garden",
            description=description,
            generate_text=generate_text,
            generate_multimodal=generate_multimodal,
            search_fn=search_fn,
        )
        self.assertEqual(result["card_source"], "web_images")
        self.assertEqual(result["retrieved"][0]["images"], images)
        self.assertIn("let the hem trail", result["habit_card"])
        self.assertIn("soften tailoring into a promenade line", result["habit_card"])
        self.assertNotIn(description, result["habit_card"])
        self.assertEqual(result["description"], "A light coat with a trailing hem.")
        self.assertEqual([item["source"] for item in result["conflicts"]], ["review", "image"])

    def test_one_sided_conflict_rewrites(self) -> None:
        description = "A grey coat with a straight hem."

        def generate_multimodal(**_kwargs):
            return '{"styles": ["let the hem trail while the cloth stays light"]}'

        def generate_text(**kwargs):
            system = kwargs["system_prompt"]
            if "You read one show review" in system:
                return '{"stances": ["soften tailoring into a promenade line"]}'
            if "You compare one generated description" in system:
                return (
                    '{"checks": ['
                    '{"source": "review", "stance": "soften tailoring into a promenade line", '
                    '"axis": "structure", "quote": "straight hem", "status": "conflict"},'
                    '{"source": "image", "stance": "let the hem trail while the cloth stays light", '
                    '"axis": "volume", "quote": "grey coat", "status": "carried"}'
                    ']}'
                )
            if "concrete edit points" in system:
                self.assertIn("straight hem", kwargs["user_prompt"])
                self.assertIn("CARRIED, DO NOT CHANGE", kwargs["user_prompt"])
                return (
                    '{"points": [{"edit": "soften the hem", '
                    '"pair": "a light promenade cloth", "drop": "the straight hem"}]}'
                )
            if "abstract score" in system:
                return '{"scores": [{"ids": [1], "score": 0.8}]}'
            self.assertIn("soften the hem", kwargs["user_prompt"])
            return '{"description": "A grey coat with a softened hem."}'

        result = rewrite_generated_description(
            brand="Dior",
            theme="a walk in the garden",
            description=description,
            generate_text=generate_text,
            generate_multimodal=generate_multimodal,
            search_fn=lambda _brand, _theme: [
                {
                    "title": "Dior",
                    "url": "https://example.com/dior",
                    "snippet": "Dior shows a fitted navy wool Bar jacket.",
                    "images": ["https://assets.example/1.jpg"],
                }
            ],
        )
        self.assertEqual(result["description"], "A grey coat with a softened hem.")
        self.assertNotIn("skipped", result)
        self.assertEqual([item["source"] for item in result["conflicts"]], ["review"])
        self.assertEqual(result["checks"][0]["status"], "conflict")
        self.assertEqual(result["checks"][1]["status"], "carried")

    def test_invented_quote_is_not_a_conflict(self) -> None:
        description = "A grey coat."

        def generate_multimodal(**_kwargs):
            return '{"styles": ["let the hem trail while the cloth stays light"]}'

        def generate_text(**kwargs):
            system = kwargs["system_prompt"]
            if "You read one show review" in system:
                return '{"stances": ["soften tailoring into a promenade line"]}'
            if "You compare one generated description" in system:
                return (
                    '{"checks": ['
                    '{"source": "review", "stance": "soften tailoring into a promenade line", '
                    '"axis": "structure", "quote": "stiff wool", "status": "conflict"},'
                    '{"source": "image", "stance": "let the hem trail while the cloth stays light", '
                    '"axis": "volume", "quote": "grey coat", "status": "conflict"}'
                    ']}'
                )
            if "concrete edit points" in system:
                self.assertNotIn("stiff wool", kwargs["user_prompt"])
                self.assertIn("grey coat", kwargs["user_prompt"])
                return (
                    '{"points": [{"edit": "let the cloth trail", '
                    '"pair": "the grey coat", "drop": "a fixed hem"}]}'
                )
            if "abstract score" in system:
                return '{"scores": [{"ids": [1], "score": 0.7}]}'
            return '{"description": "A grey coat with a trailing cloth."}'

        result = rewrite_generated_description(
            brand="Dior",
            theme="a walk in the garden",
            description=description,
            generate_text=generate_text,
            generate_multimodal=generate_multimodal,
            search_fn=lambda _brand, _theme: [
                {
                    "title": "Dior",
                    "url": "https://example.com/dior",
                    "snippet": "Dior shows a fitted navy wool Bar jacket.",
                    "images": ["https://assets.example/1.jpg"],
                }
            ],
        )
        self.assertEqual(result["description"], "A grey coat with a trailing cloth.")
        self.assertNotIn("skipped", result)
        self.assertEqual(result["checks"][0]["status"], "absent")
        self.assertEqual(result["checks"][0]["quote"], "")
        self.assertEqual(result["checks"][1]["status"], "conflict")
        self.assertEqual([item["quote"] for item in result["conflicts"]], ["grey coat"])

    def test_image_call_failure_keeps_the_description(self) -> None:
        def generate_multimodal(**_kwargs):
            raise RuntimeError("vision unavailable")

        def generate_text(**kwargs):
            self.assertIn("You read one show review", kwargs["system_prompt"])
            self.assertIn("Bar jacket", kwargs["user_prompt"])
            self.assertNotIn("A grey coat.", kwargs["user_prompt"])
            return '{"stances": ["soften tailoring into a promenade line"]}'

        result = rewrite_generated_description(
            brand="Dior",
            theme="a walk in the garden",
            description="A grey coat.",
            generate_text=generate_text,
            generate_multimodal=generate_multimodal,
            search_fn=lambda _brand, _theme: [
                {
                    "title": "Dior",
                    "url": "https://example.com/dior",
                    "snippet": "Dior shows a fitted navy wool Bar jacket.",
                    "images": ["https://assets.example/1.jpg"],
                }
            ],
        )
        self.assertEqual(result["card_source"], "web")
        self.assertIn("soften tailoring into a promenade line", result["habit_card"])
        self.assertEqual(result["description"], "A grey coat.")
        self.assertEqual(result["skipped"], "no reference")
        self.assertEqual(result["image_styles"], [])

    def test_empty_review_stance_keeps_the_description(self) -> None:
        def generate_text(**kwargs):
            self.assertIn("You read one show review", kwargs["system_prompt"])
            self.assertNotIn("A navy coat.", kwargs["user_prompt"])
            return '{"stances": []}'

        result = rewrite_generated_description(
            brand="Acme Atelier",
            theme="shore",
            description="A navy coat.",
            generate_text=generate_text,
            search_fn=lambda _brand, _theme: [
                {
                    "title": "Acme",
                    "url": "https://example.com/acme",
                    "snippet": "Acme shows a straight navy coat.",
                }
            ],
        )
        self.assertEqual(result["description"], "A navy coat.")
        self.assertEqual(result["skipped"], "no reference")
        self.assertEqual(result["card_source"], "")
        self.assertEqual(result["retrieved"][0]["url"], "https://example.com/acme")


class WebSearchParseTests(unittest.TestCase):
    def test_parse_keeps_only_the_named_brand(self) -> None:
        page = """
        <div data-item="{&quot;dangerousHed&quot;:&quot;Christian Dior&quot;,&quot;hotelLink&quot;:&quot;/fashion-shows/fall-2026-ready-to-wear/christian-dior&quot;}"></div>
        <div data-item="{&quot;dangerousHed&quot;:&quot;Christian Dior&quot;,&quot;hotelLink&quot;:&quot;/fashion-shows/fall-2026-couture/christian-dior&quot;}"></div>
        <div data-item="{&quot;dangerousHed&quot;:&quot;Prada&quot;,&quot;hotelLink&quot;:&quot;/fashion-shows/fall-2026-ready-to-wear/prada&quot;}"></div>
        """
        hits = parse_vogue_search_html(page)
        self.assertEqual(len(hits), 3)
        kept = select_brand_hits("Dior", hits)
        self.assertEqual(len(kept), 2)
        ranked = prefer_theme("Fall 2026 ready-to-wear promenade in the Tuileries", kept)
        self.assertIn("fall-2026-ready-to-wear", ranked[0]["url"])
        self.assertTrue(mentions_brand("Dior", ranked[0]["title"] + ranked[0]["url"]))
        self.assertTrue(is_vogue_url(ranked[0]["url"]))
        self.assertFalse(mentions_brand("Dior", "Prada shows a crystal skirt."))
        self.assertTrue(
            is_vogue_url("https://duckduckgo.com/l/?uddg=" + "https%3A%2F%2Fwww.vogue.com%2Ffashion-shows%2Fchristian-dior")
        )
        self.assertFalse(is_vogue_url("https://www.vogue.com.evil.example/dior"))
        snippet = extract_review_snippet(
            '<div class="RunwayShowReviewContent-x"><p class="body">Dior shows a fitted navy wool Bar jacket with a peplum over a narrow skirt.</p></div>'
        )
        self.assertIn("Bar jacket", snippet)
        self.assertEqual(
            vogue_query("Dior", "Fall 2026 ready-to-wear promenade: dressing up to walk in the Tuileries"),
            "Dior Fall 2026 ready-to-wear",
        )
        show = "https://www.vogue.com/fashion-shows/fall-2026-ready-to-wear/christian-dior"
        self.assertEqual(collection_url(show), show + "/slideshow/collection")
        page = """
        https://assets.vogue.com/photos/aaaaaaaaaaaaaaaaaaaaaaaa/master/w_640,c_limit/00002-christian-dior-fall-2026-ready-to-wear-credit-gorunway.jpg
        https://assets.vogue.com/photos/bbbbbbbbbbbbbbbbbbbbbbbb/master/pass/00001-christian-dior-fall-2026-ready-to-wear-credit-gorunway.jpg
        https://assets.vogue.com/photos/cccccccccccccccccccccccc/master/w_640,c_limit/00003-christian-dior-fall-2026-ready-to-wear-detail-credit-gorunway.jpg
        https://assets.vogue.com/photos/dddddddddddddddddddddddd/master/w_640,c_limit/00001-christian-dior-spring-2026-couture-credit-gorunway.jpg
        """
        looks = look_image_urls(page, show)
        self.assertEqual(
            [item.rsplit("/", 1)[-1][:5] for item in looks],
            ["00001", "00002"],
        )
        gallery = [f"{index:05d}" for index in range(1, 67)]
        sampled = interval_sample(gallery, 6)
        self.assertEqual(sampled, ["00001", "00014", "00027", "00039", "00052", "00065"])
        self.assertNotIn("00066", sampled)


if __name__ == "__main__":
    unittest.main()
