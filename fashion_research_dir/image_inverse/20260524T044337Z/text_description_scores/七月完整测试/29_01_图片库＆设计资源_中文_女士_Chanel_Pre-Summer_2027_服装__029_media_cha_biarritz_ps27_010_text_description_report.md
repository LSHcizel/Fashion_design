# Text Evaluation Report

- **Source:** 29_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__029_media_cha_biarritz_ps27_010_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.8172 (Strong)
- **Coverage axis:** 1.0
- **Quality axis (raw / base / penalized):** 0.7679 / 0.7708 / 0.7708
- **Penalties (mean):** 0.15
- **R_content:** 0.774297

## Gates

- Score gate: 0.8172 (threshold 0.7) → **PASS**
- Penalty gate: 0.15 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `asymmetry` | 1.0 | 1 |  | The lower garment is explicitly asymmetrical through diagonal draping and a side/front slit. |
| `body_coverage` | 1.0 | 1 |  | The text clearly describes exposed body areas and coverage level. |
| `closure` | 1.0 | 1 |  | Clear closure details are described via buttons on the jacket and skirt area. |
| `color_relationship_logic` | 1.0 | 1 |  | The text explicitly explains the palette logic: monochrome base with gold and red accents, plus black underlayers against the textured outerwear. |
| `cross_garment_binding` | 1.0 | 1 |  | The description distinguishes which features belong to the outer layer, bra top, skirt, waistband/underlayer, and accessories, so the multi-garment relations are clearly assigned. |
| `fabric_family` | 1.0 | 1 |  | The main garment material family is clearly identified as tweed-like woven fabric. |
| `functional_detail` | 1.0 | 1 |  | The text explicitly mentions pockets/flaps and utility-oriented functional detailing. |
| `garment_category` | 1.0 | 1 |  | The text clearly names the main garment categories: outerwear, bra top, and skirt. |
| `hardware_embellishment` | 1.0 | 1 |  | Prominent metal hardware is clearly present and repeatedly noted. |
| `jewelry` | 1.0 | 1 |  | Salient jewelry is explicitly present and described. |
| `layering` | 1.0 | 1 |  | The text clearly describes layered garments and their visible order/relationship. |
| `length_hemline` | 1.0 | 1 |  | The text gives clear length and hem/slit information. |
| `primary_color` | 1.0 | 1 |  | Black is the dominant primary color, reinforced by the monochrome palette and black underlayers. |
| `secondary_color` | 1.0 | 1 |  | Secondary colors are clearly present, especially grey/white within the garment and red/gold as visible accents. |
| `shoulder_architecture` | 1.0 | 1 |  | Shoulder structure is explicitly stated through broad shoulders and a bra-style top. |
| `silhouette` | 1.0 | 1 |  | Overall shape and structural trend are explicitly described. |
| `surface_finish` | 1.0 | 1 |  | The text gives clear surface traits: nubby texture, woven structure, and draped/gathered handling. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes the overall upper-to-lower body balance and silhouette emphasis, including an oversized top layer, minimal underlayer, and a skirt with slit that shapes the proportion. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are bound to the correct garments, and the layering is understandable. There is only mild ambiguity around the skirt vs. skirt panel and the waistband/underlayer phrasing, but it does  |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is compact and heavily focused on visible garment facts, with clear trunk details and styling. There is some descriptive layering and interpretive phrasing, but no long essay or repeat |
| `craft_embellishment_salience` | 0.75 | 1 | 工艺装饰显著度 | The hardware is clearly located and visually described, but the craft language is still mostly hardware-level rather than a deeper construction or embellishment technique. |
| `design_distinctiveness` | 0.75 | 1 | 设计独特性 | The look has a clear memory point in the textured monochrome tweed-like outer layer plus diagonal wrap-skirt construction and prominent gold hardware. It is distinctive, though not highly avant-garde. |
| `design_signal_purity` | 1.0 | 1 | 设计信号纯度 | The text is dominated by concrete design facts—materials, structure, placement, and color relationships—with almost no essay-like or mood-diluting prose. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly visual, garment-specific, and already close to a generation prompt. It clearly states silhouette, layers, materials, colors, and key styling details. Minor reduction from 1.0 becaus |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a mostly natural top-to-bottom garment order and then moves to styling details, so the outfit can be reconstructed clearly. Minor compression and some repeated detail layering  |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text keeps the jacket, bra top, and skirt mostly distinct and correctly related. Minor uncertainty remains in the skirt/underlayer wording, but the multi-garment structure is still clear and usabl |
| `quantity_accuracy` | 0.75 | 1 | 语言清晰度 | Quantity language is generally clear and consistent, but terms like “multiple” and the layered garment descriptions leave slight ambiguity about exact counts and attachment relations. |
| `reference_clarity` | 0.75 | 1 | 语言清晰度 | References and layering are mostly well anchored, with clear antecedents for the outer layer, bra top, and bottom. Minor complexity comes from long chained descriptions, but pronoun and omission handl |
| `silhouette_combination_originality` | 0.5 | 0 | 组合原创性 | The combination is more specific than a basic formula, especially with the open oversized coat over a bra top and wrap-skirt panel, but it still reads as a fairly wearable luxury layering arrangement. |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and attachment relationships are mostly clear and imageable, with coherent inside/outside and front-side placement. Score is slightly below top because a few phrases remain ambiguous, such as |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | The text prioritizes visible, image-dominant elements like silhouette, exposure, texture, and hardware. Accessories and styling are present but secondary, and there is little hidden or low-visibility  |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly anchored in visible garment details and body zones, with clear layering and placement observations and very little mood-only language. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.25 | No strong trunk-level contradiction; only mild ambiguity in garment naming (jacket/coat, skirt/skirt panel) without clear conflicting identities. |
| `coordination_penalty` | 0.0 | The look is stylistically coherent: monochrome tweed, black underlayers, gold hardware, and red accents work together. |
| `formula_template_penalty` | 0.25 | Some formulaic runway prose and styling-summary phrasing are present, but the description still contains concrete craft and silhouette details. |
| `generation_content_penalty` | 0.25 | Mostly imageable garment description, but it includes runway-framing and styling-summary language that slightly dilutes prompt efficiency. |
| `rationality_penalty` | 0.0 | All described materials and construction are physically plausible as ordinary fashion wear. |

## Quality issues (质量短板)

- **`silhouette_combination_originality`** (score 0.5) — The combination is more specific than a basic formula, especially with the open oversized coat over a bra top and wrap-skirt panel, but it still reads as a fairly wearable luxury layering arrangement.

## Skipped metrics (不适用)

- `pattern_type` (coverage_score) — No distinct pattern or print is described; the text refers to texture and weave rather than a pattern type.
- `construction_technique` (coverage_score) — No specific construction technique like pleating, quilting, embroidery, or cutwork is clearly described.
- `deconstruction` (coverage_score) — The text does not mention deconstruction, splicing, displacement, or reconstruction.
- `bag` (coverage_score) — No bag is mentioned or visually implied as part of the look.
- `footwear` (coverage_score) — The text does not describe any footwear.
- `belt` (coverage_score) — No visible belt, sash, waist strap, or harness is described; the waist emphasis comes from garment cut and layering.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral garment differences are described.
- `cultural_reference` (bonus_score) — No cultural, historical, or brand-specific reference is provided.
- `gender_expression` (bonus_score) — The description does not explicitly discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is stated beyond the outfit description.
- `brand_alignment` (bonus_score) — There is no explicit brand language or brand identity target in the text.
- `negation_control` (bonus_score) — The text does not emphasize exclusions or absence of elements as a meaningful requirement.
