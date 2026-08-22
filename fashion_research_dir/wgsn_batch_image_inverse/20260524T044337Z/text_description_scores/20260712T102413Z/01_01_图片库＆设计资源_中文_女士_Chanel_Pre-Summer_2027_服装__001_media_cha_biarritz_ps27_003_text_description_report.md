# Text Evaluation Report

- **Source:** 01_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__001_media_cha_biarritz_ps27_003_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.0
- **Total score (S_fp):** 0.8446 (Strong)
- **Coverage axis:** 1.0
- **Quality axis (raw / base / penalized):** 0.875 / 0.8051 / 0.8051
- **Penalties (mean):** 0.1
- **R_content:** 0.815039

## Gates

- Score gate: 0.8446 (threshold 0.7) → **PASS**
- Penalty gate: 0.1 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `bag` | 1.0 | 1 |  | Bag is a salient styling element and the text covers category, material/texture, color, and carrying method. |
| `body_coverage` | 1.0 | 1 |  | The text clearly describes exposed legs and layered coverage. |
| `closure` | 1.0 | 1 |  | A clear front button closure is described. |
| `color_relationship_logic` | 1.0 | 1 |  | The text explains the palette logic as a black base with bright contrasting handmade accents, plus a red accessory that echoes the jacket embellishments. |
| `construction_technique` | 1.0 | 1 |  | A specific craft technique is identified and localized to the neckline, front edges, and cuffs. |
| `cross_garment_binding` | 1.0 | 1 |  | The description distinguishes which attributes belong to the jacket, underlayer, shorts, and handbag, making the multi-item composition clear. |
| `fabric_family` | 1.0 | 1 |  | The text clearly indicates textile/material families: a textured jacket and crochet-like decorative elements, plus a crochet handbag. |
| `functional_detail` | 1.0 | 1 |  | The text mentions a pocket on the jacket and a functional carried bag with straps/handles. |
| `garment_category` | 1.0 | 1 |  | The text clearly identifies the main garment categories: jacket, top, shorts, and handbag. |
| `hardware_embellishment` | 1.0 | 1 |  | Visible hardware and metallic embellishment are explicitly described. |
| `layering` | 1.0 | 1 |  | Clear outerwear-over-underlayer relationship is described and visually reconstructible. |
| `length_hemline` | 1.0 | 1 |  | The text gives clear garment length and hemline information. |
| `pattern_type` | 1.0 | 1 |  | A decorative motif is described, including floral/starfish-shaped elements, which functions as a clear pattern/type of ornamentation. |
| `primary_color` | 1.0 | 1 |  | Black is the dominant base color across the main garments. |
| `secondary_color` | 1.0 | 1 |  | Secondary accent colors are clearly present, especially the vivid red accessory and multicolor embellishments against the black base. |
| `silhouette` | 1.0 | 1 |  | Overall shape and structural contour are explicitly described. |
| `surface_finish` | 1.0 | 1 |  | Surface and handfeel traits are explicitly described, including texture, structure, and a softly flared hem. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes the upper and lower proportions and their visual balance, with a cropped jacket over abbreviated shorts. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 1.0 | 1 | 属性绑定准确度 | Attributes are consistently attached to the correct garments and accessory, with clear separation between jacket, underlayer, shorts, and handbag. |
| `core_information_density` | 0.5 | 0 | 信息密度与简洁性 | 主体服装轮廓清楚，且关键可见信息较多；但描述偏长，装饰细节、材质与情绪总结占比高，信息组织略显堆叠，主干虽明确但不够精炼。 |
| `craft_embellishment_salience` | 1.0 | 1 | 工艺装饰显著度 | The craft is clearly identified by type, placement, and visual effect, and it functions as a main design feature. |
| `design_distinctiveness` | 1.0 | 1 | 设计独特性 | The look has multiple strong memory anchors: unusual crochet-like appliqué/charm trim placement, a distinctive multicolor handmade motif, and a matching openwork crochet bag. |
| `design_signal_purity` | 1.0 | 1 | 设计信号纯度 | The text is dominated by concrete design facts, with very little mood or essay-like filler; it reads like a precise runway caption. |
| `fine_grained_attribute_usage` | 1.0 | 1 | 术语具体度 | Color, material, construction, silhouette, and trim details are all described with fine-grained fashion language and strong visual specificity. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly imageable and already close to a prompt, with clear garment types, layering, silhouette, and accessory details. It is slightly verbose and reads partly like a design description, bu |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a mostly natural order from main garment to layered pieces, then to construction details, lower-half styling, and finally the accessory. It is clear and easy to reconstruct, th |
| `multi_garment_binding` | 1.0 | 1 | 属性绑定准确度 | Multiple garments are described with stable bindings and coherent layering; no major attribute drift or cross-assignment is present. |
| `quantity_accuracy` | 1.0 | 1 | 语言清晰度 | Quantities and count-like relations are internally consistent and easy to parse; no conflicting numbers or ambiguous count references appear. |
| `reference_clarity` | 1.0 | 1 | 语言清晰度 | References are explicit and stable, with clear antecedents for pronouns and ellipsis; the garment descriptions remain easy to track throughout. |
| `silhouette_combination_originality` | 0.75 | 1 | 组合原创性 | The combination is specific and somewhat unexpected, especially the embellished boxy jacket with sporty bike shorts and a handmade crochet bag, though the base formula remains relatively legible. |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and attachment positions are clearly described and visually reconstructable. Minor verbosity aside, the spatial relations are coherent and easy to image. |
| `specific_noun_usage` | 1.0 | 1 | 术语具体度 | The description uses highly specific fashion nouns and accessory terms throughout, clearly identifying garment types, trims, and hardware. |
| `visibility_priority` | 0.5 | 0 | 信息密度与简洁性 | 可见主体如外套、内搭、短裤和手袋都有优先描述；但仍加入较多边缘装饰、工艺与风格总结，部分篇幅被次要细节占用，影响可见主体的优先级。 |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is tightly anchored to visible garment zones and readable layers, with clear front/edge/cuff/hem observations. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | The trunk garments read coherently; no left-right or mutually exclusive garment identities are described. |
| `coordination_penalty` | 0.0 | The styling contrast is intentional but unified; the jacket, shorts, and bag coordinate through black base, red accents, and craft texture. |
| `formula_template_penalty` | 0.25 | The description follows a common look-description formula with mood conclusion, but it does not rely on rigid section headers or heavy template markers. |
| `generation_content_penalty` | 0.25 | Mostly imageable garment description, but it includes runway/editorial framing and a concluding mood statement that adds conceptual prose beyond the core look. |
| `rationality_penalty` | 0.0 | All materials and construction cues are physically plausible as fashion details. |

## Quality issues (质量短板)

- **`core_information_density`** (score 0.5) — 主体服装轮廓清楚，且关键可见信息较多；但描述偏长，装饰细节、材质与情绪总结占比高，信息组织略显堆叠，主干虽明确但不够精炼。
- **`visibility_priority`** (score 0.5) — 可见主体如外套、内搭、短裤和手袋都有优先描述；但仍加入较多边缘装饰、工艺与风格总结，部分篇幅被次要细节占用，影响可见主体的优先级。

## Skipped metrics (不适用)

- `shoulder_architecture` (coverage_score) — No prominent shoulder-specific construction is described.
- `deconstruction` (coverage_score) — The text does not mention deconstruction, splicing, displacement, or reconstruction.
- `footwear` (coverage_score) — No footwear is described.
- `jewelry` (coverage_score) — No jewelry or body ornament is explicitly present.
- `belt` (coverage_score) — No visible belt, sash, or waist strap is mentioned.
- `asymmetry` (coverage_score) — No clear asymmetrical design, one-shoulder, uneven hem, or single-sleeve structure is described.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral asymmetry is described.
- `cultural_reference` (bonus_score) — No clear cultural, historical, or brand-specific reference is provided.
- `gender_expression` (bonus_score) — The description does not explicitly discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is explicitly stated beyond general styling.
- `brand_alignment` (bonus_score) — There is no explicit brand language or brand identity target.
- `negation_control` (bonus_score) — The text does not emphasize exclusions or absence of elements.
