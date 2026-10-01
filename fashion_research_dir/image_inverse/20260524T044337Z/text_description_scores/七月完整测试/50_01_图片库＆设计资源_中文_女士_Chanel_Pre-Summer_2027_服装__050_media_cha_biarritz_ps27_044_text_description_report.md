# Text Evaluation Report

- **Source:** 50_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__050_media_cha_biarritz_ps27_044_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.813 (Strong)
- **Coverage axis:** 0.8947
- **Quality axis (raw / base / penalized):** 0.8077 / 0.7917 / 0.7917
- **Penalties (mean):** 0.1
- **R_content:** 0.784545

## Gates

- Score gate: 0.813 (threshold 0.7) → **PASS**
- Penalty gate: 0.1 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `asymmetry` | 1.0 | 1 |  | An explicit asymmetric hem is described, so the metric is clearly covered. |
| `bag` | 1.0 | 1 |  | The bag is clearly identified by type/handling, shape/structure, and color/material detailing. |
| `body_coverage` | 1.0 | 1 |  | The text clearly describes a significant body-reveal element at the neckline. |
| `closure` | 0.0 | 0 |  | A tie-like detail is mentioned, but no clear garment closure mechanism is described. |
| `color_relationship_logic` | 1.0 | 1 |  | 文本给出了明确的配色逻辑：主体为单色黑，配以高对比的多色包袋作为点缀，主次关系清楚。 |
| `cross_garment_binding` | 1.0 | 1 |  | The description clearly distinguishes which attributes belong to the top and which belong to the skirt, satisfying cross-garment binding. |
| `fabric_family` | 1.0 | 1 |  | 主体材质虽未给出具体纤维名，但明确描述了面料家族特征为有纹理、带微闪的礼服感面料，并且整体为同一套装面料语境。 |
| `footwear` | 0.0 | 0 |  | Footwear is mentioned, but the description does not clearly specify shoe type or enough form/material detail to meet the coverage rule. |
| `garment_category` | 1.0 | 1 |  | The text clearly identifies the main garment categories: a top and a midi skirt. |
| `jewelry` | 1.0 | 1 |  | A visible jewelry detail is explicitly present. |
| `layering` | 1.0 | 1 |  | The text clearly describes a layered relationship between top and skirt with readable ordering. |
| `length_hemline` | 1.0 | 1 |  | Both garment length and hemline behavior are clearly stated. |
| `pattern_type` | 1.0 | 1 |  | 图案类型明确，包括竖向条纹以及花卉/挂毯感图案侧片。 |
| `primary_color` | 1.0 | 1 |  | 主色明确为黑色。 |
| `secondary_color` | 1.0 | 1 |  | 除主体黑色外，包袋存在明显副色与多色条纹/拼接，属于清晰可见的次要色彩信息。 |
| `shoulder_architecture` | 1.0 | 1 |  | The shoulder treatment is salient and clearly described as sleeveless with broad shoulders. |
| `silhouette` | 1.0 | 1 |  | It explicitly describes the overall shape and structural contour. |
| `surface_finish` | 1.0 | 1 |  | 文本清楚给出表面性质：微微闪烁的光泽感，以及裙装的流动垂坠感。 |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes the relationship between the upper and lower pieces and emphasizes overall vertical proportion. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 1.0 | 1 | 属性绑定准确度 | Attributes are consistently tied to the correct entities: top, skirt, bag, and hand placement are all clearly distinguished with no major cross-binding. |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is mostly concentrated on visible garment facts and styling, with clear silhouette, fabric, hem, and bag details. There is some interpretive phrasing like “dress-like evening effect” a |
| `craft_embellishment_salience` | 0.75 | 1 | 工艺装饰显著度 | A specific decorative/craft detail is identified with location and visual effect, especially the rosette/tied point at the neckline. The craft is clear, though not highly elaborate. |
| `design_distinctiveness` | 0.75 | 1 | 设计独特性 | The look has several memorable anchors: textured sparkle, a rosette/tied neckline detail, asymmetric hem, and a graphic striped tote. These are distinct and not formulaic, though the garment set itsel |
| `design_signal_purity` | 0.75 | 1 | 设计信号纯度 | The text is dominated by concrete design facts, with only a small amount of interpretive phrasing such as the dress-like effect. Design signal remains strong and mostly unblurred. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly imageable and already organized around visible silhouette, garment layers, and accessories, so it is close to a usable generation prompt. It is still somewhat descriptive and explan |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a mostly natural order from overall look to garment layers, then silhouette, fabric, skirt details, accessories, and footwear. It is clear and easy to reconstruct, though some  |
| `multi_garment_binding` | 1.0 | 1 | 属性绑定准确度 | The description cleanly separates multiple garments and accessories, and each set of attributes is assigned to the correct item without confusion. |
| `reference_clarity` | 1.0 | 1 | 语言清晰度 | References are stable and unambiguous; each sentence clearly anchors to a specific garment or accessory without confusing pronouns or omitted subjects. |
| `silhouette_combination_originality` | 0.5 | 0 | 组合原创性 | The separated top-and-skirt evening set with an elongated silhouette is polished and coherent, but not especially unexpected. It is more refined than novel. |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and placement are clearly described, and the asymmetric hem is visually coherent and easy to imagine. The spatial relations are mostly clean and reconstructable, with only minor descriptive l |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | The text generally prioritizes visible, image-dominant elements such as the ensemble, hem shape, and bag, while also acknowledging limited visibility where relevant. Minor attention goes to less impor |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly anchored in visible garment facts and body locations, with clear layering and hem placement. It reads like direct runway observation rather than mood prose. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | The top, skirt, and accessories read as a coherent single look with no trunk-level left-right or material conflicts. |
| `coordination_penalty` | 0.0 | Overall styling is coordinated; the bag is contrasting but not in conflict with the black ensemble, and footwear is not clearly described as discordant. |
| `formula_template_penalty` | 0.25 | The look is somewhat formulaic and runway-generic, but it remains grounded in specific garment construction and texture rather than relying on a fully interchangeable cruise/resort template. |
| `generation_content_penalty` | 0.25 | Mostly grounded garment description, but includes some runway-style evaluative framing and repeated silhouette commentary that slightly reduces prompt efficiency. |
| `rationality_penalty` | 0.0 | All described materials and construction are physically plausible in ordinary fashion wear. |

## Missing coverage (未覆盖)

- **`closure`** — A tie-like detail is mentioned, but no clear garment closure mechanism is described.
- **`footwear`** — Footwear is mentioned, but the description does not clearly specify shoe type or enough form/material detail to meet the coverage rule.

## Quality issues (质量短板)

- **`silhouette_combination_originality`** (score 0.5) — The separated top-and-skirt evening set with an elongated silhouette is polished and coherent, but not especially unexpected. It is more refined than novel.

## Skipped metrics (不适用)

- `functional_detail` (coverage_score) — No pockets, straps, or utility features are described on the clothing.
- `construction_technique` (coverage_score) — The text describes texture and drape, but not a specific named construction technique with placement.
- `deconstruction` (coverage_score) — No deconstruction, splicing, displacement, or reconstruction is mentioned.
- `hardware_embellishment` (coverage_score) — No salient hardware or metallic embellishment is described.
- `belt` (coverage_score) — No visible belt, sash, waist strap, or harness is described.
- `quantity_accuracy` (quality_score) — The text does not use explicit quantities, counts, or numerical relations that need quantity verification.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral garment differences are described.
- `cultural_reference` (bonus_score) — No cultural, historical, or brand grounding is provided.
- `gender_expression` (bonus_score) — No explicit gender expression or androgyny is mentioned.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is stated.
- `brand_alignment` (bonus_score) — No brand language or brand identity target is mentioned.
