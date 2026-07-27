# Text Evaluation Report

- **Source:** 20_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__020_media_cha_biarritz_ps27_070_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.857 (Strong)
- **Coverage axis:** 0.95
- **Quality axis (raw / base / penalized):** 0.8269 / 0.8333 / 0.8333
- **Penalties (mean):** 0.1
- **R_content:** 0.827005

## Gates

- Score gate: 0.857 (threshold 0.7) → **PASS**
- Penalty gate: 0.1 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `bag` | 1.0 | 1 |  | Bag type and carry method are explicit, with color/material cues and handle detail. |
| `body_coverage` | 1.0 | 1 |  | The text clearly describes exposure and partial coverage through an open front, open neckline, and sheer overlay. |
| `closure` | 1.0 | 1 |  | The text clearly describes button closures on both the coat and shirt. |
| `color_relationship_logic` | 1.0 | 1 |  | The text explains the color logic as a dominant red-and-white outer layer over blue inner layers, with green as an accent in a multi-tone palette. |
| `construction_technique` | 1.0 | 1 |  | The text identifies notable construction/material techniques and gives their placement on the garment body. |
| `cross_garment_binding` | 1.0 | 1 |  | The description distinguishes which attributes belong to the coat, shirt/shirt-dress, and sheer net layer, so the multi-garment relations are clearly bound to specific items. |
| `fabric_family` | 1.0 | 1 |  | The text identifies clear material families: a structured coat, a sheer net layer, and a shirt/shirt-dress base. |
| `functional_detail` | 1.0 | 1 |  | Functional details are explicitly mentioned, especially the coat pockets. |
| `garment_category` | 1.0 | 1 |  | The text clearly names the main garment categories, including a coat and a shirt/shirt-dress. |
| `hardware_embellishment` | 0.0 | 0 |  | Jewelry is present, but the text does not clearly mention salient hardware such as chains, studs, metal rings, or crystals. |
| `jewelry` | 1.0 | 1 |  | Visible jewelry/body adornment is clearly present and salient. |
| `layering` | 1.0 | 1 |  | The text clearly describes multiple stacked garments and their visible order/coverage relationships. |
| `length_hemline` | 1.0 | 1 |  | The text gives clear length information for the coat and layered underpiece. |
| `pattern_type` | 1.0 | 1 |  | Multiple pattern types are explicitly named, including a lattice pattern and printed motifs. |
| `primary_color` | 1.0 | 1 |  | Red and white are clearly established as the dominant outer color story, with red especially emphasized in the coat. |
| `secondary_color` | 1.0 | 1 |  | Blue is a salient secondary color, repeatedly tied to the layered understructure beneath the red-and-white coat. |
| `shoulder_architecture` | 1.0 | 1 |  | Shoulder-area structure is salient through the broad lapel/collar framing and explicit shoulder detailing. |
| `silhouette` | 1.0 | 1 |  | The overall shape is explicitly described as structured and boxy. |
| `surface_finish` | 1.0 | 1 |  | It describes surface qualities including structure/hardness, sheerness, and a distressed textured finish. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes vertical proportion and layering between the upper coat and the longer blue layers beneath, making the top-bottom balance imageable. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are clearly tied to the correct garment or accessory, and the layering order is understandable. Minor ambiguity remains in phrases like "shirt or shirt-dress" and "reads like a vest, d |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is packed with concrete garment details and mostly prioritizes visible clothing structure, color, and layering. There is some extra elaboration on texture and styling, but it remains e |
| `craft_embellishment_salience` | 0.75 | 1 | 工艺装饰显著度 | Craft and surface treatment are clearly identified with placement and effect, though some elements are described with a bit of uncertainty (woven or printed). |
| `design_distinctiveness` | 1.0 | 1 | 设计独特性 | The look has multiple clear memory points: unusual distressed tufting, a net overlay, and a strong red-white lattice pattern with mixed-textile layering. |
| `design_signal_purity` | 1.0 | 1 | 设计信号纯度 | The text is dominated by concrete design facts, materials, layers, and placement, with essentially no mood-essay dilution. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly imageable and already organized around visible garments, layers, colors, and key construction details, so it is close to a usable generation prompt. It is slightly more descriptive  |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a mostly natural top-down structure: main garment first, then underlayers, then accessories. It is easy to reconstruct the outfit, though some details are densely packed within |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text keeps most garment-specific attributes attached to the right item and preserves the overall layering structure. There is slight cross-item ambiguity in the sheer blue layer's exact garment id |
| `reference_clarity` | 1.0 | 1 | 语言清晰度 | References are consistently anchored to clear noun phrases, with no confusing pronoun chains or ambiguous omissions. |
| `silhouette_combination_originality` | 0.75 | 1 | 组合原创性 | The combination is more inventive than a standard formula because of the open coat plus mesh overlay and layered shirt-dress structure, though the base tailoring remains fairly conventional. |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and relative placement are clearly described, and the coat-over-shirt-over-sheer-layer structure is visually coherent. Minor ambiguity remains in the exact identity of the sheer layer (“vest, |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | The text emphasizes image-dominant, visible features such as silhouette, layering, surface pattern, and accessories. It includes a few lower-visibility descriptors like the shirt opening and layered n |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is anchored in visible garment zones and layer relationships, with concrete observations rather than mood-led prose. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | No clear trunk-level left-right contradiction; the layers are described as stacked and compatible rather than mutually exclusive. |
| `coordination_penalty` | 0.0 | The look has mixed textures, but they are coordinated into one coherent styling language without trunk-level clash. |
| `formula_template_penalty` | 0.25 | Some runway-essay phrasing and a familiar layered-look structure make it mildly formulaic, but it remains grounded in specific garment details. |
| `generation_content_penalty` | 0.25 | Mostly imageable, but includes some runway-style framing and interpretive summary that slightly reduces prompt efficiency. |
| `rationality_penalty` | 0.0 | All described materials and accessories are physically plausible as fashion elements. |

## Missing coverage (未覆盖)

- **`hardware_embellishment`** — Jewelry is present, but the text does not clearly mention salient hardware such as chains, studs, metal rings, or crystals.

## Skipped metrics (不适用)

- `deconstruction` (coverage_score) — The text suggests distressed and mixed-textile styling, but does not explicitly describe deconstruction, splicing, displacement, or reconstruction.
- `footwear` (coverage_score) — No footwear is described.
- `belt` (coverage_score) — No visible belt, sash, or waist strap is mentioned.
- `asymmetry` (coverage_score) — No clear asymmetrical garment structure is described.
- `quantity_accuracy` (quality_score) — The text does not use explicit counts or quantity relations that need verification.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral asymmetry is described.
- `cultural_reference` (bonus_score) — No clear cultural, historical, or brand grounding is provided.
- `gender_expression` (bonus_score) — The description does not explicitly discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is explicitly stated beyond the garment description.
- `brand_alignment` (bonus_score) — No brand language or brand identity target is mentioned.
- `negation_control` (bonus_score) — The text does not emphasize exclusions or absence of elements.
