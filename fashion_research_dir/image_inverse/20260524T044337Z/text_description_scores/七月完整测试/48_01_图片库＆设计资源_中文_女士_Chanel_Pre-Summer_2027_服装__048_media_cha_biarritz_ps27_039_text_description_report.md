# Text Evaluation Report

- **Source:** 48_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__048_media_cha_biarritz_ps27_039_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.8344 (Strong)
- **Coverage axis:** 1.0
- **Quality axis (raw / base / penalized):** 0.7885 / 0.7917 / 0.7917
- **Penalties (mean):** 0.1
- **R_content:** 0.805196

## Gates

- Score gate: 0.8344 (threshold 0.7) → **PASS**
- Penalty gate: 0.1 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `asymmetry` | 1.0 | 1 |  | The garment includes uneven graphic placement and an asymmetrical hem opening, so asymmetry is explicitly present. |
| `bag` | 1.0 | 1 |  | The bag is clearly identified by type, shape, and carrying detail, satisfying the coverage requirement. |
| `body_coverage` | 1.0 | 1 |  | The text clearly mentions both limited upper-torso visibility and a front opening that reveals more of the legs. |
| `color_relationship_logic` | 1.0 | 1 |  | The text states the palette logic as a coordinated combination of a dominant green base with black graphic contrast and cream/gold accents. |
| `construction_technique` | 1.0 | 1 |  | The text names construction techniques and locates them on the skirt/body of the garment. |
| `cross_garment_binding` | 1.0 | 1 |  | Multiple items are described and their roles are distinguishable: the main green garment, the draped outerwear, and the handbag. |
| `footwear` | 1.0 | 1 |  | The text covers shoe family, toe shape, and color/material detail, so footwear is clearly specified. |
| `functional_detail` | 1.0 | 1 |  | The bag’s straps and drawstring are clear functional details. |
| `garment_category` | 1.0 | 1 |  | The text clearly identifies the main garment as a dress or skirted look, with the skirt as the visible主体品类. |
| `hardware_embellishment` | 1.0 | 1 |  | The shoe toe caps/ornaments are a clear metallic embellishment. |
| `layering` | 1.0 | 1 |  | The text describes multiple worn/carried elements and their relation to the body, making the layered styling readable. |
| `length_hemline` | 1.0 | 1 |  | The text gives both approximate length and hemline behavior. |
| `pattern_type` | 1.0 | 1 |  | A clear graphic pattern type is described, even if abstract rather than a named print category. |
| `primary_color` | 1.0 | 1 |  | The main color is explicitly and repeatedly identified as green. |
| `secondary_color` | 1.0 | 1 |  | Multiple secondary colors are clearly present and visually salient alongside the green base. |
| `silhouette` | 1.0 | 1 |  | It explicitly describes the overall shape and structural contour of the garment. |
| `surface_finish` | 1.0 | 1 |  | Surface and drape qualities are clearly described, supporting a visible finish/handfeel reading. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes the lower-body silhouette and its proportion relative to the waist/hips, including skirt length and movement balance. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are bound to the correct entities, and the left-hand drape, handbag, and shoes are clearly separated. Minor ambiguity remains in “dress or coordinated skirted look” and “coat or jacket |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is compact and mostly devoted to visible garment facts, with clear silhouette, pattern, hem, bag, and shoe details. There is some stylistic framing (“runway view,” “reads polished and  |
| `craft_embellishment_salience` | 0.75 | 1 | 工艺装饰显著度 | Craft and embellishment are clearly identified and positioned, but the exact technique remains somewhat interpretive rather than fully specified. |
| `design_distinctiveness` | 0.75 | 1 | 设计独特性 | The look has clear non-formula memory points through graphic surface treatment and embellished footwear, though it is still a fairly straightforward dress/skirted silhouette. |
| `design_signal_purity` | 1.0 | 1 | 设计信号纯度 | The text is dominated by concrete design facts, with minimal mood language and strong visual specificity. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is already close to a usable image prompt: it specifies view, garment type, silhouette, patterning, accessories, and shoes. Minor issues remain because it is somewhat explanatory and includes |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a mostly natural body-to-detail order: overall view, garment shape, skirt behavior, accessories, then shoes. Minor compression and some repeated styling summary keep it from be |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text describes multiple garments and accessories with mostly stable assignment of colors and features to each item. The main weakness is mild uncertainty around the base garment identity, but ther |
| `reference_clarity` | 1.0 | 1 | 语言清晰度 | References are consistently anchored to clear nouns, and the few pronouns/ellipses are easy to resolve without ambiguity. |
| `silhouette_combination_originality` | 0.5 | 0 | 组合原创性 | The combination is coherent and polished, but the overall silhouette remains relatively conventional aside from the graphic surface treatment and shoe detail. |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Spatial relations are mostly clear and imageable, including cropping, drape, hanging position, and front opening in motion. The description is coherent enough for generation, though it still reads par |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | The text prioritizes highly visible, image-dominant elements such as silhouette, pattern placement, hem movement, and footwear. It does mention the coat draped over the hand, but that is still a visib |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly anchored in visible, imageable details and body/garment positions, with honest uncertainty only where the upper torso is cropped out. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | No clear trunk-level contradiction; the only ambiguity is dress vs coordinated skirted look, which does not create a direct garment conflict. |
| `coordination_penalty` | 0.0 | The palette and accessories are coherent and intentionally coordinated; no strong styling clash across trunk garments. |
| `formula_template_penalty` | 0.25 | Some formulaic runway prose and color-summary phrasing, but the description still contains a clear imaging trunk and specific garment details. |
| `generation_content_penalty` | 0.25 | Mostly grounded garment description, but ends with a broad stylistic summary that adds some redundant conceptual framing. |
| `rationality_penalty` | 0.0 | All described materials and constructions are physically plausible as ordinary fashion items. |

## Quality issues (质量短板)

- **`silhouette_combination_originality`** (score 0.5) — The combination is coherent and polished, but the overall silhouette remains relatively conventional aside from the graphic surface treatment and shoe detail.

## Skipped metrics (不适用)

- `shoulder_architecture` (coverage_score) — The neckline and shoulder area are not visible or described in a way that makes shoulder structure salient.
- `fabric_family` (coverage_score) — The text does not clearly identify the main fabric family; it describes silhouette, color, and surface behavior but not a material category.
- `closure` (coverage_score) — No explicit closure detail such as buttons, zipper, ties, or buckle is mentioned.
- `deconstruction` (coverage_score) — The description does not explicitly mention deconstruction, splicing, displacement, or reconstruction.
- `jewelry` (coverage_score) — No jewelry or body ornament is explicitly described.
- `belt` (coverage_score) — No visible belt, sash, waist cincher, or harness is mentioned; the waist shaping comes from garment cut.
- `quantity_accuracy` (quality_score) — The text does not use explicit counts or quantity relations that need verification.
- `bilateral_coherence` (quality_score) — No explicit left-right bilateral garment difference is described; the text mentions only a single-side placement (“left hand,” “left hip”) without contrasting the opposite side.
- `cultural_reference` (bonus_score) — No cultural, historical, or brand reference is provided.
- `gender_expression` (bonus_score) — The text does not explicitly discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is stated.
- `brand_alignment` (bonus_score) — No brand language or brand identity target is mentioned.
