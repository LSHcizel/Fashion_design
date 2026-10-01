# Text Evaluation Report

- **Source:** 65_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__065_media_cha_biarritz_ps27_061_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.8675 (Strong)
- **Coverage axis:** 1.0
- **Quality axis (raw / base / penalized):** 0.8214 / 0.8333 / 0.8333
- **Penalties (mean):** 0.1
- **R_content:** 0.837137

## Gates

- Score gate: 0.8675 (threshold 0.7) → **PASS**
- Penalty gate: 0.1 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `asymmetry` | 1.0 | 1 |  | Asymmetry is explicitly stated and reinforced by the irregular hem and split panels. |
| `bag` | 1.0 | 1 |  | The bag is clearly identified by type, appearance, and carrying method, satisfying the coverage rule. |
| `body_coverage` | 1.0 | 1 |  | The text clearly indicates exposed areas and limited coverage. |
| `color_relationship_logic` | 1.0 | 1 |  | The text explains the color relationship as a strong red-and-black contrast with linear striping over a red ground. |
| `cross_garment_binding` | 1.0 | 1 |  | The description distinguishes details belonging to the dress, necklace, handbag, and sandals, making multi-item attribution clear. |
| `deconstruction` | 1.0 | 1 |  | Deconstruction is explicitly stated and reinforced by the split, irregular panel treatment. |
| `footwear` | 1.0 | 1 |  | The text specifies the footwear family, functional form, and color/finish sufficiently for coverage. |
| `functional_detail` | 1.0 | 1 |  | The text clearly mentions functional strap details on both the dress and handbag. |
| `garment_category` | 1.0 | 1 |  | The main garment category is explicitly identified as a dress. |
| `hardware_embellishment` | 1.0 | 1 |  | The text clearly describes visible metallic embellishment and hardware accents. |
| `jewelry` | 1.0 | 1 |  | A salient necklace is explicitly present, and additional gold-toned adornment reinforces the jewelry/body ornament presence. |
| `length_hemline` | 1.0 | 1 |  | Length and hemline are explicitly stated. |
| `pattern_type` | 1.0 | 1 |  | A stripe-like pattern is clearly described. |
| `primary_color` | 1.0 | 1 |  | The main color is explicitly stated as red. |
| `secondary_color` | 1.0 | 1 |  | Clear secondary and accent colors are described alongside the red base. |
| `shoulder_architecture` | 1.0 | 1 |  | The shoulder/upper-edge construction is clearly specified through straps and neckline. |
| `silhouette` | 1.0 | 1 |  | The text clearly describes the overall silhouette and structural contour. |
| `surface_finish` | 1.0 | 1 |  | The description clearly conveys a drapey, fluid surface quality. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes upper-vs-lower silhouette balance and the dress’s vertical proportion from fitted torso to looser skirt. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are bound to the correct entities and body zones, with clear separation between dress details, necklace, handbag, and sandals. Minor ambiguity remains in phrases like “hardware or broo |
| `bilateral_coherence` | 0.75 | 1 | 生成适配度 | The only bilateral cue is a mirrored shoulder/strap treatment, and the differences are limited to small accessories and draped strips rather than conflicting trunk garments. This is coherent and image |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is mostly concentrated on visible garment construction, silhouette, color, and accessories. There is some mood framing at the end, but it does not dominate or become essay-like. |
| `craft_embellishment_salience` | 0.75 | 1 | 工艺装饰显著度 | The craft/detailing is clearly located and functionally described, but the embellishment language is still somewhat broad rather than fully technical. |
| `design_distinctiveness` | 1.0 | 1 | 设计独特性 | The look has multiple clear memory points beyond a formula outfit: suspended strips, deconstructed split panels, and an asymmetric handkerchief hem create a strongly identifiable structure. |
| `design_signal_purity` | 0.75 | 1 | 设计信号纯度 | Design facts dominate the text, with only a brief mood summary at the end; the signal remains mostly concrete and imageable. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly visual, garment-specific, and mostly prompt-ready, with clear silhouette, color, and construction details. It still reads a bit like a descriptive fashion analysis rather than a ful |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a mostly natural order from main garment to construction details, then color/trim, then accessories and footwear. It is clear and easy to reconstruct overall, though some detai |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text cleanly distinguishes the main dress from accessories and keeps their attributes mostly attached to the right items. There is no major cross-binding across garments, only slight softness in d |
| `reference_clarity` | 1.0 | 1 | 语言清晰度 | References are clear and stable; pronouns and omitted subjects do not create ambiguity, and the described elements are consistently anchored to the dress and model. |
| `silhouette_combination_originality` | 1.0 | 1 | 组合原创性 | The silhouette combination is unusual and not a standard formula template; the deconstructed dress shape and irregular hem make the overall pairing hard to predict. |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and attachment positions are clearly described, and the dress’s drape, hanging strips, and hem are spatially understandable. Minor ambiguity remains in the exact placement of some fluttering  |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | The text prioritizes image-dominant features that are easy to visualize, with only brief mood language. Hidden or low-visibility details are not overemphasized. |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is anchored in visible garment parts and positions, with precise neckline, strap, hem, and accessory observations rather than mood-only prose. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | Single coherent dress silhouette with no trunk-level left-right or garment-identity conflict. |
| `coordination_penalty` | 0.0 | The styling reads coordinated overall; accessories and footwear support the dress rather than clash with it. |
| `formula_template_penalty` | 0.25 | Some formulaic runway prose and mood-summary language are present, but the description still contains specific craft and silhouette details. |
| `generation_content_penalty` | 0.25 | Mostly grounded garment description, but it includes runway-framing and mood language that slightly dilutes prompt efficiency. |
| `rationality_penalty` | 0.0 | No clearly impossible material or wearing condition is described; the deconstructed details remain plausible as fashion construction. |

## Skipped metrics (不适用)

- `fabric_family` (coverage_score) — The text describes silhouette, drape, and construction, but does not clearly identify the dress's main fabric family.
- `closure` (coverage_score) — No explicit closure detail such as buttons, zipper, ties, or buckle is mentioned.
- `construction_technique` (coverage_score) — The description notes deconstructed styling and panels, but does not clearly name a specific fabrication technique with a defined placement.
- `belt` (coverage_score) — No visible belt, sash, waist strap, or harness is described; the waist shaping comes from dress cut, not an accessory.
- `layering` (coverage_score) — The description focuses on a single dress with attached strips and panels, not a clear multi-garment layering structure.
- `quantity_accuracy` (quality_score) — The text contains no explicit counts, numerals, or quantity relations that require quantity verification.
- `cultural_reference` (bonus_score) — No cultural, historical, or brand-specific reference is provided.
- `gender_expression` (bonus_score) — The description does not explicitly discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is explicitly stated beyond the garment description.
- `brand_alignment` (bonus_score) — There is no explicit brand language or brand identity target.
- `negation_control` (bonus_score) — The text does not emphasize exclusions or absence of elements.
