# Text Evaluation Report

- **Source:** 72_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__072_media_cha_biarritz_ps27_071_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.8883 (Strong)
- **Coverage axis:** 0.9375
- **Quality axis (raw / base / penalized):** 0.8654 / 0.875 / 0.875
- **Penalties (mean):** 0.1
- **R_content:** 0.857209

## Gates

- Score gate: 0.8883 (threshold 0.7) → **PASS**
- Penalty gate: 0.1 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `asymmetry` | 1.0 | 1 |  | Asymmetry is explicitly described through the cascade and panel arrangement. |
| `body_coverage` | 1.0 | 1 |  | The text describes exposed upper chest and bare arms, making body coverage salient. |
| `color_relationship_logic` | 1.0 | 1 |  | The text explains the color logic as a monochrome-like newspaper print with light base tones and black graphic/text contrast. |
| `construction_technique` | 1.0 | 1 |  | A clear construction technique is described, with sculptural ruffles/folded panels and their placement on the front of the skirt. |
| `fabric_family` | 0.0 | 0 |  | The text identifies the garment and print, but does not specify a clear fabric family such as silk, chiffon, satin, or tulle. |
| `garment_category` | 1.0 | 1 |  | The main garment category is explicitly identified as an evening gown. |
| `jewelry` | 1.0 | 1 |  | Earrings are explicitly mentioned as visible and salient body adornment. |
| `layering` | 1.0 | 1 |  | The gown clearly describes layered garment relations with an underskirt and overskirt panels, making the layering visually imageable. |
| `length_hemline` | 1.0 | 1 |  | Length and hem behavior are explicitly stated. |
| `pattern_type` | 1.0 | 1 |  | The pattern type is clearly identified as newspaper print with text and graphic blocks. |
| `primary_color` | 1.0 | 1 |  | The main color palette is clearly stated, with pale grey/off-white as the dominant light base and black as the key contrast. |
| `secondary_color` | 1.0 | 1 |  | A secondary dark color is clearly present as part of the gown’s palette and print contrast. |
| `shoulder_architecture` | 1.0 | 1 |  | The shoulder/upper-body structure is clearly specified through sleeveless construction and broad straps. |
| `silhouette` | 1.0 | 1 |  | The text clearly describes the overall shape and structural contour. |
| `surface_finish` | 1.0 | 1 |  | The description gives surface/handling cues indicating a structured, stiffened quality rather than a soft drape. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly states the upper body is fitted while the lower portion is voluminous, giving a readable top-bottom proportion and silhouette balance. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are clearly tied to the gown or earrings, and the text keeps the garment structure coherent. Minor ambiguity remains in phrases like “feather-like or brushstroke motif,” but this does  |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is densely packed with visible garment facts and construction details, with little mood prose. It is somewhat long and layered, but the main dress information remains dominant and usab |
| `craft_embellishment_salience` | 1.0 | 1 | 工艺装饰显著度 | The craft details are specific, located, and visually functional: appliqué at the bodice center and sculptural ruffles/panels shaping the skirt. |
| `design_distinctiveness` | 1.0 | 1 | 设计独特性 | The look has multiple clear memory points: unusual newspaper-print fabric, a strong bust motif, and an asymmetric sculptural ruffle construction. |
| `design_signal_purity` | 1.0 | 1 | 设计信号纯度 | The text is dominated by concrete design facts, materials, placement, and structure, with only minimal styling commentary. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly imageable and organized around visible silhouette, garment type, and layered construction, so it is close to prompt-ready. It is slightly more descriptive than direct prompt languag |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description generally moves from overall garment to bodice, waist/skirt structure, then styling details, so the hierarchy is easy to reconstruct. There is some density and a few layered clauses, b |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The description distinguishes bodice, skirt, and earrings cleanly, with accessories separated from the trunk garment. There is no major cross-binding between the gown’s parts, though some decorative e |
| `reference_clarity` | 1.0 | 1 | 语言清晰度 | References are clear and stable throughout; pronouns and omitted subjects do not create ambiguity, and the garment descriptions remain consistently anchored. |
| `silhouette_combination_originality` | 1.0 | 1 | 组合原创性 | The combination of a fitted sleeveless bodice, architectural fullness, and asymmetric sculptural skirt treatment is distinctive and not a standard formula template. |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and attachment relationships are clearly described and visually reconstructable. The only minor limitation is that the dense surface description makes the garment slightly more interpretive t |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | The text prioritizes the gown’s visible silhouette, print, and surface treatment. It also clearly notes low-visibility items and absence of bag/footwear, but these do not overwhelm the main outfit des |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is tightly anchored to visible garment zones and clearly distinguishes visible from not visible details, with little mood prose. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | The gown reads as a single coherent silhouette with no trunk-level left-right conflict or mutually exclusive garment identities. |
| `coordination_penalty` | 0.0 | The asymmetry is integrated into one couture language and does not create a coordination conflict across main garment parts. |
| `formula_template_penalty` | 0.25 | The description is somewhat formulaic in fashion-prompt terms, but it remains specific and craft-grounded rather than a generic interchangeable template. |
| `generation_content_penalty` | 0.25 | Mostly grounded garment description, but the styling note and accessory emphasis add a small amount of non-essential prompt content. |
| `rationality_penalty` | 0.0 | The materials and construction are stylized but physically plausible for couture dressmaking. |

## Missing coverage (未覆盖)

- **`fabric_family`** — The text identifies the garment and print, but does not specify a clear fabric family such as silk, chiffon, satin, or tulle.

## Skipped metrics (不适用)

- `closure` (coverage_score) — No explicit closure detail such as buttons, zipper, ties, or buckles is mentioned.
- `functional_detail` (coverage_score) — The text does not describe pockets, straps as functional hardware, or other utility details.
- `deconstruction` (coverage_score) — The text does not explicitly mention deconstruction, splicing, displacement, or reconstruction.
- `hardware_embellishment` (coverage_score) — No salient hardware or metal embellishment such as chains, studs, rings, or crystals is described.
- `bag` (coverage_score) — The text explicitly says there is "no bag" visible, so this metric does not apply.
- `footwear` (coverage_score) — Footwear is not visually present; the text says the hem "mostly concealing the feet" and "no ... footwear is visible."
- `belt` (coverage_score) — No visible belt, sash, waist strap, or harness is described; the waist shaping comes from the gown's cut and silhouette.
- `cross_garment_binding` (coverage_score) — Only one main garment is described, with accessories noted separately; there is no multi-garment attribute binding to judge.
- `quantity_accuracy` (quality_score) — The text does not use explicit counts or quantity relations that need verification.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral differences are described.
- `gender_expression` (bonus_score) — No explicit gender expression or androgyny is mentioned.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is explicitly stated beyond the garment description.
- `brand_alignment` (bonus_score) — No brand identity or brand-language target is mentioned.
