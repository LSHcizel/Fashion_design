# Text Evaluation Report

- **Source:** look_02.txt
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.1.0
- **Total score (S_fp):** 0.8887 (Strong)
- **Coverage axis:** 1.0
- **Quality axis (raw / base / penalized):** 0.8864 / 0.8438 / 0.8438
- **Penalties (mean):** 0.0625
- **R_content:** 0.86926

## Gates

- Score gate: 0.8887 (threshold 0.7) → **PASS**
- Penalty gate: 0.0625 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `belt` | 1.0 | 1 |  | A visible belt is explicitly present and its placement/function at the waist is clearly described. |
| `body_coverage` | 1.0 | 1 |  | The description clearly emphasizes visible/revealed areas, including layered visibility and exposed feet. |
| `closure` | 1.0 | 1 |  | The text clearly describes multiple closure/fastening elements, including a front fastening, buttons, and a belt closure. |
| `color_relationship_logic` | 1.0 | 1 |  | The text explains the color logic through contrast and tonal echoing, making the palette coherent and imageable. |
| `cross_garment_binding` | 1.0 | 1 |  | The description clearly distinguishes which attributes belong to the jacket, shirt, shorts, belt, and sandals, showing how the items relate across the full outfit. |
| `fabric_family` | 1.0 | 1 |  | The text clearly names the main fabric families for the garments. |
| `footwear` | 1.0 | 1 |  | Footwear is clearly specified as sandals, with shape and material/finish details covered. |
| `functional_detail` | 1.0 | 1 |  | Functional details are explicitly present, especially pockets and structural straps. |
| `garment_category` | 1.0 | 1 |  | The text clearly names the main garment categories in the look. |
| `hardware_embellishment` | 1.0 | 1 |  | The text includes salient hardware, especially the branded metal buckle and metal fastening. |
| `layering` | 1.0 | 1 |  | The text clearly describes layered garments and their visible order: jacket over shirt over shorts, with the belt at the waist. |
| `length_hemline` | 1.0 | 1 |  | The text explicitly states garment lengths and hem positions. |
| `pattern_type` | 1.0 | 1 |  | A clear stripe pattern is described for the shirt. |
| `primary_color` | 1.0 | 1 |  | The dominant palette is clearly established, led by navy, white, and black accents. |
| `secondary_color` | 1.0 | 1 |  | Secondary colors are explicitly present as accents and supporting tones alongside the main navy-white scheme. |
| `shoulder_architecture` | 1.0 | 1 |  | Shoulder construction is directly described and is visually salient. |
| `silhouette` | 1.0 | 1 |  | It gives a clear overall structural read: boxy cropped top, straight shorts, and a crisp tailored frame. |
| `surface_finish` | 1.0 | 1 |  | It specifies multiple surface traits such as smoothness, polish, and matte finish, plus the jacket’s crisp structure. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes waist placement and the visual balance between the cropped jacket, tucked shirt, and shorts, including a stated lengthening proportion. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 1.0 | 1 | 属性绑定准确度 | Attributes are consistently attached to the correct garments and body area: jacket material/structure, belt at the waist, and sandals on the feet are all clearly and coherently bound. |
| `core_information_density` | 0.5 | 0 | 信息密度与简洁性 | The text clearly prioritizes the main garments and their silhouette, but it is quite verbose and repeatedly explains mood, symbolism, and styling intent. Core clothing information is present and coher |
| `fine_grained_attribute_usage` | 1.0 | 1 | 术语具体度 | Color, material, and construction details are consistently fine-grained and fashion-specific, with strong structural and surface precision. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly visual, garment-specific, and organized as a coherent single look with clear layering and styling logic, so it is close to prompt-ready. It is still somewhat prose-like and interpre |
| `information_ordering` | 1.0 | 1 | 结构清晰度 | The description is organized from main garment to layered pieces, then accessories, then footwear, making the outfit easy to reconstruct in a clear top-to-bottom sequence. |
| `multi_garment_binding` | 1.0 | 1 | 属性绑定准确度 | Multiple garments are described with clear separation of their materials, colors, and roles, and the text keeps each attribute tied to the correct item without cross-binding. |
| `quantity_accuracy` | 1.0 | 1 | 语言清晰度 | The explicit quantity relation is clear and consistent; the text cleanly distinguishes first/second straps and maintains stable reference throughout. |
| `reference_clarity` | 1.0 | 1 | 语言清晰度 | Pronouns and omitted subjects are easy to resolve, with each sentence’s referent remaining stable and visually coherent. |
| `spatial_coherence` | 1.0 | 1 | 生成适配度 | Layering, tuck-in relation, waist placement, and footwear completion are all clearly articulated and visually reconstructable. The spatial grammar is coherent and easy to image. |
| `specific_noun_usage` | 1.0 | 1 | 术语具体度 | The description uses highly specific garment names, materials, and accessory terms throughout, creating a clear fashion object with strong visual precision. |
| `visibility_priority` | 0.5 | 0 | 信息密度与简洁性 | Visible, image-dominant elements are mostly foregrounded, especially jacket, shirt, shorts, belt, and sandals. However, the description also spends substantial space on less directly visible or interp |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | The jacket, shirt, shorts, belt, and sandals form a coherent single outfit without trunk-level contradictions or left-right conflicts. |
| `coordination_penalty` | 0.0 | The styling language is unified: tailored, maritime, crisp, and minimal, with accessories and footwear supporting the same mood. |
| `generation_content_penalty` | 0.25 | Mostly imageable garment description, but it includes some runway/editorial framing and conceptual lifestyle language that slightly reduces prompt efficiency. |
| `rationality_penalty` | 0.0 | Materials and construction are realistic and wearable; no physically implausible garment structure is asserted. |

## Quality issues (质量短板)

- **`core_information_density`** (score 0.5) — The text clearly prioritizes the main garments and their silhouette, but it is quite verbose and repeatedly explains mood, symbolism, and styling intent. Core clothing information is present and coherent, yet the density is diluted by descriptive framing and interpretive commentary.
- **`visibility_priority`** (score 0.5) — Visible, image-dominant elements are mostly foregrounded, especially jacket, shirt, shorts, belt, and sandals. However, the description also spends substantial space on less directly visible or interpretive details such as construction intent, atmosphere, and symbolic reading, which reduces strict visibility priority.

## Skipped metrics (不适用)

- `construction_technique` (coverage_score) — The text describes tailoring and topstitching, but not a salient named construction technique of the type required by the rule.
- `deconstruction` (coverage_score) — No deconstruction, splicing, displacement, or reconstruction is explicitly mentioned.
- `bag` (coverage_score) — No bag is described or implied as part of the look.
- `jewelry` (coverage_score) — No jewelry or body ornament is mentioned.
- `asymmetry` (coverage_score) — No asymmetrical design, uneven structure, or one-sided garment detail is described.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral asymmetry is described.
