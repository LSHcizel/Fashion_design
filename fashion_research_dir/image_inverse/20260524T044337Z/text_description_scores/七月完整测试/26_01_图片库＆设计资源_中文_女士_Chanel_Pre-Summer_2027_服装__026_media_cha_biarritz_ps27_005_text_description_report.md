# Text Evaluation Report

- **Source:** 26_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__026_media_cha_biarritz_ps27_005_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.8284 (Strong)
- **Coverage axis:** 1.0
- **Quality axis (raw / base / penalized):** 0.8 / 0.7847 / 0.7847
- **Penalties (mean):** 0.1
- **R_content:** 0.799406

## Gates

- Score gate: 0.8284 (threshold 0.7) → **PASS**
- Penalty gate: 0.1 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `bag` | 1.0 | 1 |  | Bag is explicitly present and its carry method plus material/strap detail are described. |
| `body_coverage` | 1.0 | 1 |  | The text describes both coverage and reveal, including cutout-like detailing and exposed neckline/leg area. |
| `closure` | 1.0 | 1 |  | Button closures/details are explicitly described and clearly salient. |
| `color_relationship_logic` | 1.0 | 1 |  | The text clearly explains the palette logic as a coordinated monochrome black-and-white contrast. |
| `construction_technique` | 1.0 | 1 |  | The text describes a specific engineered panel/cutout construction and its placement on the jacket body. |
| `cross_garment_binding` | 1.0 | 1 |  | The description distinguishes which features belong to the jacket, underlayer, and lower garment, so the multi-garment relations are clearly bound to specific items. |
| `functional_detail` | 1.0 | 1 |  | Functional details such as pockets/tabs and a strap are mentioned. |
| `garment_category` | 1.0 | 1 |  | The text clearly identifies the main garment categories: jacket, top/tunic, and lower garment. |
| `hardware_embellishment` | 1.0 | 1 |  | Metallic decorative hardware is clearly present through gold buttons and a chain strap. |
| `jewelry` | 1.0 | 1 |  | Salient jewelry is clearly described with multiple pieces. |
| `layering` | 1.0 | 1 |  | The text clearly describes layered garments and their visible order/coverage. |
| `length_hemline` | 1.0 | 1 |  | Garment lengths and hem details are clearly stated. |
| `pattern_type` | 1.0 | 1 |  | A clear abstract motif print is described on the lower garment. |
| `primary_color` | 1.0 | 1 |  | Black is clearly the dominant base color across the main garments. |
| `secondary_color` | 1.0 | 1 |  | White is a salient secondary color used as contrast panels, trim, and print elements. |
| `shoulder_architecture` | 1.0 | 1 |  | The shoulder structure is explicitly emphasized as broad and straight. |
| `silhouette` | 1.0 | 1 |  | It explicitly describes the overall shape and structural silhouette of the look. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly states the relative length balance between the cropped top layer and the longer lower layers, making the top-bottom proportion explicit. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are clearly attached to the correct garment or accessory, and the left-side bag is properly separated from the clothing. Minor ambiguity remains in phrases like “top or tunic” and “upp |
| `bilateral_coherence` | 1.0 | 1 | 生成适配度 | No problematic left-right asymmetry is introduced on trunk garments; the only bilateral reference is a coherent mirrored detail on both side seams. The look remains unified and visually stable for gen |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is compact and mostly devoted to visible garment facts, with clear prioritization of silhouette, construction, color blocking, and accessories. There is some stylistic framing (“overal |
| `craft_embellishment_salience` | 0.75 | 1 | 工艺装饰显著度 | The trim and embellishment are clearly located and visually described, especially the buttons and side-panel treatment. The craft is legible, though not especially complex or artisanal. |
| `design_distinctiveness` | 0.75 | 1 | 设计独特性 | The look has clear memory points through graphic side-panel striping and oversized abstract motifs, plus a cropped structured proportion. It is distinctive, though still within a recognizable tailored |
| `design_signal_purity` | 1.0 | 1 | 设计信号纯度 | The text is dominated by concrete design facts—shape, placement, trim, pattern, and materials—with only a brief closing mood phrase. Design signal purity is very high. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly imageable and already organized around visible silhouette, layering, and graphic details, so it is close to a usable prompt. Minor reduction from 1.0 because it still reads somewhat |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a mostly natural top-down structure from overall view to jacket, underlayer, lower garment, and accessories. It is easy to reconstruct the outfit, though the dense detail withi |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text distinguishes jacket, underlayer, lower garment, jewelry, and bag well, so multi-item binding is mostly stable. There is slight ambiguity in the exact identity of the underlayer and some pock |
| `quantity_accuracy` | 0.75 | 1 | 语言清晰度 | Quantities and side references are mostly clear and internally consistent. There is minor ambiguity in phrases like “small gold button details near the upper front pockets or tabs,” but it does not ma |
| `reference_clarity` | 0.75 | 1 | 语言清晰度 | Pronoun and ellipsis references are generally easy to track, with clear antecedents for “it” and the garment descriptions. The text is readable and visually coherent, with only slight local ambiguity  |
| `silhouette_combination_originality` | 0.5 | 0 | 组合原创性 | The silhouette is coherent and somewhat layered, but the overall combination remains fairly safe: cropped structured jacket, longer underlayer, patterned lower garment, and accessory accents. It is mo |
| `spatial_coherence` | 1.0 | 1 | 生成适配度 | Layering and attachment positions are clearly described and easy to reconstruct visually. The jacket-over-underlayer relationship, hem lengths, and bag placement are coherent and imageable. |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | The text emphasizes image-dominant, visible elements such as jacket shape, contrast panels, hem lengths, and the visible lower garment. Hidden or low-visibility details are minimal, and mood language  |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly anchored in visible garment facts and precise placement details, with clear layering and surface observations and little mood-only language. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | The layers read as a coherent stacked outfit without trunk-level left-right contradictions or mutually exclusive garment identities. |
| `coordination_penalty` | 0.0 | The styling language is unified and consistent across the jacket, underlayer, and lower garment. |
| `formula_template_penalty` | 0.25 | The description is somewhat formulaic runway prose with a familiar cropped-jacket-plus-contrast-accents structure, but it remains fairly specific and craft-grounded. |
| `generation_content_penalty` | 0.25 | Mostly grounded garment description, but it includes some runway/framing language and mood summary that adds little imaging value. |
| `rationality_penalty` | 0.0 | No physically implausible materials or wearing constructions are asserted as ordinary garment facts. |

## Quality issues (质量短板)

- **`silhouette_combination_originality`** (score 0.5) — The silhouette is coherent and somewhat layered, but the overall combination remains fairly safe: cropped structured jacket, longer underlayer, patterned lower garment, and accessory accents. It is more distinctive in surface treatment than in overall outfit formula.

## Skipped metrics (不适用)

- `fabric_family` (coverage_score) — The text describes colors, structure, and embellishments, but does not clearly specify a material family such as wool, cotton, leather, silk, denim, or knit.
- `surface_finish` (coverage_score) — It mentions tailoring and structured proportions, but not a clear surface trait like glossy, matte, drapey, stiff, or pleated as a material finish.
- `deconstruction` (coverage_score) — The text does not explicitly mention deconstruction, splicing, displacement, or reconstruction.
- `footwear` (coverage_score) — No footwear is mentioned in the text.
- `belt` (coverage_score) — No visible belt, sash, or waist strap is mentioned.
- `asymmetry` (coverage_score) — No clear asymmetrical garment structure is described.
- `cultural_reference` (bonus_score) — No cultural, historical, or brand-specific reference is provided.
- `gender_expression` (bonus_score) — The description does not explicitly discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is stated beyond visual description.
- `brand_alignment` (bonus_score) — The text does not mention a brand goal or brand identity language.
- `negation_control` (bonus_score) — The description does not emphasize exclusions or absence of elements.
