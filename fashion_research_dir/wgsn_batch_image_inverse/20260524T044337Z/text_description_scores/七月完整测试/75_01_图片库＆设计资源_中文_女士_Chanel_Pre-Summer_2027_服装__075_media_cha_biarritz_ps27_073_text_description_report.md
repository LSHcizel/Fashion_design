# Text Evaluation Report

- **Source:** 75_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__075_media_cha_biarritz_ps27_073_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.8122 (Strong)
- **Coverage axis:** 0.8889
- **Quality axis (raw / base / penalized):** 0.7833 / 0.7917 / 0.7917
- **Penalties (mean):** 0.1
- **R_content:** 0.783773

## Gates

- Score gate: 0.8122 (threshold 0.7) → **PASS**
- Penalty gate: 0.1 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `asymmetry` | 1.0 | 1 |  | Asymmetry is explicitly stated in both the waist treatment and skirt slit. |
| `body_coverage` | 1.0 | 1 |  | The text clearly describes exposed areas and coverage breaks. |
| `closure` | 1.0 | 1 |  | A clear tie closure is explicitly described at the waist. |
| `color_relationship_logic` | 1.0 | 1 |  | The text states the palette logic as a minimal two-tone ivory-and-black contrast with graphic emphasis. |
| `cross_garment_binding` | 1.0 | 1 |  | The description distinguishes how binding and wrapping elements belong to different parts of the dress, clearly separating garment-specific attributes. |
| `footwear` | 0.0 | 0 |  | Footwear is mentioned, but only as a vague glimpse; the text does not specify shoe type, shape, heel/boot structure, or material/finish. |
| `functional_detail` | 1.0 | 1 |  | The text describes functional strap/band elements as part of the garment structure. |
| `garment_category` | 1.0 | 1 |  | The main garment is explicitly identified as a dress. |
| `hardware_embellishment` | 1.0 | 1 |  | The medallion/emblem details count as visible decorative hardware-like embellishment. |
| `jewelry` | 0.0 | 0 |  | Jewelry is referenced only as minimal/visible absence, not as a salient ornament with identifiable details. |
| `layering` | 1.0 | 1 |  | The text clearly describes an overlaid element and its relation to the base dress, making the layering readable. |
| `length_hemline` | 1.0 | 1 |  | Garment length and hem treatment are explicitly stated. |
| `primary_color` | 1.0 | 1 |  | The main garment color is clearly ivory/cream. |
| `secondary_color` | 1.0 | 1 |  | Black is a clear secondary/accent color used in edging, binding, and sash details. |
| `shoulder_architecture` | 1.0 | 1 |  | The shoulder/upper-body structure is clearly specified through sleeveless construction and straps. |
| `silhouette` | 1.0 | 1 |  | The text clearly describes the overall shape as slim and narrow. |
| `surface_finish` | 1.0 | 1 |  | The description clearly conveys a soft, fluid drape as the salient surface/property trait. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes the silhouette balance between upper body, waist, and skirt length, making top-bottom proportion salient. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are clearly tied to the dress and its left-side placement is stable. Minor complexity comes from multiple layered waist/hip details, but the bindings remain coherent and imageable. |
| `bilateral_coherence` | 0.75 | 1 | 生成适配度 | The left-side differences are limited to waist knot placement and slit placement on a single dress, not conflicting trunk-level garment identities. The asymmetry is coherent and imageable. |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is compact and heavily focused on visible garment construction, silhouette, trim, and placement. There is a small amount of styling/mood language (“runway look,” “graphic resort/evenin |
| `craft_embellishment_salience` | 0.75 | 1 | 工艺装饰显著度 | Trim and embellishment are clearly located and visually relevant, but the craft language is more descriptive than technically specific. |
| `design_distinctiveness` | 0.75 | 1 | 设计独特性 | The look has a clear non-formula memory point through the asymmetrical knot-and-sash waist treatment plus graphic black edging/banding, though it is still within a relatively restrained resort/evening |
| `design_signal_purity` | 1.0 | 1 | 设计信号纯度 | The text is dominated by concrete design facts, placement, and construction details, with only a brief concluding mood phrase. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly visual and mostly prompt-ready, with clear garment type, silhouette, color blocking, and key construction details. It is slightly more descriptive than a direct generation prompt, b |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description generally follows a natural body-to-detail progression from overall silhouette to bodice, waist, skirt, and finishing accents. There is some compression and a few later insertions (med |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text describes one main garment with added structural details and footwear; the attributes are mostly assigned to the correct item. There is slight complexity from layered waist/hip elements, but  |
| `quantity_accuracy` | 0.75 | 1 | 语言清晰度 | Quantity and side references are mostly clear and internally consistent, with only mild complexity from multiple repeated descriptors and layered details. |
| `reference_clarity` | 0.75 | 1 | 语言清晰度 | Pronouns and omitted subjects are easy to resolve, and the spatial references remain coherent; the description is dense but not ambiguous. |
| `silhouette_combination_originality` | 0.75 | 1 | 组合原创性 | The silhouette is coherent and somewhat unusual due to the asymmetrical waist and slit, though the base dress form remains fairly accessible and not highly unpredictable. |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and attachment positions are clearly described, and the waist/hip/slit relationships are visually reconstructable. Minor complexity remains, but the spatial logic is coherent. |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | The text prioritizes highly visible, image-dominant features such as neckline, waist knot, slit, and hem treatment. It includes a mild mood cue, but hidden or low-visibility details are not overemphas |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly anchored in visible garment zones and spatial relations, with precise placement cues and little mood-only prose. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | The asymmetry is coherent within one dress design; no trunk-level left-right contradiction or conflicting garment identities. |
| `coordination_penalty` | 0.0 | The styling language is unified and graphic, with no major coordination clash across the main garment and footwear. |
| `formula_template_penalty` | 0.25 | Some resort/evening formula language is present, but the description remains fairly specific and craft-grounded rather than fully interchangeable. |
| `generation_content_penalty` | 0.25 | Mostly grounded garment description, but includes some styling/mood framing and a weak footwear mention that adds little imaging value. |
| `rationality_penalty` | 0.0 | All described construction details are physically plausible for a dress and do not rely on unrealistic materials or impossible wear conditions. |

## Missing coverage (未覆盖)

- **`footwear`** — Footwear is mentioned, but only as a vague glimpse; the text does not specify shoe type, shape, heel/boot structure, or material/finish.
- **`jewelry`** — Jewelry is referenced only as minimal/visible absence, not as a salient ornament with identifiable details.

## Skipped metrics (不适用)

- `fabric_family` (coverage_score) — The text describes color, cut, and drape, but does not clearly identify the main fabric family.
- `pattern_type` (coverage_score) — No pattern or print is described; the look is defined by solid color blocking and trim.
- `construction_technique` (coverage_score) — No specific fabrication technique like pleating, quilting, embroidery, or engineered cutwork is clearly named.
- `deconstruction` (coverage_score) — The text does not explicitly mention deconstruction, splicing, displacement, or reconstruction.
- `bag` (coverage_score) — No bag is described or implied as a visible styling element.
- `belt` (coverage_score) — The waist detail is a tied sash/knot integrated into the dress, not a separate visible belt or waist accessory.
- `cultural_reference` (bonus_score) — No clear cultural, historical, or brand reference is provided.
- `gender_expression` (bonus_score) — The description does not explicitly discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is stated.
- `brand_alignment` (bonus_score) — The text does not explicitly target brand language or identity.
