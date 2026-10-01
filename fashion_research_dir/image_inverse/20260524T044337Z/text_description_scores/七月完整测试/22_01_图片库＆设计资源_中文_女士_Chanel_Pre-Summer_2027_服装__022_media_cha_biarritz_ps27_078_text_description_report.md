# Text Evaluation Report

- **Source:** 22_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__022_media_cha_biarritz_ps27_078_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.8006 (Strong)
- **Coverage axis:** 0.75
- **Quality axis (raw / base / penalized):** 0.8077 / 0.8125 / 0.8125
- **Penalties (mean):** 0.1
- **R_content:** 0.772579

## Gates

- Score gate: 0.8006 (threshold 0.7) → **PASS**
- Penalty gate: 0.1 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `bag` | 1.0 | 1 |  | The bag is explicitly described with category, shape, and material/finish cues. |
| `body_coverage` | 1.0 | 1 |  | The text describes substantial body coverage and limited visibility at the lower body/feet. |
| `closure` | 0.0 | 0 |  | A possible opening is mentioned, but no clear closure type or visible fastening detail is specified. |
| `color_relationship_logic` | 1.0 | 1 |  | The text gives a clear dominant/accent relationship: red-orange base with metallic gold highlights concentrated in specific areas. |
| `construction_technique` | 1.0 | 1 |  | A clear craft technique is described and located on the garment surface, especially across the ensemble and center front. |
| `cross_garment_binding` | 1.0 | 1 |  | Multiple garments are present and the description distinguishes which features belong to the upper garment versus the skirt. |
| `fabric_family` | 0.0 | 0 |  | The text describes surface decoration and embellishment, but not a clear underlying fabric family for the garment body. |
| `footwear` | 0.0 | 0 |  | Footwear is mentioned only as hidden, with no clear shoe type, shape, or material details. |
| `functional_detail` | 0.0 | 0 |  | The text mentions a handbag, but not salient garment functional details like pockets, straps, or utility features on the clothing. |
| `garment_category` | 1.0 | 1 |  | The text clearly identifies the main garment types as an embellished top/jacket and skirt ensemble. |
| `hardware_embellishment` | 1.0 | 1 |  | The look clearly features prominent decorative embellishment consistent with hardware-like ornamentation. |
| `layering` | 1.0 | 1 |  | The text clearly describes a layered outfit with an upper garment over a skirt. |
| `length_hemline` | 1.0 | 1 |  | The garment length and hem treatment are directly stated. |
| `pattern_type` | 0.0 | 0 |  | A mottled effect is mentioned, but not a sufficiently clear pattern type such as stripes, florals, checks, or print category. |
| `primary_color` | 1.0 | 1 |  | The main color is explicitly stated. |
| `secondary_color` | 1.0 | 1 |  | Gold is a clear secondary color accent alongside the red-orange base. |
| `shoulder_architecture` | 1.0 | 1 |  | Shoulder and sleeve structure are clearly specified, indicating a defined shoulder line. |
| `silhouette` | 1.0 | 1 |  | Overall structure and contour are explicitly described as fitted and columnar. |
| `surface_finish` | 1.0 | 1 |  | The look clearly conveys a glossy, reflective, highly embellished surface finish. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes the upper and lower silhouette relationship, including waist placement and the contrast between a fitted top and narrow long skirt. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are bound to the correct garment or accessory, and the layering relation is clear. Minor ambiguity remains in “top or jacket” and “front opening or seam,” but these do not seriously di |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is compact and packed with visible garment facts, with only light stylistic framing. There is some redundancy and interpretive hedging, but the main outfit structure remains clear and  |
| `craft_embellishment_salience` | 1.0 | 1 | 工艺装饰显著度 | The craft is clearly identified by type, placement, and visual effect, and it functions as a main hook of the look. |
| `design_distinctiveness` | 0.75 | 1 | 设计独特性 | The look has a clear memory point through dense reflective embellishment plus a peplum-like waist treatment and fiery red-orange/gold palette. It is distinctive, though not so singularly structured th |
| `design_signal_purity` | 0.75 | 1 | 设计信号纯度 | The text is dominated by concrete design facts, with only a small amount of evaluative mood language at the end. The design signal remains strong and mostly unblurred. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly imageable and already organized around visible silhouette, garment types, palette, and surface treatment, so it is close to a usable generation prompt. Minor issues remain because i |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a mostly natural order from overall look to garment layers, then to upper garment, skirt, embellishment, and accessory. It is clear and easy to reconstruct, though some hedging |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text cleanly separates the upper garment, skirt, and handbag while keeping shared embellishment and palette consistent across items. There is slight ambiguity in the upper piece being “top or jack |
| `reference_clarity` | 1.0 | 1 | 语言清晰度 | References are stable and unambiguous; each sentence clearly anchors to a specific garment or accessory without confusing pronouns or unclear antecedents. |
| `silhouette_combination_originality` | 0.75 | 1 | 组合原创性 | The silhouette combination is coherent and somewhat unusual, especially with the peplum-like waist release over a column skirt. Still, it remains within a recognizable couture evening framework rather |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and attachment relationships are mostly clear and visually reconstructable: an upper garment over a skirt, peplum at the hips, and hem obscuring the feet. The spatial logic is coherent, thoug |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | Visible silhouette, surface treatment, and accessory details are prioritized well. A few lower-visibility interpretive phrases appear, but they do not overwhelm the image-dominant clothing information |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly anchored in visible garment details and body zones, with careful distinction between what is seen and what is inferred. It reads like a runway observation rather than conce |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | No clear trunk-level left-right or garment-identity conflict; the outfit reads as one coherent ensemble with only mild uncertainty in garment naming. |
| `coordination_penalty` | 0.0 | Color, silhouette, and accessory all align into a unified ornate evening/couture styling. |
| `formula_template_penalty` | 0.25 | Some runway-essay/generalized styling language is present, but the description remains fairly specific and craft-grounded rather than fully formulaic. |
| `generation_content_penalty` | 0.25 | Mostly grounded garment description, but includes some evaluative/runway-style framing that slightly reduces prompt efficiency. |
| `rationality_penalty` | 0.0 | The described materials and wearing conditions are physically plausible for fashion imagery. |

## Missing coverage (未覆盖)

- **`fabric_family`** — The text describes surface decoration and embellishment, but not a clear underlying fabric family for the garment body.
- **`pattern_type`** — A mottled effect is mentioned, but not a sufficiently clear pattern type such as stripes, florals, checks, or print category.
- **`closure`** — A possible opening is mentioned, but no clear closure type or visible fastening detail is specified.
- **`functional_detail`** — The text mentions a handbag, but not salient garment functional details like pockets, straps, or utility features on the clothing.
- **`footwear`** — Footwear is mentioned only as hidden, with no clear shoe type, shape, or material details.

## Skipped metrics (不适用)

- `deconstruction` (coverage_score) — No deconstruction, splicing, displacement, or reconstruction is explicitly described.
- `jewelry` (coverage_score) — No jewelry or body ornament is explicitly present.
- `belt` (coverage_score) — No visible belt, sash, waist strap, or harness is described; the waist shaping comes from garment cut.
- `asymmetry` (coverage_score) — No clear asymmetry, one-shoulder, uneven hem, or other uneven structure is described.
- `quantity_accuracy` (quality_score) — The text does not use explicit counts or quantity relations that need verification.
- `bilateral_coherence` (quality_score) — No explicit left-right, bilateral, or side-specific garment differences are described.
- `cultural_reference` (bonus_score) — No clear cultural, historical, or brand reference is provided.
- `gender_expression` (bonus_score) — The description does not explicitly discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is stated.
- `brand_alignment` (bonus_score) — There is no explicit brand language or brand identity target.
