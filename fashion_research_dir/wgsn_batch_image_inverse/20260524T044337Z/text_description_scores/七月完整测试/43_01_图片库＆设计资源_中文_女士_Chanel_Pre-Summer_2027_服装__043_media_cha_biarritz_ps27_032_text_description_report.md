# Text Evaluation Report

- **Source:** 43_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__043_media_cha_biarritz_ps27_032_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.8685 (Strong)
- **Coverage axis:** 0.9231
- **Quality axis (raw / base / penalized):** 0.8393 / 0.8542 / 0.8542
- **Penalties (mean):** 0.1
- **R_content:** 0.838102

## Gates

- Score gate: 0.8685 (threshold 0.7) → **PASS**
- Penalty gate: 0.1 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `asymmetry` | 1.0 | 1 |  | Asymmetry is explicitly stated and visually grounded in the trailing panel on one side. |
| `body_coverage` | 1.0 | 1 |  | The text describes notable exposure at the chest and close body coverage through the bodice. |
| `cross_garment_binding` | 1.0 | 1 |  | The text distinguishes which draped elements belong to the gown versus the carried trailing panel, making the multi-part garment relation clear. |
| `fabric_family` | 0.0 | 0 |  | The text suggests surface qualities but does not clearly identify a material family such as silk, satin, wool, leather, etc. |
| `footwear` | 1.0 | 1 |  | Footwear is explicitly identified with type and color/material tone, satisfying coverage. |
| `garment_category` | 1.0 | 1 |  | The主体品类 is explicitly identified as a gown/dress. |
| `layering` | 1.0 | 1 |  | The text clearly describes layered garment relations and draped additions with visible placement and attachment context. |
| `length_hemline` | 1.0 | 1 |  | Length and hem behavior are explicitly stated. |
| `primary_color` | 1.0 | 1 |  | The main color is clearly stated as a warm camel-gold tone. |
| `shoulder_architecture` | 1.0 | 1 |  | Shoulder structure is salient through broad straps and cape-like shoulder drape. |
| `silhouette` | 1.0 | 1 |  | The text clearly describes the overall silhouette and structural contour. |
| `surface_finish` | 1.0 | 1 |  | Surface behavior is explicitly described with finish and drape qualities. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes the silhouette’s upper-to-lower balance and waist-to-hem proportion. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are clearly tied to the correct garment parts and side references are explicit. Minor ambiguity remains around the exact relationship between the draped panels, cape sleeves, and the c |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is compact and heavily focused on visible garment facts, with clear silhouette, neckline, surface, drape, and footwear details. There is some stylistic framing and repeated emphasis on |
| `craft_embellishment_salience` | 1.0 | 1 | 工艺装饰显著度 | The embellishment is clearly identified by type, position, and role as a focal point at the chest. The text also notes surface treatment in a way that supports the garment’s visual read. |
| `design_distinctiveness` | 1.0 | 1 | 设计独特性 | The look has multiple clear memory points: a prominent rosette/appliqué, cape-like draped panels, and an asymmetrical carried train. These are structural and craft-based, not formula resort basics. |
| `design_signal_purity` | 1.0 | 1 | 设计信号纯度 | The text is dominated by concrete design facts: cut, placement, drape, surface, and footwear. There is minimal mood language, so the design signal remains very pure. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly visual and mostly prompt-ready, with clear silhouette, garment type, drape, and footwear. It reads slightly like a design description rather than a direct generation prompt, but onl |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description generally follows a clear top-down structure from overall look to garment shape, surface, drape, and footwear. Minor compression and some late-added side details slightly interrupt the |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text describes multiple components and keeps them mostly separated: dress, draped panels, trailing panel/train, and footwear. There is slight binding ambiguity between the cape-like panels and the |
| `quantity_accuracy` | 0.75 | 1 | 语言清晰度 | The side reference is mostly clear and the quantity relation is understandable, but the description introduces multiple similar draped elements that require a bit of parsing to separate from the main  |
| `reference_clarity` | 0.75 | 1 | 语言清晰度 | Pronouns and spatial references are generally well anchored, with only minor complexity from repeated references to panels, train, and draped sleeves. |
| `silhouette_combination_originality` | 1.0 | 1 | 组合原创性 | This is a distinctive gown composition with cape-like drape and a carried train, not a common formula template. The combination of silhouette, drape, and asymmetrical trailing volume is highly specifi |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and attachment positions are clearly described and imageable, including front focal point, shoulder/back drape, and a carried side train. The only minor issue is that the carried panel is som |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | The text prioritizes highly visible, image-dominant elements like neckline, rosette, drape, hem, and sandals. It also briefly mentions less visible or absent accessories, but these do not dominate the |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly anchored in visible garment parts and spatial placement, with clear front/back and hem-level observations. It reads like a direct runway observation rather than mood prose. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | The look reads as one coherent gown with matching drape and compatible footwear; no trunk-level left-right contradiction. |
| `coordination_penalty` | 0.0 | Color, drape, and footwear are coordinated into a unified monochrome styling language. |
| `formula_template_penalty` | 0.25 | Some runway-description formula is present, but the look is still anchored by specific craft details like the rosette/appliqué and draped panels. |
| `generation_content_penalty` | 0.25 | Mostly grounded garment description, but includes some evaluative/runway-style framing that slightly reduces prompt efficiency. |
| `rationality_penalty` | 0.0 | All described materials and construction are plausible for a fashion garment; no physically implausible wear or fabrication claims. |

## Missing coverage (未覆盖)

- **`fabric_family`** — The text suggests surface qualities but does not clearly identify a material family such as silk, satin, wool, leather, etc.

## Skipped metrics (不适用)

- `secondary_color` (coverage_score) — No distinct secondary color is clearly described; the look reads as monochrome with tonal footwear.
- `color_relationship_logic` (coverage_score) — The text does not present a multi-tone or contrasting color story beyond a single monochrome palette.
- `pattern_type` (coverage_score) — No explicit pattern or print is described.
- `closure` (coverage_score) — No explicit closure detail is mentioned.
- `functional_detail` (coverage_score) — No pockets, straps as utility parts, or other functional details are described.
- `construction_technique` (coverage_score) — The text describes drape, rosette/appliqué, and texture, but not a clearly named construction technique with a specific placement.
- `deconstruction` (coverage_score) — No deconstruction, splicing, displacement, or reconstruction is explicitly mentioned.
- `hardware_embellishment` (coverage_score) — No hardware or metal embellishment is described.
- `bag` (coverage_score) — No bag is described or visually emphasized.
- `jewelry` (coverage_score) — The text explicitly says there is "no prominent jewelry".
- `belt` (coverage_score) — No visible belt, sash, or waist strap is present; the waist shaping comes from the dress cut.
- `bilateral_coherence` (quality_score) — No explicit left-right bilateral contrast is described; the asymmetry is only a single-side trailing panel, not a bilateral mismatch.
- `cultural_reference` (bonus_score) — No cultural, historical, or brand-specific reference is provided.
- `gender_expression` (bonus_score) — The description does not explicitly discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is explicitly stated.
- `brand_alignment` (bonus_score) — The text does not target a brand identity or brand language.
