# Text Evaluation Report

- **Source:** look_02.txt
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.1
- **Total score (S_fp):** 0.7487 (Usable)
- **Coverage axis:** 1.0
- **Quality axis (raw / base / penalized):** 0.7344 / 0.6886 / 0.6886
- **Penalties (mean):** 0.25
- **R_content:** 0.683189

## Gates

- Score gate: 0.7487 (threshold 0.7) → **PASS**
- Penalty gate: 0.25 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `belt` | 1.0 | 1 |  | A visible waist belt is explicitly described and its relation to the wrap layer is clear. |
| `body_coverage` | 1.0 | 1 |  | The text clearly describes exposed and covered body areas. |
| `closure` | 1.0 | 1 |  | Multiple explicit closure methods are described for the jacket and top. |
| `color_relationship_logic` | 1.0 | 1 |  | The text explains the palette relationship as a navy-dominant look with lighter accents and linked tonal contrasts. |
| `cross_garment_binding` | 1.0 | 1 |  | The description distinguishes how the jacket, wrap top, trouser, and belt each function and relate to one another, making the multi-garment structure clear. |
| `fabric_family` | 1.0 | 1 |  | The text clearly names the main fabric families for the garments. |
| `footwear` | 1.0 | 1 |  | Footwear is clearly specified with type, shape, and materials/finish. |
| `functional_detail` | 1.0 | 1 |  | The text clearly mentions pockets and functional strap/hardware details. |
| `garment_category` | 1.0 | 1 |  | The text clearly names the main garment categories. |
| `hardware_embellishment` | 1.0 | 1 |  | The description includes salient hardware elements and metallic embellishment. |
| `layering` | 1.0 | 1 |  | The text clearly describes jacket over top over trouser layering with visible relationships and coverage order. |
| `length_hemline` | 1.0 | 1 |  | Multiple length and hemline cues are given for the jacket, trouser, and shoe relation. |
| `primary_color` | 1.0 | 1 |  | Navy is the dominant color across the look, with indigo reinforcing the main palette. |
| `secondary_color` | 1.0 | 1 |  | Secondary light accents are clearly described and anchored to specific garments and details. |
| `shoulder_architecture` | 1.0 | 1 |  | Shoulder structure is explicitly stated and is visually salient. |
| `silhouette` | 1.0 | 1 |  | Overall shape and structural contour are explicitly described. |
| `surface_finish` | 1.0 | 1 |  | It explicitly describes finish and surface qualities such as washed, softened, matte, and satin trim. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes upper-lower proportion and silhouette balance, including cropped jacket, visible waist, and leg-elongating trouser. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are clearly tied to the correct garment or body zone, including the jacket, wrap top, trouser, and footwear. Minor complexity comes from multiple waist-related closures and accents, bu |
| `core_information_density` | 0.5 | 0 | 信息密度与简洁性 | The description contains substantial concrete garment detail, but it is repeatedly wrapped in mood/identity framing and transition prose, which reduces prompt efficiency. It is not a four-section temp |
| `craft_embellishment_salience` | 0.75 | 1 | 工艺装饰显著度 | Craft details are clearly identified with type and placement, and they contribute to the look’s identity. A few elements are still described in broader finish language, so it is not fully maximal. |
| `design_distinctiveness` | 0.75 | 1 | 设计独特性 | The look has clear non-formula anchors in the seam topstitching, mixed closures, and contrast piping. It is distinctive, though still grounded in a fairly wearable tailored-workwear vocabulary. |
| `design_signal_purity` | 0.5 | 0 | 设计信号纯度 | Design facts dominate, but repeated mood/identity framing and transition language dilute the signal somewhat. The text still stays mostly grounded in garment description. |
| `fine_grained_attribute_usage` | 1.0 | 1 | 术语具体度 | Color, fabric, construction, and trim details are consistently fine-grained and technically precise, with strong visual imageability. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly visual and garment-specific, with clear silhouette, layering, materials, and footwear, so it is close to a usable prompt. However, it still reads as polished design prose with metap |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a clear garment-to-detail progression: jacket, then top and trouser, then accessories/hardware, then footwear. Minor digressions into mood and metaphor slightly interrupt the f |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text cleanly separates several garments and generally assigns colors, materials, and closures to the correct item. There is some dense layering and multiple waist details, but no major cross-garme |
| `quantity_accuracy` | 0.75 | 1 | 语言清晰度 | Quantities and counts are mostly clear and internally consistent, with only mild vagueness in phrases like “a few” and “small,” which do not impede understanding. |
| `reference_clarity` | 1.0 | 1 | 语言清晰度 | Pronouns and omitted subjects are easy to resolve throughout; references remain stable and the description is straightforward to follow. |
| `silhouette_combination_originality` | 0.5 | 0 | 组合原创性 | The combination is coherent and polished, but it remains within a recognizable tailored coastal/workwear framework. It is more specific than a pure formula, yet not especially unexpected. |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and attachment positions are clearly described and imageable, with coherent inside/outside and top-to-bottom relations. The only limitation is that the text remains somewhat essayistic rather |
| `specific_noun_usage` | 1.0 | 1 | 术语具体度 | Uses highly specific garment names, materials, and footwear terms throughout, creating a clear and concrete fashion image. |
| `visibility_priority` | 0.5 | 0 | 信息密度与简洁性 | Visible clothing facts are present and fairly detailed, but they are consistently interleaved with essay-like atmosphere and interpretive framing. Hidden or low-visibility details are not dominant, ye |
| `visual_observation_grounding` | 0.75 | 1 | 视觉观察 grounded | The description is strongly anchored to visible garment zones and construction details. There is some mood language, but the text mostly reads like direct observation of the look. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | The jacket, top, trouser, and shoe descriptions are internally coherent and do not present trunk-level left-right or identity conflicts. |
| `coordination_penalty` | 0.0 | The styling language is unified across outerwear, top, trouser, and footwear, with no major coordination clash on the trunk garments. |
| `formula_template_penalty` | 0.75 | The text follows a predictable fashion-essay formula with repeated salon/shore framing and brand-symbol-like cues such as 'Chanel note,' though it does not use explicit fixed section headers. |
| `generation_content_penalty` | 0.5 | The description is heavily essayistic and conceptual, with repeated mood/stance framing and metaphorical runway language that reduces prompt efficiency, though it still retains a clear garment trunk. |
| `rationality_penalty` | 0.0 | All materials and garment constructions are physically plausible and consistent with ordinary wear. |

## Quality issues (质量短板)

- **`core_information_density`** (score 0.5) — The description contains substantial concrete garment detail, but it is repeatedly wrapped in mood/identity framing and transition prose, which reduces prompt efficiency. It is not a four-section template, so the stricter 0.25 cap does not apply.
- **`visibility_priority`** (score 0.5) — Visible clothing facts are present and fairly detailed, but they are consistently interleaved with essay-like atmosphere and interpretive framing. Hidden or low-visibility details are not dominant, yet the prose still dilutes the image-first priority.
- **`silhouette_combination_originality`** (score 0.5) — The combination is coherent and polished, but it remains within a recognizable tailored coastal/workwear framework. It is more specific than a pure formula, yet not especially unexpected.
- **`design_signal_purity`** (score 0.5) — Design facts dominate, but repeated mood/identity framing and transition language dilute the signal somewhat. The text still stays mostly grounded in garment description.

## Skipped metrics (不适用)

- `pattern_type` (coverage_score) — No pattern or print is described.
- `construction_technique` (coverage_score) — No specific advanced construction technique like quilting, pleating, cut-outs, or engineered panel work is clearly described.
- `deconstruction` (coverage_score) — The text does not explicitly mention deconstruction, splicing, displacement, or reconstruction.
- `bag` (coverage_score) — No bag is described or implied as a visible styling element.
- `jewelry` (coverage_score) — No salient jewelry or body ornament is present.
- `asymmetry` (coverage_score) — No clear asymmetrical garment structure is described.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral asymmetry is described.
