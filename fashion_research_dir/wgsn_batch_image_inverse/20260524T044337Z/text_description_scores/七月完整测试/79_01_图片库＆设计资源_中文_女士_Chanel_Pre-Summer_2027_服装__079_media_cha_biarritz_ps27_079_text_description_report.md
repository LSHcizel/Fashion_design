# Text Evaluation Report

- **Source:** 79_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__079_media_cha_biarritz_ps27_079_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.8045 (Strong)
- **Coverage axis:** 0.9333
- **Quality axis (raw / base / penalized):** 0.7692 / 0.7708 / 0.7708
- **Penalties (mean):** 0.1
- **R_content:** 0.776342

## Gates

- Score gate: 0.8045 (threshold 0.7) → **PASS**
- Penalty gate: 0.1 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `body_coverage` | 1.0 | 1 |  | The text describes both exposure at the neckline and close body coverage through the torso and hips. |
| `color_relationship_logic` | 1.0 | 1 |  | The text gives a clear multi-tone palette and explains its relationship as an all-over mosaic with silvery accents over the aqua-toned base. |
| `construction_technique` | 1.0 | 1 |  | The text clearly identifies an embellishment technique and its placement across the dress body. |
| `fabric_family` | 0.0 | 0 |  | The text describes surface embellishment but does not clearly identify the underlying fabric family of the dress. |
| `garment_category` | 1.0 | 1 |  | The main garment is explicitly identified as a gown/dress. |
| `hardware_embellishment` | 1.0 | 1 |  | Sequins/paillettes are a clear decorative hardware-like embellishment and are prominently described. |
| `jewelry` | 1.0 | 1 |  | A salient jewelry item is explicitly present and visible. |
| `length_hemline` | 1.0 | 1 |  | Length and hem behavior are explicitly stated. |
| `pattern_type` | 1.0 | 1 |  | The embellishment pattern is identifiable as an irregular mosaic made from sequins/paillettes. |
| `primary_color` | 1.0 | 1 |  | The dominant color family is clearly aqua/turquoise/mint with silvery accents. |
| `secondary_color` | 1.0 | 1 |  | A secondary silvery tone is explicitly present alongside the main aqua-green palette. |
| `shoulder_architecture` | 1.0 | 1 |  | Shoulder/strap structure is clearly specified. |
| `silhouette` | 1.0 | 1 |  | The text clearly describes the overall shape as a column silhouette with a long, lean line. |
| `surface_finish` | 1.0 | 1 |  | The surface finish is clearly described as glossy and reflective. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes the overall vertical proportion and silhouette balance of the gown. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are clearly bound to the gown and its visible surface, with color, fit, neckline, and hem all attached to the dress. The only slight ambiguity is the small projecting detail, which is  |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is mostly garment-focused and imageable, with clear silhouette, surface, and hem details. There is some mood framing, but it does not dominate or become essay-like. |
| `craft_embellishment_salience` | 0.75 | 1 | 工艺装饰显著度 | The embellishment is clearly identified by type, coverage, and visual effect, though the craft language is still somewhat broad rather than highly technical. |
| `design_distinctiveness` | 0.75 | 1 | 设计独特性 | The look has a clear non-formula memory point through the allover sequined mosaic surface and puddled hem, which gives it a distinct visual identity beyond a standard column gown. |
| `design_signal_purity` | 0.75 | 1 | 设计信号纯度 | Design facts dominate the text, and the mood language is limited to a brief closing phrase, so the signal remains mostly pure. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly imageable and already close to a generation prompt, with clear garment type, silhouette, surface treatment, and styling. It is slightly more descriptive than prompt-optimized, but s |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description moves from overall garment type to construction details, then silhouette, hem behavior, and styling/accessories in a mostly natural order. It is clear and easy to reconstruct, with onl |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text includes multiple entities, but their attributes are mostly kept separate and correctly assigned: dress details stay with the gown, while earrings and hair are treated as styling. There is mi |
| `reference_clarity` | 0.75 | 1 | 语言清晰度 | References are mostly clear and the garment description is easy to follow. The only slight ambiguity is the partially unseen side/back accent, but it does not materially hinder understanding. |
| `silhouette_combination_originality` | 0.75 | 1 | 组合原创性 | The silhouette is coherent and elegant, with a strong column shape and puddled hem, but it remains within a recognizable formal gown framework rather than a highly unexpected combination. |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Spatial relations are mostly clear and visually coherent, including garment continuity, hem behavior, and a partially seen side/back accent. The only limitation is that the projecting detail is not fu |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | Visible, dominant garment features are prioritized over hidden or low-visibility details. The small shoulder-side accent is noted cautiously, and the mood language is brief rather than distracting. |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly anchored in visible garment facts and body zones, with clear distinctions between seen and unseen details. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | The gown reads as a single coherent silhouette with no trunk-level left-right or garment-identity conflict. |
| `coordination_penalty` | 0.0 | Accessories and styling are compatible with the dress; no trunk-level coordination conflict is present. |
| `formula_template_penalty` | 0.25 | Some runway-essay framing and mood language are present, but the description remains fairly specific and craft-grounded rather than fully formulaic. |
| `generation_content_penalty` | 0.25 | Mostly grounded garment description, but it includes some mood/framing language that slightly dilutes the imaging trunk. |
| `rationality_penalty` | 0.0 | The materials and construction are physically plausible for a runway gown. |

## Missing coverage (未覆盖)

- **`fabric_family`** — The text describes surface embellishment but does not clearly identify the underlying fabric family of the dress.

## Skipped metrics (不适用)

- `closure` (coverage_score) — No explicit closure mechanism is mentioned.
- `functional_detail` (coverage_score) — No pockets, straps, or utility features are described as functional details.
- `deconstruction` (coverage_score) — No deconstruction, splicing, displacement, or reconstruction is explicitly described.
- `bag` (coverage_score) — No bag is described or visually emphasized.
- `footwear` (coverage_score) — Footwear is explicitly not shown and not a styling focus.
- `belt` (coverage_score) — No visible belt, sash, or waist strap is mentioned.
- `layering` (coverage_score) — The look is described as a single gown, not a layered outfit.
- `asymmetry` (coverage_score) — No clear asymmetrical garment structure is described; the small projecting detail is not enough to establish asymmetry.
- `cross_garment_binding` (coverage_score) — Only one main garment is described, so there is no multi-item relation to bind.
- `quantity_accuracy` (quality_score) — No explicit numbers, counts, or quantity relations are used in the text.
- `bilateral_coherence` (quality_score) — No explicit left-right or bilateral garment differences are described.
- `cultural_reference` (bonus_score) — No cultural, historical, or brand reference is provided.
- `gender_expression` (bonus_score) — The text does not discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is stated beyond general mood.
- `brand_alignment` (bonus_score) — No brand language or brand identity is mentioned.
