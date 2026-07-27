# Text Evaluation Report

- **Source:** 13_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__013_media_cha_biarritz_ps27_038_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.8669 (Strong)
- **Coverage axis:** 1.0
- **Quality axis (raw / base / penalized):** 0.8393 / 0.8333 / 0.8333
- **Penalties (mean):** 0.1
- **R_content:** 0.836558

## Gates

- Score gate: 0.8669 (threshold 0.7) → **PASS**
- Penalty gate: 0.1 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `bag` | 1.0 | 1 |  | Bag type and carry style are explicit, and the structured shape plus black finish are clearly described. |
| `body_coverage` | 1.0 | 1 |  | The text clearly describes exposed coverage at the arms and chest/neckline area. |
| `closure` | 1.0 | 1 |  | A clear front fastening is described via buttons. |
| `color_relationship_logic` | 1.0 | 1 |  | The text explains the color logic as contrast and clash between the beige-gold suit, dark/orange trim, and graphic striped underlayer. |
| `cross_garment_binding` | 1.0 | 1 |  | The description distinguishes multiple garments and assigns their attributes clearly to each item, making the cross-garment relationships readable. |
| `deconstruction` | 1.0 | 1 |  | The description explicitly frames the look as deconstructed. |
| `fabric_family` | 1.0 | 1 |  | The main garment material family is clearly indicated as tweed-like. |
| `garment_category` | 1.0 | 1 |  | The text clearly identifies the main garment category as a tailored skirt suit with jacket and skirt. |
| `hardware_embellishment` | 1.0 | 1 |  | Prominent metallic embellishment is clearly present. |
| `jewelry` | 1.0 | 1 |  | A prominent necklace is explicitly described as a salient accessory. |
| `layering` | 1.0 | 1 |  | The text clearly describes a layered outfit with an outer jacket over an inner top, making the layering relationship imageable. |
| `length_hemline` | 1.0 | 1 |  | The description states both jacket length and skirt extent/hem visibility. |
| `pattern_type` | 1.0 | 1 |  | Pattern types are clearly identified: flecked tweed texture and striped patterning. |
| `primary_color` | 1.0 | 1 |  | The dominant suit color is clearly beige-gold with golden-yellow tones. |
| `secondary_color` | 1.0 | 1 |  | Secondary colors are explicitly described, including dark trim, orange edging, and the striped top’s black/white/cream palette. |
| `shoulder_architecture` | 1.0 | 1 |  | The shoulder structure is explicitly emphasized. |
| `silhouette` | 1.0 | 1 |  | It gives explicit structural shape information for both the jacket and skirt. |
| `surface_finish` | 1.0 | 1 |  | The text gives clear surface traits: nubby texture and raw/frayed edges. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes the upper and lower proportions, including waist placement and the relative cropped length of the jacket versus the skirt silhouette. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are clearly attached to the correct garment or accessory, and the layering is understandable. Minor ambiguity remains in phrases like “elongated lapel or scarf extensions” and “small s |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is packed with visible garment facts and mostly stays on silhouette, texture, trim, and accessories. There is some stylistic framing and mood language, but it does not overwhelm the co |
| `craft_embellishment_salience` | 0.75 | 1 | 工艺装饰显著度 | The craft details are clear and well located, especially the raw edges and trim, though the description is still more observational than deeply craft-analytic. |
| `design_distinctiveness` | 1.0 | 1 | 设计独特性 | The look has multiple clear memory points: raw edging, vivid contrast trim, and a mixed-print striped underlayer. These are specific and non-formula. |
| `design_signal_purity` | 1.0 | 1 | 设计信号纯度 | The text is dominated by concrete design facts, with only one brief mood sentence at the end. Design signal remains primary. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly visual and mostly prompt-ready, with clear garment types, silhouette, layering, texture, and accessories. It reads slightly like a descriptive analysis rather than a compact generat |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a mostly natural subject-to-detail order: overall look, jacket, underlayer, skirt, then accessories/styling. Minor compression and dense modifier stacking reduce ease slightly, |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text distinguishes jacket, top, skirt, necklace, head covering, nails, and handbag with mostly stable bindings. There is slight fuzziness around the underlayer’s side patterning and the jacket-fro |
| `quantity_accuracy` | 1.0 | 1 | 语言清晰度 | The text uses quantities and part counts in a stable, non-conflicting way; references are internally consistent and easy to parse. |
| `reference_clarity` | 1.0 | 1 | 语言清晰度 | Antecedents are explicit and the sentence chain stays clear, with no confusing pronouns or ambiguous omissions. |
| `silhouette_combination_originality` | 0.75 | 1 | 组合原创性 | The combination is specific and somewhat unusual, with a boxy cropped jacket over a graphic vest-like top and a close skirt. It is not a standard formula template, though it remains within a tailored  |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and attachment relationships are clearly described and imageable. The only slight weakness is that some elements are interpretive (“like elongated lapel or scarf extensions”), but the overall |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | The text prioritizes highly visible, image-dominant details such as shape, texture, trim, and accessories. It includes a small amount of interpretive mood language, but the visible clothing descriptio |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly anchored in visible garment parts and placement, with clear layering and construction observations rather than mood prose. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | The outfit reads as one coherent suit with no trunk-level left-right or garment-identity conflict. |
| `coordination_penalty` | 0.0 | The styling elements are coordinated into a single deconstructed tailored language rather than conflicting on the main garments. |
| `formula_template_penalty` | 0.25 | Some runway-essay framing and mood language are present, but the description remains grounded in specific craft details and is not strongly formulaic. |
| `generation_content_penalty` | 0.25 | Mostly concrete garment description, but ends with evaluative mood language that slightly dilutes prompt efficiency. |
| `rationality_penalty` | 0.0 | No physically implausible materials or wear constructions are asserted as ordinary facts. |

## Skipped metrics (不适用)

- `functional_detail` (coverage_score) — No salient pockets, straps, or utility features are described.
- `construction_technique` (coverage_score) — The text mentions texture and raw edges, but not a specific named construction technique with a clear garment zone.
- `footwear` (coverage_score) — No footwear is mentioned in the text.
- `belt` (coverage_score) — No visible belt, sash, or waist strap is described; the waist emphasis comes from garment cut.
- `asymmetry` (coverage_score) — No clear asymmetrical design, one-shoulder, uneven hem, or similar structure is described.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral differences are described.
- `cultural_reference` (bonus_score) — No specific cultural, historical, or brand reference is grounded in the description.
- `gender_expression` (bonus_score) — The text does not explicitly discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is explicitly stated.
- `brand_alignment` (bonus_score) — The description does not explicitly target a brand identity or brand language.
- `negation_control` (bonus_score) — The text does not emphasize exclusions or absence of elements.
