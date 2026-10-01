# Text Evaluation Report

- **Source:** 51_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__051_media_cha_biarritz_ps27_043_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.8287 (Strong)
- **Coverage axis:** 0.8889
- **Quality axis (raw / base / penalized):** 0.8077 / 0.8125 / 0.8125
- **Penalties (mean):** 0.1
- **R_content:** 0.799696

## Gates

- Score gate: 0.8287 (threshold 0.7) → **PASS**
- Penalty gate: 0.1 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `asymmetry` | 1.0 | 1 |  | Asymmetry is explicitly described through the skirt’s wrap construction, diagonal drape, and uneven hem. |
| `body_coverage` | 1.0 | 1 |  | The text clearly mentions body exposure through the slit and partial visibility of the top. |
| `color_relationship_logic` | 1.0 | 1 |  | The text explains the color relationship as a beige base with a border-print graphic treatment and contrasting bands/stripes. |
| `cross_garment_binding` | 1.0 | 1 |  | The description distinguishes how the top, skirt, and shoes relate to each other, making the multi-garment composition clear. |
| `fabric_family` | 0.0 | 0 |  | The text suggests drape and a scarf-like effect, but it does not clearly name the main fabric family of the garment. |
| `footwear` | 1.0 | 1 |  | Footwear is clearly specified with shoe type, heel style, and color/material details. |
| `functional_detail` | 1.0 | 1 |  | The skirt includes clear functional/structural details: a slit and tassel-like ends are explicitly described. |
| `garment_category` | 1.0 | 1 |  | The text clearly identifies the main garment categories: skirt, top, and footwear. |
| `hardware_embellishment` | 0.0 | 0 |  | Jewelry is mentioned, but there is no clear hardware embellishment on the garment itself such as chains, studs, rings, or crystals. |
| `jewelry` | 1.0 | 1 |  | Salient jewelry is explicitly present and visually prominent. |
| `layering` | 1.0 | 1 |  | The text describes a clear top-over-skirt outfit with visible garment relations and partial overlap. |
| `length_hemline` | 1.0 | 1 |  | The text explicitly describes hemline behavior and length through the slit and ankle-reaching uneven hem. |
| `pattern_type` | 1.0 | 1 |  | The pattern type is clearly identified as a border print with striped detailing. |
| `primary_color` | 1.0 | 1 |  | The main color of the skirt is explicitly stated. |
| `secondary_color` | 1.0 | 1 |  | Secondary accent colors are clearly described as part of the skirt’s visible print. |
| `silhouette` | 1.0 | 1 |  | It gives a clear structural silhouette description, emphasizing asymmetry, drape, and layered panel flow. |
| `surface_finish` | 1.0 | 1 |  | The description clearly conveys a draped, fluid surface quality. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly states the crop framing and the relative top-bottom balance, including waist placement and limited visibility of the top versus the skirt. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are clearly tied to the correct garment or body part, and the skirt/top/shoes/accessories are distinguished well. Minor ambiguity remains in the cropped description and layered print d |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is mostly packed with visible garment facts and spatial details, with only a small amount of mood framing at the end. It remains prompt-useful and imageable, though slightly verbose. |
| `craft_embellishment_salience` | 0.75 | 1 | 工艺装饰显著度 | The trim/print treatment is clearly described with type and placement, though the craft is more decorative than technically constructed. |
| `design_distinctiveness` | 0.75 | 1 | 设计独特性 | The skirt has a clear non-formula memory point through its asymmetrical wrap construction, scarf-print treatment, and handkerchief hem with slit. |
| `design_signal_purity` | 1.0 | 1 | 设计信号纯度 | The text is dominated by concrete design facts, materials, placement, and silhouette details rather than mood essay or identity framing. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly imageable and already organized around visible silhouette, garment type, layering, and styling, so it is close to a usable generation prompt. Minor reduction comes from some explana |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a mostly natural body-to-detail order: framing, main garment, upper layer, then accessories and shoes. It is clear and easy to reconstruct, though some dense print and styling  |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | Multiple garments and accessories are present, and their attributes are mostly assigned to the correct item. The text keeps the skirt, top, bracelets, and shoes separate, with only slight complexity f |
| `reference_clarity` | 1.0 | 1 | 语言清晰度 | References are clear and stable: each pronoun or omitted subject has an obvious antecedent, and the spatial relations between skirt, top, and accessories are easy to parse. |
| `silhouette_combination_originality` | 0.75 | 1 | 组合原创性 | The combination is coherent and somewhat distinctive, especially the draped skirt against a fitted top, but it still sits within a broadly wearable resort-luxury framework. |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | The spatial relations are clear and visually reconstructable: placement at the waist/hip, diagonal wrap across the front, overlap, slit, and hem direction are all coherent. It is strong for prompt use |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | The text prioritizes visible, image-dominant clothing details and body placement. Accessories and mood language are present but do not overwhelm the main outfit description. |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly anchored in visible garment zones and spatial relations, with precise, imageable observations and little mood-only prose. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | No trunk-level left-right or garment-identity conflict; the look reads as a coherent asymmetric skirt outfit. |
| `coordination_penalty` | 0.0 | The styling elements align with the skirt’s polished resort direction; no major coordination clash across top, bottom, or shoes. |
| `formula_template_penalty` | 0.25 | There is mild resort/formula styling language, but the description remains fairly specific and craft-grounded rather than fully interchangeable. |
| `generation_content_penalty` | 0.25 | Mostly grounded garment description, but the closing mood language and resort framing slightly dilute the imaging trunk. |
| `rationality_penalty` | 0.0 | All described materials and constructions are physically plausible for ordinary fashion wear. |

## Missing coverage (未覆盖)

- **`fabric_family`** — The text suggests drape and a scarf-like effect, but it does not clearly name the main fabric family of the garment.
- **`hardware_embellishment`** — Jewelry is mentioned, but there is no clear hardware embellishment on the garment itself such as chains, studs, rings, or crystals.

## Skipped metrics (不适用)

- `shoulder_architecture` (coverage_score) — No salient shoulder design is described; only the lower portion of the top is visible.
- `closure` (coverage_score) — No explicit closure detail such as buttons, zipper, ties, buckles, or fastening is mentioned.
- `construction_technique` (coverage_score) — The text describes draping and overlapping panels, but not a named construction technique like pleating, quilting, embroidery, cut-outs, or engineered panel work.
- `deconstruction` (coverage_score) — No deconstruction, splicing, displacement, or reconstruction language is present.
- `bag` (coverage_score) — No bag is described or implied as a visible styling element.
- `belt` (coverage_score) — No visible belt, sash, waist cincher, or harness is mentioned; the waist emphasis comes from skirt cut and drape.
- `quantity_accuracy` (quality_score) — The text contains no explicit counts, numerals, or quantity relations that require quantity accuracy judgment.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral contrast is described.
- `gender_expression` (bonus_score) — No explicit gender expression or androgyny is mentioned.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is stated.
- `brand_alignment` (bonus_score) — No brand identity or brand-language target is provided.
- `negation_control` (bonus_score) — The text does not emphasize exclusions or absence of elements.
