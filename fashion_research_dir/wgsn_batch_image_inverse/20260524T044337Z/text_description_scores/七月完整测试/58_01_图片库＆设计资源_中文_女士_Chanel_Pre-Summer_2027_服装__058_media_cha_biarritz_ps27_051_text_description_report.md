# Text Evaluation Report

- **Source:** 58_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__058_media_cha_biarritz_ps27_051_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.859 (Strong)
- **Coverage axis:** 1.0
- **Quality axis (raw / base / penalized):** 0.8214 / 0.8229 / 0.8229
- **Penalties (mean):** 0.1
- **R_content:** 0.828935

## Gates

- Score gate: 0.859 (threshold 0.7) → **PASS**
- Penalty gate: 0.1 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `bag` | 1.0 | 1 |  | The bag is clearly identified by type, size/shape, and color/material details, satisfying the coverage requirement. |
| `body_coverage` | 1.0 | 1 |  | The text specifies visible body exposure and the covered/revealed upper-body area. |
| `color_relationship_logic` | 1.0 | 1 |  | 文本明确交代了黑色主体与多色条纹、金色首饰之间的对比关系，配色逻辑清晰。 |
| `construction_technique` | 1.0 | 1 |  | It describes a clear construction technique and placement: panelled skirt construction with seam lines, plus fringe/feather-like trim at the hem. |
| `cross_garment_binding` | 1.0 | 1 |  | Multiple items are present and the text distinguishes them clearly by role and placement, separating the dress from the bag and jewelry. |
| `fabric_family` | 1.0 | 1 |  | 主体材质类别明确指向皮革感面料，并补充了羽毛/流苏感装饰。 |
| `footwear` | 1.0 | 1 |  | The text specifies the shoe family and heel form, with visible placement in the look; this is sufficient coverage. |
| `functional_detail` | 1.0 | 1 |  | The text includes functional/structural details on the bag and garment, especially the visible tied detail and seam lines. |
| `garment_category` | 1.0 | 1 |  | The主体品类 is explicitly identified as a dress. |
| `hardware_embellishment` | 1.0 | 1 |  | There are clearly stated metallic embellishments/jewelry, which satisfy the presence of salient hardware-like adornment. |
| `jewelry` | 1.0 | 1 |  | Multiple pieces of prominent jewelry/body adornment are explicitly described. |
| `length_hemline` | 1.0 | 1 |  | Garment length and hem treatment are explicitly described. |
| `pattern_type` | 1.0 | 1 |  | 图案类型明确为条纹。 |
| `primary_color` | 1.0 | 1 |  | 主色明确为黑色。 |
| `secondary_color` | 1.0 | 1 |  | 存在明显副色与配饰色彩，尤其是包袋上的多色条带构成次要色彩信息。 |
| `shoulder_architecture` | 1.0 | 1 |  | The shoulder area is clearly defined through strap and exposure details. |
| `silhouette` | 1.0 | 1 |  | The text clearly states the overall silhouette and its structural shape. |
| `surface_finish` | 1.0 | 1 |  | 文本清楚描述了光泽、微闪与兼具垂坠和挺括的表面/手感特征。 |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes the dress’s upper-to-lower balance through a low waist and voluminous skirt, making the proportion salient. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are clearly attached to the correct entities, and the dress/bag/jewelry/shoes are distinguished well. Minor ambiguity remains in phrases like "bracelet or cuff" and the bag's "tied det |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is compact and heavily garment-focused, with clear main-look details prioritized. There is some stylistic framing at the end, but not enough to significantly dilute the core fashion in |
| `craft_embellishment_salience` | 0.75 | 1 | 工艺装饰显著度 | Craft and trim are clearly present and positioned, especially the hem treatment and panel seams. The description is strong, though the craft language is slightly more descriptive than technical. |
| `design_distinctiveness` | 1.0 | 1 | 设计独特性 | The look has multiple clear memory points: unusual fringe/feather-like hem trim, visible panel construction, and a bold striped tote. These are distinct structural and surface details, not a formula o |
| `design_signal_purity` | 0.75 | 1 | 设计信号纯度 | The text is mostly design-fact driven, with only a brief mood conclusion at the end. The garment details remain dominant and readable. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly visual, garment-first, and mostly prompt-ready with clear silhouette, materials, accessories, and palette. Minor issues remain because it reads a bit like a descriptive fashion anal |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a mostly natural order from main garment to construction details, then accessories and styling. It is clear and easy to reconstruct, though some detail clusters are dense and s |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | Multiple items are described with generally stable bindings across dress, bag, jewelry, and footwear. The text is coherent overall, with only slight looseness in accessory specificity, so it is strong |
| `quantity_accuracy` | 0.75 | 1 | 语言清晰度 | The text uses several quantity-like relations and counts clearly enough overall, with only mild complexity from compound descriptors and long lists. Side references and item counts remain readable and |
| `reference_clarity` | 1.0 | 1 | 语言清晰度 | References are explicit and well anchored to the dress, bag, and styling elements. Pronouns are minimal, and the sentence subjects remain clear throughout. |
| `silhouette_combination_originality` | 1.0 | 1 | 组合原创性 | The silhouette combination is unusual and specific, with a long sleeveless dress, low waist, voluminous skirt, and heavy fringe border. It reads as a distinctive runway construction rather than a comm |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Spatial relations are clear and imageable: the dress silhouette, hem, and bag placement are coherently described. The only limitation is that the text is still somewhat explanatory rather than purely  |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | The text foregrounds visible, image-dominant clothing features and keeps hidden or low-visibility details minimal. Accessories and mood language are present, but they do not overpower the main silhoue |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly anchored in visible garment facts and body zones, with precise placement and silhouette details. Mood language is minimal and does not overwhelm the observation. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | The main dress, bag, and shoes read as a single coherent look with no trunk-level left-right or garment-identity conflict. |
| `coordination_penalty` | 0.0 | Styling elements are coordinated around a polished dramatic palette; no strong clash in the main outfit language. |
| `formula_template_penalty` | 0.25 | The description is mostly specific, but it includes some runway-mood framing and a summary-style palette statement that makes it slightly formulaic. |
| `generation_content_penalty` | 0.25 | Mostly grounded garment description, but begins with runway framing and ends with a mood/palette summary that adds some conceptual prose beyond the imaging trunk. |
| `rationality_penalty` | 0.0 | The described materials and construction are plausible as fashion styling and do not rely on physically impossible garment facts. |

## Skipped metrics (不适用)

- `closure` (coverage_score) — No clear closure detail is mentioned; the dress description does not specify buttons, zipper, ties, buckles, or similar fastening.
- `deconstruction` (coverage_score) — The text does not mention deconstruction, splicing, displacement, or reconstruction.
- `belt` (coverage_score) — No visible belt, sash, waist cincher, or harness is described; the low waistline is a garment cut detail, not a belt.
- `layering` (coverage_score) — The look is described as a single dress with accessories, not as a multi-layer outfit with explicit layering relations.
- `asymmetry` (coverage_score) — No clear asymmetrical garment structure is described; the look reads as generally symmetrical.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral garment differences are described.
- `cultural_reference` (bonus_score) — No cultural, historical, or brand-specific reference is provided.
- `gender_expression` (bonus_score) — The description does not explicitly discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is stated beyond general styling mood.
- `brand_alignment` (bonus_score) — The text does not explicitly target a brand identity or brand language.
- `negation_control` (bonus_score) — The text does not emphasize exclusions or absence of elements.
