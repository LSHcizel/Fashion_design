# Text Evaluation Report

- **Source:** 37_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__037_media_cha_biarritz_ps27_022_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.834 (Strong)
- **Coverage axis:** 1.0
- **Quality axis (raw / base / penalized):** 0.7885 / 0.7917 / 0.7917
- **Penalties (mean):** 0.1
- **R_content:** 0.80481

## Gates

- Score gate: 0.834 (threshold 0.7) → **PASS**
- Penalty gate: 0.1 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `body_coverage` | 1.0 | 1 |  | The text clearly describes exposed chest coverage through a sheer underlayer and open front. |
| `closure` | 1.0 | 1 |  | A clear closure detail is described via paired buttons, and the open-front construction is explicitly stated. |
| `color_relationship_logic` | 1.0 | 1 |  | The text explains the color relationship as a striped palette with a light base, strong black contrast, and yellow accenting. |
| `construction_technique` | 1.0 | 1 |  | The text names specific construction/craft elements and their placement, including lace/openwork at the chest and trim finishing on the skirt slit and garment edges. |
| `cross_garment_binding` | 1.0 | 1 |  | Multiple garments are present and the description clearly distinguishes which attributes belong to the jacket, underlayer, and skirt. |
| `fabric_family` | 1.0 | 1 |  | The text identifies fabric families for key pieces and trims, enough to infer material categories. |
| `garment_category` | 1.0 | 1 |  | The text clearly names the main garment categories: outer top layer, skirt, and visible underlayer. |
| `hardware_embellishment` | 1.0 | 1 |  | The gold buttons function as visible hardware embellishment and are clearly salient in the description. |
| `jewelry` | 1.0 | 1 |  | Visible jewelry is explicitly described and is a noticeable styling element. |
| `layering` | 1.0 | 1 |  | The text clearly describes a layered outfit with an outer piece over an inner layer and visible accessory layering. |
| `length_hemline` | 1.0 | 1 |  | Length and hem details are clearly stated for both the jacket and skirt. |
| `pattern_type` | 1.0 | 1 |  | The pattern type is clearly identified as vertical stripes. |
| `primary_color` | 1.0 | 1 |  | The main color base is explicitly stated as cream-white, with black as the dominant graphic color. |
| `secondary_color` | 1.0 | 1 |  | A clear secondary color is present in the pale yellow striping, with gold as an additional accent. |
| `shoulder_architecture` | 1.0 | 1 |  | The shoulder line is explicitly specified and is visually salient. |
| `silhouette` | 1.0 | 1 |  | The overall structural shape is explicitly described, including boxy upper volume and slim fitted lower half. |
| `surface_finish` | 1.0 | 1 |  | It clearly describes surface qualities such as textured, openwork, and fuzzy trim. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly states the top is cropped at the waist and contrasts it with a high-waisted skirt, giving a readable top-bottom proportion. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are bound to the correct garment layers, and the jacket, bralette, skirt, and accessories are distinguished clearly. Minor uncertainty remains from hedged wording like “appears to be”  |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is compact and heavily garment-focused, with clear visible construction details. There is some stylistic framing and interpretive language, but it does not become essay-like or drown o |
| `craft_embellishment_salience` | 1.0 | 1 | 工艺装饰显著度 | The trim treatment is clearly identified, located, and visually functional as a major design hook. |
| `design_distinctiveness` | 0.75 | 1 | 设计独特性 | The look has clear memory points through unusual trim, button placement, and a strong stripe treatment. It is distinctive, though not so singular that it reaches the highest tier. |
| `design_signal_purity` | 1.0 | 1 | 设计信号纯度 | The text is dominated by concrete design facts and visible construction details, with only a brief concluding mood phrase. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly imageable and organized around visible silhouette, garment types, layering, and materials, so it is close to prompt-ready. It is still slightly explanatory and hedged in places (“ja |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a mostly natural order from overall look to top, underlayer, bottom, and accessories. Minor compression and repeated styling commentary slightly interrupt the flow, but the str |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text handles multiple garments well and keeps most properties attached to the correct item. There is slight ambiguity in garment naming and visibility, but no major cross-binding between the outer |
| `reference_clarity` | 0.75 | 1 | 语言清晰度 | References and ellipses are mostly clear and the garment relationships are easy to follow. There is only mild uncertainty from hedging like "appears to be" and "or" alternatives, but the overall struc |
| `silhouette_combination_originality` | 0.5 | 0 | 组合原创性 | The silhouette is coherent and somewhat specific, but it still reads as a fairly legible fashion set with a cropped top layer and slim skirt, so it is not highly unpredictable. |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and attachment relationships are clear and visually reconstructable: open outer layer over visible inner layer, plus skirt slit and trim placement. Minor uncertainty remains from hedged wordi |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | The text prioritizes visible, imageable elements such as silhouette, trim, stripes, and layering. A few speculative phrases appear, but hidden or low-visibility details do not dominate. |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is tightly anchored to visible garment zones and layered structure, with careful observation of neckline, cuffs, hem, and slit details. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | No strong trunk-level contradictions; the layers and skirt read as a coherent coordinated look. |
| `coordination_penalty` | 0.0 | The styling elements are compatible and reinforce the same ornate tailored direction rather than conflicting. |
| `formula_template_penalty` | 0.25 | The description has some formula-like fashion prose and a familiar coordinated set structure, but it is still anchored by specific craft details like fringe trim and buttons. |
| `generation_content_penalty` | 0.25 | Mostly grounded garment description, but it includes some runway/framing language and a mood summary that slightly dilutes prompt efficiency. |
| `rationality_penalty` | 0.0 | Materials and construction remain plausible for fashion description; no physically implausible garment structure is asserted. |

## Quality issues (质量短板)

- **`silhouette_combination_originality`** (score 0.5) — The silhouette is coherent and somewhat specific, but it still reads as a fairly legible fashion set with a cropped top layer and slim skirt, so it is not highly unpredictable.

## Skipped metrics (不适用)

- `functional_detail` (coverage_score) — No pockets, straps, utility parts, or comparable functional details are mentioned.
- `deconstruction` (coverage_score) — The text does not mention deconstruction, splicing, displacement, or reconstruction as a design approach.
- `bag` (coverage_score) — No bag is described or implied as a salient part of the look.
- `footwear` (coverage_score) — Footwear is not mentioned in the text.
- `belt` (coverage_score) — No visible belt, sash, waist strap, or harness is described; the waist emphasis comes from garment cut.
- `asymmetry` (coverage_score) — No clear asymmetrical design, one-shoulder, uneven hem, or similar imbalance is described.
- `quantity_accuracy` (quality_score) — The text uses a few quantity-like terms such as "pairs" and "layered," but it does not present explicit count relations that need quantity verification in the sense of this metric.
- `bilateral_coherence` (quality_score) — No explicit left-right, bilateral, or side-specific differences are described.
- `cultural_reference` (bonus_score) — No clear cultural, historical, or brand grounding is provided.
- `gender_expression` (bonus_score) — The text does not explicitly discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is stated.
- `brand_alignment` (bonus_score) — No brand language or brand identity is mentioned.
- `negation_control` (bonus_score) — The description does not emphasize exclusions or absences as a meaningful part of the prompt.
