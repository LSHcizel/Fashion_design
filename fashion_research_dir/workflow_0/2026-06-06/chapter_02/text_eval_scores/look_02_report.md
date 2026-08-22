# Text Evaluation Report

- **Source:** look_02.txt
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.1.0
- **Total score (S_fp):** 0.8446 (Strong)
- **Coverage axis:** 1.0
- **Quality axis (raw / base / penalized):** 0.8182 / 0.7812 / 0.7812
- **Penalties (mean):** 0.0625
- **R_content:** 0.826124

## Gates

- Score gate: 0.8446 (threshold 0.7) → **PASS**
- Penalty gate: 0.0625 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `belt` | 1.0 | 1 |  | A visible waist belt is explicitly described and its relation to the wrap layer is clear. |
| `body_coverage` | 1.0 | 1 |  | The text clearly indicates exposed/revealed body areas and coverage level. |
| `closure` | 1.0 | 1 |  | Multiple explicit closure methods are described clearly. |
| `color_relationship_logic` | 1.0 | 1 |  | The text explains the color logic as a coordinated navy/indigo palette with white and metallic accents, not just isolated color names. |
| `cross_garment_binding` | 1.0 | 1 |  | The text distinguishes how the jacket, wrap top, trouser, and belt each function and relate to one another, making the multi-garment structure clear. |
| `fabric_family` | 1.0 | 1 |  | The text clearly names the main fabric families across the look. |
| `footwear` | 1.0 | 1 |  | Footwear is clearly specified with type, shape, and materials/finish. |
| `functional_detail` | 1.0 | 1 |  | The text clearly includes pockets and other functional garment details. |
| `garment_category` | 1.0 | 1 |  | The text clearly names the main garment categories and footwear. |
| `hardware_embellishment` | 1.0 | 1 |  | Visible hardware is prominent and repeatedly emphasized. |
| `layering` | 1.0 | 1 |  | The text clearly describes a jacket over a wrap-front top over trousers, with readable layer relationships. |
| `length_hemline` | 1.0 | 1 |  | Multiple length and hemline cues are given for jacket, trouser, and shoe relation to the ankle. |
| `primary_color` | 1.0 | 1 |  | The dominant palette is clearly established, especially navy/indigo with white footwear accents. |
| `secondary_color` | 1.0 | 1 |  | Secondary colors are clearly present as accents and contrast details. |
| `shoulder_architecture` | 1.0 | 1 |  | The shoulder structure is explicitly described as slightly squared. |
| `silhouette` | 1.0 | 1 |  | Overall shape and structural contour are explicitly described. |
| `surface_finish` | 1.0 | 1 |  | Multiple surface qualities are explicitly described, including washed/softened, matte, and sheen. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes upper-lower proportion and waist emphasis, with a cropped jacket balancing the trouser silhouette. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are clearly attached to the correct garment or accessory, and the layering is coherent. Minor complexity comes from multiple waist-related elements in close proximity, but the text sti |
| `core_information_density` | 0.5 | 0 | 信息密度与简洁性 | The text contains strong, imageable garment details and a clear outfit structure, but it is heavily elaborated with metaphorical framing and repeated interpretive commentary. Core clothing information |
| `fine_grained_attribute_usage` | 1.0 | 1 | 术语具体度 | Color, material, construction, and trim details are consistently fine-grained and visually actionable, producing a precise and coherent garment image. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly visual, garment-specific, and organized as a coherent full look, so it is close to prompt-ready. It is still somewhat essay-like and stylistically interpretive, which keeps it just  |
| `information_ordering` | 1.0 | 1 | 结构清晰度 | The description is organized from main garment to layered pieces, then accessories/hardware, and finally footwear, making the outfit easy to reconstruct in a clear visual hierarchy. |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The description handles several garments with mostly stable bindings and clear sequencing. There is some density around waist hardware and layered closures, but no major cross-assignment of colors, ma |
| `quantity_accuracy` | 1.0 | 1 | 语言清晰度 | Quantity expressions are modest and internally consistent; the text uses clear, non-conflicting counts and no ambiguous numerical relations. |
| `reference_clarity` | 1.0 | 1 | 语言清晰度 | Pronouns and references are consistently anchored to clear antecedents, with no confusing shifts in subject or object. |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and attachment relations are clearly described and visually reconstructable, with coherent top-to-bottom styling. The prose is still somewhat explanatory rather than purely spatial, so it is  |
| `specific_noun_usage` | 1.0 | 1 | 术语具体度 | The description uses highly specific garment names, materials, and footwear terminology throughout, with clear fashion semantics and little reliance on generic wording. |
| `visibility_priority` | 0.5 | 0 | 信息密度与简洁性 | Visible outfit elements are prioritized overall, but the description still spends substantial space on interpretive mood, brand-like associations, and subtle hardware details that are less visually do |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | The trunk garments and footwear read as a coherent layered outfit without direct left-right or mutually exclusive garment conflicts. |
| `coordination_penalty` | 0.0 | The workwear, nautical, and polished elements are coordinated into one consistent coastal-utility styling language. |
| `generation_content_penalty` | 0.25 | The description is imageable overall, but it leans repeatedly into conceptual/runway-style framing and evaluative language rather than staying purely on garment facts. |
| `rationality_penalty` | 0.0 | The materials and construction are physically plausible and described as ordinary wearable garments. |

## Quality issues (质量短板)

- **`core_information_density`** (score 0.5) — The text contains strong, imageable garment details and a clear outfit structure, but it is heavily elaborated with metaphorical framing and repeated interpretive commentary. Core clothing information remains present and coherent, yet the density is diluted by long descriptive passages and stylistic explanation.
- **`visibility_priority`** (score 0.5) — Visible outfit elements are prioritized overall, but the description still spends substantial space on interpretive mood, brand-like associations, and subtle hardware details that are less visually dominant than the main silhouette. The balance is acceptable, though not tightly optimized for immediate image generation.

## Skipped metrics (不适用)

- `pattern_type` (coverage_score) — No explicit pattern or print is described.
- `construction_technique` (coverage_score) — No clearly named special construction technique like quilting, pleating, cut-outs, or engineered panel work is described.
- `deconstruction` (coverage_score) — The text does not mention deconstruction, splicing, displacement, or reconstruction as a design approach.
- `bag` (coverage_score) — No bag is described or implied as a visible styling element.
- `jewelry` (coverage_score) — No salient jewelry or body ornament is explicitly present.
- `asymmetry` (coverage_score) — No clear asymmetrical garment structure is described.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral asymmetry is described.
- `gender_expression` (bonus_score) — No explicit gender-expression or androgyny framing is requested or stated.
