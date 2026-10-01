# Text Evaluation Report

- **Source:** 18_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__018_media_cha_biarritz_ps27_059_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.8336 (Strong)
- **Coverage axis:** 0.8333
- **Quality axis (raw / base / penalized):** 0.8269 / 0.8333 / 0.8333
- **Penalties (mean):** 0.2
- **R_content:** 0.775248

## Gates

- Score gate: 0.8336 (threshold 0.7) → **PASS**
- Penalty gate: 0.2 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `bag` | 0.0 | 0 |  | A bag is implied, but the text does not clearly cover at least two required facets such as bag type, shape/volume, and material/finish. |
| `body_coverage` | 1.0 | 1 |  | The text describes coverage clearly, including a covered torso and wrist-extending sleeves, while also implying limited leg exposure via the short skirt. |
| `closure` | 0.0 | 0 |  | A placket is mentioned, but no clear closure type such as buttons, zipper, ties, or buckles is specified. |
| `color_relationship_logic` | 1.0 | 1 |  | The text explains the color relationship through a dominant red-white striped scheme with a contrasting darker layer visible beneath, making the palette logic imageable. |
| `construction_technique` | 1.0 | 1 |  | Specific construction/craft techniques are named and localized, including appliqué on the front placket and layered pointed shapes at the hem. |
| `cross_garment_binding` | 1.0 | 1 |  | The description distinguishes the top/jacket, the visible intermediate layer, and the skirt, making the garment relationships clear. |
| `functional_detail` | 1.0 | 1 |  | The text clearly describes functional-style details including pocket-like bands/flaps and chain straps. |
| `garment_category` | 1.0 | 1 |  | The text clearly identifies the main garment types: an upper garment and a short skirt, with a head covering accessory. |
| `hardware_embellishment` | 1.0 | 1 |  | Chain hardware is explicitly mentioned and is visually salient. |
| `layering` | 1.0 | 1 |  | The text clearly describes a layered outfit with an outer upper garment over a skirt and a visible intermediate layer. |
| `length_hemline` | 1.0 | 1 |  | The text explicitly states garment length and hemline details for both top and skirt. |
| `pattern_type` | 1.0 | 1 |  | The pattern types are clearly identified as vertical stripes and pointed appliqué motifs. |
| `primary_color` | 1.0 | 1 |  | The main color story is clearly red and white. |
| `secondary_color` | 1.0 | 1 |  | A secondary color layer is explicitly described, including a darker navy/black-and-white visible layer and gold-toned accessory detail. |
| `shoulder_architecture` | 1.0 | 1 |  | Shoulder structure is directly described, with narrow shoulders and sleeve anchoring. |
| `silhouette` | 1.0 | 1 |  | It gives a clear structural silhouette: fitted torso, peplum-like waist, and very short skirt. |
| `surface_finish` | 0.0 | 0 |  | The description suggests structure, but it does not explicitly state a surface finish like glossy, matte, drapey, or stiff enough to count as a clear surface-trait hit. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes the relationship between the upper garment and the short skirt, including waist/hip break and overall silhouette balance. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are bound to the correct garment or accessory, and the layering is generally clear. Minor ambiguity remains in phrases like “top or jacket” and “suggesting a small bag mostly out of fr |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is dense with visible garment facts and construction details, with little mood or essay framing. It is somewhat long and layered, but the main look remains clear and imageable. |
| `craft_embellishment_salience` | 1.0 | 1 | 工艺装饰显著度 | The craft is specific in type, location, and visual effect, and it functions as a main hook of the look. |
| `design_distinctiveness` | 1.0 | 1 | 设计独特性 | The look has multiple clear memory points: strong graphic striping, unusual flame/leaf appliqué, and a jagged scalloped peplum/fringe structure. |
| `design_signal_purity` | 1.0 | 1 | 设计信号纯度 | The text is dominated by concrete design facts, with only a brief concluding mood phrase and no extended essay-like framing. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly imageable and mostly prompt-ready, with clear garment types, silhouette, layering, and surface details. It is slightly weakened by some hedging/alternatives like “top or jacket” and |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description moves from overall look to garment layers, then to neckline, sleeves, waist/hem, skirt, and accessories in a mostly natural hierarchy. There is some compression and a few dense detail  |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text distinguishes multiple garments and mostly keeps their attributes attached to the right item: upper layer, skirt, inner visible layer, and accessory. There is slight uncertainty around the ex |
| `reference_clarity` | 0.75 | 1 | 语言清晰度 | References are mostly clear and stable, with consistent subjects and object tracking. Minor ambiguity remains in phrases like “long-sleeve top or jacket” and “suggesting a small bag mostly out of fram |
| `silhouette_combination_originality` | 0.75 | 1 | 组合原创性 | The silhouette is more distinctive than a standard formula because of the peplum/scalloped construction and ornamental layering, though the base top-over-skirt pairing remains relatively familiar. |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and attachment relationships are generally clear and visually reconstructable, especially the top-over-skirt structure and visible intermediate layer. Minor ambiguity remains in the exact gar |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | Most of the text prioritizes visible, renderable clothing features. There is a small amount of inferential wording, such as the bag being “mostly out of frame,” but it does not dominate the prompt. |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is anchored in visible garment parts and placement, with clear layering and hem/cuff observations rather than mood prose. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.25 | Main silhouette is coherent, but there is mild ambiguity between top and jacket and a layered hem transition that could be read as slightly conflicting. |
| `coordination_penalty` | 0.25 | The look is largely coordinated, with only a small accessory color/material accent that does not disrupt the main outfit language. |
| `formula_template_penalty` | 0.25 | Some formula-like runway phrasing and a familiar coordinated set structure are present, but the description still contains specific craft and silhouette details. |
| `generation_content_penalty` | 0.25 | Mostly grounded garment description, but includes some evaluative framing and a weak out-of-frame accessory hint that slightly reduces prompt efficiency. |
| `rationality_penalty` | 0.0 | The described construction is ornate but still physically plausible as fashion detailing. |

## Missing coverage (未覆盖)

- **`surface_finish`** — The description suggests structure, but it does not explicitly state a surface finish like glossy, matte, drapey, or stiff enough to count as a clear surface-trait hit.
- **`closure`** — A placket is mentioned, but no clear closure type such as buttons, zipper, ties, or buckles is specified.
- **`bag`** — A bag is implied, but the text does not clearly cover at least two required facets such as bag type, shape/volume, and material/finish.

## Skipped metrics (不适用)

- `fabric_family` (coverage_score) — The text describes color, pattern, and silhouette, but does not clearly identify a main fabric family such as silk, cotton, knit, leather, or denim.
- `deconstruction` (coverage_score) — No explicit deconstruction, splicing, displacement, or reconstruction is described.
- `footwear` (coverage_score) — No footwear is described.
- `jewelry` (coverage_score) — No salient jewelry or body ornament is explicitly present.
- `belt` (coverage_score) — No visible belt, sash, or waist strap is described; the waist emphasis comes from garment cut and peplum-like shaping.
- `asymmetry` (coverage_score) — No clear asymmetry, one-shoulder, single-sleeve, or uneven structural design is described.
- `quantity_accuracy` (quality_score) — The text contains no explicit counts or quantity relations that need verification.
- `bilateral_coherence` (quality_score) — No explicit left-right or bilateral asymmetry is described.
- `cultural_reference` (bonus_score) — No cultural, historical, or brand grounding is provided.
- `gender_expression` (bonus_score) — The text does not explicitly discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is stated.
- `brand_alignment` (bonus_score) — No brand identity or brand-language target is mentioned.
- `negation_control` (bonus_score) — The description does not emphasize exclusions or absence of elements.
