# Text Evaluation Report

- **Source:** 12_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__012_media_cha_biarritz_ps27_036_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.8439 (Strong)
- **Coverage axis:** 0.8824
- **Quality axis (raw / base / penalized):** 0.8214 / 0.8333 / 0.8333
- **Penalties (mean):** 0.1
- **R_content:** 0.814363

## Gates

- Score gate: 0.8439 (threshold 0.7) → **PASS**
- Penalty gate: 0.1 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `bag` | 0.0 | 0 |  | A bag-like object is only vaguely and partially visible; the text does not clearly establish bag category, shape, or material/finish. |
| `body_coverage` | 1.0 | 1 |  | The text clearly describes both coverage and exposure through sheer construction. |
| `closure` | 1.0 | 1 |  | A clear front opening with cord tie detail is described, which satisfies a salient closure mention. |
| `color_relationship_logic` | 1.0 | 1 |  | 文本给出了底色与多色立体花饰的关系，属于黑底上多色装饰的明确配色逻辑。 |
| `construction_technique` | 1.0 | 1 |  | The text names notable fabrication techniques and places them on the dress body and sleeves, including crochet/lace and appliqué. |
| `cross_garment_binding` | 1.0 | 1 |  | The text includes multiple distinct items and keeps them separable from the main dress, so cross-item attribution is sufficiently clear. |
| `fabric_family` | 1.0 | 1 |  | 主体材质类别明确，可判断为钩编/蕾丝类的半透明网眼面料。 |
| `garment_category` | 1.0 | 1 |  | The main garment is explicitly identified as a dress. |
| `hardware_embellishment` | 1.0 | 1 |  | Bead-like hanging elements and gold-tone jewelry count as visible embellishment/hardware-like decoration. |
| `jewelry` | 1.0 | 1 |  | Jewelry is explicitly and saliently described. |
| `length_hemline` | 1.0 | 1 |  | The garment length is directly indicated by the visible extent and implied short hem coverage. |
| `pattern_type` | 1.0 | 1 |  | 图案类型明确为花卉/花朵装饰图案。 |
| `primary_color` | 1.0 | 1 |  | 主色明确为黑色。 |
| `secondary_color` | 1.0 | 1 |  | 除黑色底色外，存在清晰的副色与装饰色块，红、奶油色和米色都被明确描述。 |
| `silhouette` | 1.0 | 1 |  | The text clearly states the overall shape and contour. |
| `surface_finish` | 1.0 | 1 |  | 文本清楚描述了半透明、透视和有纹理的表面特征。 |
| `top_bottom_proportion` | 0.0 | 0 |  | The text gives overall framing and silhouette, but it does not clearly describe a top-bottom proportion or visual balance between upper and lower body. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are clearly bound to the correct entities, and the dress/accessories are distinguished well. Minor ambiguity remains around the partially visible dark object near the hand and the tent |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is mostly concentrated on visible garment facts and surface treatment, with clear silhouette, material, and embellishment details. There is some extra elaboration, but little mood/essa |
| `craft_embellishment_salience` | 1.0 | 1 | 工艺装饰显著度 | The craft is central, specific, and well located: appliqué, bead-like strands, and their distribution across the dress are clearly described as the main visual hook. |
| `design_distinctiveness` | 1.0 | 1 | 设计独特性 | The look has multiple clear memory points: sheer crochet/lace construction, dense floral appliqué, and hanging bead-like strands. These are distinctive craft-led features rather than a formula outfit. |
| `design_signal_purity` | 1.0 | 1 | 设计信号纯度 | The text is dominated by concrete design facts: garment type, material, embellishment, placement, and accessories. There is very little mood or essay language. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly visual and mostly prompt-ready, with clear garment type, silhouette, materials, surface treatment, and styling. It is slightly less than perfect because it reads like a detailed des |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description generally moves from the main garment to construction details, then surface decoration, then accessories. It is easy to reconstruct the look, though there is some minor jumping between |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | Multiple items are present, but their attributes are mostly assigned to the correct item: the embellished details belong to the dress, while jewelry and head covering are separately identified. The on |
| `quantity_accuracy` | 0.75 | 1 | 语言清晰度 | Quantity and plurality are mostly clear and consistent, but some counts are approximate rather than exact, so the text is understandable with only minor ambiguity. |
| `reference_clarity` | 0.75 | 1 | 语言清晰度 | References are generally well anchored to the dress and styling elements, with only slight complexity in the long descriptive sentence structure. |
| `silhouette_combination_originality` | 0.75 | 1 | 组合原创性 | The silhouette is coherent and somewhat unusual due to the sheer embellished dress and turquoise head covering, but the overall combination remains centered on a single dress look rather than a highly |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Spatial relations are clear and imageable: front opening, cord edging/tie, transparency through the mesh, and hanging front strands all describe coherent placement. Minor uncertainty remains from hedg |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | The text prioritizes the visible dress and its readable construction, while accessories and the partially visible side object are secondary. A few lower-priority styling details are included, but they |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly anchored in visible garment facts and body zones, with clear placement and transparency observations. It reads like direct runway observation rather than mood prose. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | The main garment reads as a single coherent dress with no trunk-level left-right or structural contradictions. |
| `coordination_penalty` | 0.0 | Accessories and dress styling are coordinated; no major clash in the trunk outfit language. |
| `formula_template_penalty` | 0.25 | Some generic runway phrasing and standard styling cues are present, but the description remains fairly specific and craft-anchored rather than fully formulaic. |
| `generation_content_penalty` | 0.25 | Mostly grounded garment description, but it includes some redundant surface-detail listing and runway framing that slightly dilutes prompt efficiency. |
| `rationality_penalty` | 0.0 | The materials and wearing description are physically plausible for fashion imagery. |

## Missing coverage (未覆盖)

- **`bag`** — A bag-like object is only vaguely and partially visible; the text does not clearly establish bag category, shape, or material/finish.
- **`top_bottom_proportion`** — The text gives overall framing and silhouette, but it does not clearly describe a top-bottom proportion or visual balance between upper and lower body.

## Skipped metrics (不适用)

- `shoulder_architecture` (coverage_score) — No salient shoulder construction such as off-shoulder, structured shoulders, or strapless design is described.
- `functional_detail` (coverage_score) — No pockets, straps, utility parts, or comparable functional garment details are described.
- `deconstruction` (coverage_score) — The description does not mention deconstruction, splicing, displacement, or reconstruction.
- `footwear` (coverage_score) — No footwear is described.
- `belt` (coverage_score) — No visible belt, sash, or waist strap is mentioned.
- `layering` (coverage_score) — The text describes a single dress with accessories, not multi-garment layering relations.
- `asymmetry` (coverage_score) — No clear asymmetrical garment structure is described.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral garment differences are described.
- `cultural_reference` (bonus_score) — No explicit cultural, historical, or brand grounding is provided.
- `gender_expression` (bonus_score) — The description does not explicitly discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is stated.
- `brand_alignment` (bonus_score) — No brand identity or brand-language target is mentioned.
