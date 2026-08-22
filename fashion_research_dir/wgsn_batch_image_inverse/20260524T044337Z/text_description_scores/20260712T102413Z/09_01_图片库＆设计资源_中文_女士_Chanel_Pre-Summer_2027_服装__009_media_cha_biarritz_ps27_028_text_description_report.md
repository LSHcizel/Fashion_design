# Text Evaluation Report

- **Source:** 09_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__009_media_cha_biarritz_ps27_028_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.0
- **Total score (S_fp):** 0.8112 (Strong)
- **Coverage axis:** 1.0
- **Quality axis (raw / base / penalized):** 0.7833 / 0.7628 / 0.7628
- **Penalties (mean):** 0.1
- **R_content:** 0.782808

## Gates

- Score gate: 0.8112 (threshold 0.7) → **PASS**
- Penalty gate: 0.1 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `asymmetry` | 1.0 | 1 |  | An off-center front slit is an explicit asymmetrical design element, so the metric is applicable and covered. |
| `body_coverage` | 1.0 | 1 |  | The text explicitly describes exposed areas at the neckline and leg slit. |
| `closure` | 1.0 | 1 |  | A clear front button closure is described, making the opening/closure detail salient. |
| `color_relationship_logic` | 1.0 | 1 |  | The text explains the color logic as a classic graphic cream-black-gold scheme with strong contrast trim. |
| `cross_garment_binding` | 1.0 | 1 |  | The description clearly distinguishes which attributes belong to the jacket, inner top, and skirt, satisfying cross-garment binding. |
| `fabric_family` | 1.0 | 1 |  | The text clearly names the main fabric family as tweed and also identifies the inner top as leather-like. |
| `functional_detail` | 1.0 | 1 |  | Functional pocket details are explicitly mentioned and visually specific. |
| `garment_category` | 1.0 | 1 |  | The text clearly identifies the main garment categories in the look. |
| `hardware_embellishment` | 1.0 | 1 |  | The gold-tone buttons function as visible hardware embellishment and are a salient decorative detail. |
| `jewelry` | 1.0 | 1 |  | A salient jewelry item is explicitly present. |
| `layering` | 1.0 | 1 |  | The text clearly describes a layered outfit with an outer jacket over an inner top. |
| `length_hemline` | 1.0 | 1 |  | Garment length and hem detail are directly stated. |
| `primary_color` | 1.0 | 1 |  | The dominant garment palette is clearly centered on cream/off-white with black as a major visible color. |
| `secondary_color` | 1.0 | 1 |  | Secondary accent colors are clearly present, especially gold hardware and red earrings. |
| `shoulder_architecture` | 1.0 | 1 |  | The shoulder/sleeve line is salient and clearly described as dropped and relaxed. |
| `silhouette` | 1.0 | 1 |  | Overall shape and structural contour are explicitly described. |
| `surface_finish` | 1.0 | 1 |  | It explicitly describes surface qualities: textured, smooth/shiny, and leather-like. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes the upper and lower silhouette relationship, including an oversized jacket over a fitted, high-waisted skirt, so proportion is salient and well specified. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are clearly tied to the correct garment or accessory, and the layering is understandable. Minor ambiguity remains in phrases like “scarf-like black panels or lapels” and some trim/butt |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | 主体服装轮廓清晰，品类、材质、配色和关键结构都被有效组织；但细节较多，尤其是对领口、口袋、按钮、缝线和饰品的逐项展开，略有冗余，密度高但不算极致精炼。 |
| `craft_embellishment_salience` | 0.75 | 1 | 工艺装饰显著度 | Trim and button placement are clearly described by type and location, and they function as visible design accents. The craft is not highly elaborate, but it is specific enough to serve as a strong vis |
| `design_distinctiveness` | 0.75 | 1 | 设计独特性 | The look has a clear memory anchor through the cream tweed plus black trim contrast and the scarf-like front panels, which makes it more distinctive than a generic jacket-and-skirt formula. It is stil |
| `design_signal_purity` | 0.75 | 1 | 设计信号纯度 | Most of the text is devoted to concrete design facts, with only a small amount of evaluative mood language at the end. The signal is strong and usable for generation. |
| `fine_grained_attribute_usage` | 1.0 | 1 | 术语具体度 | Color, material, construction, and silhouette details are all finely specified, producing a precise and imageable fashion description. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The description is highly visual, garment-specific, and already organized like a prompt, with clear silhouette, layering, materials, and palette. It is slightly more explanatory than a direct generati |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a clear主体→分层→下装→配色/配饰 order, making the outfit easy to reconstruct. There is minor compression from long attribute chains, but the overall hierarchy remains stable and readable |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The description keeps jacket, inner top, skirt, and earrings mostly separated and correctly attributed. There is slight cross-structure ambiguity around the front black elements on the top versus jack |
| `reference_clarity` | 0.75 | 1 | 语言清晰度 | References are generally clear and consistently anchored to the jacket, top, and skirt. There is only minor complexity from long descriptive clauses, but no serious pronoun or omission ambiguity. |
| `silhouette_combination_originality` | 0.5 | 0 | 组合原创性 | The silhouette is coherent and polished, but the overall combination remains a fairly familiar luxury tailoring formula: structured jacket, fitted top, straight skirt. The slit and scarf-like front ad |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and front-facing structure are clearly described and visually reconstructable. The spatial relations are coherent, though the text still reads as descriptive fashion analysis rather than a fu |
| `specific_noun_usage` | 1.0 | 1 | 术语具体度 | Uses highly specific garment, material, and accessory nouns throughout, with clear fashion terminology and little generic wording. |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | 可见且决定成像的外套、内搭、裙装开衩和耳饰都被优先描述，整体可视化导向明确；不过仍包含一些相对次级的工艺与边缘细节，如按钮、细线和口袋结构，稍微分散了重点。 |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly anchored to visible garment zones and readable construction details, with clear front/back and layering cues. It reads like a direct runway observation rather than a concep |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | The jacket, inner top, and skirt form a coherent layered outfit without trunk-level contradictions or left-right conflicts. |
| `coordination_penalty` | 0.0 | The palette and textures are coordinated into a single polished couture-like language; no major styling clash appears across trunk garments. |
| `formula_template_penalty` | 0.25 | The description follows a common runway-look formula with broad silhouette/material/palette summary language, though it is not heavily templated. |
| `generation_content_penalty` | 0.25 | Mostly imageable garment description, but it includes runway-style evaluative framing and summary language that slightly reduces prompt efficiency. |
| `rationality_penalty` | 0.0 | All described materials and garment structures are physically plausible in ordinary fashion construction. |

## Quality issues (质量短板)

- **`silhouette_combination_originality`** (score 0.5) — The silhouette is coherent and polished, but the overall combination remains a fairly familiar luxury tailoring formula: structured jacket, fitted top, straight skirt. The slit and scarf-like front add interest, yet the template is still relatively predictable.

## Skipped metrics (不适用)

- `pattern_type` (coverage_score) — No explicit pattern or print is described; tweed texture is material, not a pattern type in this context.
- `construction_technique` (coverage_score) — No notable named construction technique such as quilting, pleating, embroidery, or engineered panel work is clearly described.
- `deconstruction` (coverage_score) — The text does not mention deconstruction, splicing, displacement, or reconstruction.
- `bag` (coverage_score) — No bag is mentioned or implied as part of the look.
- `footwear` (coverage_score) — No footwear is described.
- `belt` (coverage_score) — No visible belt, sash, or waist strap is described.
- `quantity_accuracy` (quality_score) — The text contains no explicit counts, numerals, or quantity relations that require verification.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral differences are described.
- `cultural_reference` (bonus_score) — No clear cultural, historical, or brand reference is provided.
- `gender_expression` (bonus_score) — The description does not explicitly discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is stated.
- `brand_alignment` (bonus_score) — The text does not explicitly target a brand identity or brand language.
- `negation_control` (bonus_score) — The description does not emphasize exclusions or absence of elements.
