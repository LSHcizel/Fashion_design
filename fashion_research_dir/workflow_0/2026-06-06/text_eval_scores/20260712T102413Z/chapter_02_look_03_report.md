# Text Evaluation Report

- **Source:** look_03.txt
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.0
- **Total score (S_fp):** 0.7438 (Usable)
- **Coverage axis:** 1.0
- **Quality axis (raw / base / penalized):** 0.75 / 0.6833 / 0.6833
- **Penalties (mean):** 0.15
- **R_content:** 0.704751

## Gates

- Score gate: 0.7438 (threshold 0.7) → **PASS**
- Penalty gate: 0.15 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `belt` | 1.0 | 1 |  | A visible waist belt is explicitly described, including its material and function relative to the jacket and silhouette. |
| `body_coverage` | 1.0 | 1 |  | The text clearly describes exposed body area at the collarbone and how it is covered by layering. |
| `closure` | 1.0 | 1 |  | The text clearly describes the jacket’s button front closure and also mentions a tied belt closure at the waist. |
| `color_relationship_logic` | 1.0 | 1 |  | The palette is organized with explicit color logic: navy base, pale/white accents, and linked contrast details. |
| `cross_garment_binding` | 1.0 | 1 |  | The description distinguishes how each garment contributes to the overall outfit and explicitly links them through shared finishing and silhouette logic. |
| `fabric_family` | 1.0 | 1 |  | The text clearly names the main fabric families for the garments and shoes. |
| `footwear` | 1.0 | 1 |  | Footwear is clearly specified with shoe type, heel height/toe shape, and material/finish. |
| `functional_detail` | 1.0 | 1 |  | Multiple functional elements are explicitly described, including pockets and utility strap tabs. |
| `garment_category` | 1.0 | 1 |  | The text explicitly names the main garment categories and footwear. |
| `hardware_embellishment` | 1.0 | 1 |  | The text clearly includes visible hardware embellishment in the form of snaps. |
| `layering` | 1.0 | 1 |  | The text clearly describes a multi-layer outfit with explicit outer-to-inner relationships. |
| `length_hemline` | 1.0 | 1 |  | The text gives clear length and hemline/cuff information for the jacket and trousers. |
| `primary_color` | 1.0 | 1 |  | The dominant palette is clearly specified, with navy as the main color across the outfit. |
| `secondary_color` | 1.0 | 1 |  | The text includes clear secondary accent colors and visible contrast details. |
| `shoulder_architecture` | 1.0 | 1 |  | Shoulder structure is explicitly stated. |
| `silhouette` | 1.0 | 1 |  | Overall shape and structural contour are clearly described. |
| `surface_finish` | 1.0 | 1 |  | Multiple surface traits are explicitly described, including washed, matte, weathered, and glazed finishes. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes the relationship between the cropped jacket and the trouser rise, giving a readable top-bottom proportion and silhouette balance. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are clearly attached to the correct garments, with stable binding across jacket, trousers, top, belt, and shoes. Minor complexity comes from many layered details, but there is no major |
| `core_information_density` | 0.25 | 0 | 信息密度与简洁性 | The description contains strong garment detail, but it is heavily expanded with mood, metaphor, and interpretive commentary that dilutes the core outfit information. The main clothing pieces are prese |
| `craft_embellishment_salience` | 0.75 | 1 | 工艺装饰显著度 | Craft and trim are clearly located and visually functional, especially stitching, piping, and snaps, though the language remains polished rather than highly singular. |
| `design_distinctiveness` | 0.75 | 1 | 设计独特性 | The look has a clear memory hook in the marine/workwear hybrid with wrap-front top, contrast piping, pale cuff flash, and self-belt, though it still reads as a refined luxury variation rather than hig |
| `design_signal_purity` | 0.5 | 0 | 设计信号纯度 | There is substantial concrete design information, but it is repeatedly interwoven with mood, narrative, and evaluative phrasing, so the signal is mixed rather than purely design-fact driven. |
| `fine_grained_attribute_usage` | 1.0 | 1 | 术语具体度 | Color, material, finish, and structural details are consistently fine-grained and internally coherent, with strong visual specificity and minimal generic wording. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly visual, garment-specific, and largely prompt-ready, with clear silhouette, materials, colors, and styling. It is still somewhat prose-like and descriptive rather than concise prompt |
| `information_ordering` | 1.0 | 1 | 结构清晰度 | The description follows a clear body-to-details progression: outer layer, then trousers and top, then accessories/finishing, then footwear. The hierarchy is easy to track and the outfit can be reconst |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text coordinates multiple garments well and generally keeps each material, color, and detail with the right item. A few relations are dense, but the multi-item binding remains coherent and imageab |
| `reference_clarity` | 1.0 | 1 | 语言清晰度 | References and ellipses are clear throughout; antecedents are stable and the sequence of garments remains easy to track without ambiguity. |
| `silhouette_combination_originality` | 0.5 | 0 | 组合原创性 | The silhouette is coherent and attractive, but the overall combination is still a fairly legible luxury formula of cropped jacket, tailored trouser, and loafers, with only moderate novelty from the wr |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and attachment relationships are clearly described and visually imageable, with coherent over/under and waistband/cuff interactions. The spatial logic is strong, though the prose includes som |
| `specific_noun_usage` | 1.0 | 1 | 术语具体度 | The description uses highly specific garment names, materials, colors, and construction terms throughout, producing a clear and fashion-legible visual. |
| `visibility_priority` | 0.5 | 0 | 信息密度与简洁性 | Most details are visible and imageable, but the text also spends substantial space on lower-priority conceptual framing and tactile/atmospheric language. Visible garment structure is still prioritized |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly anchored to visible garment zones and readable construction details, with clear front/hem/cuff references and visible layering. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | The trunk garments and shoes read as a coherent layered outfit without left-right or mutually exclusive garment conflicts. |
| `coordination_penalty` | 0.0 | The palette and material language are coordinated across outerwear, trousers, top, and shoes; no major styling clash appears on trunk pieces. |
| `formula_template_penalty` | 0.25 | The look follows a fairly common fashion-description formula built from standard garment types and interchangeable material adjectives, though it is not strongly template-like. |
| `generation_content_penalty` | 0.5 | The description leans heavily into conceptual, editorial mood language and repeated maritime metaphors, which reduces prompt efficiency despite clear garment details. |
| `rationality_penalty` | 0.0 | All described construction details are physically plausible for ordinary apparel; no implausible materials or impossible garment mechanics are asserted. |

## Quality issues (质量短板)

- **`core_information_density`** (score 0.25) — The description contains strong garment detail, but it is heavily expanded with mood, metaphor, and interpretive commentary that dilutes the core outfit information. The main clothing pieces are present, yet the prompt is not highly concise or efficiently organized.
- **`visibility_priority`** (score 0.5) — Most details are visible and imageable, but the text also spends substantial space on lower-priority conceptual framing and tactile/atmospheric language. Visible garment structure is still prioritized overall, though not as tightly as it could be.
- **`silhouette_combination_originality`** (score 0.5) — The silhouette is coherent and attractive, but the overall combination is still a fairly legible luxury formula of cropped jacket, tailored trouser, and loafers, with only moderate novelty from the wrap top and marine detailing.
- **`design_signal_purity`** (score 0.5) — There is substantial concrete design information, but it is repeatedly interwoven with mood, narrative, and evaluative phrasing, so the signal is mixed rather than purely design-fact driven.

## Skipped metrics (不适用)

- `pattern_type` (coverage_score) — No pattern or print is described.
- `construction_technique` (coverage_score) — The text mentions tailoring and topstitching, but not a salient specialized construction technique of the type required by the rule.
- `deconstruction` (coverage_score) — No deconstruction, splicing, displacement, or reconstruction is explicitly described.
- `bag` (coverage_score) — No bag is described or implied as a visible styling element.
- `jewelry` (coverage_score) — No salient jewelry or body ornament is present.
- `asymmetry` (coverage_score) — No clear asymmetrical design or uneven garment structure is described.
- `quantity_accuracy` (quality_score) — The text contains no explicit counts, numerals, or quantity relations to evaluate.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral asymmetry is described.
