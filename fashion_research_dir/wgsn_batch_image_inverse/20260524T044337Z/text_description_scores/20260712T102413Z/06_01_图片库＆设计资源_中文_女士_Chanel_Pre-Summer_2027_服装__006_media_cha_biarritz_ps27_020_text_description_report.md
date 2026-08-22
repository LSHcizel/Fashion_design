# Text Evaluation Report

- **Source:** 06_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__006_media_cha_biarritz_ps27_020_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.0
- **Total score (S_fp):** 0.8372 (Strong)
- **Coverage axis:** 1.0
- **Quality axis (raw / base / penalized):** 0.8438 / 0.7962 / 0.7962
- **Penalties (mean):** 0.1
- **R_content:** 0.807898

## Gates

- Score gate: 0.8372 (threshold 0.7) → **PASS**
- Penalty gate: 0.1 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `body_coverage` | 1.0 | 1 |  | The text clearly describes significant body exposure and coverage balance. |
| `closure` | 1.0 | 1 |  | The text clearly describes multiple closure types: an open-front coat with buttons and a tie-front top. |
| `color_relationship_logic` | 1.0 | 1 |  | The text explains the color relationship as a white outer layer framing a matching pastel printed inner set, with multicolored trim as accent. |
| `construction_technique` | 1.0 | 1 |  | The text names specific construction/craft techniques and gives their placement on the garments, including quilting/bouclé-like texture on the coat and embroidery/fringing on the skirt. |
| `cross_garment_binding` | 1.0 | 1 |  | The description clearly distinguishes which attributes belong to the coat versus the coordinated top and skirt, making the multi-garment relationship explicit. |
| `fabric_family` | 1.0 | 1 |  | The text identifies the main garment family/material context clearly enough: a coat and a printed two-piece, with textile texture cues. |
| `garment_category` | 1.0 | 1 |  | The text clearly identifies the main garment categories: coat, top, and mini skirt. |
| `hardware_embellishment` | 1.0 | 1 |  | The coat features clearly described decorative hardware-like embellishment, including metallic-looking beads/tufts and silver-toned buttons. |
| `layering` | 1.0 | 1 |  | The text clearly describes a layered outfit with an outer coat over an inner top and skirt, making the layering relationship visually recoverable. |
| `length_hemline` | 1.0 | 1 |  | The text gives clear length and hemline information for multiple garments. |
| `pattern_type` | 1.0 | 1 |  | A clear pattern type is given: floral or abstract print. |
| `primary_color` | 1.0 | 1 |  | White is clearly the dominant outerwear color and primary visible color. |
| `secondary_color` | 1.0 | 1 |  | Secondary color accents are clearly present, including multicolored trim and a visible burgundy lining. |
| `shoulder_architecture` | 1.0 | 1 |  | The shoulder line is explicitly salient, with dropped shoulders and sleeve structure noted. |
| `silhouette` | 1.0 | 1 |  | Overall shape and structural contour are explicitly described for both the coat and the set underneath. |
| `surface_finish` | 1.0 | 1 |  | It explicitly describes surface qualities including texture, raised/quilted-bouclé-like finish, and frayed edges. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes the upper-to-lower body balance: a long outer coat over a very cropped top and low-rise mini skirt, with exposed midriff indicating a strong top-bottom proportion. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are clearly attached to the correct garment, with coat, top, and skirt distinguished well. Minor complexity comes from dense layered description and the coat lining/trim details, but t |
| `core_information_density` | 0.5 | 0 | 信息密度与简洁性 | The description is rich in visible garment detail and keeps the main outfit readable, but it is somewhat over-elaborated with many stacked material/trim/texture descriptors. Core silhouette and key pi |
| `craft_embellishment_salience` | 1.0 | 1 | 工艺装饰显著度 | Craft and embellishment are clearly identified by type, placement, and visual role, and they function as major recognition points of the look. |
| `design_distinctiveness` | 0.75 | 1 | 设计独特性 | The look has clear memorable anchors: ornate multicolor trim, visible contrast lining, and a fringed mini skirt hem. These go beyond a generic resort formula, though the overall silhouette remains fai |
| `design_signal_purity` | 1.0 | 1 | 设计信号纯度 | The text is dominated by concrete design facts, with very little mood-only or essay-like language, making it highly usable for generation. |
| `fine_grained_attribute_usage` | 1.0 | 1 | 术语具体度 | Attributes are richly and precisely described across color, texture, construction, and finish, giving a highly detailed and imageable fashion description. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly imageable and already close to a prompt, with clear garment hierarchy, silhouette, colors, and styling. It is slightly verbose and reads more like a detailed description than a conc |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a mostly natural order from overall look to outer layer, then inner garments, then styling summary. It is clear and easy to reconstruct, though some detail density within the c |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text keeps the outer coat, cropped top, and mini skirt mostly separate and correctly matched to their own attributes. The only slight risk is dense descriptive layering, but the multi-garment bind |
| `quantity_accuracy` | 1.0 | 1 | 语言清晰度 | The text uses quantities and count-like relations consistently, and they are easy to track without contradiction. The described items and counts are internally coherent. |
| `reference_clarity` | 1.0 | 1 | 语言清晰度 | References and pronouns are clear and stable throughout. Each descriptor cleanly points back to a specific garment or part, with no confusing antecedents. |
| `silhouette_combination_originality` | 0.75 | 1 | 组合原创性 | The combination is specific and somewhat distinctive, especially with the long coat over a barely-there printed set, but it still sits within a recognizable resort-couture template. |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and placement are clearly described, and the relationships between coat, top, and skirt are visually coherent. Minor complexity comes from the dense descriptive detail, but the spatial struct |
| `specific_noun_usage` | 1.0 | 1 | 术语具体度 | Uses highly specific garment nouns and fashion terms throughout, with clear item-level identification and coherent styling language. |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | The text prioritizes visible, image-dominant elements like the coat, top, skirt, and exposed midriff, and it explicitly notes when footwear is not visible. A few lower-visibility details such as linin |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly grounded in visible, imageable observations with precise body/garment anchors and explicit visibility limits. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | The coat, top, and skirt read as a coherent layered look with no trunk-level left-right contradiction. |
| `coordination_penalty` | 0.0 | The styling language is internally aligned: ornate outerwear, delicate printed base, and handcrafted trim details work together. |
| `formula_template_penalty` | 0.25 | The description follows a common runway-look formula with standard garment sequencing and mood framing, though it is not heavily templated. |
| `generation_content_penalty` | 0.25 | Mostly imageable, but includes some analytical/material-interpretive phrasing and mood language that slightly reduces prompt efficiency. |
| `rationality_penalty` | 0.0 | All described materials and construction details are plausible in fashion imagery. |

## Quality issues (质量短板)

- **`core_information_density`** (score 0.5) — The description is rich in visible garment detail and keeps the main outfit readable, but it is somewhat over-elaborated with many stacked material/trim/texture descriptors. Core silhouette and key pieces remain clear, yet the density is only moderate rather than highly efficient.

## Skipped metrics (不适用)

- `functional_detail` (coverage_score) — No pockets, straps, or other functional utility details are described.
- `deconstruction` (coverage_score) — The description does not mention deconstruction, splicing, displacement, or reconstruction.
- `bag` (coverage_score) — No bag is mentioned or implied as part of the look.
- `footwear` (coverage_score) — Footwear is explicitly not visible, so this metric is not applicable.
- `jewelry` (coverage_score) — No salient jewelry or body ornament is described.
- `belt` (coverage_score) — No visible belt, sash, waist strap, or harness is described; the waist emphasis comes from garment cut only.
- `asymmetry` (coverage_score) — No clear asymmetrical garment structure is described.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral differences are described.
- `cultural_reference` (bonus_score) — No clear cultural, historical, or brand reference is provided.
- `gender_expression` (bonus_score) — The description does not explicitly discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is explicitly stated beyond styling mood.
- `brand_alignment` (bonus_score) — No brand identity or brand-language target is mentioned.
