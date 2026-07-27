# Text Evaluation Report

- **Source:** look_04.txt
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.1.0
- **Total score (S_fp):** 0.8512 (Strong)
- **Coverage axis:** 0.9474
- **Quality axis (raw / base / penalized):** 0.8636 / 0.8125 / 0.8125
- **Penalties (mean):** 0.0625
- **R_content:** 0.83258

## Gates

- Score gate: 0.8512 (threshold 0.7) → **PASS**
- Penalty gate: 0.0625 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `bag` | 1.0 | 1 |  | The bag is explicitly identified by type, material/color, and carrying position, satisfying coverage. |
| `belt` | 1.0 | 1 |  | A visible belt is explicitly present, with clear attachment and function at the waist. |
| `closure` | 1.0 | 1 |  | The text clearly specifies closure details for the jacket and a buckle at the waist. |
| `color_relationship_logic` | 1.0 | 1 |  | The text explains the palette as a controlled white-and-navy scheme with deliberate contrast and accent logic. |
| `cross_garment_binding` | 1.0 | 1 |  | The text distinguishes how the jacket, shirt, shorts, and belt relate to each other, making the multi-garment binding clear. |
| `fabric_family` | 1.0 | 1 |  | The text clearly names the main fabric families for the garments. |
| `footwear` | 1.0 | 1 |  | The text clearly specifies footwear type plus shape and material/color details. |
| `functional_detail` | 1.0 | 1 |  | Functional elements like pockets and a handled bag are explicitly described. |
| `garment_category` | 1.0 | 1 |  | The text clearly names the main garment categories and completes the look with footwear and a bag. |
| `hardware_embellishment` | 0.0 | 0 |  | The text includes hardware, but it is not a clearly salient embellishment like chains, studs, rings, or crystals. |
| `layering` | 1.0 | 1 |  | The text clearly describes a layered outfit with readable outerwear-over-shirt relations and visible overlap. |
| `length_hemline` | 1.0 | 1 |  | The description explicitly states hem and length information for both jacket and shorts. |
| `pattern_type` | 1.0 | 1 |  | A specific pattern type is named: banker stripes. |
| `primary_color` | 1.0 | 1 |  | White/chalk-white is the dominant base color of the look. |
| `secondary_color` | 1.0 | 1 |  | Clear secondary colors are present alongside the white base, including navy accents and black accessories/trim. |
| `shoulder_architecture` | 1.0 | 1 |  | Shoulder structure is directly described and is visually salient. |
| `silhouette` | 1.0 | 1 |  | It gives a clear overall structural read: cropped, boxy, tailored, and vertically elongated. |
| `surface_finish` | 1.0 | 1 |  | It specifies surface/hand-feel traits such as stiffness, weight, and lacquered finish. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes upper-lower proportion and silhouette balance through waist placement, cropped jacket length, and mid-thigh shorts. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 1.0 | 1 | 属性绑定准确度 | Attributes are consistently attached to the correct garments and accessories, with clear separation between jacket, shirt, shorts, belt, sandals, and bag. |
| `core_information_density` | 0.5 | 0 | 信息密度与简洁性 | The main outfit is clearly established and imageable, but the description is quite long and layered with repeated interpretive phrasing and multiple accessory/detail clauses. Core garment information  |
| `fine_grained_attribute_usage` | 1.0 | 1 | 术语具体度 | Color, fabric, construction, and silhouette details are consistently fine-grained and visually precise, producing a strong imageable fashion description. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly visual, garment-specific, and layered in a way that is close to a generation prompt. It clearly defines silhouette, materials, colors, and styling, though it still reads somewhat li |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a clear garment-to-detail progression: jacket, inner shirt, shorts, then accessories and finishing notes. There is some repetition and occasional stylistic elaboration, but the |
| `multi_garment_binding` | 1.0 | 1 | 属性绑定准确度 | The multi-item outfit is described with stable, unambiguous binding across layers and accessories, and no major attribute is misassigned between garments. |
| `quantity_accuracy` | 1.0 | 1 | 语言清晰度 | Quantity expressions are consistent and unambiguous; the singular/plural references and part-to-part relations are easy to track. |
| `reference_clarity` | 1.0 | 1 | 语言清晰度 | Pronouns and omitted subjects are clearly anchored to nearby nouns, and the garment references remain stable throughout. |
| `spatial_coherence` | 1.0 | 1 | 生成适配度 | Layering, inside/outside visibility, and attachment positions are clearly and coherently described. The spatial relationships are easy to visualize and internally consistent, making the ensemble highl |
| `specific_noun_usage` | 1.0 | 1 | 术语具体度 | Uses highly specific garment, material, and accessory nouns throughout, with clear fashion terminology and little generic wording. |
| `visibility_priority` | 0.5 | 0 | 信息密度与简洁性 | Visible clothing elements are prioritized overall, but the text still spends meaningful space on subtle interior lining and mood/staging language that is less directly visible. The prompt remains usab |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | The trunk garments and footwear read as a coherent nautical tailored look with no direct left-right or mutually exclusive garment conflicts. |
| `coordination_penalty` | 0.0 | Color, material, and styling cues are coordinated around a consistent white/navy/black maritime palette without major trunk-level clash. |
| `generation_content_penalty` | 0.25 | The description is mostly imageable, but it includes some conceptual/runway-style framing and brand-reference commentary that slightly reduces prompt efficiency. |
| `rationality_penalty` | 0.0 | The materials and garment construction are physically plausible and consistent with ordinary wear. |

## Missing coverage (未覆盖)

- **`hardware_embellishment`** — The text includes hardware, but it is not a clearly salient embellishment like chains, studs, rings, or crystals.

## Quality issues (质量短板)

- **`core_information_density`** (score 0.5) — The main outfit is clearly established and imageable, but the description is quite long and layered with repeated interpretive phrasing and multiple accessory/detail clauses. Core garment information remains strong, yet the density is diluted by extended scene-setting and stylistic explanation.
- **`visibility_priority`** (score 0.5) — Visible clothing elements are prioritized overall, but the text still spends meaningful space on subtle interior lining and mood/staging language that is less directly visible. The prompt remains usable, though not maximally focused on what will dominate the image.

## Skipped metrics (不适用)

- `body_coverage` (coverage_score) — The text does not emphasize notable skin exposure or cutout-style reveal beyond ordinary garment coverage.
- `construction_technique` (coverage_score) — No specific advanced construction technique such as pleating, quilting, embroidery, cut-outs, or engineered panel work is clearly described.
- `deconstruction` (coverage_score) — The text does not mention deconstruction, splicing, displacement, or reconstruction.
- `jewelry` (coverage_score) — No jewelry or body ornament is mentioned.
- `asymmetry` (coverage_score) — No asymmetrical garment structure is described.
- `bilateral_coherence` (quality_score) — No explicit left-right bilateral differences are described.
- `gender_expression` (bonus_score) — No explicit gender expression or androgyny is stated.
- `negation_control` (bonus_score) — The text does not primarily emphasize exclusions or absence of elements as a design requirement.
