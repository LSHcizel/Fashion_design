# Text Evaluation Report

- **Source:** 44_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__044_media_cha_biarritz_ps27_030_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.8236 (Strong)
- **Coverage axis:** 0.95
- **Quality axis (raw / base / penalized):** 0.7833 / 0.7917 / 0.7917
- **Penalties (mean):** 0.2
- **R_content:** 0.765948

## Gates

- Score gate: 0.8236 (threshold 0.7) → **PASS**
- Penalty gate: 0.2 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `asymmetry` | 1.0 | 1 |  | The look includes explicit asymmetrical elements on different sides of the body, so the asymmetry is clearly covered. |
| `body_coverage` | 1.0 | 1 |  | The text clearly describes exposed/covered areas through the open front, visible underlayer, and slit. |
| `closure` | 0.0 | 0 |  | The text describes the jacket as open-front, but does not specify a clear closure mechanism. |
| `color_relationship_logic` | 1.0 | 1 |  | 文本交代了主色与点缀色、内搭与外套的对比关系，以及条纹/印花与底色的配色逻辑。 |
| `construction_technique` | 1.0 | 1 |  | The text clearly identifies craft techniques/material treatments and their placement on the garment. |
| `cross_garment_binding` | 1.0 | 1 |  | The description distinguishes which details belong to the jacket, underlayer, and skirt, so the multi-garment relations are clearly assigned. |
| `fabric_family` | 1.0 | 1 |  | 主体材质类别明确指向粗花呢/粗花呢风格织物，并补充了织造质感。 |
| `functional_detail` | 1.0 | 1 |  | A visible chain strap and a functional skirt slit are both salient functional details. |
| `garment_category` | 1.0 | 1 |  | The main garment category is explicitly identified as a skirt suit. |
| `hardware_embellishment` | 1.0 | 1 |  | Stud-like trim and a chain strap are clear hardware/embellishment elements. |
| `jewelry` | 1.0 | 1 |  | The text explicitly includes visible jewelry/body ornament, especially dangling earrings and a prominent brooch-like adornment. |
| `layering` | 1.0 | 1 |  | The outfit clearly describes layered garments and their visible order: jacket over a printed underlayer, with the underlayer extending beyond the jacket and over the skirt. |
| `length_hemline` | 1.0 | 1 |  | Length and hemline details are explicitly stated for the jacket, underlayer, and skirt. |
| `pattern_type` | 1.0 | 1 |  | 图案类型明确，包括断续条纹、印花线条和链条状图形。 |
| `primary_color` | 1.0 | 1 |  | 主色明确给出为米金/金米色系。 |
| `secondary_color` | 1.0 | 1 |  | 存在清晰副色与对比色块：黑、红以及白色内搭都被明确描述。 |
| `shoulder_architecture` | 1.0 | 1 |  | The shoulder construction is directly specified as structured. |
| `silhouette` | 1.0 | 1 |  | The text clearly describes the overall structural silhouette of both jacket and skirt. |
| `surface_finish` | 1.0 | 1 |  | 文本清楚描述了表面为厚织、粗糙、带流苏边的纹理感，属于明确的表面性质。 |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes the relationship between the cropped jacket, visible underlayer, and fitted skirt, giving a readable top-bottom proportion and silhouette balance. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are clearly tied to the correct garment or body location, including jacket, skirt, chest appliqué, and side-held strap. Minor ambiguity remains in phrases like “white sleeveless or sho |
| `bilateral_coherence` | 0.75 | 1 | 生成适配度 | The only explicit left-right differences are limited to an accessory detail and a skirt slit, while the main trunk garments remain unified. This is coherent and imageable, with no hostile multi-part b |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is packed with visible garment facts and construction details, with only a brief mood close. It is somewhat long and layered, but the main outfit information remains dominant and usabl |
| `craft_embellishment_salience` | 1.0 | 1 | 工艺装饰显著度 | Craft details are clearly identified by type, location, and visual effect, and they function as major hooks of the outfit. |
| `design_distinctiveness` | 0.75 | 1 | 设计独特性 | The look has a clear memory point through textured tweed-like fabric, fringe, and a prominent asymmetric appliqué, though the base skirt-suit formula remains fairly classic. |
| `design_signal_purity` | 1.0 | 1 | 设计信号纯度 | The text is dominated by concrete design facts—shape, material, trim, placement, and layering—with only a brief mood phrase at the end. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly imageable and organized around visible garment structure, layers, and styling, so it is close to prompt-ready. It is still somewhat explanatory and dense, with mood/commentary phras |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a mostly natural order from overall outfit to jacket, underlayer, skirt, and accessories. It is easy to reconstruct the look, though some detail clusters are dense and slightly |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The description keeps jacket, skirt, underlayer, and accessories mostly separated correctly, with the skirt explicitly matched to the suit and the underlayer clearly distinct. There is slight ambiguit |
| `quantity_accuracy` | 0.75 | 1 | 语言清晰度 | Quantity and side references are mostly clear and consistent, with only minor ambiguity in alternatives like “sleeveless or short-sleeved.” |
| `reference_clarity` | 0.75 | 1 | 语言清晰度 | Pronouns and ellipsis are generally easy to resolve from context, and the garment references stay coherent; only a few phrases are slightly dense but not confusing. |
| `silhouette_combination_originality` | 0.5 | 0 | 组合原创性 | The silhouette is polished and coherent, but it still reads as a recognizable cropped jacket plus skirt suit with embellishment rather than a highly unexpected combination. |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and attachment positions are clearly described, and the underlayer-to-jacket-to-skirt relationship is easy to visualize. Minor complexity comes from the dense description, but the spatial log |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | Most of the text prioritizes visible clothing structure, texture, and silhouette. Accessories and mood are present, but they do not overwhelm the core outfit description. |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly anchored in visible garment parts and placement, with precise structural and layering observations and little mood-only prose. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.25 | Main skirt suit is coherent; only minor ambiguity and accessory-level asymmetry are present, not a trunk-level conflict. |
| `coordination_penalty` | 0.25 | The look is stylistically aligned overall, with only a slight tension between the crisp suit structure and the busy printed underlayer. |
| `formula_template_penalty` | 0.25 | The description is fairly specific, but it still leans on a familiar suit formula with mood-forward runway language. |
| `generation_content_penalty` | 0.25 | Mostly grounded garment description, but the closing mood/essay framing slightly dilutes prompt efficiency. |
| `rationality_penalty` | 0.0 | All described materials and construction read as physically plausible fashion details. |

## Missing coverage (未覆盖)

- **`closure`** — The text describes the jacket as open-front, but does not specify a clear closure mechanism.

## Quality issues (质量短板)

- **`silhouette_combination_originality`** (score 0.5) — The silhouette is polished and coherent, but it still reads as a recognizable cropped jacket plus skirt suit with embellishment rather than a highly unexpected combination.

## Skipped metrics (不适用)

- `deconstruction` (coverage_score) — The text does not mention deconstruction, splicing, displacement, or reconstruction.
- `bag` (coverage_score) — A bag is not clearly described as a visible styling element; only a generic 'gold chain strap' is mentioned, which is insufficient to establish a bag with category, shape, and material.
- `footwear` (coverage_score) — No footwear is described in the text.
- `belt` (coverage_score) — No visible belt, sash, waist cincher, or harness is described.
- `cultural_reference` (bonus_score) — No specific cultural, historical, or brand grounding is provided.
- `gender_expression` (bonus_score) — The text does not explicitly discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is explicitly stated.
- `brand_alignment` (bonus_score) — No brand language or brand identity target is mentioned.
- `negation_control` (bonus_score) — The description does not emphasize exclusions or absence conditions.
