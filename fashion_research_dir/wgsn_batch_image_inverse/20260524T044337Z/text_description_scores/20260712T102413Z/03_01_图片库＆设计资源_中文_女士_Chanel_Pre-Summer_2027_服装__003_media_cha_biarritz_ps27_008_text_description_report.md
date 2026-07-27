# Text Evaluation Report

- **Source:** 03_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__003_media_cha_biarritz_ps27_008_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.0
- **Total score (S_fp):** 0.7973 (Strong)
- **Coverage axis:** 1.0
- **Quality axis (raw / base / penalized):** 0.7812 / 0.7462 / 0.7462
- **Penalties (mean):** 0.2
- **R_content:** 0.741489

## Gates

- Score gate: 0.7973 (threshold 0.7) → **PASS**
- Penalty gate: 0.2 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `bag` | 1.0 | 1 |  | Bag type, carrying method, shape, and material/color details are clearly described. |
| `body_coverage` | 1.0 | 1 |  | The text describes visible coverage and exposure zones. |
| `closure` | 1.0 | 1 |  | Clear closure details are described through button-front construction and centered button fastening. |
| `color_relationship_logic` | 1.0 | 1 |  | The text explains the color logic as a muted, earthy layered palette with accent colors, not just isolated hue listing. |
| `cross_garment_binding` | 1.0 | 1 |  | The description distinguishes which features belong to the jacket, inner layer, and skirt, so the multi-garment relationships are clearly bound to specific items. |
| `deconstruction` | 1.0 | 1 |  | The description explicitly frames the look as deconstructed and reinforces it with frayed finishing. |
| `fabric_family` | 1.0 | 1 |  | The text clearly indicates a woven textile family and a soft bag material, enough to infer fabric category. |
| `functional_detail` | 1.0 | 1 |  | The text explicitly mentions pockets and a functional shoulder strap, both salient utility details. |
| `garment_category` | 1.0 | 1 |  | The text clearly names the main garment categories. |
| `hardware_embellishment` | 1.0 | 1 |  | Multiple hardware elements are clearly present, including buttons, toggle-like tabs, and a chain strap. |
| `layering` | 1.0 | 1 |  | The text clearly establishes a multi-layer outfit with readable outer jacket, inner layer, and skirt relationships. |
| `length_hemline` | 1.0 | 1 |  | Garment lengths and hem details are directly stated. |
| `pattern_type` | 1.0 | 1 |  | A clear stripe pattern is specified. |
| `primary_color` | 1.0 | 1 |  | The main palette is clearly stated, with pale grey and tan/khaki as dominant colors. |
| `secondary_color` | 1.0 | 1 |  | Distinct secondary accent colors are explicitly described on the garment and bag. |
| `shoulder_architecture` | 1.0 | 1 |  | Shoulder construction is clearly specified. |
| `silhouette` | 1.0 | 1 |  | Overall shape and structural contour are explicitly described. |
| `surface_finish` | 1.0 | 1 |  | Surface qualities are explicitly described, including texture, structure, and softness/crumpling. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes the overall vertical proportion and the relative lengths of the jacket and skirt, making the top-bottom balance imageable. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are clearly attached to the correct garment or accessory, and the layering is understandable. Minor ambiguity remains in phrases like “top or vest” and some overlapping trim/pocket des |
| `core_information_density` | 0.5 | 0 | 信息密度与简洁性 | 主体服装轮廓和关键细节很完整，但描述偏长，层层堆叠材质、边缘、扣件和装饰信息，信息密度中等偏高但不够精炼。 |
| `craft_embellishment_salience` | 0.75 | 1 | 工艺装饰显著度 | Craft and trim details are clearly identified with location and visual effect, though the description is more about surface treatment than a single dominant craft technique. |
| `design_distinctiveness` | 0.75 | 1 | 设计独特性 | The look has a clear memory anchor in the frayed trim and deconstructed-luxe layering, plus an unusual bag color-blocking. Distinctive, though still grounded in a somewhat wearable luxury formula. |
| `design_signal_purity` | 1.0 | 1 | 设计信号纯度 | The text is overwhelmingly composed of concrete design facts, with only a brief mood summary at the end. Design signal is very high and not diluted by essay-like narration. |
| `fine_grained_attribute_usage` | 1.0 | 1 | 术语具体度 | Color, material, texture, and construction details are consistently fine-grained and visually actionable, with strong specificity across the outfit. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly visual and already close to a generation prompt, with clear silhouette, layering, materials, colors, and accessories. It is slightly more descriptive than prompt-tight, but still re |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a mostly natural body-to-garment-to-accessory order and makes the outfit structure easy to reconstruct. There is some density and a few layered detail clusters, but the main vi |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text keeps the jacket, inner layer, skirt, and bag mostly distinct and correctly related. There is slight fuzziness around whether the close-fitting tan piece is a top or vest, but the multi-item  |
| `quantity_accuracy` | 0.75 | 1 | 语言清晰度 | Quantity and extent references are mostly clear and internally consistent, with only minor ambiguity in the cropped visibility and garment layering. |
| `reference_clarity` | 0.75 | 1 | 语言清晰度 | Pronouns and omitted subjects are generally easy to track, and the garment references remain coherent, though the layered outfit description is somewhat dense. |
| `silhouette_combination_originality` | 0.5 | 0 | 组合原创性 | The silhouette is coherent and layered, but the overall combination remains fairly legible and fashion-standard: structured jacket, slim skirt, shoulder bag. The deconstructed trim adds interest witho |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and attachment positions are clearly stated and visually reconstructable. The spatial logic is coherent, with only minor verbosity rather than any real ambiguity. |
| `specific_noun_usage` | 1.0 | 1 | 术语具体度 | Uses highly specific fashion nouns and garment-part terms throughout, with clear item identities and accessory construction. |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | 可见主体轮廓、层次和配色优先写出，整体以外观可见信息为主；虽有少量较细的装饰与结构描述，但没有明显让隐藏信息喧宾夺主。 |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly anchored to visible garment parts and placement, with careful visible/inferred language throughout. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.25 | The trunk is broadly coherent, but the inner layer is described with some identity ambiguity (“top or vest”) and the outfit stacks multiple tan layers without a sharp separation. |
| `coordination_penalty` | 0.25 | The silhouette mixes boxy outerwear, fitted mid-layer, and slim skirt in a way that is still workable, but the styling language is slightly mixed rather than fully unified. |
| `formula_template_penalty` | 0.25 | It follows a common runway-description formula with silhouette, materials, palette, and mood sections, though not in a rigid fixed template. |
| `generation_content_penalty` | 0.25 | Mostly imageable, but it leans into stylistic commentary and dense symbolic detailing, which slightly reduces prompt efficiency. |
| `rationality_penalty` | 0.0 | No clearly impossible materials or physically implausible garment construction are asserted. |

## Quality issues (质量短板)

- **`core_information_density`** (score 0.5) — 主体服装轮廓和关键细节很完整，但描述偏长，层层堆叠材质、边缘、扣件和装饰信息，信息密度中等偏高但不够精炼。
- **`silhouette_combination_originality`** (score 0.5) — The silhouette is coherent and layered, but the overall combination remains fairly legible and fashion-standard: structured jacket, slim skirt, shoulder bag. The deconstructed trim adds interest without fully escaping a predictable luxury template.

## Skipped metrics (不适用)

- `construction_technique` (coverage_score) — No specific fabrication technique like quilting, pleating, embroidery, cut-outs, or engineered panel work is clearly identified.
- `footwear` (coverage_score) — No footwear is mentioned in the text.
- `jewelry` (coverage_score) — No salient jewelry or body ornament is described.
- `belt` (coverage_score) — No visible belt, sash, or waist strap/harness is mentioned; waist shaping comes from garment cut only.
- `asymmetry` (coverage_score) — No clear asymmetrical design, one-shoulder, uneven hem, or similar structure is described.
- `bilateral_coherence` (quality_score) — No explicit left-right bilateral contrast is described for sleeves, legs, shoes, or other paired trunk elements.
- `cultural_reference` (bonus_score) — No clear cultural, historical, or brand-specific reference is provided.
- `gender_expression` (bonus_score) — The description does not explicitly discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is explicitly stated.
- `brand_alignment` (bonus_score) — There is no explicit brand language or brand identity target.
- `negation_control` (bonus_score) — The text does not emphasize exclusions or absence of elements.
