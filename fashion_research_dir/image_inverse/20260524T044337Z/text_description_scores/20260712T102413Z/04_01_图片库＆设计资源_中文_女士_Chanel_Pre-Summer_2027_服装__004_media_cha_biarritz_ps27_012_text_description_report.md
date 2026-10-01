# Text Evaluation Report

- **Source:** 04_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__004_media_cha_biarritz_ps27_012_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.0
- **Total score (S_fp):** 0.8235 (Strong)
- **Coverage axis:** 1.0
- **Quality axis (raw / base / penalized):** 0.7969 / 0.7782 / 0.7782
- **Penalties (mean):** 0.1
- **R_content:** 0.794678

## Gates

- Score gate: 0.8235 (threshold 0.7) → **PASS**
- Penalty gate: 0.1 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `bag` | 1.0 | 1 |  | The text clearly identifies the bag type, how it is carried, and its material/finish. |
| `body_coverage` | 1.0 | 1 |  | The text indicates the visible body coverage and exposed leg area. |
| `color_relationship_logic` | 1.0 | 1 |  | The text explains the color logic as a cream-dominant palette with contrasting black piping and a bright yellow accent. |
| `construction_technique` | 1.0 | 1 |  | A specific craft technique is named and localized to the edge of the draped textile piece. |
| `cross_garment_binding` | 1.0 | 1 |  | Multiple items are described with distinct roles, and the text distinguishes which attributes belong to the shorts, boots, draped textile, and bag. |
| `fabric_family` | 1.0 | 1 |  | The text clearly identifies material/fabric families or textile types for multiple items, including a textile wrap/coat-like piece and a plush fuzzy bag. |
| `footwear` | 1.0 | 1 |  | Footwear is clearly specified with shoe family, shaft height/shape, and color/material-like surface details. |
| `functional_detail` | 1.0 | 1 |  | The text includes functional/attached styling elements and carried accessory-like details, though not a classic pocket or strap. |
| `garment_category` | 1.0 | 1 |  | The text clearly identifies the main garment categories worn in the look. |
| `layering` | 1.0 | 1 |  | The text describes multiple visible textile layers and their relative placement, making the layering readable. |
| `length_hemline` | 1.0 | 1 |  | The text gives clear length information for both shorts and boots. |
| `pattern_type` | 1.0 | 1 |  | Pattern/decorative treatment is clearly described through appliqué/embroidery-like motifs and fringed textile detailing. |
| `primary_color` | 1.0 | 1 |  | Cream is the dominant and repeatedly emphasized main color across the look. |
| `secondary_color` | 1.0 | 1 |  | Clear secondary accent colors are present alongside the cream base, especially black and pale blue. |
| `silhouette` | 1.0 | 1 |  | It explicitly describes the overall silhouette and structural contour. |
| `surface_finish` | 1.0 | 1 |  | Surface qualities are explicitly described, including smoothness, fuzziness, and a clean structured shaft. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly establishes the vertical proportion from waist to feet and describes the main lower-body silhouette, making the top-bottom balance imageable. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are bound to the correct garment or accessory, and the text keeps shorts, boots, wrap/coat, and bag distinct. Minor ambiguity remains in the speculative 'possibly a coat or wrap' phras |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | 主体服装轮廓清楚，信息主要围绕短裤、长靴和手持配件展开；但对材质、边缘装饰和侧边层叠的描述较多，略有冗余，降低了整体压缩度。 |
| `craft_embellishment_salience` | 0.75 | 1 | 工艺装饰显著度 | Craft details are clearly identified and located along edges/layers, with a visible decorative role. The exact technique is somewhat hedged, so it is strong but not perfect. |
| `design_distinctiveness` | 0.75 | 1 | 设计独特性 | The look has several clear memory anchors: sporty piping on shorts, unusual cream thigh-high boots with color accents, and a plush yellow mini bag. Distinctive, though not fully singular or highly exp |
| `design_signal_purity` | 0.75 | 1 | 设计信号纯度 | Most of the text is devoted to concrete design facts, materials, placement, and visible detailing. There is a brief summary impression, but it does not overwhelm the design signal. |
| `fine_grained_attribute_usage` | 1.0 | 1 | 术语具体度 | Attributes are richly and precisely specified across color, material/texture, and structure, producing a vivid and imageable fashion description. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is already close to a usable image prompt: it clearly states the silhouette, garment types, colors, and key accessories. It is slightly verbose and reads partly like a descriptive analysis, b |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a mostly natural body-to-detail order: overall framing, main garments, footwear, then handheld accessories and side-layer notes. It is easy to reconstruct the look, though the  |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The description handles multiple items with generally stable attribution: shorts, boots, draped textile, and bag each receive their own properties. There is slight uncertainty around the draped textil |
| `quantity_accuracy` | 0.75 | 1 | 语言清晰度 | Quantities and side relations are mostly clear, with only mild ambiguity in phrases like "a cream textile piece" and "possibly a coat or wrap," which do not materially disrupt understanding. |
| `reference_clarity` | 0.75 | 1 | 语言清晰度 | References are generally well anchored to the model and visible items. A few hedged references such as "carries or drapes" and "possibly a coat or wrap" introduce slight uncertainty, but the overall d |
| `silhouette_combination_originality` | 0.75 | 1 | 组合原创性 | The combination of sporty shorts, thigh-high boots, and an ornate draped textile is more specific than a standard formula look. It still reads as a coherent fashion styling rather than radically unexp |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | The layering and placement relations are mostly clear and imageable: a cropped view, a hanging textile beside the leg, and a partially visible outer layer at the frame edge. Minor ambiguity remains ar |
| `specific_noun_usage` | 1.0 | 1 | 术语具体度 | Uses highly specific fashion nouns and garment/accessory terms, with clear item types and construction details rather than generic descriptions. |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | 优先描述了可见且决定成像的下半身主体与手持包袋，整体可视化导向明确；不过仍加入了较多边缘层与装饰性推测，略分散注意力。 |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly anchored in visible, body-part-specific observations and includes explicit visibility cues and framing references. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | Main garments read coherently; no strong trunk-level left-right or mutually exclusive garment conflict is described. |
| `coordination_penalty` | 0.0 | The mixed sporty and ornate elements are still coordinated into one look without a clear trunk-level styling clash. |
| `formula_template_penalty` | 0.25 | Uses a common runway-description formula with summary-style mood language, but not enough fixed templating to be heavily penalized. |
| `generation_content_penalty` | 0.25 | Mostly imageable, but includes some runway-summary language and conceptual styling wrap-up that slightly reduces prompt efficiency. |
| `rationality_penalty` | 0.0 | All described materials and worn items are physically plausible; no impossible construction is asserted as a main fact. |

## Skipped metrics (不适用)

- `shoulder_architecture` (coverage_score) — No salient shoulder or sleeve structure is described.
- `closure` (coverage_score) — No explicit closure detail such as buttons, zippers, ties, or buckles is mentioned.
- `deconstruction` (coverage_score) — The text suggests layered styling but does not explicitly describe deconstruction, splicing, displacement, or reconstruction.
- `hardware_embellishment` (coverage_score) — No clear hardware embellishments such as chains, studs, rings, or crystals are mentioned.
- `jewelry` (coverage_score) — No jewelry or body ornament is explicitly present.
- `belt` (coverage_score) — No visible belt, sash, waist strap, or harness is described.
- `asymmetry` (coverage_score) — No clear asymmetrical garment structure is described.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral contrast is described.
- `cultural_reference` (bonus_score) — No clear cultural, historical, or brand-specific reference is provided.
- `gender_expression` (bonus_score) — The description does not explicitly discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is stated beyond the outfit description.
- `brand_alignment` (bonus_score) — No brand identity or brand-language target is mentioned.
- `negation_control` (bonus_score) — The text does not emphasize exclusions or absence of elements.
