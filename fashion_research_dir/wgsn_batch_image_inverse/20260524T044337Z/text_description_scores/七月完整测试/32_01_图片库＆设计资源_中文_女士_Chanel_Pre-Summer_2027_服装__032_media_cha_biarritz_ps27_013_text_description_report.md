# Text Evaluation Report

- **Source:** 32_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__032_media_cha_biarritz_ps27_013_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.8847 (Strong)
- **Coverage axis:** 1.0
- **Quality axis (raw / base / penalized):** 0.8654 / 0.8542 / 0.8542
- **Penalties (mean):** 0.1
- **R_content:** 0.853735

## Gates

- Score gate: 0.8847 (threshold 0.7) → **PASS**
- Penalty gate: 0.1 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `color_relationship_logic` | 1.0 | 1 |  | The text explains the color logic through contrast between the cream base and black stripes, plus a multicolor graphic print on the skirt. |
| `construction_technique` | 1.0 | 1 |  | The text names specific construction techniques and their placement on the skirt body and hem. |
| `cross_garment_binding` | 1.0 | 1 |  | Multiple garments are clearly distinguished and their attributes are assigned to the correct item, showing clear cross-garment binding. |
| `fabric_family` | 1.0 | 1 |  | The main fabric family is clearly identified as knit for the top; the skirt’s fringe also indicates a textile construction, though the primary material category is only explicit for the top. |
| `footwear` | 1.0 | 1 |  | Footwear type and key visual features are clearly specified. |
| `functional_detail` | 1.0 | 1 |  | Visible pockets are a clear functional detail. |
| `garment_category` | 1.0 | 1 |  | The text clearly names the main garment categories: skirt, top, and shoes. |
| `layering` | 1.0 | 1 |  | The outfit includes a clear top-over-skirt styling relation, with the top’s placement at the waist described. |
| `length_hemline` | 1.0 | 1 |  | The skirt length and hem treatment are clearly stated. |
| `pattern_type` | 1.0 | 1 |  | Pattern types are clearly specified: horizontal stripes on the top and an abstract graphic floral/butterfly-like print on the skirt. |
| `primary_color` | 1.0 | 1 |  | Cream functions as the dominant base color of the top and overall look, with black as a strong recurring anchor. |
| `secondary_color` | 1.0 | 1 |  | Secondary colors are clearly present and integrated into the outfit through stripes and skirt motifs, not as isolated color mentions. |
| `silhouette` | 1.0 | 1 |  | The overall shape and structural contour of the outfit are explicitly described. |
| `surface_finish` | 1.0 | 1 |  | The text gives clear surface/structure traits such as pleating, gathered volume, and heavy fringe texture, which support a readable finish and drape/stiffness impression. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes the upper-lower proportion and waist emphasis, with a cropped/full-body look, high waist, and a voluminous skirt balanced by a shorter top. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 1.0 | 1 | 属性绑定准确度 | Attributes are consistently attached to the correct garments and accessories, with clear separation between top, skirt, and shoes. |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is compact and heavily focused on visible garment facts, with clear trunk-first organization. There is some stylistic elaboration, but no essay-like drift or repeated mood framing, so  |
| `craft_embellishment_salience` | 0.75 | 1 | 工艺装饰显著度 | The fringe is a salient craft/detail feature with clear placement at the hem, and the graphic surface treatment is also specific. The craft is strong, though not described with fully technical constru |
| `design_distinctiveness` | 1.0 | 1 | 设计独特性 | The look has multiple clear memory points: graphic panel-like skirt surface, heavy layered fringe, and contrasting toe-cap pumps. These are non-formula and visually distinctive. |
| `design_signal_purity` | 1.0 | 1 | 设计信号纯度 | The text is dominated by concrete design facts, materials, shapes, and placements, with essentially no mood essay or identity framing. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly visual, garment-specific, and mostly prompt-ready, with clear silhouette, layering, color, and footwear details. It reads slightly like a design description rather than a fully comp |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a mostly natural order from main silhouette to garment details, then surface pattern, hem treatment, and footwear. It is clear and easy to reconstruct, though some detail clust |
| `multi_garment_binding` | 1.0 | 1 | 属性绑定准确度 | Multiple garments are described with their own colors, structures, and details, and the bindings remain stable without cross-item confusion. |
| `reference_clarity` | 1.0 | 1 | 语言清晰度 | References are consistently anchored to clear antecedents (top, skirt, wearer’s hands), and the description remains easy to parse without ambiguous pronoun or object shifts. |
| `silhouette_combination_originality` | 0.75 | 1 | 组合原创性 | The combination is more distinctive than a standard formula because the dramatic skirt, striped knit top, and toe-cap pumps create a strong graphic contrast. Some elements remain familiar, so it is no |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and attachment relationships are clear and visually imageable, including waist placement, pockets, and hem treatment. The spatial logic is coherent and easy to render, with only minor descrip |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | The text prioritizes highly visible, image-dominant elements such as silhouette, pattern, hem texture, and shoes. It includes a few interpretive phrases like “casual contrast” and “polished but playfu |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly anchored in visible garment parts and placement, with precise observations of waistband, pockets, hem treatment, and shoe details. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | No trunk-level left-right or garment-identity conflicts; the top, skirt, and shoes read coherently. |
| `coordination_penalty` | 0.0 | The casual knit top, graphic skirt, and pumps are stylistically coordinated into one readable look. |
| `formula_template_penalty` | 0.25 | A fairly standard top + skirt + pumps outfit formula, but still grounded by specific skirt surface and hem details rather than being fully generic. |
| `generation_content_penalty` | 0.25 | Mostly imageable garment description, but includes some evaluative styling language that slightly reduces prompt efficiency. |
| `rationality_penalty` | 0.0 | All described materials and construction details are physically plausible as ordinary fashion wear. |

## Skipped metrics (不适用)

- `shoulder_architecture` (coverage_score) — No salient shoulder construction is described; the top only mentions sleeves pushed up.
- `body_coverage` (coverage_score) — The text does not describe notable skin exposure, cutouts, or reveal-focused coverage.
- `closure` (coverage_score) — No explicit closure detail such as buttons, zipper, ties, or buckle is mentioned.
- `deconstruction` (coverage_score) — The description does not mention deconstruction, splicing, displacement, or reconstruction.
- `hardware_embellishment` (coverage_score) — No salient hardware or metallic embellishment such as chains, studs, rings, or crystals is described.
- `bag` (coverage_score) — No bag is mentioned or implied as a salient styling element.
- `jewelry` (coverage_score) — No jewelry or body ornament is described.
- `belt` (coverage_score) — The text describes a waistband on the skirt, not a separate visible belt or waist accessory.
- `asymmetry` (coverage_score) — No asymmetrical design or uneven structure is described.
- `quantity_accuracy` (quality_score) — The text contains no explicit counts, numerals, or quantity relations that require verification.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral distinction is described.
- `cultural_reference` (bonus_score) — No cultural, historical, or brand grounding is provided.
- `gender_expression` (bonus_score) — The text does not explicitly discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is stated.
- `brand_alignment` (bonus_score) — No brand language or brand identity target is mentioned.
- `negation_control` (bonus_score) — The text does not emphasize exclusions or absence of elements.
