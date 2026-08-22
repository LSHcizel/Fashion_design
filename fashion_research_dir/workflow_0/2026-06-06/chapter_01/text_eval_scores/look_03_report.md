# Text Evaluation Report

- **Source:** look_03.txt
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.1.0
- **Total score (S_fp):** 0.8891 (Strong)
- **Coverage axis:** 1.0
- **Quality axis (raw / base / penalized):** 0.875 / 0.8438 / 0.8438
- **Penalties (mean):** 0.0625
- **R_content:** 0.869651

## Gates

- Score gate: 0.8891 (threshold 0.7) → **PASS**
- Penalty gate: 0.0625 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `belt` | 1.0 | 1 |  | A visible belt is explicitly present and its placement/function on the waist is clear. |
| `body_coverage` | 1.0 | 1 |  | The text describes how much of the body is covered and how the layers sit on the body. |
| `closure` | 1.0 | 1 |  | The text clearly describes button closures on the jacket. |
| `color_relationship_logic` | 1.0 | 1 |  | It explains the palette relationship through contrast and accenting, not just isolated color names. |
| `cross_garment_binding` | 1.0 | 1 |  | The description clearly distinguishes which features belong to the jacket, knit, shorts, belt, and sandals, making the multi-garment composition coherent and attributable. |
| `fabric_family` | 1.0 | 1 |  | The text clearly names the main fabric families for the garments and footwear. |
| `footwear` | 1.0 | 1 |  | Footwear type, construction, and material/finish are clearly specified. |
| `functional_detail` | 1.0 | 1 |  | A functional waist accessory is explicitly described. |
| `garment_category` | 1.0 | 1 |  | The text clearly names the main garment categories in the outfit. |
| `layering` | 1.0 | 1 |  | The text clearly describes a jacket over a knit top over shorts, with readable layering relations. |
| `length_hemline` | 1.0 | 1 |  | The description explicitly states garment lengths and hem behavior. |
| `pattern_type` | 1.0 | 1 |  | The pattern type is clearly identified as stripes/marinière. |
| `primary_color` | 1.0 | 1 |  | The dominant outer garment color is clearly white/chalk white. |
| `secondary_color` | 1.0 | 1 |  | The text gives clear secondary colors and accent colors alongside the main white. |
| `shoulder_architecture` | 1.0 | 1 |  | Shoulder construction is directly described and is visually salient. |
| `silhouette` | 1.0 | 1 |  | It gives a clear overall silhouette and structural contour for the look. |
| `surface_finish` | 1.0 | 1 |  | It specifies surface qualities such as lightweight, polished, matte, and cushioned. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes the relationship between the cropped jacket, waist-length knit, and shorts, including where each sits on the body and how the silhouette is balanced. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 1.0 | 1 | 属性绑定准确度 | Attributes are consistently attached to the correct garments and accessory, with clear layering and no major binding ambiguity. |
| `core_information_density` | 0.5 | 0 | 信息密度与简洁性 | The text clearly prioritizes the outfit’s main garments and their visible construction, but it is also heavily layered with interpretive and atmospheric phrasing. Core fashion information remains stro |
| `fine_grained_attribute_usage` | 1.0 | 1 | 术语具体度 | Color, material, construction, and finish are described with fine granularity and strong visual specificity, making the outfit easy to imagine. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly visual and garment-specific, with clear silhouette, layering, colors, and materials, so it is close to a usable generation prompt. It is still somewhat prose-like and interpretive r |
| `information_ordering` | 1.0 | 1 | 结构清晰度 | The description follows a clear主体→内搭→下装→配件/细节→鞋履 order, with each layer introduced in a stable visual sequence. The hierarchy is easy to track and the outfit can be reconstructed without ambiguity. |
| `multi_garment_binding` | 1.0 | 1 | 属性绑定准确度 | Multiple garments are described with their own materials, colors, and functions, and the text keeps each attribute tied to the correct item. |
| `reference_clarity` | 1.0 | 1 | 语言清晰度 | References and pronouns are consistently anchored to clear antecedents, and the garment descriptions remain stable and easy to track throughout. |
| `spatial_coherence` | 1.0 | 1 | 生成适配度 | Layering, garment lengths, and attachment/visibility relationships are clearly articulated and visually coherent, making the outfit easy to reconstruct in image form. |
| `specific_noun_usage` | 1.0 | 1 | 术语具体度 | The description uses highly specific garment names, materials, and footwear terms throughout, with clear fashion vocabulary and little reliance on generic wording. |
| `visibility_priority` | 0.5 | 0 | 信息密度与简洁性 | Most of the description focuses on visible garments and silhouette-defining details, which is good for image generation. However, some attention goes to lower-visibility or interpretive elements like  |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | The outfit reads as a coherent single look with no trunk-level left-right conflicts or mutually exclusive garment identities. |
| `coordination_penalty` | 0.0 | The palette and styling language are aligned across jacket, knit, shorts, and sandals, producing a unified coastal-tailored ensemble. |
| `generation_content_penalty` | 0.25 | Mostly imageable garment description, but it includes some runway-essay style conceptual framing and brand-interpretive language that slightly reduces prompt efficiency. |
| `rationality_penalty` | 0.0 | All materials and construction details are physically plausible and consistent with ordinary wearable fashion. |

## Quality issues (质量短板)

- **`core_information_density`** (score 0.5) — The text clearly prioritizes the outfit’s main garments and their visible construction, but it is also heavily layered with interpretive and atmospheric phrasing. Core fashion information remains strong, yet the prose is somewhat verbose and stylistically padded, reducing density.
- **`visibility_priority`** (score 0.5) — Most of the description focuses on visible garments and silhouette-defining details, which is good for image generation. However, some attention goes to lower-visibility or interpretive elements like lining and thematic framing, so visibility priority is solid but not optimal.

## Skipped metrics (不适用)

- `construction_technique` (coverage_score) — No notable craft technique like quilting, embroidery, cut-outs, or engineered pleating is described.
- `deconstruction` (coverage_score) — The text does not mention deconstruction, splicing, displacement, or reconstruction.
- `hardware_embellishment` (coverage_score) — Buttons and topstitching are present, but no clearly salient decorative hardware such as chains, studs, rings, or crystals is described.
- `bag` (coverage_score) — No bag is described or implied as part of the look.
- `jewelry` (coverage_score) — No jewelry or body ornament is mentioned.
- `asymmetry` (coverage_score) — No asymmetrical design or uneven structure is described.
- `quantity_accuracy` (quality_score) — No explicit numbers, counts, or quantity relations are used in a way that requires quantity accuracy scoring.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral asymmetry is described.
- `gender_expression` (bonus_score) — No explicit gender expression or androgyny is mentioned.
