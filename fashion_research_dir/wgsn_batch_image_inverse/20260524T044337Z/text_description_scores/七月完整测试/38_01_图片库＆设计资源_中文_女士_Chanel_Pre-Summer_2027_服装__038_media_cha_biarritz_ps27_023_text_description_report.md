# Text Evaluation Report

- **Source:** 38_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__038_media_cha_biarritz_ps27_023_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.8947 (Strong)
- **Coverage axis:** 0.9412
- **Quality axis (raw / base / penalized):** 0.875 / 0.8819 / 0.8819
- **Penalties (mean):** 0.2
- **R_content:** 0.832071

## Gates

- Score gate: 0.8947 (threshold 0.7) → **PASS**
- Penalty gate: 0.2 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `asymmetry` | 1.0 | 1 |  | Asymmetry is directly stated and reinforced by the uneven hem and asymmetric draping. |
| `body_coverage` | 1.0 | 1 |  | The text describes visible exposure and partial coverage at the neckline and center front. |
| `color_relationship_logic` | 1.0 | 1 |  | The text explains the color logic as a high-contrast monochrome dress with a separate bright green accent. |
| `construction_technique` | 1.0 | 1 |  | A clear construction technique is described with placement on the waist/hip area and skirt. |
| `cross_garment_binding` | 1.0 | 1 |  | Multiple distinct garments and styling elements are clearly separated and attributed, with the dress components and footwear individually identifiable. |
| `footwear` | 0.0 | 0 |  | Footwear is present and visually salient, but the text does not clearly specify the shoe family or enough functional/material detail to satisfy the coverage rule. |
| `garment_category` | 1.0 | 1 |  | The main garment is explicitly identified as a dress. |
| `hardware_embellishment` | 1.0 | 1 |  | A salient hardware embellishment is explicitly present in the styling. |
| `jewelry` | 1.0 | 1 |  | A prominent necklace is explicitly described. |
| `layering` | 1.0 | 1 |  | The text clearly describes layered garment relationships and their order. |
| `length_hemline` | 1.0 | 1 |  | Garment length and hemline are explicitly stated. |
| `primary_color` | 1.0 | 1 |  | The main colors are clearly stated as black and ivory, with black functioning as the dominant visual anchor. |
| `secondary_color` | 1.0 | 1 |  | A clear secondary color is present: ivory alongside black, plus a vivid green accent in the footwear. |
| `shoulder_architecture` | 1.0 | 1 |  | The shoulder/upper-body construction is clearly emphasized through off-the-shoulder and strap details. |
| `silhouette` | 1.0 | 1 |  | The text clearly describes the overall shape and structural contour. |
| `surface_finish` | 1.0 | 1 |  | Surface qualities are explicitly described, including matte finish, fluid drape, and structured stiffness. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes the relationship between the fitted upper body/waist and the fuller skirt, making the top-bottom proportion explicit. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are clearly tied to the correct garment parts, and the dress vs. footwear distinction is stable. Minor complexity comes from the layered, asymmetric dress construction, but it remains  |
| `bilateral_coherence` | 1.0 | 1 | 生成适配度 | There is a left-side note, but it does not create a conflicting bilateral garment design. The look remains unified and coherent for generation. |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is compact and heavily focused on visible garment structure, with only light styling detail. It is somewhat verbose in phrasing, but not essay-like and does not dilute the core outfit  |
| `craft_embellishment_salience` | 0.75 | 1 | 工艺装饰显著度 | Craft and construction are salient and well located, though the description emphasizes structure more than a specific named technique or trim type. |
| `design_distinctiveness` | 1.0 | 1 | 设计独特性 | The look has multiple clear memory points: asymmetric folded overlay, center-front loop/keyhole panel, layered peplum, and high-low hem. These are structural and non-formulaic. |
| `design_signal_purity` | 1.0 | 1 | 设计信号纯度 | The text is dominated by concrete design facts—shape, placement, material feel, and color contrast—with minimal narrative or mood dilution. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly visual and mostly prompt-ready, with clear garment type, silhouette, layering, and color contrast. It is still somewhat explanatory and dense, but only needs light cleanup to functi |
| `information_ordering` | 1.0 | 1 | 结构清晰度 | The description moves naturally from the main garment to upper body, waist/hip construction, skirt, color/material, and finally accessories. The hierarchy is clear and easy to reconstruct visually. |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text describes multiple items and keeps their attributes mostly separated correctly: dress, necklace, and shoes are distinct. The layered dress details are intricate, but there is no major cross-b |
| `reference_clarity` | 1.0 | 1 | 语言清晰度 | References are consistently anchored to clear garment parts, with no ambiguous pronouns or unclear antecedents. |
| `silhouette_combination_originality` | 1.0 | 1 | 组合原创性 | The silhouette mix is highly specific and unusual, combining asymmetric draping, peplum layering, and a high-low tiered skirt with vivid footwear contrast. |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and attachment relationships are mostly clear and imageable, especially the overlay, center-front panel, and footwear visibility. A few phrases are interpretive, but the spatial structure is  |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | The text prioritizes highly visible silhouette, color blocking, and hem construction. Accessories are present but secondary, and there is no significant hidden or low-visibility detail dominating the  |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly anchored in visible garment parts and spatial relations, with clear body-zone references and little mood prose. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.25 | The dress is largely coherent, but there are several asymmetric structural elements that slightly complicate a single clean trunk read. |
| `coordination_penalty` | 0.25 | The black-and-ivory dress is cohesive, but the vivid green shoes introduce a noticeable styling accent that mildly disrupts the otherwise monochrome coordination. |
| `formula_template_penalty` | 0.25 | It uses a familiar runway-description template with a centered hero garment plus styling add-ons, but it remains fairly specific and craft-oriented rather than fully formulaic. |
| `generation_content_penalty` | 0.25 | Mostly grounded garment description, but it leans into evaluative runway phrasing and repeated mood framing rather than only compact imageable facts. |
| `rationality_penalty` | 0.0 | No clearly implausible materials or physically impossible construction are asserted; the description stays within realistic fashion rendering. |

## Missing coverage (未覆盖)

- **`footwear`** — Footwear is present and visually salient, but the text does not clearly specify the shoe family or enough functional/material detail to satisfy the coverage rule.

## Skipped metrics (不适用)

- `fabric_family` (coverage_score) — The text describes color, drape, and structure, but does not clearly identify a main fabric family such as silk, cotton, wool, leather, or knit.
- `pattern_type` (coverage_score) — No print or pattern type is described; the look is presented as solid black, ivory, and green color blocking/accenting.
- `closure` (coverage_score) — No explicit closure detail such as buttons, zipper, ties, or buckle is mentioned.
- `functional_detail` (coverage_score) — The text describes silhouette and draping, but no pockets, straps as functional hardware, or utility details.
- `deconstruction` (coverage_score) — The text does not explicitly mention deconstruction, splicing, displacement, or reconstruction.
- `bag` (coverage_score) — No bag is mentioned or implied.
- `belt` (coverage_score) — No visible belt, sash, or waist strap is described; the waist emphasis comes from garment construction.
- `quantity_accuracy` (quality_score) — The text contains no explicit counts or quantity relations that need verification.
- `cultural_reference` (bonus_score) — No explicit cultural, historical, or brand reference is provided.
- `gender_expression` (bonus_score) — The text does not explicitly discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is stated.
- `brand_alignment` (bonus_score) — No brand language or brand identity target is mentioned.
- `negation_control` (bonus_score) — The description does not emphasize exclusions or absences that need explicit negation.
