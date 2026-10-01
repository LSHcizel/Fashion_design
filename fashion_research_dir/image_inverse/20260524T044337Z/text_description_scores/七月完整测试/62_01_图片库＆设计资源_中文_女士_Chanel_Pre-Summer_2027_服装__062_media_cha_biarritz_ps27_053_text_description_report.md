# Text Evaluation Report

- **Source:** 62_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__062_media_cha_biarritz_ps27_053_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.838 (Strong)
- **Coverage axis:** 0.8947
- **Quality axis (raw / base / penalized):** 0.8214 / 0.8229 / 0.8229
- **Penalties (mean):** 0.1
- **R_content:** 0.80867

## Gates

- Score gate: 0.838 (threshold 0.7) → **PASS**
- Penalty gate: 0.1 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `asymmetry` | 1.0 | 1 |  | Asymmetric design is explicitly stated and visually described. |
| `bag` | 1.0 | 1 |  | The bag is clearly identified by type, shape/structure, and material/finish details, with carrying method also specified. |
| `body_coverage` | 1.0 | 1 |  | The text clearly describes exposed/covered body areas through the deep V neckline and wrap-like asymmetric paneling. |
| `closure` | 1.0 | 1 |  | The coat’s closure is explicitly described through front buttons, and the open styling makes the closure detail salient. |
| `color_relationship_logic` | 1.0 | 1 |  | The text explains the color logic as a pastel scenic print over a blue base, contrasted with burgundy and white accents. |
| `cross_garment_binding` | 1.0 | 1 |  | The description distinguishes multiple items and their roles in the look, clearly separating coat, dress, accessories, and footwear. |
| `fabric_family` | 0.0 | 0 |  | The text gives construction/fit and color, but not a clear fabric family such as wool, silk, cotton, leather, etc. |
| `footwear` | 0.0 | 0 |  | Footwear is mentioned, but the text does not clearly specify a shoe family or enough functional/finish detail to satisfy the coverage rule. |
| `garment_category` | 1.0 | 1 |  | The text clearly names the main garment categories: coat and dress. |
| `hardware_embellishment` | 1.0 | 1 |  | The text clearly includes visible hardware/ornamental elements, especially the chain handles on the handbag and the pendant necklace. |
| `jewelry` | 1.0 | 1 |  | Salient jewelry is explicitly described and visually prominent. |
| `layering` | 1.0 | 1 |  | The text clearly describes a layered look with an outer coat over an inner dress and readable open-front relation. |
| `length_hemline` | 1.0 | 1 |  | The text gives clear length and hemline information for both coat and dress. |
| `pattern_type` | 1.0 | 1 |  | The pattern type is clearly identified as a painterly scenic landscape print. |
| `primary_color` | 1.0 | 1 |  | The main colors are explicitly stated, with sky-blue as the coat base and burgundy as the dress color. |
| `secondary_color` | 1.0 | 1 |  | Multiple secondary colors are clearly described as part of the look and print accents. |
| `silhouette` | 1.0 | 1 |  | It explicitly describes the overall shape and fit of both layers. |
| `surface_finish` | 1.0 | 1 |  | It clearly describes surface/handling traits: the coat is lightly structured and the dress has a fluid silhouette. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes the relationship between the long outer layer and the dress beneath, including length and silhouette balance. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are clearly attached to the correct garment or accessory, and the layering is coherent. Minor complexity comes from dense multi-attribute description, but there is no major entity conf |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description prioritizes visible garment facts and construction details, with only a brief mood phrase at the end. It is somewhat long and layered with many attributes, but the main outfit remains  |
| `craft_embellishment_salience` | 0.75 | 1 | 工艺装饰显著度 | Craft and surface treatment are salient and fairly well located, but the description is more about print and paneling than a fully specified construction technique. |
| `design_distinctiveness` | 1.0 | 1 | 设计独特性 | The look has multiple clear memory points: an allover scenic landscape print and an asymmetric wrap-like panel treatment on the dress. |
| `design_signal_purity` | 1.0 | 1 | 设计信号纯度 | The text is dominated by concrete design facts, with only a brief mood phrase at the end and little essay-like dilution. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly imageable and already organized around visible garments, layers, colors, and accessories, so it is close to a usable generation prompt. It is slightly more descriptive/essay-like th |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a mostly natural hierarchy from main garments to underlying dress details and then accessories. There is some compression from long attribute chains, but the overall structure  |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text keeps coat, dress, handbag, jewelry, and footwear mostly separated correctly, with clear layering and placement. There is slight complexity in the dress panel description, but no strong cross |
| `quantity_accuracy` | 0.75 | 1 | 语言清晰度 | The text uses a few quantity-like descriptors and spatial counts implicitly, but they remain internally consistent and easy to parse. There is no conflicting numbering or unclear quantity relation, th |
| `reference_clarity` | 1.0 | 1 | 语言清晰度 | References are consistently anchored to clear nouns, and pronouns like “it” clearly point back to the coat. The garment descriptions are orderly and easy to follow without ambiguity. |
| `silhouette_combination_originality` | 0.75 | 1 | 组合原创性 | The combination is coherent and somewhat distinctive, especially with the scenic coat over the graphic dress, though it still reads as a wearable runway layering formula rather than highly unexpected. |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and attachment relationships are clear and visually reconstructable: coat over dress, open fronts revealing the dress, and graphic panels crossing the waist and hem. The spatial logic is cohe |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | Most details describe what can be seen on the coat, dress, accessories, and shoes. The final mood phrase is present but does not dominate or obscure the visible clothing information. |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly anchored in visible garment details and placement, with clear separation of coat, dress, accessories, and footwear. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | No trunk-level left-right conflicts or mutually exclusive garment identities; the coat, dress, and footwear read coherently. |
| `coordination_penalty` | 0.0 | The palette and accessories are stylistically aligned; no major trunk-level coordination clash is present. |
| `formula_template_penalty` | 0.25 | Some runway-essay framing and mood language is present, but the look remains specific and craft-grounded rather than fully formulaic. |
| `generation_content_penalty` | 0.25 | Mostly grounded garment description, but ends with mood-forward runway framing that slightly dilutes prompt efficiency. |
| `rationality_penalty` | 0.0 | All described materials and garment constructions are physically plausible as ordinary fashion wear. |

## Missing coverage (未覆盖)

- **`fabric_family`** — The text gives construction/fit and color, but not a clear fabric family such as wool, silk, cotton, leather, etc.
- **`footwear`** — Footwear is mentioned, but the text does not clearly specify a shoe family or enough functional/finish detail to satisfy the coverage rule.

## Skipped metrics (不适用)

- `shoulder_architecture` (coverage_score) — No prominent shoulder construction is described.
- `functional_detail` (coverage_score) — No pockets, straps, utility parts, or comparable functional garment details are described for the clothing.
- `construction_technique` (coverage_score) — The text describes print, silhouette, and paneling, but not a clearly named construction technique such as pleating, quilting, embroidery, cut-outs, or engineered craft work with body placement.
- `deconstruction` (coverage_score) — The description does not mention deconstruction, splicing, displacement, or reconstruction.
- `belt` (coverage_score) — No visible belt, sash, waist strap, or harness is described; the waist emphasis comes from garment design, not an accessory.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral garment differences are described.
- `cultural_reference` (bonus_score) — No clear cultural, historical, or brand reference is provided.
- `gender_expression` (bonus_score) — The description does not explicitly discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative task is stated beyond general styling.
- `brand_alignment` (bonus_score) — No brand identity or brand-language target is mentioned.
- `negation_control` (bonus_score) — The text does not emphasize exclusions or absence of elements.
