# Text Evaluation Report

- **Source:** 02_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__002_media_cha_biarritz_ps27_006_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.0
- **Total score (S_fp):** 0.8631 (Strong)
- **Coverage axis:** 1.0
- **Quality axis (raw / base / penalized):** 0.85 / 0.8282 / 0.8282
- **Penalties (mean):** 0.1
- **R_content:** 0.832892

## Gates

- Score gate: 0.8631 (threshold 0.7) → **PASS**
- Penalty gate: 0.1 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `bag` | 1.0 | 1 |  | Bag type, shape, color/material, and carrying position are all clearly described. |
| `body_coverage` | 1.0 | 1 |  | The text clearly describes coverage and exposure through the sleeveless-looking top and layered arrangement. |
| `color_relationship_logic` | 1.0 | 1 |  | The text explains the color/story relationship as coordinated patterned outer pieces layered over a brown tunic, not just a list of hues. |
| `construction_technique` | 1.0 | 1 |  | A notable fabrication/finish is described, including a woven-looking pattern and frayed trim placed on specific garment zones. |
| `cross_garment_binding` | 1.0 | 1 |  | The description distinguishes which attributes belong to the jacket, top/tunic, skirt, and handbag, making the multi-garment relationships clear. |
| `fabric_family` | 1.0 | 1 |  | The text clearly implies a woven textile family for the jacket/skirt set, enough to identify the main material category. |
| `functional_detail` | 1.0 | 1 |  | The text clearly mentions functional details: patch pockets on the jacket and carrying straps/hardware on the handbag. |
| `garment_category` | 1.0 | 1 |  | The text clearly names the main garment categories and accessory. |
| `hardware_embellishment` | 1.0 | 1 |  | Visible metallic embellishment is present, especially the handbag hardware and gold-toned jewelry. |
| `jewelry` | 1.0 | 1 |  | Prominent jewelry/body adornment is explicitly present and visually salient. |
| `layering` | 1.0 | 1 |  | The text clearly describes a multi-layer outfit with an outer jacket over a tunic/top and skirt beneath, with visible layering order. |
| `length_hemline` | 1.0 | 1 |  | The text gives multiple clear length and hemline cues. |
| `pattern_type` | 1.0 | 1 |  | A clear pattern type is given: abstract, woven-looking patterning. |
| `primary_color` | 1.0 | 1 |  | The look has clear dominant colors, with grey/black/orange patterning and a brown underlayer. |
| `secondary_color` | 1.0 | 1 |  | Multiple secondary colors are explicitly named and visually anchored to specific garments and trim. |
| `shoulder_architecture` | 1.0 | 1 |  | Shoulder structure is explicitly stated and salient. |
| `silhouette` | 1.0 | 1 |  | It explicitly describes the overall shape and structural contour. |
| `surface_finish` | 1.0 | 1 |  | It describes salient surface/handfeel and structure traits, especially texture and stiffness. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes the upper-to-lower body framing and the relative length balance between the top/tunic and skirt. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are bound to the correct garment and layer, with clear separation between jacket, tunic, skirt, and accessories. Minor ambiguity remains in phrases like “sleeveless-looking long top or |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The main garment silhouette is clearly established first and most of the text stays on visible clothing details, but the accessory list and repeated material/color elaboration add some redundancy. |
| `craft_embellishment_salience` | 1.0 | 1 | 工艺装饰显著度 | The trim is clearly identified by type, placement, and visual effect, making it a major look-defining craft detail. |
| `design_distinctiveness` | 0.75 | 1 | 设计独特性 | The look has a clear memory anchor through the abstract woven pattern, frayed trim, and layered skirt-suit construction. It is distinctive, though not so singular or experimental as to merit the top s |
| `design_signal_purity` | 1.0 | 1 | 设计信号纯度 | The text is overwhelmingly composed of concrete design facts, with very little mood language beyond a brief closing summary. |
| `fine_grained_attribute_usage` | 1.0 | 1 | 术语具体度 | The description is rich in fine-grained color, texture, construction, and material-like detail, with strong visual specificity and coherent layering. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly visual, organized around visible garments, layering, colors, and accessories, so it is close to a usable prompt. It is still somewhat explanatory and verbose rather than fully promp |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a mostly natural order from overall look to jacket, underlayer, skirt, and accessories, making the outfit easy to reconstruct. There is some density and a few long detail chain |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The multi-garment relations are mostly well organized: the jacket, tunic, and skirt are clearly distinguished, and accessories are separately described. There is slight ambiguity in the tunic/top word |
| `reference_clarity` | 1.0 | 1 | 语言清晰度 | References are consistently anchored to clear antecedents, and the layering sequence is easy to follow without ambiguity. |
| `silhouette_combination_originality` | 0.75 | 1 | 组合原创性 | The silhouette mix is specific and somewhat unusual, especially the tunic-over-skirt layering, but it still sits within a recognizable tailored-fashion framework. |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and attachment positions are clearly described and visually reconstructable. The spatial relations are coherent, though the prose remains somewhat descriptive rather than tightly prompt-struc |
| `specific_noun_usage` | 1.0 | 1 | 术语具体度 | Uses highly specific garment and accessory nouns with clear fashion semantics, plus precise structural descriptors and styling terms. |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | The description prioritizes visible, image-dominant elements like silhouette, pattern, trim, and carried accessories. It includes a few lower-priority specifics, but hidden or interior details do not  |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly anchored in visible garment parts and spatial relations, with precise placement cues throughout. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | The jacket, tunic, and skirt read as a coherent layered outfit without trunk-level contradictions. |
| `coordination_penalty` | 0.0 | Styling elements are coordinated around a polished retro-luxe look; no major trunk or accessory clash. |
| `formula_template_penalty` | 0.25 | Uses runway-description framing and mood language, but not enough fixed template structure to warrant a higher penalty. |
| `generation_content_penalty` | 0.25 | Mostly imageable, but includes some evaluative mood language and a long symbol list that slightly reduces prompt efficiency. |
| `rationality_penalty` | 0.0 | All described garments and accessories are physically plausible in ordinary fashion terms. |

## Skipped metrics (不适用)

- `closure` (coverage_score) — No explicit closure method is mentioned; the jacket is described as 'open-front,' which indicates absence of a closure rather than a closure detail.
- `deconstruction` (coverage_score) — The text does not mention deconstruction, splicing, displacement, or reconstruction.
- `footwear` (coverage_score) — No footwear is mentioned in the text.
- `belt` (coverage_score) — No visible belt, sash, waist strap, or harness is described.
- `asymmetry` (coverage_score) — No clear asymmetrical garment structure is described.
- `quantity_accuracy` (quality_score) — The text contains no explicit counts, numerals, or quantity relations that need verification.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral asymmetry is described.
- `cultural_reference` (bonus_score) — No specific cultural, historical, or brand reference is grounded in the description.
- `gender_expression` (bonus_score) — The text does not explicitly discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is stated beyond general styling.
- `brand_alignment` (bonus_score) — No brand language or brand identity is explicitly targeted.
- `negation_control` (bonus_score) — The description does not emphasize exclusions or absence of elements.
