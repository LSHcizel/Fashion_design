# Text Evaluation Report

- **Source:** 53_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__053_media_cha_biarritz_ps27_042_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.8723 (Strong)
- **Coverage axis:** 0.9412
- **Quality axis (raw / base / penalized):** 0.8462 / 0.8542 / 0.8542
- **Penalties (mean):** 0.2
- **R_content:** 0.811239

## Gates

- Score gate: 0.8723 (threshold 0.7) → **PASS**
- Penalty gate: 0.2 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `asymmetry` | 1.0 | 1 |  | Asymmetric structure is explicitly stated in both the top hem and the trouser hems. |
| `bag` | 1.0 | 1 |  | The bag is clearly identified by type, shape/volume, and color/material details. |
| `body_coverage` | 1.0 | 1 |  | The text clearly indicates covered areas on the torso and partial exposure at the feet/ankles through strappy sandals. |
| `color_relationship_logic` | 1.0 | 1 |  | The palette is organized as a clear contrast between a simple dark top and vivid multicolor printed bottoms, with the print itself structured in large angular panels and striped/crosshatched sections. |
| `cross_garment_binding` | 1.0 | 1 |  | Multiple garments and accessories are clearly distinguished and described with their own attributes, so item-to-item binding is coherent. |
| `fabric_family` | 0.0 | 0 |  | The text describes garment shapes and drape, but does not clearly identify a material family such as silk, cotton, denim, leather, knit, or chiffon. |
| `footwear` | 1.0 | 1 |  | The footwear is specified by shoe family, heel form, and visible color/ornamental details. |
| `functional_detail` | 1.0 | 1 |  | The text clearly mentions functional/structural strap details on both the tote and sandals. |
| `garment_category` | 1.0 | 1 |  | The text clearly identifies the main garment categories: top/tunic, trousers/culottes, and sandals. |
| `layering` | 1.0 | 1 |  | The text clearly describes a layered outfit with an over-top and trousers beneath, plus visible inner panels in the bag. |
| `length_hemline` | 1.0 | 1 |  | The text gives clear hem and length information for both the top and trousers. |
| `pattern_type` | 1.0 | 1 |  | The text explicitly identifies the pattern types as patchwork graphic print with stripes and crosshatching. |
| `primary_color` | 1.0 | 1 |  | Black is the dominant base color of the upper layer and footwear, making it a clear primary color. |
| `secondary_color` | 1.0 | 1 |  | The text includes visible secondary accent colors against the black base, especially pale trim and pale pink ankle ties. |
| `silhouette` | 1.0 | 1 |  | It explicitly describes the overall shape as loose, fluid, wide-leg, and silhouette-dominating. |
| `surface_finish` | 1.0 | 1 |  | The description clearly conveys a draped, flowing surface quality for the trousers. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes the upper-to-lower body balance and how the top falls over the waist while the bottoms dominate the silhouette. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are bound to the correct entities, with clear separation between top, trousers, sandals, and tote. Minor ambiguity remains from hedged phrasing like “top or tunic” and “trousers or cul |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is compact and heavily garment-focused, with clear visible-body coverage and layered outfit details. There is some stylistic framing and a few interpretive phrases, but no long essay-l |
| `craft_embellishment_salience` | 0.75 | 1 | 工艺装饰显著度 | Craft and embellishment are clearly visible and positioned, especially the trim and printed panel construction, though the description emphasizes graphic structure more than a single refined craft tec |
| `design_distinctiveness` | 1.0 | 1 | 设计独特性 | The look has multiple clear memory points: unusual draped culotte hems, strong patchwork paneling, and fluttering extensions. It is far from a formula outfit. |
| `design_signal_purity` | 1.0 | 1 | 设计信号纯度 | The text is overwhelmingly made of concrete design facts: silhouette, hem, print, straps, and bag construction. Mood language is minimal and does not dilute the design signal. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly imageable and already organized around visible silhouette, garment categories, layering, and accessories, so it is close to a usable generation prompt. Minor issues remain because i |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a mostly natural body-to-detail order: overall framing, top, bottoms, footwear, then bag and summary. Minor compression and some dense print details interrupt flow, but the mai |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text keeps most multi-item attributes attached to the correct garment or accessory, and the layering order is coherent. There is some mild ambiguity in garment naming and in the accessory descript |
| `reference_clarity` | 1.0 | 1 | 语言清晰度 | References are stable and easy to track: the top is clearly linked by “Under it,” and the tote and sandals are explicitly assigned to the model, with no confusing pronoun shifts or ambiguous anteceden |
| `silhouette_combination_originality` | 1.0 | 1 | 组合原创性 | The combination is unusual and strongly shaped by the draped, asymmetric cropped trousers and the oversized tote. It does not read as a standard formula template. |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and attachment positions are clearly described, and the garment relationships are visually reconstructable. The only limitation is some ambiguity from optional phrasing and the dense descript |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | The text prioritizes visible, image-dominant elements such as silhouette, hem shape, print scale, footwear, and bag. It includes some interpretive styling language, but hidden or low-visibility detail |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is tightly anchored to visible garment zones and readable details, with honest uncertainty only where noted ('or'). It reads like direct runway observation. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.25 | Main garments are coherent, but there is mild uncertainty in garment identity wording ('top or tunic', 'trousers or culottes') rather than a hard trunk conflict. |
| `coordination_penalty` | 0.25 | The look is intentionally mixed but still readable; the main coordination is slightly busy due to the strong print, delicate heels, and casual tote, without a severe trunk-level clash. |
| `formula_template_penalty` | 0.25 | Some formulaic runway-summary phrasing and generic styling language are present, but the description remains grounded in specific garment details rather than a fully interchangeable cruise/resort template. |
| `generation_content_penalty` | 0.25 | Mostly imageable garment description, but includes some runway/framing language and a closing interpretive summary that slightly dilutes prompt efficiency. |
| `rationality_penalty` | 0.0 | No materially implausible construction or physically impossible wear is asserted. |

## Missing coverage (未覆盖)

- **`fabric_family`** — The text describes garment shapes and drape, but does not clearly identify a material family such as silk, cotton, denim, leather, knit, or chiffon.

## Skipped metrics (不适用)

- `shoulder_architecture` (coverage_score) — No salient shoulder construction is described.
- `closure` (coverage_score) — No explicit closure details such as buttons, zippers, ties, or buckles are described.
- `construction_technique` (coverage_score) — The description notes drape and asymmetric hems, but does not clearly identify a specific construction technique like pleating, quilting, embroidery, cut-outs, or engineered panel work.
- `deconstruction` (coverage_score) — The text does not explicitly mention deconstruction, splicing, displacement, or reconstruction.
- `hardware_embellishment` (coverage_score) — No salient hardware or metallic embellishment such as chains, studs, rings, or crystals is described.
- `jewelry` (coverage_score) — No jewelry or body ornament is explicitly present.
- `belt` (coverage_score) — No visible belt, sash, waist strap, or harness is described.
- `quantity_accuracy` (quality_score) — The text contains no explicit counts, numerals, or quantity relations that need verification.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral garment differences are described.
- `cultural_reference` (bonus_score) — No cultural, historical, or brand grounding is provided.
- `gender_expression` (bonus_score) — The description does not explicitly discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is stated beyond visual styling.
- `brand_alignment` (bonus_score) — No brand identity or brand-language target is mentioned.
- `negation_control` (bonus_score) — The text does not emphasize exclusions or absence of elements.
