# Text Evaluation Report

- **Source:** 67_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__067_media_cha_biarritz_ps27_063_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.8836 (Strong)
- **Coverage axis:** 1.0
- **Quality axis (raw / base / penalized):** 0.8462 / 0.8542 / 0.8542
- **Penalties (mean):** 0.15
- **R_content:** 0.837211

## Gates

- Score gate: 0.8836 (threshold 0.7) → **PASS**
- Penalty gate: 0.15 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `bag` | 1.0 | 1 |  | The text clearly identifies a carried bag-like item and gives its material/ornamentation and color details, satisfying at least two required facets. |
| `body_coverage` | 1.0 | 1 |  | The text clearly describes both significant exposure at the chest and leg reveal through sheer fabric. |
| `color_relationship_logic` | 1.0 | 1 |  | 文本交代了黑色为主、青绿为点缀的主次关系，并明确说明黄色鞋履是对比色点缀，配色逻辑清楚。 |
| `construction_technique` | 1.0 | 1 |  | Specific construction/craft techniques are named and located on the neckline, shoulders/upper arms, and lower edge/skirt area. |
| `cross_garment_binding` | 1.0 | 1 |  | Multiple items/layers are present and the text distinguishes their roles: tunic bodice, skirt layer, and carried accessory. |
| `fabric_family` | 1.0 | 1 |  | 主体材质类别清楚指向半透明/薄纱感的轻薄面料，并伴有蕾丝或刺绣层。 |
| `footwear` | 1.0 | 1 |  | Footwear type and toe shape are specified, along with color, so the description sufficiently covers the shoe. |
| `garment_category` | 1.0 | 1 |  | The text clearly identifies the main garment as a dress with layered tunic-and-skirt construction. |
| `hardware_embellishment` | 1.0 | 1 |  | The look clearly includes visible embellishment/hardware-like decoration through beads, reflective elements, and studs. |
| `jewelry` | 1.0 | 1 |  | Salient jewelry is explicitly present and described. |
| `layering` | 1.0 | 1 |  | The text clearly describes multi-layer garment relations and the visible order between the tunic and skirt layer. |
| `length_hemline` | 1.0 | 1 |  | Length and hemline details are clearly stated for both layers. |
| `pattern_type` | 1.0 | 1 |  | 图案类型明确，为花卉与卷草藤蔓式装饰图案。 |
| `primary_color` | 1.0 | 1 |  | 主色明确为黑色。 |
| `secondary_color` | 1.0 | 1 |  | 存在清晰副色：青绿/蓝绿色作为主要点缀色，另有黄色鞋履形成明显辅助撞色。 |
| `shoulder_architecture` | 1.0 | 1 |  | The shoulder area is explicitly described with a sleeveless/barely capped structure and decorative shoulder treatment. |
| `silhouette` | 1.0 | 1 |  | The overall shape is explicitly described and visually coherent. |
| `surface_finish` | 1.0 | 1 |  | 文本明确描述了半透明、轻盈垂坠的表面性质，并带有反光装饰。 |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes the relationship between the fitted upper body and the longer lower layer, making the top-bottom proportion visually explicit. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are bound to the correct garment or accessory, and the look is internally coherent. Minor ambiguity remains in phrases like “sleeveless or barely capped” and “beneath or continuing fro |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is dense with concrete garment details and visible styling cues, with only a small amount of mood framing at the end. It remains prompt-useful and mostly prioritizes the outfit over es |
| `craft_embellishment_salience` | 1.0 | 1 | 工艺装饰显著度 | Craft is clearly identified by type, placement, and visual role, and it functions as a main hook of the look. |
| `design_distinctiveness` | 1.0 | 1 | 设计独特性 | The look has multiple clear memory points: layered sheer construction, dense beadwork, floral/leaf appliqué, turquoise embroidery, and a strong color-pop shoe contrast. |
| `design_signal_purity` | 1.0 | 1 | 设计信号纯度 | The text is dominated by concrete design facts; the mood phrase is brief and secondary, so the signal remains highly pure. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly visual and mostly prompt-ready, with clear garment type, silhouette, layering, embellishment, and footwear. It is slightly more descriptive than a clean generation prompt, but only  |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description generally moves from overall look to garment structure, then materials/details, and finally accessories and shoes. The hierarchy is easy to follow, though some mid-paragraph layering a |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text distinguishes the dress/tunic bodice, skirt layer, jewelry, bag-like item, and shoes reasonably well. There is slight uncertainty about whether the lower layer is part of the same dress or a  |
| `reference_clarity` | 0.75 | 1 | 语言清晰度 | References are mostly clear and the garment relationships are understandable, but a few phrases introduce mild ambiguity about whether the skirt is separate or continuous and what exactly the carried  |
| `silhouette_combination_originality` | 1.0 | 1 | 组合原创性 | The combination is unusual and specific, with an elongated tunic-over-sheer-skirt structure and a striking shoe contrast that is not formulaic. |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and placement are generally coherent and imageable, with clear top-to-skirt progression and attached shoulder details. A few phrases remain slightly ambiguous, such as “beneath or continuing  |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | Most of the text focuses on visible, image-dominant features such as silhouette, neckline, transparency, embroidery, and shoes. The mood phrase is present but brief and does not dominate the descripti |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is anchored in visible garment zones and readable layers, with specific placement and shape details rather than mood-only prose. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | The main garment reads as a coherent layered dress with no strong trunk-level left-right or identity conflict. |
| `coordination_penalty` | 0.25 | Overall styling is coherent, but the bright yellow pumps introduce a noticeable color contrast against the otherwise black/turquoise evening look. |
| `formula_template_penalty` | 0.25 | The text is still fairly grounded, but it uses runway/mood framing and a somewhat reusable silhouette-description template that makes it mildly formulaic. |
| `generation_content_penalty` | 0.25 | Mostly grounded garment description, but it includes some mood-forward framing and repeated surface-decoration listing that slightly reduces prompt efficiency. |
| `rationality_penalty` | 0.0 | The described materials and construction are plausible as fashion garments and accessories. |

## Skipped metrics (不适用)

- `closure` (coverage_score) — No explicit closure detail such as buttons, zipper, ties, or buckle is mentioned.
- `functional_detail` (coverage_score) — The text does not clearly describe pockets, straps, or other functional utility details.
- `deconstruction` (coverage_score) — The text describes layered and sheer construction, but does not explicitly mention deconstruction, splicing, displacement, or reconstruction.
- `belt` (coverage_score) — No visible belt, sash, waist cincher, or harness is described; only silhouette shaping and layering are mentioned.
- `asymmetry` (coverage_score) — No clear asymmetrical design, one-shoulder, single-sleeve, or uneven structural garment feature is described.
- `quantity_accuracy` (quality_score) — The text contains no explicit counts or quantity relations that need verification.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral asymmetry is described.
- `cultural_reference` (bonus_score) — No cultural, historical, or brand grounding is provided.
- `gender_expression` (bonus_score) — The description does not explicitly discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is stated beyond the garment description.
- `brand_alignment` (bonus_score) — No brand identity or brand-language target is mentioned.
- `negation_control` (bonus_score) — The text does not emphasize exclusions or absences that need explicit control.
