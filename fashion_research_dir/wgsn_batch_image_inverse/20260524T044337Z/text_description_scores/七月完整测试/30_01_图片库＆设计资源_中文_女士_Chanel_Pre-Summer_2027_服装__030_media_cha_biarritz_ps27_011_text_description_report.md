# Text Evaluation Report

- **Source:** 30_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__030_media_cha_biarritz_ps27_011_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.8065 (Strong)
- **Coverage axis:** 0.9474
- **Quality axis (raw / base / penalized):** 0.7692 / 0.7708 / 0.7708
- **Penalties (mean):** 0.15
- **R_content:** 0.764159

## Gates

- Score gate: 0.8065 (threshold 0.7) → **PASS**
- Penalty gate: 0.15 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `bag` | 0.0 | 0 |  | A bag is mentioned, but only as a glimpse; the text gives no clear bag type, shape, or material/finish details, so the coverage rule is not satisfied. |
| `body_coverage` | 1.0 | 1 |  | The text clearly indicates exposed coverage at the front and neckline. |
| `closure` | 1.0 | 1 |  | The text clearly indicates an open front closure/closure state. |
| `color_relationship_logic` | 1.0 | 1 |  | The text explains the palette as a pale mint/white base with multicolor accents and contrasting prints, giving a clear color relationship. |
| `construction_technique` | 1.0 | 1 |  | The jacket’s woven construction and applied braided trim describe a clear craft/construction technique with garment placement. |
| `cross_garment_binding` | 1.0 | 1 |  | Multiple garments are present and the text distinguishes their roles and placement, making the cross-garment relationships clear. |
| `fabric_family` | 1.0 | 1 |  | The main garment material family is clearly described as woven/textured woven. |
| `functional_detail` | 1.0 | 1 |  | Pockets are explicitly mentioned as a functional garment detail. |
| `garment_category` | 1.0 | 1 |  | The text clearly identifies the main garment categories. |
| `hardware_embellishment` | 1.0 | 1 |  | Chains and a pendant are clearly present as metallic embellishment/hardware. |
| `jewelry` | 1.0 | 1 |  | Jewelry is clearly salient and explicitly described with multiple pieces. |
| `layering` | 1.0 | 1 |  | The text clearly describes layered garments and their visible order. |
| `length_hemline` | 1.0 | 1 |  | Garment length is directly stated. |
| `pattern_type` | 1.0 | 1 |  | Multiple pattern types are clearly identified, including branch-like motif, grid/check, and curved motifs. |
| `primary_color` | 1.0 | 1 |  | The dominant color of the jacket/look is clearly pale mint with white. |
| `secondary_color` | 1.0 | 1 |  | Secondary accent colors are explicitly stated and anchored to the jacket trim and motif. |
| `silhouette` | 1.0 | 1 |  | Overall shape and structural contour are explicitly described. |
| `surface_finish` | 1.0 | 1 |  | The text gives clear surface/handfeel cues: structured and boxy, implying a stiff, tailored finish rather than drapey. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes upper and lower body proportions and the balance between the cropped jacket and the visible lower garment. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are clearly tied to the correct garment or accessory, and the layering is understandable. Minor ambiguity remains around the lower garment being “a skirt or dress,” but this does not s |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is fairly dense with visible garment facts and construction details, and it stays mostly focused on the outfit. There is some accessory/styling elaboration and mood framing, but not en |
| `craft_embellishment_salience` | 1.0 | 1 | 工艺装饰显著度 | The craft detail is specific in type, placement, and visual effect, making it a primary design hook. |
| `design_distinctiveness` | 0.75 | 1 | 设计独特性 | The look has a clear memory point in the unusual braided trim plus layered mixed-print surface, though it is still within a recognizable jacket-and-skirt runway framework. |
| `design_signal_purity` | 0.75 | 1 | 设计信号纯度 | Most of the text is devoted to concrete design facts, with only a brief mood phrase at the end. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly visual and mostly prompt-ready, with clear garment hierarchy, silhouette, layering, and styling details. It is slightly less than perfect because it includes some interpretive uncer |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a mostly natural body-to-detail progression: main jacket, then underlayers, then lower garment, then accessories/styling. There is some minor jumping between garment details an |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text distinguishes jacket, inner layered pieces, lower garment, jewelry, and handbag fairly well. There is slight uncertainty in the exact identity of the lower garment, but no major cross-binding |
| `reference_clarity` | 0.75 | 1 | 语言清晰度 | References are mostly clear and the garment subjects are easy to track, but a few hedge phrases and alternations (“collarless or has…”, “skirt or dress”) introduce mild ambiguity. |
| `silhouette_combination_originality` | 0.5 | 0 | 组合原创性 | The silhouette is coherent and styled, but the overall combination remains a fairly legible runway jacket-plus-skirt formula rather than a highly unexpected pairing. |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and attachment relationships are generally clear and imageable, especially front opening, center-front panel, and jewelry overlap. The main limitation is a small amount of ambiguity in the lo |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | The most visible, image-defining garments are prioritized first, and the text generally keeps hidden or secondary details subordinate. A few styling and mood phrases appear, but they do not overwhelm  |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly anchored to visible garment zones and distinguishes what is seen versus inferred. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.25 | The bottom is somewhat uncertain in identity (skirt or dress), but there is no strong trunk-level left-right or material conflict. |
| `coordination_penalty` | 0.0 | The look is eclectic but still coherently styled around patterned jacket, mixed-print bottom, and coordinated artisanal trim; no major trunk-level clash. |
| `formula_template_penalty` | 0.25 | The description is somewhat runway-essay-like and styling-led, but it still contains concrete craft details and is not strongly formulaic. |
| `generation_content_penalty` | 0.25 | Mostly grounded garment description, but the styling/mood list adds some non-essential accessory and atmosphere emphasis that slightly dilutes the imaging trunk. |
| `rationality_penalty` | 0.0 | All described materials and garments are physically plausible as ordinary fashion construction. |

## Missing coverage (未覆盖)

- **`bag`** — A bag is mentioned, but only as a glimpse; the text gives no clear bag type, shape, or material/finish details, so the coverage rule is not satisfied.

## Quality issues (质量短板)

- **`silhouette_combination_originality`** (score 0.5) — The silhouette is coherent and styled, but the overall combination remains a fairly legible runway jacket-plus-skirt formula rather than a highly unexpected pairing.

## Skipped metrics (不适用)

- `shoulder_architecture` (coverage_score) — No prominent shoulder construction is specified beyond sleeve length and general silhouette.
- `deconstruction` (coverage_score) — No deconstruction, splicing, displacement, or reconstruction is explicitly described.
- `footwear` (coverage_score) — No footwear is described.
- `belt` (coverage_score) — No visible belt, sash, or waist strap is mentioned.
- `asymmetry` (coverage_score) — No clear asymmetrical design, one-shoulder, uneven hem, or similar structure is described.
- `quantity_accuracy` (quality_score) — The text contains no explicit counts, numerals, or quantity relations that require verification.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral differences are described.
- `cultural_reference` (bonus_score) — No clear cultural, historical, or brand-specific grounding is provided.
- `gender_expression` (bonus_score) — The description does not explicitly discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is explicitly stated.
- `brand_alignment` (bonus_score) — No brand identity or brand-language target is mentioned.
- `negation_control` (bonus_score) — The text does not emphasize exclusions or absence as an important design constraint.
