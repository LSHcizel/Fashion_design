# Text Evaluation Report

- **Source:** 59_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__059_media_cha_biarritz_ps27_052_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.8509 (Strong)
- **Coverage axis:** 1.0
- **Quality axis (raw / base / penalized):** 0.8214 / 0.8125 / 0.8125
- **Penalties (mean):** 0.1
- **R_content:** 0.821118

## Gates

- Score gate: 0.8509 (threshold 0.7) → **PASS**
- Penalty gate: 0.1 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `body_coverage` | 1.0 | 1 |  | The text clearly describes exposed body areas and partial coverage. |
| `color_relationship_logic` | 1.0 | 1 |  | The text explains the color logic through stripe alternation, layered contrast between striped shell and golden fringe, and a coordinated vivid palette. |
| `cross_garment_binding` | 1.0 | 1 |  | Multiple garments are described and their roles are distinguished: the striped skirt outer layer, the fringe beneath it, and the separate upper garment. |
| `fabric_family` | 1.0 | 1 |  | The text gives a clear material family for the skirt trim/fringe and indicates a textured textile top, enough to infer material category coverage. |
| `footwear` | 1.0 | 1 |  | Footwear is clearly specified with shoe type, toe shape, and color blocking. |
| `garment_category` | 1.0 | 1 |  | The text clearly identifies the main garment category as a skirt, with an additional top partially visible. |
| `hardware_embellishment` | 1.0 | 1 |  | Visible metallic bracelets count as salient hardware embellishment. |
| `jewelry` | 1.0 | 1 |  | Bracelets are salient body adornments and explicitly present. |
| `layering` | 1.0 | 1 |  | The text clearly describes layered garments and their visible order, including an outer striped layer over fringe and a partially visible top beneath the framing. |
| `length_hemline` | 1.0 | 1 |  | The garment length and hemline are directly stated. |
| `pattern_type` | 1.0 | 1 |  | The pattern types are clearly identified as vertical stripes and painterly banding. |
| `primary_color` | 1.0 | 1 |  | The look clearly establishes red and white as the dominant visible colors on the skirt, with additional multicolor accents above. |
| `secondary_color` | 1.0 | 1 |  | Several secondary colors are explicitly described, including gold fringe, multicolor top bands, and two-tone footwear. |
| `silhouette` | 1.0 | 1 |  | The overall shape is explicitly described and is visually clear. |
| `surface_finish` | 1.0 | 1 |  | It describes drape/shape and tactile surface qualities, including bulky textured fringe and the skirt’s flared movement. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes the relationship between the upper body and the dominant lower silhouette, emphasizing a top-to-bottom composition with a heavy skirt-led proportion. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are clearly tied to the correct entities, with separate binding for skirt, top, arms, and shoes. Minor ambiguity remains in the top description (“sleeveless or short-sleeved”) and the  |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is compact and mostly devoted to visible garment facts, with clear focus on silhouette, stripe pattern, fringe texture, top, bracelets, and shoes. There is some stylistic framing at th |
| `craft_embellishment_salience` | 0.75 | 1 | 工艺装饰显著度 | The fringe treatment is a salient craft-like detail with clear location and visual effect, though the construction is described more than technically specified. |
| `design_distinctiveness` | 0.75 | 1 | 设计独特性 | The look has a clear memory point through the striped skirt plus bulky raffia-like fringe, which is more distinctive than a formula resort outfit. |
| `design_signal_purity` | 1.0 | 1 | 设计信号纯度 | The text is dominated by concrete design observations rather than mood or essay-like framing. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly visual and mostly prompt-ready, with clear garment types, silhouette, color, texture, and footwear. It reads slightly like a descriptive analysis rather than a compact generation pr |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a mostly natural top-down structure: overall view, main garment, upper garment, accessories, then footwear. It is clear and imageable, though some details are compressed into l |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text keeps the skirt, top, and shoes distinct and generally binds colors/materials to the correct garments. There is slight uncertainty around the top’s sleeve length and the relationship between  |
| `quantity_accuracy` | 1.0 | 1 | 语言清晰度 | Quantities and side references are explicit and internally consistent; the text clearly distinguishes multiple bracelets, both wrists, and alternating stripe colors without ambiguity. |
| `reference_clarity` | 1.0 | 1 | 语言清晰度 | References are stable and easy to track, with clear subjects and no confusing pronoun chains or unclear omissions. |
| `silhouette_combination_originality` | 0.75 | 1 | 组合原创性 | The combination is unusual and imageable, especially the oversized striped skirt with fringe and the two-tone footwear, though the top is only partially described. |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and attachment relationships are clear and imageable: the fringe sits under the skirt edge, and the top is positioned above the skirt. The spatial structure is coherent, though the upper garm |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | The text prioritizes highly visible, image-dominant elements such as skirt shape, stripe pattern, fringe, and shoes. It includes a brand-like wordmark and palette framing, but these do not overpower t |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly anchored in visible garment facts, with clear placement cues and little mood-only language. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | No trunk-level left-right or mutually exclusive garment conflicts are described; the look reads as one coherent skirt-top-shoe ensemble. |
| `coordination_penalty` | 0.0 | The styling language is mixed but still coordinated around a single vacation-inspired palette and texture story, without a strong trunk-level clash. |
| `formula_template_penalty` | 0.25 | There is some formula-like resort/vacation styling language, but the description remains grounded in specific visible construction details rather than becoming a fully interchangeable template. |
| `generation_content_penalty` | 0.25 | Mostly concrete and imageable, but ends with a broad stylistic summary that adds some conceptual framing beyond the garment description. |
| `rationality_penalty` | 0.0 | The described materials and construction are plausible as fashion details; no physically implausible garment structure is asserted. |

## Skipped metrics (不适用)

- `shoulder_architecture` (coverage_score) — The text does not describe any salient shoulder structure; it only says the top is partially visible and sleeveless or short-sleeved.
- `closure` (coverage_score) — No explicit closure detail such as buttons, zipper, ties, or buckle is mentioned.
- `functional_detail` (coverage_score) — The text does not describe pockets, straps, utility parts, or other functional garment details.
- `construction_technique` (coverage_score) — Although the skirt has stripes and fringe, no specific construction technique like pleating, quilting, embroidery, cut-outs, or engineered panel work is clearly identified.
- `deconstruction` (coverage_score) — The description does not mention deconstruction, splicing, displacement, or reconstruction.
- `bag` (coverage_score) — No bag is described or implied as a visible styling element.
- `belt` (coverage_score) — No visible belt, sash, or waist strap is mentioned; the waist shape comes from the skirt silhouette.
- `asymmetry` (coverage_score) — No clear asymmetrical design, one-shoulder, single-sleeve, or uneven garment structure is described.
- `bilateral_coherence` (quality_score) — No explicit left-right or bilateral garment differences are described.
- `gender_expression` (bonus_score) — No explicit gender expression or androgyny is described.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is explicitly stated.
- `brand_alignment` (bonus_score) — No explicit brand language or brand identity target is given.
- `negation_control` (bonus_score) — The text does not emphasize exclusions or absences that need control.
