# Text Evaluation Report

- **Source:** 21_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__021_media_cha_biarritz_ps27_077_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.8543 (Strong)
- **Coverage axis:** 0.9333
- **Quality axis (raw / base / penalized):** 0.8214 / 0.8333 / 0.8333
- **Penalties (mean):** 0.2
- **R_content:** 0.794499

## Gates

- Score gate: 0.8543 (threshold 0.7) → **PASS**
- Penalty gate: 0.2 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `body_coverage` | 1.0 | 1 |  | The text describes both exposed areas and layered coverage/reveal. |
| `color_relationship_logic` | 1.0 | 1 |  | The palette is presented as a monochrome black look with tonal depth and a darker inner layer, giving a clear same-color tonal relationship. |
| `construction_technique` | 1.0 | 1 |  | The text clearly names construction techniques and locates them on the garment: ruching at the chest and waist, folded sculptural hip panels, and engineered overlapping front panels on the skirt. |
| `cross_garment_binding` | 1.0 | 1 |  | The description distinguishes multiple garment parts and their roles, clearly binding attributes to the bodice, skirt, and inner layer. |
| `fabric_family` | 1.0 | 1 |  | The main material family is clearly indicated as formal cloth, suitable for the garment's body and structure. |
| `footwear` | 1.0 | 1 |  | Footwear type and key features are clearly described: a heeled closed-toe shoe with color and ornament detail. |
| `garment_category` | 1.0 | 1 |  | The text clearly identifies a formal garment ensemble with a bodice and skirt. |
| `hardware_embellishment` | 1.0 | 1 |  | A visible metallic decorative detail is explicitly mentioned, which qualifies as hardware embellishment. |
| `layering` | 1.0 | 1 |  | The text clearly describes a layered garment relationship with an outer skirt opening to reveal an inner layer beneath. |
| `length_hemline` | 1.0 | 1 |  | Garment length and hem behavior are clearly stated. |
| `primary_color` | 1.0 | 1 |  | The dominant color is clearly black. |
| `secondary_color` | 0.0 | 0 |  | A darker inner layer is mentioned, but no distinct secondary color is clearly specified beyond black/darker tonal variation. |
| `silhouette` | 1.0 | 1 |  | Overall shape and structural contour are explicitly described. |
| `surface_finish` | 1.0 | 1 |  | The text explicitly describes finish and hand-feel traits: sheen, crispness, and textured/ruched surface. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes the relationship between the fitted upper body and the voluminous lower half, including waist emphasis and overall silhouette balance. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are bound to the correct garment zones, and the shoe detail is clearly attached to the visible foot. Minor ambiguity remains in the open-front lower section, where the text hedges betw |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is compact and heavily centered on visible garment structure, with only a brief mood phrase at the end. It is not essay-like or dominated by transition framing, so density remains stro |
| `craft_embellishment_salience` | 0.75 | 1 | 工艺装饰显著度 | Craft and structure are clearly identified and positioned, though the description is more structural than richly technical in craft terminology. |
| `design_distinctiveness` | 1.0 | 1 | 设计独特性 | The look has multiple clear, non-formula memory points: ruched bodice texture, sculptural hip panels, and an architectural open-front skirt structure. |
| `design_signal_purity` | 1.0 | 1 | 设计信号纯度 | The text is dominated by concrete design facts, with only minimal mood language at the end and no essay-like drift. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly imageable and already organized around visible silhouette, garment layers, and material behavior, so it is close to a usable generation prompt. It is still somewhat explanatory and  |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description generally follows a natural top-to-bottom garment order, moving from overall look to bodice, skirt construction, fabric, and footwear. It is clear and easy to reconstruct, though some  |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text distinguishes multiple garments and layers in a mostly coherent way: bodice, skirt/overskirt, inner layer, and shoe. The main weakness is slight uncertainty about whether the revealed lower l |
| `quantity_accuracy` | 0.75 | 1 | 语言清晰度 | Quantity relations are mostly clear and internally consistent. There is a minor ambiguity in the singular visible foot versus the broader garment description, but it does not create a real conflict. |
| `reference_clarity` | 0.75 | 1 | 语言清晰度 | References are generally explicit and easy to track, with clear noun repetition instead of ambiguous pronouns. The description is coherent, with only slight density in the long garment sentence struct |
| `silhouette_combination_originality` | 1.0 | 1 | 组合原创性 | The silhouette combination is highly specific and unusual, with a fitted upper body contrasted against an architectural, voluminous lower half. |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering, front opening, and inner-versus-outer structure are clearly described and visually reconstructable. Minor ambiguity remains in the exact identity of the inner layer, but the overall spatial  |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | The text prioritizes imageable, visible clothing features and silhouette cues. It does mention a darker inner layer, but that detail is secondary and does not overwhelm the clearly visible outer form. |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly anchored in visible garment parts and layered structure, with careful distinction between what is seen and what is inferred. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.25 | The main silhouette is coherent, but the skirt description mixes skirt and trouser-like inner layer language, creating a mild trunk-level identity blur. |
| `coordination_penalty` | 0.25 | The look is dramatic but still stylistically unified; no strong left-right or footwear coordination conflict is present. |
| `formula_template_penalty` | 0.25 | Some generic runway-style mood language and familiar formal silhouette cues appear, but the description still contains specific structural details and is not heavily formulaic. |
| `generation_content_penalty` | 0.25 | Mostly grounded garment description, with only light mood-forward framing and little redundant conceptual prose. |
| `rationality_penalty` | 0.0 | The described materials and construction are physically plausible for fashion imagery. |

## Missing coverage (未覆盖)

- **`secondary_color`** — A darker inner layer is mentioned, but no distinct secondary color is clearly specified beyond black/darker tonal variation.

## Skipped metrics (不适用)

- `shoulder_architecture` (coverage_score) — No salient shoulder design is described beyond sleeveless construction.
- `pattern_type` (coverage_score) — No explicit pattern or print is described.
- `closure` (coverage_score) — No salient closure mechanism is described; the text mentions silhouette and panels but not buttons, zippers, ties, buckles, or similar garment closure details.
- `functional_detail` (coverage_score) — No pockets, straps, utility parts, or other functional details are mentioned.
- `deconstruction` (coverage_score) — The text describes an open-front layered skirt structure, but does not explicitly indicate deconstruction, splicing, displacement, or reconstruction as a design approach.
- `bag` (coverage_score) — No bag is mentioned or implied.
- `jewelry` (coverage_score) — No salient jewelry or body ornament is explicitly present.
- `belt` (coverage_score) — No visible belt, sash, waist strap, or harness is described; the waist shaping comes from garment construction.
- `asymmetry` (coverage_score) — No clear asymmetrical design is described; the silhouette reads as structured and centered rather than uneven.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral distinction is described.
- `cultural_reference` (bonus_score) — No cultural, historical, or brand reference is provided.
- `gender_expression` (bonus_score) — The text does not explicitly discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is stated beyond general mood.
- `brand_alignment` (bonus_score) — No brand language or brand identity is mentioned.
- `negation_control` (bonus_score) — The text does not emphasize exclusions or absence as a meaningful requirement.
