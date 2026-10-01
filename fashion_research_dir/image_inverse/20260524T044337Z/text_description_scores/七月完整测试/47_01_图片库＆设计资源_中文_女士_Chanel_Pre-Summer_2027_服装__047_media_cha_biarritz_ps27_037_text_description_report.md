# Text Evaluation Report

- **Source:** 47_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__047_media_cha_biarritz_ps27_037_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.8174 (Strong)
- **Coverage axis:** 1.0
- **Quality axis (raw / base / penalized):** 0.7692 / 0.7708 / 0.7708
- **Penalties (mean):** 0.25
- **R_content:** 0.745877

## Gates

- Score gate: 0.8174 (threshold 0.7) → **PASS**
- Penalty gate: 0.25 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `bag` | 1.0 | 1 |  | Bag is clearly described with category, shape, and material/finish details. |
| `body_coverage` | 1.0 | 1 |  | The text includes clear coverage/reveal information, noting a glimpse above and footwear visible beneath the hem. |
| `closure` | 1.0 | 1 |  | A clear tie closure is explicitly described. |
| `color_relationship_logic` | 1.0 | 1 |  | The text explains the color story as a cream base with burgundy/dark stripe accents and a black lower half, giving a clear layered contrast structure. |
| `cross_garment_binding` | 1.0 | 1 |  | The description distinguishes multiple items and their roles: the tied wrap top layer, the lower garment beneath it, and the separate handbag and shoes. |
| `fabric_family` | 1.0 | 1 |  | The text clearly indicates fabric family/character through scarf-like material and a fluid drapey lower garment. |
| `footwear` | 1.0 | 1 |  | Footwear is specified by type, heel/toe form, and surface finish/color. |
| `functional_detail` | 1.0 | 1 |  | The text includes a functional carrying detail: a handbag with a chain handle/strap. |
| `garment_category` | 1.0 | 1 |  | The text clearly identifies the main garment categories: a wrapped upper layer and a lower garment that is either wide-leg trousers or a divided skirt. |
| `hardware_embellishment` | 1.0 | 1 |  | Visible metallic hardware and chain detailing are clearly described. |
| `layering` | 1.0 | 1 |  | The text clearly describes layered garments and their visible order/relationship. |
| `length_hemline` | 1.0 | 1 |  | Length and hemline are directly stated for the lower garment. |
| `pattern_type` | 1.0 | 1 |  | A stripe pattern is explicitly described. |
| `primary_color` | 1.0 | 1 |  | The look has clearly stated main colors, especially cream and black, with black dominating the lower garment. |
| `secondary_color` | 1.0 | 1 |  | Secondary colors are explicitly present as border stripes and a visible contrasting glimpse above the wrap. |
| `silhouette` | 1.0 | 1 |  | The overall shape is explicitly described, including the compact upper portion and voluminous lower silhouette. |
| `surface_finish` | 1.0 | 1 |  | Surface qualities are explicitly described as smooth and heavily draped. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly states the upper-to-lower proportion and visual balance, with a compact waist contrasted against a voluminous lower half. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are bound to the correct garment or accessory, and the upper layer, lower garment, bag, and shoes are clearly distinguished. Minor ambiguity remains in phrases like 'wide-leg trousers  |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is mostly garment-focused and imageable, with clear trunk, bag, and shoe details. There is some stylistic framing at the end, but not enough to make it essay-like or low-density. |
| `craft_embellishment_salience` | 0.5 | 0 | 工艺装饰显著度 | There are craft-like details and trim, but they are described somewhat generally rather than as a sharply specified construction feature with exact placement and function. |
| `design_distinctiveness` | 0.75 | 1 | 设计独特性 | The look has a clear non-formula memory point in the scarf-like wrap tied with long sash ends, plus an unusual wide-leg/divided-skirt lower half and a strong red shoe accent. |
| `design_signal_purity` | 0.75 | 1 | 设计信号纯度 | The text is dominated by concrete design facts, with only a brief mood summary at the end, so the signal remains mostly pure. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly imageable and already organized around visible silhouette, garment layers, accessories, and footwear, so it is close to a usable generation prompt. It is slightly less than perfect  |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a mostly natural body-to-detail order: overall framing, upper layer, lower garment, accessories, then footwear. The structure is easy to reconstruct, though some material/color |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text separates multiple garments and accessories cleanly, with color and structure mostly attached to the right item. The only notable uncertainty is the lower garment identity, but the cross-item |
| `reference_clarity` | 1.0 | 1 | 语言清晰度 | References are consistently anchored to clear nouns and garment layers, with no confusing pronoun chains or ambiguous omissions. |
| `silhouette_combination_originality` | 0.75 | 1 | 组合原创性 | The combination is more distinctive than a standard resort formula because of the wrap-sash top paired with an ambiguous trouser/skirt volume and a vivid heel accent, though it still remains broadly w |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and attachment positions are clearly described, and the wrap-over-lower-garment relationship is visually coherent. Minor uncertainty remains because the lower garment is described as “appears |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | The text prioritizes visible, compositional details that affect the image, and it does not dwell on hidden or internal features. The closing mood sentence adds some framing, but visible garment facts  |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly anchored in visible garment zones and readable layers, with honest uncertainty where needed ('appears to be'). |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.25 | The lower garment is slightly ambiguous between trousers and a divided skirt, but there is no strong left-right or multi-garment contradiction on the trunk. |
| `coordination_penalty` | 0.25 | The red pumps and heavy black drape create a mild styling contrast, but the overall look still reads as a coherent resort/evening outfit. |
| `formula_template_penalty` | 0.5 | The description leans on a recognizable resort/evening formula and mood-led summary, with several interchangeable style tokens, though it still includes some concrete construction details. |
| `generation_content_penalty` | 0.25 | Mostly grounded garment description, but the closing mood-summary and symbol list add some formulaic, essay-like framing beyond the imaging trunk. |
| `rationality_penalty` | 0.0 | No clearly implausible material or construction claims; the described elements are physically plausible as ordinary fashion details. |

## Quality issues (质量短板)

- **`craft_embellishment_salience`** (score 0.5) — There are craft-like details and trim, but they are described somewhat generally rather than as a sharply specified construction feature with exact placement and function.

## Skipped metrics (不适用)

- `shoulder_architecture` (coverage_score) — No salient shoulder design is described; the text focuses on waist wrap and lower-garment volume instead.
- `construction_technique` (coverage_score) — No specific fabrication technique like pleating, quilting, embroidery, or cutwork is clearly named.
- `deconstruction` (coverage_score) — The text does not explicitly mention deconstruction, splicing, displacement, or reconstruction.
- `jewelry` (coverage_score) — No jewelry or body ornament is explicitly present.
- `belt` (coverage_score) — The waist tie is part of the wrap garment, not a separate belt or waist accessory.
- `asymmetry` (coverage_score) — No clear asymmetrical garment structure is described.
- `quantity_accuracy` (quality_score) — The text does not use explicit counts or quantity relations that need verification.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral distinction is described.
- `cultural_reference` (bonus_score) — No explicit cultural, historical, or brand reference is provided.
- `gender_expression` (bonus_score) — The text does not discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is explicitly stated.
- `brand_alignment` (bonus_score) — No brand language or brand identity target is mentioned.
- `negation_control` (bonus_score) — The text does not emphasize exclusions or absence of elements.
