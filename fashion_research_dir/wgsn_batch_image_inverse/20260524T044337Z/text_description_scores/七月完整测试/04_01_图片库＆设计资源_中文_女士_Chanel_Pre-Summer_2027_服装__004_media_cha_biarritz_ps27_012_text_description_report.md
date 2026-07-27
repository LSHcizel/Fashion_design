# Text Evaluation Report

- **Source:** 04_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__004_media_cha_biarritz_ps27_012_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.1
- **Total score (S_fp):** 0.8227 (Strong)
- **Coverage axis:** 1.0
- **Quality axis (raw / base / penalized):** 0.7833 / 0.7773 / 0.7773
- **Penalties (mean):** 0.15
- **R_content:** 0.779508

## Gates

- Score gate: 0.8227 (threshold 0.7) → **PASS**
- Penalty gate: 0.15 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `bag` | 1.0 | 1 |  | The text clearly identifies the bag type, its compact mini form, and its material/finish. |
| `body_coverage` | 1.0 | 1 |  | The text describes coverage and exposed leg area through the shorts and thigh-high boots. |
| `color_relationship_logic` | 1.0 | 1 |  | The text gives a coherent color story: a cream-dominant look accented by black, pale blue, yellow, and small multicolor trim details. |
| `construction_technique` | 1.0 | 1 |  | A clear craft technique is named and localized on the draped textile piece along its edge. |
| `cross_garment_binding` | 1.0 | 1 |  | Multiple items are present and the text distinguishes them by role and placement, making the garment-to-item relationships clear enough to score. |
| `fabric_family` | 1.0 | 1 |  | The text identifies main material families at least broadly as textile/cloth for the wrap and a garment surface for the shorts, enough to infer fabric category at a high level. |
| `footwear` | 1.0 | 1 |  | Footwear type and key form/material cues are clearly described. |
| `garment_category` | 1.0 | 1 |  | The text clearly identifies the main garment categories worn in the look. |
| `layering` | 1.0 | 1 |  | The text explicitly describes layered textile elements and their partial overlap/placement. |
| `length_hemline` | 1.0 | 1 |  | The text gives clear length information for both shorts and boots. |
| `pattern_type` | 1.0 | 1 |  | A decorative motif pattern is described, with appliqué/embroidery-like elements functioning as the pattern type. |
| `primary_color` | 1.0 | 1 |  | Cream is the dominant base color across the main garments and accessories. |
| `secondary_color` | 1.0 | 1 |  | Several secondary colors are explicitly present alongside the cream base, with clear visible placement on garments and accessories. |
| `silhouette` | 1.0 | 1 |  | It explicitly describes the overall silhouette and structural contour. |
| `surface_finish` | 1.0 | 1 |  | Clear surface traits are described, including smoothness, softness/fuzziness, and a clean structured shaft. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly states the visible vertical framing and the waist-to-feet proportion, with a short bottom-heavy silhouette described through shorts and thigh-high boots. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are bound to the correct entities, and the look is spatially coherent. Minor ambiguity remains in phrases like “possibly a coat or wrap” and “small green detail appears near one outer  |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The text is compact and mostly foregrounds visible garment facts, with clear trunk-to-accessory ordering. There is some descriptive layering and interpretive phrasing, but no long essay or repeated fr |
| `craft_embellishment_salience` | 0.75 | 1 | 工艺装饰显著度 | Craft is clearly identified and located along the edge, with visible fringe and appliqué-like decoration, though the exact technique remains partly hedged. |
| `design_distinctiveness` | 0.75 | 1 | 设计独特性 | The look has a clear non-formula memory point through the ornate edge decoration and the sporty piping/boots contrast, though it is not highly complex. |
| `design_signal_purity` | 1.0 | 1 | 设计信号纯度 | The text is dominated by concrete design facts, materials, placement, and trim details, with essentially no essay-like mood framing. |
| `fine_grained_attribute_usage` | 0.75 | 1 | 术语具体度 | The description uses detailed color, material, and construction language with good visual specificity. Minor uncertainty remains in a few hedged material terms like "appliqué or embroidery-like" and " |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is already close to a usable image prompt: it names the main garments, silhouette, colors, and accessory accents clearly. It is slightly more descriptive than prompt-like because it includes  |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a mostly natural body-to-detail order: overall framing, main garments, then accessories and peripheral elements. There is a small amount of side-note layering and a late-added  |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | Multiple garments and an accessory are described with mostly stable attribution. The shorts, boots, draped textile, and bag are kept distinct, with only slight uncertainty around the draped textile’s  |
| `reference_clarity` | 0.75 | 1 | 语言清晰度 | References are mostly clear and the garment/object chain is easy to follow, with only minor ambiguity in phrases like “carries or drapes” and “possibly a coat or wrap,” which slightly reduce precision |
| `silhouette_combination_originality` | 0.75 | 1 | 组合原创性 | The shorts-plus-thigh-high-boots pairing with a draped textile and fuzzy mini bag is more distinctive than a standard formula, though still readable and not radically unexpected. |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Spatial relations are mostly clear and imageable: the textile hangs beside the leg, the boots extend to the lower thigh, and another layer is partially visible at the frame edge. The only weakness is  |
| `specific_noun_usage` | 0.75 | 1 | 术语具体度 | Uses several concrete fashion nouns and garment/accessory types with clear visual referents. A few phrases remain hedged or generic, such as "possibly a coat or wrap" and "textile piece," so it is str |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | The description prioritizes what is visibly image-dominant: shorts, boots, bag, and the draped textile. It includes a few lower-visibility interpretive notes like “possibly a coat or wrap” and “sugges |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly anchored in visible garment parts, placement, and surface details, with clear spatial reading and little mood prose. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.25 | Main trunk is coherent, with only mild ambiguity around the draped cream piece; no strong left-right or mutually exclusive trunk conflict. |
| `coordination_penalty` | 0.25 | The look mixes sporty, ornate, and plush accents, but they are still coordinated around a cream base and do not create a severe trunk-level clash. |
| `formula_template_penalty` | 0.0 | The description is freeform prose rather than a fixed fashion-template structure. |
| `generation_content_penalty` | 0.25 | Mostly imageable, but includes some interpretive/summary phrasing and a speculative garment label that slightly reduces prompt efficiency. |
| `rationality_penalty` | 0.0 | All described items are physically plausible fashion elements; no implausible materials or constructions are asserted. |

## Skipped metrics (不适用)

- `shoulder_architecture` (coverage_score) — No salient shoulder or sleeve structure is described.
- `closure` (coverage_score) — No explicit closure details such as buttons, zippers, ties, or buckles are mentioned.
- `functional_detail` (coverage_score) — The text does not clearly describe pockets, straps, or other functional garment details.
- `deconstruction` (coverage_score) — The text suggests layered styling but does not explicitly describe deconstruction, splicing, displacement, or reconstruction.
- `hardware_embellishment` (coverage_score) — No salient hardware or metal embellishment is described.
- `jewelry` (coverage_score) — No jewelry or body ornament is explicitly present.
- `belt` (coverage_score) — No visible belt, sash, waist strap, or harness is described.
- `asymmetry` (coverage_score) — No clear asymmetrical garment structure is described.
- `quantity_accuracy` (quality_score) — The text contains no explicit counts, numerals, or quantity relations that need verification.
- `bilateral_coherence` (quality_score) — The text does not explicitly distinguish left/right sides or other bilateral differences in the worn look.
- `cultural_reference` (bonus_score) — No cultural, historical, or brand grounding is provided.
- `gender_expression` (bonus_score) — The text does not explicitly discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is explicitly stated.
- `brand_alignment` (bonus_score) — No brand identity or brand-language target is mentioned.
- `negation_control` (bonus_score) — The text does not emphasize exclusions or absences as important.
