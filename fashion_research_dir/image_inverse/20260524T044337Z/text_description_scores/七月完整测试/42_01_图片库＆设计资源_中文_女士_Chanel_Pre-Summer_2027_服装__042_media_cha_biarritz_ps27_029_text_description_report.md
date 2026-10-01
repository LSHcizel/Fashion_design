# Text Evaluation Report

- **Source:** 42_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__042_media_cha_biarritz_ps27_029_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.8172 (Strong)
- **Coverage axis:** 1.0
- **Quality axis (raw / base / penalized):** 0.7692 / 0.7708 / 0.7708
- **Penalties (mean):** 0.25
- **R_content:** 0.745695

## Gates

- Score gate: 0.8172 (threshold 0.7) → **PASS**
- Penalty gate: 0.25 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `asymmetry` | 1.0 | 1 |  | Asymmetry is explicitly stated and visually supported by the mixed stripe directions and diagonal front panel. |
| `body_coverage` | 1.0 | 1 |  | The text clearly describes both coverage and reveal through covered neckline and leg-exposing slit/open panels. |
| `closure` | 1.0 | 1 |  | A clear button closure is explicitly described, along with a front opening. |
| `color_relationship_logic` | 1.0 | 1 |  | The text explains the color logic through high-contrast stripes, clashing stripe directions, and layered scarf print accents. |
| `cross_garment_binding` | 1.0 | 1 |  | The description distinguishes the shirt layer, lower skirt/dress section, and accessories, making the garment relationships clear. |
| `footwear` | 1.0 | 1 |  | Footwear type, heel height, and color/strap detail are clearly specified. |
| `garment_category` | 1.0 | 1 |  | The text clearly identifies the main garment types: a shirt-dress/long shirt with a skirt or dress section, plus sandals. |
| `jewelry` | 1.0 | 1 |  | Earrings are explicitly noted as visible body adornment. |
| `layering` | 1.0 | 1 |  | The text clearly describes layered garments and their relationship, including an upper shirt layer, a lower skirt/dress section, and a scarf over the neckline. |
| `length_hemline` | 1.0 | 1 |  | The description gives clear length and hemline information, including ankle length and a slit. |
| `pattern_type` | 1.0 | 1 |  | The pattern types are clearly identified as stripes, with an additional chevron-like panel and graphic print motifs. |
| `primary_color` | 1.0 | 1 |  | Red is presented as the dominant color in the ensemble. |
| `secondary_color` | 1.0 | 1 |  | Secondary colors are clearly present alongside the main red, especially black/navy and white, with yellow appearing in the scarf accent. |
| `silhouette` | 1.0 | 1 |  | Overall shape and structural flow are explicitly described. |
| `surface_finish` | 1.0 | 1 |  | The description clearly conveys a drapey, fluid surface quality, which satisfies the surface-trait requirement. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes the overall vertical proportion and balance of the look, including a long upper layer and ankle-length lower section. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are bound to the correct garment or accessory, and the layered outfit is generally coherent. There is some mild ambiguity in phrases like “beneath or continuing from the shirt layer” a |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is mostly anchored in visible garment facts and silhouette details, with only a modest amount of mood framing. It is somewhat verbose and repetitive in places, but still efficient enou |
| `craft_embellishment_salience` | 0.5 | 0 | 工艺装饰显著度 | There are salient structural and styling details, but the craft is not deeply specified in terms of technique, exact construction, and visual function beyond general slit panels, bow tying, and border |
| `design_distinctiveness` | 0.75 | 1 | 设计独特性 | The look has clear non-formula memory points through strong graphic striping, slit sleeve panels, and a diagonal chevron-like panel. It is distinctive, though still within a coherent striped resort/ru |
| `design_signal_purity` | 1.0 | 1 | 设计信号纯度 | The text is dominated by concrete design facts—color, stripe direction, garment structure, and accessories—with only a brief mood note at the end. Design signal clearly outweighs narrative framing. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly visual and mostly prompt-ready, with clear silhouette, layering, colors, and accessories. Minor issues remain because it uses some hedging language (“appears,” “or”) and reads a bit |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description generally follows a clear body-to-detail progression: overall look, main garment layers, lower section, then accessories. There is some hedging and overlap in the garment breakdown (“b |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text distinguishes multiple garments and accessories reasonably well, with most colors and structural details attached to the right item. Minor uncertainty remains around whether the lower portion |
| `reference_clarity` | 0.75 | 1 | 语言清晰度 | References are mostly clear and the garment layering is understandable, though some phrasing remains slightly hedged and alternative-based, creating minor ambiguity. |
| `silhouette_combination_originality` | 0.75 | 1 | 组合原创性 | The silhouette combines an oversized shirt-like top with a skirt/dress hybrid and directional stripe clashes, creating a more unusual full-length look. It is still somewhat legible and fashion-editori |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and garment relationships are mostly clear and imageable, including upper layer, lower section, and slit reveal. The main limitation is some uncertainty in phrasing (“appears,” “beneath or co |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | The text prioritizes highly visible, image-dominant features such as stripes, silhouette, slit, and footwear. It includes some styling/mood language, but hidden or low-visibility details do not domina |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly anchored in visible garment details and body locations, with clear layering and hem/center-front observations. It reads like a direct runway caption rather than concept pro |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.25 | There is mild ambiguity between shirt-dress and skirt/dress continuation, but no strong trunk-level left-right contradiction or mutually exclusive garment identity. |
| `coordination_penalty` | 0.25 | The look is intentionally busy and mixed in stripe direction, but the palette and accessories are still broadly unified; coordination is slightly strained, not broken. |
| `formula_template_penalty` | 0.5 | The description leans on a familiar resort/runway formula with mood-forward framing and interchangeable styling language, though it still includes some concrete garment details. |
| `generation_content_penalty` | 0.25 | Mostly imageable, but somewhat essay-like and style-framing heavy; the description spends space on mood/coordination rather than only garment construction. |
| `rationality_penalty` | 0.0 | No materially implausible garment construction or physically impossible wearing condition is asserted. |

## Quality issues (质量短板)

- **`craft_embellishment_salience`** (score 0.5) — There are salient structural and styling details, but the craft is not deeply specified in terms of technique, exact construction, and visual function beyond general slit panels, bow tying, and border panels.

## Skipped metrics (不适用)

- `shoulder_architecture` (coverage_score) — No salient shoulder-specific construction is described; the text mentions sleeves and neckline coverage, but not shoulder architecture.
- `fabric_family` (coverage_score) — The text describes color, stripe structure, and drape, but does not clearly identify a main fabric family such as cotton, silk, wool, denim, etc.
- `functional_detail` (coverage_score) — No salient pockets, straps, or utility-specific functional details are described beyond general styling and footwear lacing.
- `construction_technique` (coverage_score) — The text describes silhouette and paneling, but not a clearly named construction technique such as pleating, quilting, embroidery, or engineered cutwork with a specific placement.
- `deconstruction` (coverage_score) — The description suggests layered asymmetry, but does not explicitly mention deconstruction, splicing, displacement, or reconstruction.
- `hardware_embellishment` (coverage_score) — No chains, studs, metal rings, crystals, or similar hardware embellishment is mentioned.
- `bag` (coverage_score) — No bag is mentioned or implied as a salient part of the look.
- `belt` (coverage_score) — No visible belt, sash, waist cincher, or harness is described.
- `quantity_accuracy` (quality_score) — No explicit numeric quantities, counts, or quantity relations are used.
- `bilateral_coherence` (quality_score) — No explicit left-right bilateral distinction is described.
- `cultural_reference` (bonus_score) — No specific cultural, historical, or brand reference is grounded in the description.
- `gender_expression` (bonus_score) — The text does not explicitly discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is stated beyond the outfit description.
- `brand_alignment` (bonus_score) — No brand identity or brand-language target is mentioned.
- `negation_control` (bonus_score) — The description does not rely on important exclusions or absence statements.
