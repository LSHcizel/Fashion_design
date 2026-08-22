# Text Evaluation Report

- **Source:** 08_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__008_media_cha_biarritz_ps27_026_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.0
- **Total score (S_fp):** 0.7969 (Strong)
- **Coverage axis:** 1.0
- **Quality axis (raw / base / penalized):** 0.7969 / 0.7449 / 0.7449
- **Penalties (mean):** 0.1
- **R_content:** 0.769008

## Gates

- Score gate: 0.7969 (threshold 0.7) → **PASS**
- Penalty gate: 0.1 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `bag` | 1.0 | 1 |  | The bag is explicitly identified by type, shape/texture, and how it is carried, so the coverage rule is satisfied. |
| `belt` | 1.0 | 1 |  | A visible waist accessory is described, and it is clearly positioned relative to the pants. |
| `body_coverage` | 1.0 | 1 |  | The text clearly describes visible body/lingerie exposure through the neckline. |
| `closure` | 1.0 | 1 |  | Clear closure details are explicitly described. |
| `color_relationship_logic` | 1.0 | 1 |  | The palette is described as a coordinated blue look with white/black lingerie contrast and a beige neutral accent. |
| `cross_garment_binding` | 1.0 | 1 |  | Multiple items are present and their roles are distinguished: jacket over top, pants below, and accessories separately identified, so garment-to-garment binding is clear. |
| `fabric_family` | 1.0 | 1 |  | The main fabric family is clearly indicated as denim-like. |
| `functional_detail` | 1.0 | 1 |  | Functional pocket detail is clearly mentioned; the clutch is an accessory, but the pockets alone satisfy the metric. |
| `garment_category` | 1.0 | 1 |  | The text clearly names the main garment categories: a shirt jacket and pants, with layered inner top. |
| `hardware_embellishment` | 1.0 | 1 |  | Sequins/glittering surface and metal buttons are clear embellishment/hardware details. |
| `jewelry` | 1.0 | 1 |  | A salient jewelry item is explicitly present. |
| `layering` | 1.0 | 1 |  | The text clearly describes a multi-layer outfit with readable over/under relationships. |
| `length_hemline` | 1.0 | 1 |  | Garment length and hem information are directly stated. |
| `primary_color` | 1.0 | 1 |  | The dominant color is clearly light aqua-blue / light blue. |
| `secondary_color` | 1.0 | 1 |  | Several secondary colors are explicitly visible and anchored to specific garment elements. |
| `shoulder_architecture` | 1.0 | 1 |  | Shoulder structure is explicitly specified. |
| `silhouette` | 1.0 | 1 |  | Overall shape and structural contour are explicitly described. |
| `surface_finish` | 1.0 | 1 |  | The text clearly specifies a shiny, glittering surface finish. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes the upper and lower garment relationship, including a fitted top under an oversized jacket and relaxed pants at the waist, so the top-bottom proportion is explicit. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are clearly attached to the correct garment or layer, and the lingerie layering is understandable. Minor ambiguity remains around “black belt or waistband,” which slightly blurs whethe |
| `core_information_density` | 0.5 | 0 | 信息密度与简洁性 | The description contains strong, usable garment information and a clear outfit structure, but it is somewhat verbose and detail-heavy, with many surface treatments and accessory notes layered onto the |
| `craft_embellishment_salience` | 1.0 | 1 | 工艺装饰显著度 | The embellishment and finish are clearly specified by type, placement, and visual effect, making them central identifying features. |
| `design_distinctiveness` | 1.0 | 1 | 设计独特性 | The look has multiple memorable anchors: denim-workwear proportions fused with allover sparkle, plus visible lingerie layering. This is clearly beyond a standard formula outfit. |
| `design_signal_purity` | 0.75 | 1 | 设计信号纯度 | The text is dominated by design facts and visible details, with only a small amount of mood framing that does not significantly dilute the signal. |
| `fine_grained_attribute_usage` | 1.0 | 1 | 术语具体度 | Color, material, surface treatment, construction, and silhouette are described with fine-grained fashion detail, making the look highly imageable and precise. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The description is highly visual, garment-specific, and mostly prompt-ready, with clear silhouette, layering, materials, and accessories. It is slightly less than perfect because it reads a bit like a |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a mostly natural order from overall look to top layer, underlayer, bottoms, and accessories. It is easy to reconstruct the outfit, though some details are compressed into long  |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text keeps the jacket, inner layer, pants, and accessory mostly well separated, with coherent multi-garment relations. The only notable binding uncertainty is the belt/waistband phrasing, but it d |
| `quantity_accuracy` | 0.75 | 1 | 语言清晰度 | The explicit counts and references are mostly clear and consistent. There is minor ambiguity in phrases like "black belt or waistband" and "camisole or bodysuit," but the quantity relations themselves |
| `reference_clarity` | 0.75 | 1 | 语言清晰度 | Referents are generally well anchored and the garment sequence is easy to follow. A few alternations such as "camisole or bodysuit" and "belt or waistband" introduce slight uncertainty, but they do no |
| `silhouette_combination_originality` | 0.75 | 1 | 组合原创性 | The silhouette is distinctive due to the oversized sparkling denim set and lingerie layering, though it still retains some recognizable jacket-and-pants structure. |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and attachment relationships are clearly described and visually imageable, including what sits over/under what and what is visible through the neckline. Minor ambiguity remains in the optiona |
| `specific_noun_usage` | 1.0 | 1 | 术语具体度 | Uses highly specific fashion nouns for garments, underlayers, closures, and accessories, with clear item-level identification throughout. |
| `visibility_priority` | 0.5 | 0 | 信息密度与简洁性 | Most of the text focuses on visible outfit elements, but it also gives notable weight to lower-priority or less essential details such as lingerie visibility and multiple surface-edge treatments. The  |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly anchored to visible garment parts and layered visibility, with repeated body-zone references and explicit visible/inferred wording. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | The trunk garments read as one coherent layered outfit without left-right or garment-identity conflicts. |
| `coordination_penalty` | 0.0 | The palette and accessories are coordinated; no strong styling clash appears across top, bottom, or footwear since shoes are not described. |
| `formula_template_penalty` | 0.25 | It follows a common look-description formula of top, bottom, accessories, and mood, though not heavily templated. |
| `generation_content_penalty` | 0.25 | The description is imageable, but it leans on conceptual styling language and repeated mood framing rather than a compact garment-first prompt. |
| `rationality_penalty` | 0.0 | The materials and layering are stylized but still physically plausible as fashion styling. |

## Quality issues (质量短板)

- **`core_information_density`** (score 0.5) — The description contains strong, usable garment information and a clear outfit structure, but it is somewhat verbose and detail-heavy, with many surface treatments and accessory notes layered onto the core look. The main silhouette is still readable, yet the prompt density is only moderate rather than highly efficient.
- **`visibility_priority`** (score 0.5) — Most of the text focuses on visible outfit elements, but it also gives notable weight to lower-priority or less essential details such as lingerie visibility and multiple surface-edge treatments. The visible silhouette remains clear, though the hierarchy is not fully optimized for prompt efficiency.

## Skipped metrics (不适用)

- `pattern_type` (coverage_score) — No distinct print or pattern type is described; only wash variation and glittering texture.
- `construction_technique` (coverage_score) — No specific construction technique like quilting, embroidery, cut-outs, or engineered panel work is described with a clear garment zone.
- `deconstruction` (coverage_score) — The text suggests an undone styling mood, but does not explicitly mention deconstruction, splicing, displacement, or reconstruction.
- `footwear` (coverage_score) — No footwear is mentioned in the text.
- `asymmetry` (coverage_score) — No clear asymmetrical design, one-shoulder, uneven hem, or similar structure is described.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral asymmetry is described.
- `cultural_reference` (bonus_score) — No clear cultural, historical, or brand-specific reference is provided.
- `gender_expression` (bonus_score) — The description does not explicitly discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is explicitly stated.
- `brand_alignment` (bonus_score) — There is no explicit brand language or brand identity target.
- `negation_control` (bonus_score) — The text does not emphasize exclusions or absence as a meaningful design requirement.
