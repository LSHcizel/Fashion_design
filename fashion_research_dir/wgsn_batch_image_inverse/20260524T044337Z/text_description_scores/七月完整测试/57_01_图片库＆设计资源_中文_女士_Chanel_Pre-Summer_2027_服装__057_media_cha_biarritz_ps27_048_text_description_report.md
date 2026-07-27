# Text Evaluation Report

- **Source:** 57_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__057_media_cha_biarritz_ps27_048_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.8627 (Strong)
- **Coverage axis:** 0.8947
- **Quality axis (raw / base / penalized):** 0.8571 / 0.8542 / 0.8542
- **Penalties (mean):** 0.1
- **R_content:** 0.832506

## Gates

- Score gate: 0.8627 (threshold 0.7) → **PASS**
- Penalty gate: 0.1 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `asymmetry` | 1.0 | 1 |  | Asymmetry is directly described in the top hem, making this metric clearly applicable and covered. |
| `bag` | 1.0 | 1 |  | Bag presence, carry method, and material/color description are all clearly provided. |
| `body_coverage` | 1.0 | 1 |  | It clearly describes coverage and exposure through the sleeveless cut and torso coverage. |
| `color_relationship_logic` | 1.0 | 1 |  | The text explains the color logic through alternating stripes and coordinated graphic accents, giving a clear relationship between the palette elements. |
| `construction_technique` | 1.0 | 1 |  | A specific construction technique is named and localized to the skirt body, so the craft detail is clearly covered. |
| `cross_garment_binding` | 1.0 | 1 |  | The description clearly distinguishes multiple garments and accessories, assigning attributes to each item in a coherent way. |
| `fabric_family` | 0.0 | 0 |  | The text describes garment shapes and surface treatment, but does not clearly identify a material family such as silk, cotton, wool, leather, or knit for the main garments. |
| `footwear` | 1.0 | 1 |  | The text specifies shoe type, heel form, toe shape, and color/finish details. |
| `functional_detail` | 1.0 | 1 |  | The text clearly mentions functional strap details on the shoe and a carried bag accessory, satisfying functional detail coverage. |
| `garment_category` | 1.0 | 1 |  | The text clearly names the main garment categories: top, skirt, and footwear. |
| `layering` | 1.0 | 1 |  | The outfit explicitly describes a layered top-over-skirt relationship with clear ordering. |
| `length_hemline` | 1.0 | 1 |  | Length and hemline are directly specified for the skirt and top. |
| `pattern_type` | 1.0 | 1 |  | The description clearly includes multiple pattern types: stripes, dots/curving lines, and circular graphic motifs. |
| `primary_color` | 1.0 | 1 |  | Black is clearly the main color of the look, especially for the top and as a dominant ground in the skirt and accessories. |
| `secondary_color` | 1.0 | 1 |  | Multiple secondary colors are explicitly present and visually salient, especially in the striped skirt and graphic embellishments. |
| `shoulder_architecture` | 0.0 | 0 |  | The text indicates sleevelessness, but does not describe a distinct shoulder architecture such as structured shoulders, off-shoulder, or strap design. |
| `silhouette` | 1.0 | 1 |  | It explicitly describes the overall shape and structural contour of the look. |
| `surface_finish` | 1.0 | 1 |  | Pleating and high-volume structure clearly convey surface/handfeel traits such as texture and stiffness/drape, satisfying the surface-finish requirement. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly states the relationship between the top and bottom and explicitly notes that the skirt dominates the silhouette, so proportion is well covered. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are clearly attached to the correct garment or accessory, and the layering relation between top and skirt is stable. Minor ambiguity remains in phrases like “second tan/black patterned |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is compact and heavily garment-focused, with clear visible-body details prioritized. There is some stylistic framing and repeated elaboration of texture/mood, but not enough to signifi |
| `craft_embellishment_salience` | 1.0 | 1 | 工艺装饰显著度 | The craft is clearly specified by type, placement, and visual effect: graphic embellishments on the top and fringe/lace-like trim at the skirt hem. These are salient design hooks. |
| `design_distinctiveness` | 1.0 | 1 | 设计独特性 | The look has multiple clear memory points: asymmetric top hem, highly graphic striped accordion pleats, and artisanal fringe trim. These are non-formula and visually distinctive. |
| `design_signal_purity` | 1.0 | 1 | 设计信号纯度 | The text is dominated by concrete design facts: garment types, shapes, trims, textures, and placement. Mood language is minimal and does not dilute the design signal. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly visual and already close to a prompt, with clear garment types, silhouette, layering, texture, and accessories. It is slightly more descriptive/essay-like than a direct generation p |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a mostly natural body-to-detail order: main garments first, then top details, skirt details, accessories, and footwear. It is clear and easy to reconstruct, though some later e |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The description keeps most attributes correctly assigned across multiple items: top, skirt, bags, and shoes are distinguished well. There is slight looseness around the second bag/accessory, but no ma |
| `quantity_accuracy` | 1.0 | 1 | 语言清晰度 | The few explicit quantity relations are clear and consistent: one top, one skirt, one shoulder bag, and a second bag/accessory are unambiguously distinguished. No conflicting counts or unclear side re |
| `reference_clarity` | 1.0 | 1 | 语言清晰度 | References are well anchored to clear antecedents, and the prose maintains stable object tracking throughout. Pronouns and ellipses are easy to resolve without backtracking. |
| `silhouette_combination_originality` | 0.75 | 1 | 组合原创性 | The combination is specific and somewhat unexpected, especially the graphic top with a highly textured pleated skirt and striped pumps. It is not a standard formula template, though the overall stylin |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and attachment positions are clearly described and imageable. The spatial relations are coherent overall, with only minor complexity from the layered hem and fringe details. |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | Most of the text describes visible, image-dominant garments and accessories. The mood sentence is present but brief and does not overpower the concrete outfit description, so visibility priority remai |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is anchored in visible garment parts and positions, with clear separation of top, skirt, bags, and shoes. It reads like direct runway observation rather than mood essay. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | No trunk-level left-right conflict or mutually exclusive garment identities are described. |
| `coordination_penalty` | 0.0 | The top, skirt, and shoes are stylistically aligned rather than in conflict. |
| `formula_template_penalty` | 0.25 | Some runway-essay style framing and mood language slightly dilute the design facts, but the description remains fairly specific and grounded. |
| `generation_content_penalty` | 0.25 | Mostly grounded in visible garments, but the closing mood framing and symbol-heavy embellishment list add some prompt dilution. |
| `rationality_penalty` | 0.0 | All described materials and constructions are plausible as fashion details. |

## Missing coverage (未覆盖)

- **`shoulder_architecture`** — The text indicates sleevelessness, but does not describe a distinct shoulder architecture such as structured shoulders, off-shoulder, or strap design.
- **`fabric_family`** — The text describes garment shapes and surface treatment, but does not clearly identify a material family such as silk, cotton, wool, leather, or knit for the main garments.

## Skipped metrics (不适用)

- `closure` (coverage_score) — No explicit closure detail such as buttons, zipper, ties, or buckle is mentioned.
- `deconstruction` (coverage_score) — The text does not mention deconstruction, splicing, displacement, or reconstruction.
- `hardware_embellishment` (coverage_score) — No clear hardware or metal embellishment such as chains, studs, rings, or crystals is described.
- `jewelry` (coverage_score) — No jewelry or body ornament is mentioned.
- `belt` (coverage_score) — No visible belt, sash, waist strap, or harness is described.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral contrast is described.
- `cultural_reference` (bonus_score) — No cultural, historical, or brand reference is provided.
- `gender_expression` (bonus_score) — The description does not explicitly discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is stated beyond the outfit description.
- `brand_alignment` (bonus_score) — No brand identity or brand-language target is mentioned.
- `negation_control` (bonus_score) — The text does not emphasize exclusions or absences that need explicit negation control.
