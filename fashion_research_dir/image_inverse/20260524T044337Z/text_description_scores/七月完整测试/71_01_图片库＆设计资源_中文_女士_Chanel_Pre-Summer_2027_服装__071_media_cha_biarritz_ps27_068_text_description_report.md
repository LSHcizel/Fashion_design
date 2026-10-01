# Text Evaluation Report

- **Source:** 71_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__071_media_cha_biarritz_ps27_068_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.8743 (Strong)
- **Coverage axis:** 0.95
- **Quality axis (raw / base / penalized):** 0.8462 / 0.8542 / 0.8542
- **Penalties (mean):** 0.15
- **R_content:** 0.828399

## Gates

- Score gate: 0.8743 (threshold 0.7) → **PASS**
- Penalty gate: 0.15 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `asymmetry` | 0.0 | 0 |  | No asymmetrical design is described; the cited details emphasize symmetry instead. |
| `bag` | 1.0 | 1 |  | The bag is clearly identified by type, shape/structure, and color/material details. |
| `body_coverage` | 1.0 | 1 |  | The text clearly describes exposed areas and partial coverage through cutwork and mesh. |
| `closure` | 1.0 | 1 |  | A clear front placket and notch indicate a salient opening/closure area, even though the buttons are concealed. |
| `color_relationship_logic` | 1.0 | 1 |  | The text explains the color relationship as a clear white-versus-red contrast between top and bottom. |
| `construction_technique` | 1.0 | 1 |  | It names specific construction techniques and their placement on the garment, especially cutwork lace on the upper chest and mesh in the lower garment. |
| `cross_garment_binding` | 1.0 | 1 |  | The description clearly distinguishes attributes of the shirt, lower garment, and handbag, keeping each item’s features separate. |
| `fabric_family` | 1.0 | 1 |  | The text clearly identifies the main fabric families as a shirt-blouse material and a sheer mesh/net construction. |
| `functional_detail` | 1.0 | 1 |  | The text includes a functional accessory with handles and hardware, which counts as a salient functional detail. |
| `garment_category` | 1.0 | 1 |  | The text clearly identifies the main garment categories: an oversized shirt-blouse and a sheer netted lower garment. |
| `hardware_embellishment` | 1.0 | 1 |  | Gold-tone hardware is explicitly mentioned and qualifies as salient hardware embellishment. |
| `layering` | 1.0 | 1 |  | The text clearly describes a layered outfit with an over-top and a separate lower garment, making the relationship imageable. |
| `length_hemline` | 1.0 | 1 |  | The description gives clear length and hemline information for the top. |
| `pattern_type` | 1.0 | 1 |  | Pattern types are explicitly given: mesh/net and cutwork lace. |
| `primary_color` | 1.0 | 1 |  | White is clearly the dominant color of the main top. |
| `secondary_color` | 1.0 | 1 |  | A strong secondary red color is clearly present, with lavender as a minor accessory accent. |
| `shoulder_architecture` | 1.0 | 1 |  | Shoulder/sleeve structure is salient and explicitly described as roomy and voluminous. |
| `silhouette` | 1.0 | 1 |  | The overall shape is explicitly described, including the boxy top and body-skimming lower piece. |
| `surface_finish` | 1.0 | 1 |  | Surface qualities are explicitly described, including crispness, stiffness, and sheerness. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes the relationship between the upper and lower halves and explicitly frames the look as a balanced top-bottom composition. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are clearly attached to the correct garment or accessory, with the top, bottom, and bag kept distinct. There is only mild ambiguity in “skirt or trouser-like bottom,” but it does not s |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is compact and heavily focused on visible garment facts, with clear construction and silhouette details. There is some stylistic framing at the end, but it does not overwhelm the cloth |
| `craft_embellishment_salience` | 1.0 | 1 | 工艺装饰显著度 | The craft is specific, located, and visually functional: cutwork lace is placed on the upper chest to create negative space, and the hip lacing adds another distinct detail. |
| `design_distinctiveness` | 1.0 | 1 | 设计独特性 | The look has multiple clear memory points: cutwork lace insertion, transparent red netting, and an unusual shirt structure with notch collar and boxy tunic-like proportion. |
| `design_signal_purity` | 1.0 | 1 | 设计信号纯度 | The text is dominated by concrete design facts, materials, placement, and silhouette, with only minimal mood language at the end. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly visual and mostly prompt-ready, with clear garment types, silhouette, layering, and material details. It is slightly weakened by some interpretive phrasing and ambiguity in the lowe |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a mostly natural order from main garment to lower garment to accessory, making the outfit easy to reconstruct. There is some local compression and repeated restatement of styli |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The description generally keeps attributes tied to the correct item across multiple garments. The only notable uncertainty is the bottom being described as either a skirt or trouser-like piece, which  |
| `reference_clarity` | 1.0 | 1 | 语言清晰度 | References are consistently anchored to clear nouns ('The shirt', 'Below') with no confusing pronoun chains or ambiguous antecedents. The description is easy to track and visually coherent. |
| `silhouette_combination_originality` | 0.75 | 1 | 组合原创性 | The combination is unusual and fashion-forward, especially the shirt-over-netted bottom pairing, though the overall styling remains legible and not maximally unpredictable. |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and attachment positions are generally clear and imageable, with coherent top-over-bottom structure and visible placement cues. Minor uncertainty remains around the exact identity and fit of  |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | The text prioritizes highly visible, image-dominant elements and gives them concrete placement and material detail. It includes a brief styling summary, but hidden or low-visibility information does n |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly anchored in visible garment details and placement, with clear separation of shirt, lower garment, and handbag. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.25 | The lower garment is ambiguously described as either a skirt or trouser-like bottom, creating a mild trunk-level identity ambiguity, though the rest of the look is coherent. |
| `coordination_penalty` | 0.0 | The styling reads as a coherent contrast between a structured white top and a sheer red bottom, with no strong trunk-level coordination conflict. |
| `formula_template_penalty` | 0.25 | The look uses a fairly familiar high-contrast formula of crisp top plus sheer bottom, but it is still grounded in specific construction details rather than pure mood or brand-symbol stacking. |
| `generation_content_penalty` | 0.25 | Mostly imageable and garment-specific, but includes some runway/framing language and a concluding interpretive summary that slightly dilutes prompt efficiency. |
| `rationality_penalty` | 0.0 | The materials and construction remain physically plausible as fashion description; no clearly impossible garment construction is asserted. |

## Missing coverage (未覆盖)

- **`asymmetry`** — No asymmetrical design is described; the cited details emphasize symmetry instead.

## Skipped metrics (不适用)

- `deconstruction` (coverage_score) — The text does not explicitly mention deconstruction, splicing, displacement, or reconstruction.
- `footwear` (coverage_score) — No footwear is described.
- `jewelry` (coverage_score) — No jewelry or body ornament is explicitly present.
- `belt` (coverage_score) — No visible belt, sash, waist strap, or harness is mentioned.
- `quantity_accuracy` (quality_score) — The text contains descriptive size/shape terms like 'small', 'large', and 'voluminous', but no explicit quantity relations, counts, or numeric quantities that require quantity accuracy judgment.
- `bilateral_coherence` (quality_score) — No explicit left-right bilateral garment differences are described.
- `cultural_reference` (bonus_score) — No cultural, historical, or brand-specific reference is provided.
- `gender_expression` (bonus_score) — The description does not explicitly discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is stated beyond the outfit description.
- `brand_alignment` (bonus_score) — No brand identity or brand-language target is mentioned.
- `negation_control` (bonus_score) — The text does not emphasize exclusions or absence as a meaningful design requirement.
