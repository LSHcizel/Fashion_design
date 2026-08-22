# Text Evaluation Report

- **Source:** 68_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__068_media_cha_biarritz_ps27_065_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.8389 (Strong)
- **Coverage axis:** 0.9412
- **Quality axis (raw / base / penalized):** 0.8077 / 0.8125 / 0.8125
- **Penalties (mean):** 0.1
- **R_content:** 0.809538

## Gates

- Score gate: 0.8389 (threshold 0.7) → **PASS**
- Penalty gate: 0.1 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `asymmetry` | 1.0 | 1 |  | Asymmetry is clearly stated in the skirt construction and reinforced by the one-sided slit and diagonal overlap. |
| `bag` | 1.0 | 1 |  | Bag is clearly salient and described with category, shape/structure, and color/trim details. |
| `body_coverage` | 1.0 | 1 |  | The text clearly describes both coverage and exposure, especially the chest partial visibility and thigh/knee reveal. |
| `closure` | 1.0 | 1 |  | The text clearly describes the coat’s opening and button closure detail. |
| `color_relationship_logic` | 1.0 | 1 |  | The text explains a coherent color structure: a dark outer layer framing lighter, mixed-toned inner and lower pieces, plus visible lining as an accent. |
| `cross_garment_binding` | 1.0 | 1 |  | The description clearly distinguishes which attributes belong to the coat, top, skirt, and handbag, making multi-garment relations explicit. |
| `fabric_family` | 1.0 | 1 |  | The main garment material family is clearly identified as tweed. |
| `garment_category` | 1.0 | 1 |  | The text clearly names the main garment categories: coat, top, skirt, and handbag. |
| `hardware_embellishment` | 0.0 | 0 |  | Buttons and trim are present, but there is no clear mention of salient hardware or metal-like embellishment such as chains, studs, rings, or crystals. |
| `layering` | 1.0 | 1 |  | The text clearly describes a multi-layered outfit with readable outerwear-to-inner-layer relationships. |
| `length_hemline` | 1.0 | 1 |  | The text gives clear length and hemline information for both coat and skirt, including the slit. |
| `pattern_type` | 1.0 | 1 |  | Pattern information is present, including speckling, print, and mélange striations. |
| `primary_color` | 1.0 | 1 |  | The dominant color family is dark navy-black, with black as a major base tone. |
| `secondary_color` | 1.0 | 1 |  | Several secondary colors are clearly described, including pale greenish accents, a gray/black/off-white skirt, and beige lining. |
| `silhouette` | 1.0 | 1 |  | It explicitly describes the overall structure and silhouette as layered, longline, and slim through the skirt. |
| `surface_finish` | 1.0 | 1 |  | The text gives clear surface traits: a nubby, textured, heavy finish. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text explicitly describes the overall top-to-bottom balance and silhouette relationship between the long coat and slim skirt. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are clearly attached to the correct garments, with coat, skirt, top, and handbag distinguished well. Minor ambiguity remains in phrases like "pale gray-white vertical panel or scarf-li |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is dense with concrete garment facts, construction, and silhouette details. There is some interpretive framing, but it remains secondary and does not significantly dilute the core outf |
| `craft_embellishment_salience` | 0.75 | 1 | 工艺装饰显著度 | Craft details are clearly identified by type and placement, and they function as visible hooks. The description is strong, though the visual effect is described a bit more than the construction method |
| `design_distinctiveness` | 0.75 | 1 | 设计独特性 | The look has a clear non-formula identity through the longline tweed coat, raw fringe trim, and asymmetrical slit skirt construction. It is distinctive, though not so singular or complex as to merit 1 |
| `design_signal_purity` | 1.0 | 1 | 设计信号纯度 | The text is dominated by concrete design facts: materials, trims, layers, proportions, and placement. There is essentially no mood essay or identity framing diluting the garment description. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly visual, garment-specific, and mostly prompt-ready, with clear silhouette, layering, materials, and accessories. It reads slightly like a descriptive analysis rather than a fully com |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a mostly natural body-to-detail order: overall silhouette, outer layer, inner layers, skirt, then accessory and visibility notes. It is clear and easy to reconstruct, though so |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text separates multiple garments and accessories cleanly and generally keeps their attributes with the right item. There is slight uncertainty around the layered front piece and some overlap langu |
| `reference_clarity` | 1.0 | 1 | 语言清晰度 | References and ellipses are stable and easy to track; the garment subjects remain clear throughout, and the single hand reference is unambiguous. |
| `silhouette_combination_originality` | 0.75 | 1 | 组合原创性 | The combination is more specific than a standard formula because of the longline coat, slim pencil skirt, and asymmetrical wrap/slit treatment. It still sits within a recognizable tailored runway voca |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering, inside/outside visibility, and front drape are clearly described and imageable. The spatial logic is coherent overall, with only minor complexity from the overlapping wrap front and slit, wh |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | The text mostly prioritizes visible, image-dominant clothing details and clearly marks what is not visible. It includes a few lower-priority details like lining, but these do not overwhelm the visible |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly anchored in visible garment parts and spatial relations, with clear distinctions between visible and hidden layers. It reads like direct runway observation rather than mood |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | The described trunk garments read coherently; no strong left-right or mutually exclusive garment identity conflict is present. |
| `coordination_penalty` | 0.0 | The outfit language is internally coordinated and consistent in mood, with no major styling clash across trunk garments. |
| `formula_template_penalty` | 0.25 | The look is somewhat formulaic in a runway-description sense, but it remains specific and craft-grounded rather than a generic cruise/resort template. |
| `generation_content_penalty` | 0.25 | Mostly grounded garment description, with a small amount of runway/framing language, but not enough redundancy or essay-like drift to warrant a higher penalty. |
| `rationality_penalty` | 0.0 | All materials and construction details are physically plausible for ordinary fashion wear. |

## Missing coverage (未覆盖)

- **`hardware_embellishment`** — Buttons and trim are present, but there is no clear mention of salient hardware or metal-like embellishment such as chains, studs, rings, or crystals.

## Skipped metrics (不适用)

- `shoulder_architecture` (coverage_score) — No prominent shoulder construction is described; the text does not mention pads, dropped shoulders, off-shoulder, or similar cues.
- `functional_detail` (coverage_score) — No clear pockets, straps, or utility features are described.
- `construction_technique` (coverage_score) — The text mentions texture, fringe, and overlap, but not a specific named construction technique with a clear body/garment placement.
- `deconstruction` (coverage_score) — The text does not explicitly mention deconstruction, splicing, displacement, or reconstruction.
- `footwear` (coverage_score) — Shoes are explicitly not visible, so the metric does not apply.
- `jewelry` (coverage_score) — No salient jewelry/body ornament is mentioned.
- `belt` (coverage_score) — There is no visible belt-like accessory; waist shaping comes from garment cut only.
- `quantity_accuracy` (quality_score) — The text contains no explicit counts or quantity relations that need verification.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral distinction is described.
- `cultural_reference` (bonus_score) — No cultural, historical, or brand-specific reference is provided.
- `gender_expression` (bonus_score) — No explicit gender expression or androgyny is mentioned.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is stated.
- `brand_alignment` (bonus_score) — No brand identity or brand-language target is explicit.
