# Text Evaluation Report

- **Source:** 41_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__041_media_cha_biarritz_ps27_027_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.7893 (Strong)
- **Coverage axis:** 0.9
- **Quality axis (raw / base / penalized):** 0.7679 / 0.7604 / 0.7604
- **Penalties (mean):** 0.15
- **R_content:** 0.747862

## Gates

- Score gate: 0.7893 (threshold 0.7) → **PASS**
- Penalty gate: 0.15 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `asymmetry` | 1.0 | 1 |  | A clear asymmetrical design element is explicitly described. |
| `bag` | 1.0 | 1 |  | The bag is explicitly identified by type and carrying method, and its color is given; this is sufficient coverage for a salient accessory. |
| `body_coverage` | 1.0 | 1 |  | The text clearly indicates exposed arms and a knee-length lower body coverage. |
| `closure` | 1.0 | 1 |  | The text clearly describes closure elements: buttons on the top and a tie/belt detail on the skirt. |
| `color_relationship_logic` | 1.0 | 1 |  | The text explains the color relationship as a beige base with striped red/green accents and an echoed green accent in the shoes. |
| `construction_technique` | 1.0 | 1 |  | A notable construction technique is described with placement on the skirt: pleating/gathering at the hem and skirt body. |
| `cross_garment_binding` | 1.0 | 1 |  | The description distinguishes how the striped motif and coordination apply across the separate top and skirt, making the multi-garment relationship clear. |
| `footwear` | 1.0 | 1 |  | The text clearly covers shoe type, heel form, and color, meeting the footwear coverage requirement. |
| `garment_category` | 1.0 | 1 |  | The text clearly identifies the main garment categories as a top and skirt. |
| `hardware_embellishment` | 1.0 | 1 |  | Visible metallic hardware/embellishment is clearly present, especially the gold-tone buttons and sculptural necklace. |
| `jewelry` | 1.0 | 1 |  | Prominent jewelry is explicitly described and visually salient. |
| `layering` | 0.0 | 0 |  | The look is coordinated but not meaningfully layered in the sense required; it describes separate top and skirt rather than a visible multi-layer arrangement with clear overlap/attachment relations. |
| `length_hemline` | 1.0 | 1 |  | The text gives clear length and hemline information for both garments. |
| `pattern_type` | 1.0 | 1 |  | The pattern type is clearly identified as stripes. |
| `primary_color` | 1.0 | 1 |  | Beige is the dominant ground color of the look. |
| `secondary_color` | 1.0 | 1 |  | Red and green are clearly present as secondary colors, with green also reinforced in the footwear. |
| `shoulder_architecture` | 0.0 | 0 |  | The shoulders are not described with a salient architectural treatment such as structured shoulders, off-shoulder, or strapless design. |
| `silhouette` | 1.0 | 1 |  | It explicitly describes the overall structural shape of both pieces. |
| `surface_finish` | 1.0 | 1 |  | The garment surface/behavior is clearly described through drape and fluidity. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly states the relative lengths and placement of the top and skirt, giving a readable top-bottom proportion and silhouette balance. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are clearly attached to the correct garment or accessory, but the phrase “front tie or narrow fabric belt detail” introduces slight ambiguity about whether it is a tie, belt, or integr |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is compact and heavily garment-focused, with clear visible details on silhouette, pattern, trim, accessories, and shoes. There is some mood framing at the end, but it does not dominate |
| `craft_embellishment_salience` | 0.75 | 1 | 工艺装饰显著度 | The trim and fastening details are clearly located and visually relevant, though they are more detail-oriented than deeply crafted embellishment. |
| `design_distinctiveness` | 0.75 | 1 | 设计独特性 | The striped coordination plus asymmetric placket and button treatment create a clear non-formula memory point, though the overall look remains within a polished resort/runway framework. |
| `design_signal_purity` | 0.75 | 1 | 设计信号纯度 | The text is dominated by design facts and visible details, with only a brief mood framing at the end. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is already close to a usable generation prompt: it names the main garments, silhouette, colors, accessories, and shoes with clear visual priorities. It is still somewhat explanatory and verbo |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a mostly natural body-to-detail order: overall look, top, skirt, then accessories and shoes. It is easy to reconstruct the outfit, though the prose is somewhat dense and occasi |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The top, skirt, bag, necklace, earrings, and shoes are mostly bound to distinct entities correctly. Minor ambiguity remains around the waist tie/belt detail, but it does not significantly confuse the  |
| `quantity_accuracy` | 0.75 | 1 | 语言清晰度 | The text uses quantities and grouped items clearly, and the counts are internally consistent. There is minor complexity from multiple coordinated elements, but no real ambiguity about how many garment |
| `reference_clarity` | 1.0 | 1 | 语言清晰度 | References are consistently anchored to explicit nouns, and pronouns like “it” and “the same” are easy to resolve from immediate context. The description is stable and readable without needing backtra |
| `silhouette_combination_originality` | 0.5 | 0 | 组合原创性 | The combination is coherent and polished, but still reads as a fairly safe coordinated resort look rather than a highly unexpected silhouette mix. |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Spatial relations are mostly clear and imageable, with understandable placement of the skirt, front detail, and bag. Minor ambiguity remains around the tie/belt phrasing, but overall the layering and  |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | The text prioritizes visible, imageable clothing and accessory features over hidden or internal details. The only lower-priority content is a brief mood summary, which remains secondary to the outfit  |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | Highly grounded in visible garment observations with multiple body-part anchors and little mood-only language. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | No trunk-level left-right or garment-identity conflict; the look reads as a coherent coordinated set. |
| `coordination_penalty` | 0.0 | Accessories and footwear support the striped palette rather than clash with the main silhouette. |
| `formula_template_penalty` | 0.5 | The look leans on a familiar resort/runway formula with mood-led framing and interchangeable styling language, though it still includes some concrete garment details. |
| `generation_content_penalty` | 0.25 | Mostly grounded garment description, but ends with mood/framing language that slightly dilutes prompt efficiency. |
| `rationality_penalty` | 0.0 | All described materials and construction are physically plausible for ordinary fashion wear. |

## Missing coverage (未覆盖)

- **`shoulder_architecture`** — The shoulders are not described with a salient architectural treatment such as structured shoulders, off-shoulder, or strapless design.
- **`layering`** — The look is coordinated but not meaningfully layered in the sense required; it describes separate top and skirt rather than a visible multi-layer arrangement with clear overlap/attachment relations.

## Quality issues (质量短板)

- **`silhouette_combination_originality`** (score 0.5) — The combination is coherent and polished, but still reads as a fairly safe coordinated resort look rather than a highly unexpected silhouette mix.

## Skipped metrics (不适用)

- `fabric_family` (coverage_score) — The text describes color, cut, and surface behavior, but does not specify a clear material family for the main garments.
- `functional_detail` (coverage_score) — No pockets, straps, utility parts, or similar functional details are described.
- `deconstruction` (coverage_score) — The text does not mention deconstruction, splicing, displacement, or reconstruction.
- `belt` (coverage_score) — The text mentions a “front tie or narrow fabric belt detail,” but this reads as a garment detail rather than a clearly visible belt/waist strap accessory with explicit attachment relation.
- `bilateral_coherence` (quality_score) — No explicit left-right, bilateral, or side-specific garment differences are described.
- `cultural_reference` (bonus_score) — No clear cultural, historical, or brand-specific reference is provided.
- `gender_expression` (bonus_score) — The description does not discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is stated beyond general styling.
- `brand_alignment` (bonus_score) — No brand identity or brand-language target is mentioned.
- `negation_control` (bonus_score) — The text does not emphasize exclusions or absences that need explicit negation.
