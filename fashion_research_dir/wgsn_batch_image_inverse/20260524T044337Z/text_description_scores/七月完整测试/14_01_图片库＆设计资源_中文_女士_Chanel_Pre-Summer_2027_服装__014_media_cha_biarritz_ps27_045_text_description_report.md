# Text Evaluation Report

- **Source:** 14_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__014_media_cha_biarritz_ps27_045_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.7887 (Strong)
- **Coverage axis:** 0.9412
- **Quality axis (raw / base / penalized):** 0.75 / 0.75 / 0.75
- **Penalties (mean):** 0.1
- **R_content:** 0.761095

## Gates

- Score gate: 0.7887 (threshold 0.7) → **PASS**
- Penalty gate: 0.1 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `body_coverage` | 1.0 | 1 |  | The text describes visible chest exposure and how it is covered/framed by layered garments. |
| `closure` | 0.0 | 0 |  | An open front is mentioned, but no explicit closure mechanism such as buttons, zipper, ties, or buckle is described. |
| `color_relationship_logic` | 1.0 | 1 |  | 文本不仅列出颜色，还说明了主次关系与呼应逻辑：黑奶油格纹为主体，橙红/白/绿作为条纹与点缀，并与头巾形成呼应。 |
| `construction_technique` | 1.0 | 1 |  | A specific construction technique is indicated by the pleated/paneled skirt structure and its garment placement. |
| `cross_garment_binding` | 1.0 | 1 |  | The description distinguishes which details belong to the jacket, skirt, inner layer, scarf panels, and sleeve/cuff layering, so multi-garment relations are clearly bound to specific items. |
| `fabric_family` | 1.0 | 1 |  | 主体材质类别虽未点明具体纤维，但可明确推知为服装面料体系：挺括的西装/外套面料与内层垂坠面料的组合，足以覆盖材质家族层面的描述。 |
| `functional_detail` | 1.0 | 1 |  | The text clearly points to functional-style details, including a pocket-area reference and visible side details. |
| `garment_category` | 1.0 | 1 |  | The text clearly identifies the main garment categories: jacket, skirt, and inner layer. |
| `layering` | 1.0 | 1 |  | The text clearly describes multiple visible layers and their over/under relationships. |
| `length_hemline` | 1.0 | 1 |  | The text gives clear length and hemline information for both jacket and skirt. |
| `pattern_type` | 1.0 | 1 |  | 图案类型明确为格纹/格子、plaid/grid，并且说明了其密集、不规则的视觉特征。 |
| `primary_color` | 1.0 | 1 |  | 主色明确为黑色与奶油色/象牙色的黑白系组合，其中黑色为最核心主色。 |
| `secondary_color` | 1.0 | 1 |  | 副色非常明确，且有清晰的配色锚点：黑/奶油底上叠加橙红、白、绿色条纹与橙色头巾。 |
| `shoulder_architecture` | 1.0 | 1 |  | Prominent shoulder structure is explicitly stated. |
| `silhouette` | 1.0 | 1 |  | Overall shape and structural contour are explicitly described. |
| `surface_finish` | 1.0 | 1 |  | 文本明确给出垂坠、挺括、褶裥/分片等表面与结构性质，满足表面特征覆盖。 |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly states the upper garment is cropped and the skirt is high-waisted, giving an explicit top-bottom proportion and waist placement. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are bound to the correct garment or body area, and the layering relations are generally clear. Minor ambiguity remains in phrases like “small visible side details” and “glove-like or b |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is mostly packed with visible garment facts and construction details, with only a light amount of mood language at the end. It stays prompt-useful and organized, though accessories and |
| `craft_embellishment_salience` | 0.5 | 0 | 工艺装饰显著度 | Craft and construction are present, but mostly as patterning and structural description rather than a sharply localized embellishment or technique with explicit visual function. The details are useful |
| `design_distinctiveness` | 0.75 | 1 | 设计独特性 | The look has clear memory points through the irregular graphic check, the vertically draped striped scarf panels, and the cropped structured jacket. It is distinctive, though still within a tailored r |
| `design_signal_purity` | 1.0 | 1 | 设计信号纯度 | The text is dominated by concrete design facts: silhouette, pattern, layering, color, and placement. Mood language is minimal and does not dilute the garment description. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly visual and already organized around garment type, silhouette, layering, and palette, so it is close to a usable generation prompt. It is still somewhat explanatory and dense, but on |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a mostly natural body-to-detail order: overall look, jacket/layering, skirt, then scarf and headscarf accents. It is easy to reconstruct the outfit, though some accessory and c |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text clearly distinguishes multiple garments and accessories and mostly keeps their attributes attached to the right items. There is slight cross-item complexity in the layered neck/front descript |
| `reference_clarity` | 0.75 | 1 | 语言清晰度 | References are mostly clear and consistently anchored to named garments, with only minor ambiguity in phrases like “the sleeves appear” and “small visible side details,” which do not seriously impede  |
| `silhouette_combination_originality` | 0.5 | 0 | 组合原创性 | The combination is coherent and somewhat more editorial than a basic formula, especially with the skirt and vertical scarf panels, but it still centers on a fairly legible tailored jacket-and-skirt en |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and attachment relationships are mostly clear and imageable, with readable over/under structure and front framing. Minor ambiguity remains in a few details such as the cuff extensions, but ov |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | The text prioritizes highly visible, image-defining elements like jacket, skirt, scarf panels, and headscarf. It includes some lower-priority palette and mood framing, but these do not overwhelm the v |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly anchored in visible garment parts and spatial relations, with clear references to neckline/chest framing, waist, hem, sleeves, and skirt silhouette. It reads like a direct  |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | The main garments read coherently; no trunk-level left-right or material identity conflict is present. |
| `coordination_penalty` | 0.0 | The styling elements are coordinated into one coherent tailored look, with no major clash across trunk garments. |
| `formula_template_penalty` | 0.25 | It uses a somewhat familiar tailored-set formula, but the scarf layering and check pattern give it enough specific grounding to keep the penalty low. |
| `generation_content_penalty` | 0.25 | Mostly grounded in a clear outfit description, but it includes some runway-style framing and mood language that slightly dilutes the imaging trunk. |
| `rationality_penalty` | 0.0 | The description stays within plausible fashion construction and does not rely on physically impossible materials or wear conditions. |

## Missing coverage (未覆盖)

- **`closure`** — An open front is mentioned, but no explicit closure mechanism such as buttons, zipper, ties, or buckle is described.

## Quality issues (质量短板)

- **`craft_embellishment_salience`** (score 0.5) — Craft and construction are present, but mostly as patterning and structural description rather than a sharply localized embellishment or technique with explicit visual function. The details are useful, though not highly specific as craft hooks.
- **`silhouette_combination_originality`** (score 0.5) — The combination is coherent and somewhat more editorial than a basic formula, especially with the skirt and vertical scarf panels, but it still centers on a fairly legible tailored jacket-and-skirt ensemble.

## Skipped metrics (不适用)

- `deconstruction` (coverage_score) — No deconstruction, splicing, displacement, or reconstruction is explicitly described.
- `hardware_embellishment` (coverage_score) — No chains, studs, rings, crystals, or similar hardware embellishment is mentioned.
- `bag` (coverage_score) — No bag is described or implied as a visual element of the look.
- `footwear` (coverage_score) — No footwear is mentioned.
- `jewelry` (coverage_score) — No jewelry or body ornament is explicitly present.
- `belt` (coverage_score) — No visible belt, sash, waist strap, or harness is described; the waist emphasis comes from garment cut.
- `asymmetry` (coverage_score) — No clear asymmetrical design, one-shoulder, single-sleeve, or uneven structure is described.
- `quantity_accuracy` (quality_score) — The text does not use explicit counts or quantity relations that need verification.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral asymmetry is described.
- `cultural_reference` (bonus_score) — No clear cultural, historical, or brand grounding is provided.
- `gender_expression` (bonus_score) — The description does not explicitly discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is explicitly stated.
- `brand_alignment` (bonus_score) — The text does not target a specific brand language or identity.
- `negation_control` (bonus_score) — The description does not emphasize exclusions or absences as important constraints.
