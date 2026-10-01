# Text Evaluation Report

- **Source:** 19_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__019_media_cha_biarritz_ps27_067_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.8837 (Strong)
- **Coverage axis:** 1.0
- **Quality axis (raw / base / penalized):** 0.8462 / 0.8542 / 0.8542
- **Penalties (mean):** 0.1
- **R_content:** 0.85277

## Gates

- Score gate: 0.8837 (threshold 0.7) → **PASS**
- Penalty gate: 0.1 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `asymmetry` | 1.0 | 1 |  | A clear one-shoulder asymmetrical detail is explicitly described. |
| `bag` | 1.0 | 1 |  | Bag is clearly salient and the text covers type, carry method, size, color, and material/finish. |
| `closure` | 1.0 | 1 |  | Closure is explicitly described via buttons on both layers. |
| `color_relationship_logic` | 1.0 | 1 |  | 文本交代了主次色关系：浅灰/米白为主体，黑色文字块作为印花对比，酒红仅在开口处露出作为内里强调。 |
| `cross_garment_binding` | 1.0 | 1 |  | The description distinguishes which features belong to the coat, inner layer, and skirt, making the multi-garment structure clear. |
| `fabric_family` | 1.0 | 1 |  | 主体面料类别明确：服装主体为印花织物，配件也点出皮革感与羽毛/纺织装饰材质。 |
| `functional_detail` | 1.0 | 1 |  | A functional carrying strap for the shoulder bag is clearly mentioned. |
| `garment_category` | 1.0 | 1 |  | The text clearly identifies the main garment categories in the look. |
| `hardware_embellishment` | 1.0 | 1 |  | Multiple hardware/metal embellishments are clearly present, including buttons, chain strap, and rings. |
| `jewelry` | 1.0 | 1 |  | Multiple pieces of jewelry/body adornment are explicitly present and salient. |
| `layering` | 1.0 | 1 |  | The outfit clearly describes layered garments with readable outer-to-inner relationships. |
| `length_hemline` | 1.0 | 1 |  | The text gives clear length and hemline information for the look and garments. |
| `pattern_type` | 1.0 | 1 |  | 图案类型明确为报纸印花，并辅以文字块与图形面板的描述。 |
| `primary_color` | 1.0 | 1 |  | 主色清楚为浅灰与米白的协调配色。 |
| `secondary_color` | 1.0 | 1 |  | 存在明显副色与点缀色：黑色文字块、低饱和图形块，以及可见的酒红内里。 |
| `shoulder_architecture` | 1.0 | 1 |  | Shoulder emphasis is salient and explicitly described through the epaulet-like embellishment and collar structure. |
| `silhouette` | 1.0 | 1 |  | Overall shape and structural contour are explicitly described. |
| `surface_finish` | 1.0 | 1 |  | 文本明确给出硬挺/结构感与毛绒触感等表面性质，足以判断材质表面效果。 |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes the overall vertical proportion and balance of the look, including the long coat over a short mini skirt and the cropped framing. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are clearly tied to the correct garment or accessory, with layered items distinguished well. Minor ambiguity remains in phrases like "jacket or shirt layer" and "feathered or shredded- |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is mostly packed with concrete garment facts and layering details, with only a small amount of mood framing at the end. It remains prompt-useful and visually grounded, though slightly  |
| `craft_embellishment_salience` | 1.0 | 1 | 工艺装饰显著度 | Craft and embellishment are clearly specified by type, placement, and visual role, and they function as major hooks in the look. |
| `design_distinctiveness` | 1.0 | 1 | 设计独特性 | The look has multiple clear memory points: an unusual newspaper-print textile, a shearling-trimmed collar, and a dramatic feathered/shredded shoulder embellishment. |
| `design_signal_purity` | 1.0 | 1 | 设计信号纯度 | The text is dominated by concrete design facts rather than mood essay, so the design signal stays very pure. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly visual and already organized around silhouette, layers, materials, and accessories, so it is close to a usable generation prompt. Minor reduction because it still reads somewhat lik |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a mostly natural top-to-bottom garment order: overall framing, outer layer, inner layer, bottom, then accessories. It is clear and easy to reconstruct, though some detail clust |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text separates coat, inner layer, skirt, and bag cleanly, so multi-item binding is mostly stable. There is slight fuzziness in the exact identity of the inner layer and the shoulder embellishment, |
| `reference_clarity` | 1.0 | 1 | 语言清晰度 | References are consistently anchored to clear nouns and layer labels, with no confusing pronoun chains or ambiguous omissions. |
| `silhouette_combination_originality` | 0.75 | 1 | 组合原创性 | The silhouette stack is coherent and somewhat unusual, especially with the layered printed coat and shoulder embellishment, though the base formula remains relatively wearable. |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and attachment positions are clearly described and visually imageable, including coat-over-jacket and lining visibility. Slightly less than perfect because some phrasing remains interpretive, |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | The text prioritizes visible silhouette, layers, print, and accessories, with only minor attention to less visible details like lining. Visible outfit-defining information clearly dominates. |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly anchored in visible garment parts, layers, trims, and placement, with little mood-only language. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | Main garments read as one coherent print-and-layered look without trunk-level contradictions. |
| `coordination_penalty` | 0.0 | The coat, inner layer, and skirt share a unified palette and styling language; accessories support rather than clash. |
| `formula_template_penalty` | 0.25 | Some runway/editorial phrasing and familiar layered-look structure make it mildly formulaic, but it remains fairly specific and grounded. |
| `generation_content_penalty` | 0.25 | Mostly grounded garment description, but ends with editorial/styling framing that adds some prompt noise. |
| `rationality_penalty` | 0.0 | All materials and construction details are plausible fashion-textile descriptions. |

## Skipped metrics (不适用)

- `body_coverage` (coverage_score) — The text does not clearly describe notable exposure or cutout/reveal beyond general length.
- `construction_technique` (coverage_score) — No specific fabrication technique like pleating, quilting, cut-outs, or engineered panel construction is clearly identified.
- `deconstruction` (coverage_score) — The text does not explicitly mention deconstruction, splicing, displacement, or reconstruction.
- `footwear` (coverage_score) — No footwear is described in the text.
- `belt` (coverage_score) — No visible belt, sash, waist cincher, or harness is mentioned.
- `quantity_accuracy` (quality_score) — The text contains no explicit counts or quantity relations that need verification.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral distinction is described.
- `gender_expression` (bonus_score) — No explicit gender expression or androgyny is mentioned.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative task is stated beyond the outfit description.
- `brand_alignment` (bonus_score) — No brand identity or brand-language target is explicitly provided.
- `negation_control` (bonus_score) — The text does not emphasize exclusions or absence of elements.
