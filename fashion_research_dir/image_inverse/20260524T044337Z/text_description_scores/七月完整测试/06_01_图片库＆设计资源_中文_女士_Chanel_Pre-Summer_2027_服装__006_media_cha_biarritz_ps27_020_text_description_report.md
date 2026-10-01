# Text Evaluation Report

- **Source:** 06_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__006_media_cha_biarritz_ps27_020_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.1
- **Total score (S_fp):** 0.8602 (Strong)
- **Coverage axis:** 1.0
- **Quality axis (raw / base / penalized):** 0.8438 / 0.825 / 0.825
- **Penalties (mean):** 0.05
- **R_content:** 0.845147

## Gates

- Score gate: 0.8602 (threshold 0.7) → **PASS**
- Penalty gate: 0.05 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `body_coverage` | 1.0 | 1 |  | The text clearly describes exposed body areas and the degree of coverage. |
| `closure` | 1.0 | 1 |  | The text clearly describes multiple closure types: an open-front coat with buttons and a tie-front top. |
| `color_relationship_logic` | 1.0 | 1 |  | 文本交代了配色逻辑：白色外套作为主框架，内搭为同色调偏柔和的粉彩印花套装，并以亮色手工装饰边形成点缀对比。 |
| `construction_technique` | 1.0 | 1 |  | The text names specific craft/finish techniques and their placement on the garments, including quilted/bouclé-like texture on the coat and embroidery/fringing on the skirt. |
| `cross_garment_binding` | 1.0 | 1 |  | The description clearly distinguishes which attributes belong to the coat versus the separate printed top and skirt, so multi-garment binding is well covered. |
| `fabric_family` | 1.0 | 1 |  | 主体服装材质类别虽未明确到具体纤维，但文本清楚给出可识别的面料/材质家族线索：外层为白色外套，内搭为印花两件套，且有“quilted/bouclé-like effect”提示织物类型感。 |
| `garment_category` | 1.0 | 1 |  | The text clearly names the main garment categories: a coat and a two-piece set. |
| `hardware_embellishment` | 1.0 | 1 |  | There is clear hardware/ornamental embellishment, including metallic buttons and metallic-looking beaded trim. |
| `layering` | 1.0 | 1 |  | The text clearly describes a layered look with an outer coat over a top and skirt, making the visible order and coverage relationship imageable. |
| `length_hemline` | 1.0 | 1 |  | Garment lengths and hem behavior are clearly stated. |
| `pattern_type` | 1.0 | 1 |  | 图案类型明确，为花卉或抽象印花。 |
| `primary_color` | 1.0 | 1 |  | 主色非常明确，外层大衣以白色为主。 |
| `secondary_color` | 1.0 | 1 |  | 存在清晰副色与可见条件：酒红色内里在开口处闪现，另有多色滚边作为辅助色块。 |
| `shoulder_architecture` | 1.0 | 1 |  | The shoulder treatment is explicitly described as dropped and structurally noticeable. |
| `silhouette` | 1.0 | 1 |  | Overall shape is explicitly described for both the coat and the skirt set. |
| `surface_finish` | 1.0 | 1 |  | 明确描述了表面质感与结构感，包括纹理、绗缝/圈圈呢般效果以及垂坠松量。 |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes the upper-to-lower body balance: a long outer coat over a very cropped top and low-rise mini skirt, with exposed midriff indicating a strong top-bottom proportion. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are clearly attached to the correct garment layers, and the coat vs. underlayer distinction is stable. Minor complexity comes from dense descriptive stacking, but there is no major ent |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is compact and heavily focused on visible garment facts, with clear outerwear, top, skirt, and trim details. There is some stylistic framing (“ornate resort-couture mood”), but it does |
| `craft_embellishment_salience` | 1.0 | 1 | 工艺装饰显著度 | Craft is described with type, placement, and visual effect very clearly, and it functions as a main hook of the look. |
| `design_distinctiveness` | 1.0 | 1 | 设计独特性 | The look has multiple clear memory points: unusual tactile trim, textured white coat surface, and a visible contrast lining. This is well beyond a generic resort formula. |
| `design_signal_purity` | 0.75 | 1 | 设计信号纯度 | Most of the text is concrete design observation, but there is one explicit mood framing sentence that slightly reduces purity. |
| `fine_grained_attribute_usage` | 1.0 | 1 | 术语具体度 | Color, texture, trim, lining, and silhouette details are described with fine granularity and strong visual specificity, making the look highly imageable. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly imageable and already organized around visible silhouette, layering, color, and texture, so it is close to a usable prompt. It is slightly more descriptive than prompt-tight, with s |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a mostly natural body-to-detail order: main outer layer first, then underlayers, then styling/completion notes. It is clear and easy to reconstruct, though the long sentence st |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text cleanly separates the coat, top, and skirt, and their shared print relationship is understandable. There is slight density in the description, but no serious cross-binding of attributes acros |
| `quantity_accuracy` | 0.75 | 1 | 语言清晰度 | Quantity relations are mostly clear and stable, but a few references are slightly dense and require careful parsing. The row of buttons and the coordinating set are understandable, with no major confl |
| `reference_clarity` | 0.75 | 1 | 语言清晰度 | Pronoun references are generally clear: 'its' consistently points back to the coat, and the layering sequence is easy to follow. There is minor sentence density, but no serious ambiguity in what each  |
| `silhouette_combination_originality` | 0.75 | 1 | 组合原创性 | The combination is distinctive and fashion-forward, with an oversized coat over a very abbreviated printed set. It is still somewhat within a recognizable resort-couture logic, so not a full 1.0. |
| `spatial_coherence` | 1.0 | 1 | 生成适配度 | Layering, front opening, neckline, and exposure relationships are clearly stated and visually coherent. The garment placement and overlap are easy to reconstruct in image form. |
| `specific_noun_usage` | 1.0 | 1 | 术语具体度 | Uses highly specific garment nouns, construction terms, and accessory/material descriptors throughout, with clear fashion semantics and little reliance on generic wording. |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | The text prioritizes what is actually visible and image-dominant: coat shape, trim, top, skirt, and exposed midriff. It includes one mood-like sentence, but visible garment structure remains clearly p |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly anchored in visible garment parts and readable construction details, with clear separation of visible and hidden elements. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | No trunk-level left-right or garment-identity conflict; the coat, top, and skirt read coherently. |
| `coordination_penalty` | 0.0 | The styling language is unified across outerwear and set, with no major coordination clash. |
| `formula_template_penalty` | 0.0 | Written as continuous grounded prose rather than a rigid template. |
| `generation_content_penalty` | 0.25 | Mostly imageable, but includes some mood-forward runway phrasing that slightly reduces prompt efficiency. |
| `rationality_penalty` | 0.0 | Materials and construction are plausible for fashion description; no physically impossible garment claim. |

## Skipped metrics (不适用)

- `functional_detail` (coverage_score) — No pockets, straps, utility parts, or comparable functional details are described.
- `deconstruction` (coverage_score) — The text does not mention deconstruction, splicing, displacement, or reconstruction as a design method.
- `bag` (coverage_score) — No bag is mentioned or implied as a visible styling element.
- `footwear` (coverage_score) — The text explicitly says footwear is not visible.
- `jewelry` (coverage_score) — No jewelry or body ornament is described.
- `belt` (coverage_score) — No visible belt, sash, waist cincher, or harness is described.
- `asymmetry` (coverage_score) — No clear asymmetrical design or uneven structure is described.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral distinction is described.
- `cultural_reference` (bonus_score) — No specific cultural, historical, or brand reference is grounded in the description.
- `gender_expression` (bonus_score) — The text does not explicitly discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is explicitly stated beyond the outfit description.
- `brand_alignment` (bonus_score) — There is no explicit brand language or brand identity target in the text.
