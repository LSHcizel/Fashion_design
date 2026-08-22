# Text Evaluation Report

- **Source:** 60_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__060_media_cha_biarritz_ps27_054_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.8075 (Strong)
- **Coverage axis:** 0.9524
- **Quality axis (raw / base / penalized):** 0.7692 / 0.7708 / 0.7708
- **Penalties (mean):** 0.2
- **R_content:** 0.750975

## Gates

- Score gate: 0.8075 (threshold 0.7) → **PASS**
- Penalty gate: 0.2 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `asymmetry` | 1.0 | 1 |  | The waist treatment is explicitly off-center and diagonally placed, indicating asymmetrical design. |
| `bag` | 1.0 | 1 |  | The bag is explicitly identified, with carry position and color clearly described. |
| `belt` | 1.0 | 1 |  | A visible waist sash/tie is explicitly described, with its placement and attachment relation to the garment clear. |
| `body_coverage` | 1.0 | 1 |  | The text clearly describes body exposure and coverage through the deep V neckline and fitted upper torso. |
| `closure` | 1.0 | 1 |  | A clear tie/sash closure is explicitly described. |
| `color_relationship_logic` | 1.0 | 1 |  | It explains the palette relationship as a black base with contrasting ivory and jewel-toned accents. |
| `cross_garment_binding` | 1.0 | 1 |  | The description distinguishes multiple items and their roles, including the main garment(s), waist tie, accessories, and footwear. |
| `fabric_family` | 0.0 | 0 |  | The text gives surface and color qualities, but not a clear main fabric family such as silk, wool, leather, cotton, or chiffon. |
| `footwear` | 1.0 | 1 |  | Footwear type, heel height, and surface/color treatment are all specified. |
| `functional_detail` | 1.0 | 1 |  | A functional accessory detail is present and clearly described. |
| `garment_category` | 1.0 | 1 |  | The text clearly identifies the main garment category as a dress or a coordinated two-piece ensemble. |
| `jewelry` | 1.0 | 1 |  | Prominent jewelry is clearly present and described as a styling element. |
| `layering` | 1.0 | 1 |  | The text describes a multi-part look with an overlaid waist tie/sash and a distinct upper and lower garment relationship. |
| `length_hemline` | 1.0 | 1 |  | The description explicitly states garment length and hem behavior. |
| `pattern_type` | 1.0 | 1 |  | A specific pattern type is present: horizontal striping. |
| `primary_color` | 1.0 | 1 |  | Black is clearly the dominant base color of the look. |
| `secondary_color` | 1.0 | 1 |  | The text identifies clear accent colors, especially ivory against black, plus green in the accessories. |
| `shoulder_architecture` | 1.0 | 1 |  | Shoulder treatment is clearly specified as sleeveless with clean shoulders. |
| `silhouette` | 1.0 | 1 |  | It gives a clear structural silhouette: fitted upper body with a voluminous lower shape. |
| `surface_finish` | 1.0 | 1 |  | It clearly describes finish and handfeel-like surface traits: matte, drapey, and non-rigid. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes upper-versus-lower proportion and visual balance, with a fitted top and much fuller lower half. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are bound to the correct entities, and the look is generally coherent. There is minor ambiguity around whether the waist wrap is a sash or tie and whether the garment is a dress or coo |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is mostly packed with visible garment facts and silhouette details, with clear trunk-first organization. There is some stylistic framing (“elegant, dramatic, and artfully bohemian”), b |
| `craft_embellishment_salience` | 0.75 | 1 | 工艺装饰显著度 | The gathering/flounce treatment and tied sash are clearly located and visually functional, though the craft language is still somewhat descriptive rather than highly technical. |
| `design_distinctiveness` | 0.75 | 1 | 设计独特性 | The diagonal off-center sash and sculptural gathered lower section create a clear non-formula memory point, though the overall black dress/top-and-bottom base remains fairly conventional. |
| `design_signal_purity` | 0.75 | 1 | 设计信号纯度 | Most of the text is concrete design observation, and the mood language is limited to a single closing sentence rather than dominating the description. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly visual and mostly prompt-ready, with clear silhouette, garment layers, and accessories. It is slightly less direct than a pure generation prompt because it includes hedging and anal |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a mostly natural body-to-detail order: main garment, waist treatment, lower silhouette, then accessories and shoes. It is clear and imageable, though slightly compressed by lon |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | Multiple garments and accessories are described with mostly stable attribution. The main uncertainty is the dress-versus-separate-ensemble framing, but the text still keeps the waist detail, lower sil |
| `reference_clarity` | 1.0 | 1 | 语言清晰度 | References and spatial relations are clear and stable; pronouns are minimal and the described objects are consistently identifiable. |
| `silhouette_combination_originality` | 0.75 | 1 | 组合原创性 | The look combines a fitted deep-V upper body with a voluminous sculptural lower half, which is more distinctive than a standard formula outfit, though still within a recognizable runway dress language |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | The spatial relationships are clear and imageable: the sash crosses the front and knots, the lower section expands below the waist, and the ruffles are localized to front and sides. Minor ambiguity re |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | The text prioritizes highly visible, image-dominant clothing structure and surface texture. Accessories and mood language are present, but they remain secondary to the main silhouette and construction |
| `visual_observation_grounding` | 0.75 | 1 | 视觉观察 grounded | The description is strongly anchored in visible garment zones and readable structure, with only light interpretive language at the end. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.25 | There is mild ambiguity between dress and two-piece ensemble, but no strong trunk-level contradiction. |
| `coordination_penalty` | 0.25 | Accessories and shoes add some mixed styling signals, but the main silhouette remains coherent and readable. |
| `formula_template_penalty` | 0.25 | Some runway-essay framing and mood summary are present, but the description still contains a clear design trunk and specific construction details. |
| `generation_content_penalty` | 0.25 | Mostly grounded garment description, but ends with interpretive mood language that slightly dilutes prompt efficiency. |
| `rationality_penalty` | 0.0 | No materially implausible construction or physically impossible wearing condition is described. |

## Missing coverage (未覆盖)

- **`fabric_family`** — The text gives surface and color qualities, but not a clear main fabric family such as silk, wool, leather, cotton, or chiffon.

## Skipped metrics (不适用)

- `construction_technique` (coverage_score) — No specific fabrication technique like pleating, quilting, embroidery, or cutwork is clearly named.
- `deconstruction` (coverage_score) — The text does not explicitly mention deconstruction, splicing, displacement, or reconstruction.
- `hardware_embellishment` (coverage_score) — Jewelry is described, but no salient hardware embellishment such as chains, studs, rings, or crystals is specified.
- `quantity_accuracy` (quality_score) — The text does not use explicit counts or quantity relations that need verification.
- `bilateral_coherence` (quality_score) — No explicit left-right or bilateral differences are described.
- `cultural_reference` (bonus_score) — No clear cultural, historical, or brand reference is provided.
- `gender_expression` (bonus_score) — The description does not explicitly discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is explicitly stated.
- `brand_alignment` (bonus_score) — The text does not target a specific brand identity or brand language.
- `negation_control` (bonus_score) — The text does not emphasize exclusions or absence of elements.
