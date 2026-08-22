# Text Evaluation Report

- **Source:** look_03.txt
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.0
- **Total score (S_fp):** 0.7789 (Strong)
- **Coverage axis:** 1.0
- **Quality axis (raw / base / penalized):** 0.7833 / 0.7256 / 0.7256
- **Penalties (mean):** 0.1
- **R_content:** 0.751638

## Gates

- Score gate: 0.7789 (threshold 0.7) → **PASS**
- Penalty gate: 0.1 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `belt` | 1.0 | 1 |  | A visible belt is explicitly present and its relation to the outfit is described. |
| `body_coverage` | 1.0 | 1 |  | The text discusses coverage and exposure through layering and open footwear. |
| `closure` | 1.0 | 1 |  | The text clearly describes button closures on the jacket. |
| `color_relationship_logic` | 1.0 | 1 |  | The text explains the palette logic through contrast and coordinated nautical layering, not just isolated color names. |
| `cross_garment_binding` | 1.0 | 1 |  | Multiple garments are present and the text consistently assigns attributes to each item, keeping the jacket, knit, shorts, belt, and sandals visually distinct. |
| `fabric_family` | 1.0 | 1 |  | The text clearly names the main fabric families for the outfit components. |
| `footwear` | 1.0 | 1 |  | Footwear is clearly specified by type, construction, and finish. |
| `functional_detail` | 1.0 | 1 |  | Functional garment details are explicitly described, including belt, waistband, and sandal straps. |
| `garment_category` | 1.0 | 1 |  | The text clearly names the main garment categories in the outfit. |
| `layering` | 1.0 | 1 |  | The text clearly describes a layered outfit with jacket over knit and shorts, with visible ordering. |
| `length_hemline` | 1.0 | 1 |  | The text explicitly states garment lengths and hem positions. |
| `pattern_type` | 1.0 | 1 |  | A clear pattern type is given: marinière/striped knit. |
| `primary_color` | 1.0 | 1 |  | The dominant palette is clearly stated, with chalk white as the main jacket color and navy/black as supporting tones. |
| `secondary_color` | 1.0 | 1 |  | Secondary colors are clearly present and anchored to specific garments and visible details. |
| `shoulder_architecture` | 1.0 | 1 |  | Shoulder structure is directly described and is visually salient. |
| `silhouette` | 1.0 | 1 |  | It gives a clear overall structural read of the look, including boxy, slim, and straight lines. |
| `surface_finish` | 1.0 | 1 |  | It explicitly describes surface and hand-feel traits such as lightweight, structured, polished, and matte. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes the relationship between the cropped jacket, waist-length knit, and shorts, including where each sits on the body and how the silhouette is balanced. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 1.0 | 1 | 属性绑定准确度 | Attributes are consistently attached to the correct garments and accessory: jacket, knit, belt, and sandals are each clearly described without cross-binding or left-right confusion. |
| `core_information_density` | 0.5 | 0 | 信息密度与简洁性 | The text contains strong, imageable garment information and a clear outfit structure, but it is also heavily elaborated with stylistic narration and repeated interpretive phrasing. Core clothing detai |
| `craft_embellishment_salience` | 0.75 | 1 | 工艺装饰显著度 | Craft and finishing details are clearly located and visually functional, especially the topstitching and binding, though they are not highly unusual or the sole defining feature. |
| `design_distinctiveness` | 0.75 | 1 | 设计独特性 | The look has a clear memory hook in the graphic seam framing plus the visible lining contrast, which goes beyond a basic resort formula, though it is still grounded in familiar Chanel-coded tailoring. |
| `design_signal_purity` | 0.5 | 0 | 设计信号纯度 | The text contains substantial design facts, but they are repeatedly interwoven with mood, setting, and brand-essay language, so the signal is only moderately pure. |
| `fine_grained_attribute_usage` | 1.0 | 1 | 术语具体度 | Attributes are consistently fine-grained across color, fabric, trim, hardware, and silhouette, with strong visual specificity and coherent garment detail. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly imageable and already organized like a fashion prompt with clear garment hierarchy, colors, materials, and styling. It is slightly verbose and interpretive in places, but still very |
| `information_ordering` | 1.0 | 1 | 结构清晰度 | The description is organized from main garment to underlayer, then accessories/finishing details, and finally footwear. The hierarchy is clear and easy to reconstruct visually. |
| `multi_garment_binding` | 1.0 | 1 | 属性绑定准确度 | The multi-item outfit is structured cleanly, with colors, materials, and functions bound to the correct pieces and layered relations remaining coherent. |
| `reference_clarity` | 1.0 | 1 | 语言清晰度 | Pronouns and omitted subjects are consistently anchored to clear antecedents, and the garment sequence is easy to follow without ambiguity. |
| `silhouette_combination_originality` | 0.25 | 0 | 组合原创性 | The outfit follows a highly predictable cropped-jacket-plus-striped-top-plus-shorts-plus-belt-plus-flat-sandal resort template, with limited combination originality. |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and attachment relationships are clear and visually coherent: jacket over knit, knit meeting shorts at the waist, and lining only glimpsed at movement. The spatial logic is strong and easy to |
| `specific_noun_usage` | 1.0 | 1 | 术语具体度 | The description uses highly specific garment nouns, materials, colors, and construction terms throughout, giving a clear and precise fashion image. |
| `visibility_priority` | 0.5 | 0 | 信息密度与简洁性 | The visible outfit components are prioritized overall, but the description still spends notable space on lower-visibility or interpretive details such as lining, salon/daylight framing, and thematic c |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly anchored to visible garment zones, layers, hems, and edge details, reading like a direct observation of the outfit. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | The trunk garments and footwear read as a coherent single outfit with no left-right or mutually exclusive garment conflicts. |
| `coordination_penalty` | 0.0 | The palette and styling language are aligned across layers; no major coordination clash appears in the main silhouette. |
| `formula_template_penalty` | 0.25 | The description follows a common fashion-look formula with repeated brand-signaling and mood-setting language, though it still contains specific craft and material details. |
| `generation_content_penalty` | 0.25 | Mostly imageable garment description, but it includes repeated conceptual/runway-style phrasing and lifestyle framing that slightly reduces prompt efficiency. |
| `rationality_penalty` | 0.0 | All materials and construction details are physically plausible for ordinary wear. |

## Quality issues (质量短板)

- **`core_information_density`** (score 0.5) — The text contains strong, imageable garment information and a clear outfit structure, but it is also heavily elaborated with stylistic narration and repeated interpretive phrasing. Core clothing details remain present and coherent, yet the density is diluted by descriptive prose rather than kept maximally concise.
- **`visibility_priority`** (score 0.5) — The visible outfit components are prioritized overall, but the description still spends notable space on lower-visibility or interpretive details such as lining, salon/daylight framing, and thematic commentary. The balance is acceptable, though not tightly optimized for visible-only prompt usefulness.
- **`silhouette_combination_originality`** (score 0.25) — The outfit follows a highly predictable cropped-jacket-plus-striped-top-plus-shorts-plus-belt-plus-flat-sandal resort template, with limited combination originality.
- **`design_signal_purity`** (score 0.5) — The text contains substantial design facts, but they are repeatedly interwoven with mood, setting, and brand-essay language, so the signal is only moderately pure.

## Skipped metrics (不适用)

- `construction_technique` (coverage_score) — No salient named construction technique like pleating, quilting, embroidery, cut-outs, or engineered panel work is described.
- `deconstruction` (coverage_score) — The text does not mention deconstruction, splicing, displacement, or reconstruction.
- `hardware_embellishment` (coverage_score) — Buttons and belt hardware are present, but no clearly salient embellishment such as chains, studs, rings, or crystals is described.
- `bag` (coverage_score) — No bag is mentioned or implied as part of the look.
- `jewelry` (coverage_score) — No jewelry or body ornament is described.
- `asymmetry` (coverage_score) — No asymmetrical design, one-shoulder, uneven hem, or similar imbalance is described.
- `quantity_accuracy` (quality_score) — The text contains no explicit counts, numerals, or quantity relations that require verification.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral asymmetry is described.
- `gender_expression` (bonus_score) — No explicit gender expression or androgyny is mentioned.
