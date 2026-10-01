# Text Evaluation Report

- **Source:** 45_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__045_media_cha_biarritz_ps27_034_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.8555 (Strong)
- **Coverage axis:** 0.9412
- **Quality axis (raw / base / penalized):** 0.8269 / 0.8333 / 0.8333
- **Penalties (mean):** 0.1
- **R_content:** 0.825558

## Gates

- Score gate: 0.8555 (threshold 0.7) → **PASS**
- Penalty gate: 0.1 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `bag` | 1.0 | 1 |  | The bag is explicitly described with carrying method, shape, and color/material details. |
| `body_coverage` | 1.0 | 1 |  | The text clearly specifies exposed and covered body areas. |
| `color_relationship_logic` | 1.0 | 1 |  | The text explicitly states the color logic as a black dominant look with a contrasting red accent. |
| `construction_technique` | 1.0 | 1 |  | A specific surface construction technique is described, with both the craft type and its placement on the dress body. |
| `cross_garment_binding` | 1.0 | 1 |  | The text distinguishes the main dress from the bag and footwear, making the multi-item relations clear. |
| `fabric_family` | 0.0 | 0 |  | The text describes surface embellishment and texture, but not a clear base fabric family such as silk, knit, leather, or chiffon. |
| `footwear` | 1.0 | 1 |  | Footwear is clearly identified by type and functional form, with visible color/finish cues. |
| `functional_detail` | 1.0 | 1 |  | The text clearly describes a functional accessory detail with a strap/handle. |
| `garment_category` | 1.0 | 1 |  | The main garment is clearly identified as a dress. |
| `hardware_embellishment` | 1.0 | 1 |  | The description includes visible decorative embellishment consistent with hardware-like or ornamented detailing. |
| `length_hemline` | 1.0 | 1 |  | Garment length and hemline are explicitly stated. |
| `primary_color` | 1.0 | 1 |  | The main garment color is clearly black. |
| `secondary_color` | 1.0 | 1 |  | A distinct secondary color, red, is clearly present in the bag accent. |
| `shoulder_architecture` | 1.0 | 1 |  | Shoulder and upper-body construction are saliently described through sleeveless coverage and narrow shoulder treatment. |
| `silhouette` | 1.0 | 1 |  | The text clearly describes the overall shape and structural contour. |
| `surface_finish` | 1.0 | 1 |  | It clearly conveys a highly textured, dimensional surface finish. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes the overall vertical proportion and body balance of the dress, including waist placement and silhouette shape. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are clearly attached to the correct entities, and the dress/bag/shoes are distinguished well. Minor ambiguity remains in phrases like “black dangling textured trim or bead-like fringe  |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is mostly anchored in visible garment facts and silhouette details, with only a brief mood-style closing. It is somewhat verbose, but not essay-like or dominated by repeated framing. |
| `craft_embellishment_salience` | 1.0 | 1 | 工艺装饰显著度 | The craft is central, specific, and well localized, with clear type, placement, and visual effect. |
| `design_distinctiveness` | 0.75 | 1 | 设计独特性 | The look has a clear non-formula memory point through the shaggy, heavily textured black dress and the contrasting red bag. It is distinctive, though not quite a two-anchor standout. |
| `design_signal_purity` | 1.0 | 1 | 设计信号纯度 | Most of the text is devoted to concrete design facts, with only a brief mood statement at the end. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly visual and mostly prompt-ready, with clear garment type, silhouette, texture, accessories, and color contrast. It is still somewhat explanatory and layered with interpretive phrasin |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a mostly natural order from main garment to surface detail, then accessories and footwear. It is clear and easy to reconstruct overall structure, though some detail layering is |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text cleanly separates the main dress from the bag and footwear, with color and material cues staying mostly attached to the right item. There is slight local ambiguity around the dangling trim on |
| `reference_clarity` | 1.0 | 1 | 语言清晰度 | References are consistently anchored to clear nouns, and pronouns/ellipsis do not create ambiguity. The garment, bag, and footwear are each identifiable without backtracking. |
| `silhouette_combination_originality` | 0.75 | 1 | 组合原创性 | The silhouette is coherent and somewhat distinctive due to the column shape and heavy texture, but the overall garment combination remains relatively straightforward. |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Spatial attachment and placement are clearly described and imageable, especially for fringe, hem, bag position, and obscured footwear. Minor ambiguity remains because some texture language is interpre |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | The most visible, image-defining elements are prioritized well: dress shape, surface texture, bag, and footwear. A few lower-visibility details appear, but they do not overwhelm the main look. |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly anchored in visible garment parts and spatial placement, with clear distinctions between visible and barely visible elements. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | The main garment, bag, and footwear read coherently; no trunk-level left-right or identity conflicts are present. |
| `coordination_penalty` | 0.0 | The styling is coordinated and unified, with only a controlled red accent against an otherwise dark look. |
| `formula_template_penalty` | 0.25 | A fairly standard runway-description template is present, but it remains anchored by specific garment construction and texture details rather than becoming fully formulaic. |
| `generation_content_penalty` | 0.25 | Mostly grounded in a single dress description, but includes some interpretive/analytical phrasing and texture speculation that slightly reduces prompt efficiency. |
| `rationality_penalty` | 0.0 | The described materials and construction are physically plausible as fashion details. |

## Missing coverage (未覆盖)

- **`fabric_family`** — The text describes surface embellishment and texture, but not a clear base fabric family such as silk, knit, leather, or chiffon.

## Skipped metrics (不适用)

- `pattern_type` (coverage_score) — No print or pattern is described; the text focuses on texture and embellishment instead.
- `closure` (coverage_score) — No closure method such as buttons, zipper, ties, or buckles is mentioned.
- `deconstruction` (coverage_score) — The text does not mention deconstruction, splicing, displacement, or reconstruction.
- `jewelry` (coverage_score) — No jewelry or body ornament is mentioned.
- `belt` (coverage_score) — No visible belt, sash, or waist strap is described; the waist shaping comes from the dress silhouette only.
- `layering` (coverage_score) — The look is described as a single dress with accessories, not as layered garments.
- `asymmetry` (coverage_score) — No clear asymmetrical garment structure is described.
- `quantity_accuracy` (quality_score) — The text does not use explicit counts or quantity relations that need verification.
- `bilateral_coherence` (quality_score) — The text does not explicitly distinguish left/right sides, sleeves, legs, shoes, or other bilateral elements.
- `cultural_reference` (bonus_score) — No cultural, historical, or brand grounding is provided.
- `gender_expression` (bonus_score) — The description does not explicitly discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is stated beyond the outfit description.
- `brand_alignment` (bonus_score) — No brand identity or brand-language target is mentioned.
- `negation_control` (bonus_score) — The text does not emphasize exclusions or absence as a meaningful requirement.
