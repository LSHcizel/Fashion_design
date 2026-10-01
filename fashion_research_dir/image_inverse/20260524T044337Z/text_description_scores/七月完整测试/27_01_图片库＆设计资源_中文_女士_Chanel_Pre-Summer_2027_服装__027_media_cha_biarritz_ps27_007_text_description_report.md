# Text Evaluation Report

- **Source:** 27_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__027_media_cha_biarritz_ps27_007_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.8428 (Strong)
- **Coverage axis:** 1.0
- **Quality axis (raw / base / penalized):** 0.8036 / 0.8021 / 0.8021
- **Penalties (mean):** 0.05
- **R_content:** 0.828051

## Gates

- Score gate: 0.8428 (threshold 0.7) → **PASS**
- Penalty gate: 0.05 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `asymmetry` | 1.0 | 1 |  | Asymmetry is explicitly stated and reinforced through the uneven hem and angled wrap-like construction. |
| `bag` | 1.0 | 1 |  | Bag type, carrying method, and material/finish are all clearly described. |
| `body_coverage` | 1.0 | 1 |  | The text clearly describes both coverage and exposure, especially the deep neckline and torso fit. |
| `color_relationship_logic` | 1.0 | 1 |  | The text explains the color relationship as a cream base with sharp black contrast accents. |
| `construction_technique` | 1.0 | 1 |  | The garment construction is described with clear paneling and engineered asymmetric layering at the skirt and top hem. |
| `cross_garment_binding` | 1.0 | 1 |  | The description clearly distinguishes which structural details belong to the top versus the skirt, making the multi-garment relations legible. |
| `footwear` | 1.0 | 1 |  | The text specifies the footwear family, heel form, and material/color finish, with added strap/ankle detail. |
| `functional_detail` | 1.0 | 1 |  | The text clearly includes functional accessory details: a handheld bag with handle and sandals with wrapping straps. |
| `garment_category` | 1.0 | 1 |  | The text clearly names the main garment categories: a top and a skirt. |
| `layering` | 1.0 | 1 |  | The look clearly uses layered garment relations, with the top worn over the skirt and a wrap-like overlay structure that is visually readable. |
| `length_hemline` | 1.0 | 1 |  | The text gives both garment length and hemline behavior. |
| `pattern_type` | 1.0 | 1 |  | A leopard print pattern is explicitly mentioned. |
| `primary_color` | 1.0 | 1 |  | The main color is clearly given as ivory/cream. |
| `secondary_color` | 1.0 | 1 |  | Black is a clear secondary accent color used as edging/trim against the cream base. |
| `shoulder_architecture` | 1.0 | 1 |  | The shoulder/upper-body construction is clearly specified through sleeveless straps and armhole treatment. |
| `silhouette` | 1.0 | 1 |  | It explicitly describes the overall shape and structural trend. |
| `surface_finish` | 1.0 | 1 |  | The text clearly describes surface behavior through drape and fluidity. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes the relationship between the fitted top and the longer skirt, including waist/hip placement and overall vertical balance. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are clearly attached to the correct garment or accessory, and the layering relation between top and skirt is explicit. Minor ambiguity remains in phrases like “waist/hip area” and the  |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is compact and heavily garment-focused, with clear visible construction and styling details. There is some added descriptive layering, but little mood essaying or repeated framing, so  |
| `craft_embellishment_salience` | 0.75 | 1 | 工艺装饰显著度 | Trim and edging are a salient design device and are located clearly, but the craft language is still fairly simple and not highly technical. |
| `design_distinctiveness` | 0.75 | 1 | 设计独特性 | The look has a clear non-formula memory point through the black-trimmed asymmetric wrap overlay and irregular layered hems, though it is still a relatively clean luxury palette rather than highly radi |
| `design_signal_purity` | 1.0 | 1 | 设计信号纯度 | The text is dominated by concrete design facts, with almost no mood or essay-like framing, so the design signal stays very pure. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly imageable and already close to a generation prompt, with clear garment types, silhouette, palette, and accessories. It is slightly more explanatory than prompt-tight, but still stro |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a mostly natural order from overall look to garment structure, then skirt details, then styling/accessories. It is clear and easy to reconstruct, though some detail layering wi |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The description keeps the top, skirt, bag, and sandals mostly distinct, with their own colors and structural details. There is slight cross-item complexity because the top extends over the skirt and b |
| `quantity_accuracy` | 0.75 | 1 | 语言清晰度 | The text uses a few quantity-like relations implicitly (single top, single skirt, one bag, one pair of sandals) and they are easy to track. There is no conflicting count or unclear numerical reference |
| `reference_clarity` | 1.0 | 1 | 语言清晰度 | References are consistently anchored to clear nouns, and pronouns like “it” clearly point back to the immediately preceding garment. The sequence is easy to follow and visually coherent. |
| `silhouette_combination_originality` | 0.75 | 1 | 组合原创性 | The combination is coherent and somewhat unusual because of the asymmetric layered top-over-skirt construction, though it remains within an elegant runway-ready silhouette rather than a highly unpredi |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering, overlap, and hem placement are clearly described and visually reconstructable. The spatial logic is coherent and mostly prompt-ready, though the description is somewhat dense and analytical  |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | The text prioritizes visible silhouette, trim, hem shape, and footwear, which are image-dominant. Accessories and hair are included but do not overwhelm the main outfit, so visibility ordering is good |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly anchored in visible garment parts and readable construction, with clear placement and layering details and little mood prose. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | No trunk-level left-right contradiction or mutually exclusive garment identity is present; the top, skirt, and shoes read as a coherent single look. |
| `coordination_penalty` | 0.0 | The styling language is internally aligned: restrained palette, crisp trim, and delicate footwear all support the same elegant draped silhouette. |
| `formula_template_penalty` | 0.25 | The look uses a somewhat familiar runway formula of clean top + asymmetric skirt + accessory styling, but it remains sufficiently specific and craft-grounded rather than fully template-like. |
| `generation_content_penalty` | 0.0 | The description is grounded in a clear garment trunk with specific construction details; it is not dominated by redundant conceptual prose or interchangeable mood language. |
| `rationality_penalty` | 0.0 | The described materials and construction are physically plausible as ordinary fashion garments and accessories. |

## Skipped metrics (不适用)

- `fabric_family` (coverage_score) — No explicit main fabric/material family is stated; only color, cut, and drape are described.
- `closure` (coverage_score) — No explicit closure such as buttons, zipper, ties, or buckle is mentioned.
- `deconstruction` (coverage_score) — The text does not explicitly mention deconstruction, splicing, displacement, or reconstruction.
- `hardware_embellishment` (coverage_score) — No salient hardware or decorative metal embellishment such as chains, studs, rings, or crystals is described.
- `jewelry` (coverage_score) — No jewelry or body ornament is explicitly described.
- `belt` (coverage_score) — No visible belt, sash, waist cincher, or harness is mentioned; the waist emphasis comes from garment cut and layering, not an accessory.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral distinction is described.
- `cultural_reference` (bonus_score) — No explicit cultural, historical, or brand grounding is provided.
- `gender_expression` (bonus_score) — The text does not explicitly discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is stated.
- `brand_alignment` (bonus_score) — No brand language or brand identity target is mentioned.
- `negation_control` (bonus_score) — The text does not emphasize exclusions or absence of elements as a meaningful design point.
