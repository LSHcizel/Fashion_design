# Text Evaluation Report

- **Source:** 02_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__002_media_cha_biarritz_ps27_006_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.1
- **Total score (S_fp):** 0.87 (Strong)
- **Coverage axis:** 0.9474
- **Quality axis (raw / base / penalized):** 0.8667 / 0.85 / 0.85
- **Penalties (mean):** 0.05
- **R_content:** 0.854775

## Gates

- Score gate: 0.87 (threshold 0.7) → **PASS**
- Penalty gate: 0.05 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `bag` | 1.0 | 1 |  | Bag type, shape, color/material, and carrying position are all clearly described. |
| `body_coverage` | 1.0 | 1 |  | The text clearly describes coverage and exposure through the sleeveless top and layered arrangement. |
| `color_relationship_logic` | 1.0 | 1 |  | The text explains the color/pattern relationship as a coordinated patterned suit layered over a brown top, giving a clear main-vs-accent and layered color logic. |
| `construction_technique` | 1.0 | 1 |  | A notable fabrication/finish is described with technique-like specificity and placement on the garment edges, cuffs, hem, and neckline. |
| `cross_garment_binding` | 1.0 | 1 |  | Multiple garments are clearly distinguished and their roles are assigned: jacket, tunic/top, and skirt are separately described and related in the outfit. |
| `fabric_family` | 0.0 | 0 |  | The text suggests texture and construction but does not clearly identify a main fabric family such as wool, cotton, silk, leather, or knit. |
| `functional_detail` | 1.0 | 1 |  | The text clearly mentions functional details including patch pockets and bag straps/hardware. |
| `garment_category` | 1.0 | 1 |  | The text clearly names the main garment categories and accessory. |
| `hardware_embellishment` | 1.0 | 1 |  | The bag explicitly includes hardware, and the look also features metallic jewelry embellishment. |
| `jewelry` | 1.0 | 1 |  | Prominent jewelry is explicitly described and visually salient. |
| `layering` | 1.0 | 1 |  | The text clearly describes a multi-layer outfit with readable over/under relationships. |
| `length_hemline` | 1.0 | 1 |  | The description includes multiple length and hemline cues. |
| `pattern_type` | 1.0 | 1 |  | A clear pattern type is given: an abstract woven-looking pattern. |
| `primary_color` | 1.0 | 1 |  | The look has a clear dominant color story centered on grey/black/orange patterning with brown as the main underlayer. |
| `secondary_color` | 1.0 | 1 |  | Multiple secondary colors are explicitly present and visually salient, especially the orange-red trim and the brown underlayer against the patterned suit. |
| `shoulder_architecture` | 1.0 | 1 |  | The jacket’s shoulder construction is explicitly described. |
| `silhouette` | 1.0 | 1 |  | It gives a clear structural silhouette for both the jacket and skirt. |
| `surface_finish` | 1.0 | 1 |  | It clearly describes surface/handfeel traits including structured, boxy, and textured/frayed finishes. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes the upper-to-lower silhouette and how the longer top extends over the skirt, making the proportion and visual balance explicit. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are bound to the correct garment or accessory, and the layering is mostly clear. Minor ambiguity remains in phrases like “sleeveless-looking long top or tunic,” but it does not serious |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is packed with visible garment facts and keeps the outfit structure clear. There is some extra styling/mood language, but it does not overwhelm the clothing details. |
| `craft_embellishment_salience` | 1.0 | 1 | 工艺装饰显著度 | The craft detail is specific in type, location, and visual effect, and functions as a main design hook. |
| `design_distinctiveness` | 1.0 | 1 | 设计独特性 | The look has multiple clear memory points: an abstract woven-like pattern and extensive frayed trim placement, plus an unusual skirt-suit layering with a tunic. |
| `design_signal_purity` | 1.0 | 1 | 设计信号纯度 | The text is dominated by concrete design facts—shape, pattern, trim, layering, and accessories—with only a brief mood summary at the end. |
| `fine_grained_attribute_usage` | 1.0 | 1 | 术语具体度 | Color, material, construction, and trim details are richly and precisely specified, making the look highly imageable. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly visual and mostly prompt-ready, with clear garment types, layering, silhouette, materials, and accessories. It reads slightly like a detailed fashion description rather than a fully |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a mostly natural order from overall look to jacket, then inner layer, skirt, and accessories. It is easy to reconstruct the outfit, though the long jacket sentence is dense and |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text keeps the jacket, tunic, skirt, and handbag mostly distinct and correctly related. There is slight ambiguity around the tunic’s exact garment identity, but the multi-item binding is still str |
| `reference_clarity` | 1.0 | 1 | 语言清晰度 | References and ellipses are clear and consistently anchored to the jacket, top, skirt, and accessories, with no ambiguous pronoun chains. |
| `silhouette_combination_originality` | 0.75 | 1 | 组合原创性 | The silhouette is more distinctive than a standard formula because of the visible tunic-over-skirt-suit layering, though the jacket-and-skirt base remains somewhat conventional. |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and attachment positions are clearly described and visually reconstructable. The spatial logic is coherent, with only minor complexity from the many trim placements and accessory details. |
| `specific_noun_usage` | 1.0 | 1 | 术语具体度 | Uses highly specific garment and accessory nouns with clear fashion semantics, plus precise structural descriptors. |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | The text prioritizes the visible outfit and accessories well. The mood sentence is present but brief and secondary, so it does not significantly displace the image-dominant garment description. |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly anchored in visible garment parts and placements, with precise structural and trim observations rather than mood prose. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | No trunk-level left-right or mutually exclusive garment conflicts; the jacket, tunic, and skirt read as a coherent layered outfit. |
| `coordination_penalty` | 0.0 | The styling language is unified and the accessories support the same retro-luxe direction without trunk-level clash. |
| `formula_template_penalty` | 0.0 | The text is a single grounded prose paragraph rather than a fixed formula template. |
| `generation_content_penalty` | 0.25 | Mostly imageable garment description, but ends with a mood-style summary and a dense accessory list that slightly reduces prompt efficiency. |
| `rationality_penalty` | 0.0 | All described materials and construction are physically plausible for ordinary fashion wear. |

## Missing coverage (未覆盖)

- **`fabric_family`** — The text suggests texture and construction but does not clearly identify a main fabric family such as wool, cotton, silk, leather, or knit.

## Skipped metrics (不适用)

- `closure` (coverage_score) — No explicit closure method is described; the jacket is only said to be 'open-front'.
- `deconstruction` (coverage_score) — The text does not mention deconstruction, splicing, displacement, or reconstruction.
- `footwear` (coverage_score) — No footwear is mentioned in the text.
- `belt` (coverage_score) — No visible belt, sash, or waist strap is described.
- `asymmetry` (coverage_score) — No asymmetrical design, one-sided structure, or uneven garment construction is described.
- `quantity_accuracy` (quality_score) — The text contains no explicit counts or quantity relations that need verification.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral asymmetry is described.
- `cultural_reference` (bonus_score) — No specific cultural, historical, or brand reference is grounded in the text.
- `gender_expression` (bonus_score) — The description does not explicitly discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is stated beyond the outfit description.
- `brand_alignment` (bonus_score) — No brand identity or brand-language target is mentioned.
- `negation_control` (bonus_score) — The text does not emphasize exclusions or absences that need explicit negation control.
