# Text Evaluation Report

- **Source:** 76_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__076_media_cha_biarritz_ps27_076_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.8321 (Strong)
- **Coverage axis:** 0.95
- **Quality axis (raw / base / penalized):** 0.7857 / 0.8021 / 0.8021
- **Penalties (mean):** 0.2
- **R_content:** 0.773853

## Gates

- Score gate: 0.8321 (threshold 0.7) → **PASS**
- Penalty gate: 0.2 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `asymmetry` | 1.0 | 1 |  | Asymmetry is explicitly stated and reinforced by uneven panels and a one-sided trailing element. |
| `body_coverage` | 1.0 | 1 |  | The text clearly describes major exposure zones, especially the deep neckline and exposed feet. |
| `closure` | 1.0 | 1 |  | A clear tie closure is explicitly described at the waist/front. |
| `color_relationship_logic` | 1.0 | 1 |  | The text clearly explains the color relationship: a black base with multicolor floral print layered over it. |
| `construction_technique` | 1.0 | 1 |  | The text identifies a specific construction treatment—clustered trim/embellishment—located around the neckline and bodice, along with structured draping at the waist. |
| `cross_garment_binding` | 1.0 | 1 |  | The description distinguishes multiple garment layers and their relationships, making it clear which attributes belong to the upper piece, lower layer, and overlaid panels. |
| `deconstruction` | 1.0 | 1 |  | Deconstruction is explicitly stated and reinforced by the uneven layered panels. |
| `footwear` | 0.0 | 0 |  | Footwear is only vaguely suggested; the text does not clearly specify a shoe family plus functional form and material/finish. |
| `garment_category` | 1.0 | 1 |  | The text clearly identifies the main garment as a full-length runway look with an upper garment and a lower culotte-like section. |
| `hardware_embellishment` | 1.0 | 1 |  | A noticeable decorative hardware-like embellishment is directly described around the neckline. |
| `jewelry` | 1.0 | 1 |  | Visible jewelry/body ornament is explicitly present and salient. |
| `layering` | 1.0 | 1 |  | The look clearly uses multiple visible layers with readable overlap and coverage relationships. |
| `length_hemline` | 1.0 | 1 |  | The description gives clear garment length and hemline information. |
| `pattern_type` | 1.0 | 1 |  | The pattern type is clearly identified as floral/painterly floral print. |
| `primary_color` | 1.0 | 1 |  | Black is clearly established as the dominant base color. |
| `secondary_color` | 1.0 | 1 |  | Multiple secondary colors are explicitly present as the floral motif and trim accents against the black ground. |
| `shoulder_architecture` | 1.0 | 1 |  | Shoulder structure is explicitly emphasized and visually salient. |
| `silhouette` | 1.0 | 1 |  | Overall shape and structural contour are explicitly described. |
| `surface_finish` | 1.0 | 1 |  | Surface behavior is clearly described through drape and layered volume, which is sufficient for this metric. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes the upper-to-lower silhouette relationship, including waist emphasis and a distinct lower section length, so proportion is salient. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are bound to the correct garment parts, and the text distinguishes upper garment from lower section clearly. There is some mild ambiguity in phrases like “lower section or wide culotte |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is mostly packed with visible garment facts and spatial structure, with only a brief mood wrap-up. There is some redundancy and stylistic framing, but the core fashion information rema |
| `craft_embellishment_salience` | 0.75 | 1 | 工艺装饰显著度 | Craft details are clearly present and located, but the embellishment is described somewhat tentatively rather than as a fully specified technique. |
| `design_distinctiveness` | 1.0 | 1 | 设计独特性 | The look has multiple strong memory points: bold painterly print, extreme plunge, oversized front knot, and sculptural asymmetrical layered drapery. |
| `design_signal_purity` | 0.75 | 1 | 设计信号纯度 | Design facts dominate, but there is a noticeable amount of mood framing in the closing sentence, slightly diluting pure garment description. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly visual and mostly prompt-ready, with clear garment type, silhouette, layering, and surface detail. It is slightly less direct than a pure generation prompt because it includes expla |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a mostly natural top-to-bottom and main-to-detail order, making the garment structure easy to reconstruct. There is some compression and a few dense, layered clauses, but the o |
| `multi_garment_binding` | 0.5 | 0 | 属性绑定准确度 | The description includes multiple garment layers and mostly keeps them organized, but some relations are somewhat blurred, especially around whether the lower look is a skirt, culotte layer, or oversk |
| `quantity_accuracy` | 0.75 | 1 | 语言清晰度 | The text uses several quantity-like relations and lists, but they remain mostly coherent. There is some mild ambiguity in alternatives such as “foot jewelry or very fine sandals,” yet no serious confl |
| `reference_clarity` | 0.75 | 1 | 语言清晰度 | References and transitions are generally clear, with the garment progression easy to follow. A few phrases are slightly dense or compound, but pronouns and omitted subjects do not create major confusi |
| `silhouette_combination_originality` | 1.0 | 1 | 组合原创性 | The combination is highly specific and unconventional, mixing a plunging evening top with wrapped drapery, asymmetrical overskirt-like layers, and culotte-like volume. |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | The layering and attachment logic is mostly clear and imageable, especially around the front knot, overskirt, and trailing panel. Minor ambiguity remains in the exact relationship between the midi-len |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | The text prioritizes highly visible silhouette, drape, and surface-print details that strongly affect image generation. Minor mood language appears at the end, but it does not overwhelm the visible ga |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly anchored to visible garment parts and placement, with clear observation of neckline, waist drape, hem layers, and side projections. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.25 | There is mild ambiguity in the lower-body identity (midi skirt-like section vs culotte-style layer), but no strong trunk-level contradiction. |
| `coordination_penalty` | 0.25 | The look is intentionally deconstructed and asymmetrical, but the overall styling remains coherent rather than sharply conflicting. |
| `formula_template_penalty` | 0.25 | Some runway-essay framing and mood language is present, but the description still contains specific design facts and craft details. |
| `generation_content_penalty` | 0.25 | Mostly grounded garment description, but the closing mood framing adds some essay-like redundancy. |
| `rationality_penalty` | 0.0 | No clearly implausible material or construction claims; the described elements are wearable in fashion context. |

## Missing coverage (未覆盖)

- **`footwear`** — Footwear is only vaguely suggested; the text does not clearly specify a shoe family plus functional form and material/finish.

## Quality issues (质量短板)

- **`multi_garment_binding`** (score 0.5) — The description includes multiple garment layers and mostly keeps them organized, but some relations are somewhat blurred, especially around whether the lower look is a skirt, culotte layer, or overskirt system. This creates moderate binding ambiguity across garments.

## Skipped metrics (不适用)

- `fabric_family` (coverage_score) — The text describes silhouette, drape, and print, but does not clearly identify a main fabric family such as silk, cotton, chiffon, or knit.
- `functional_detail` (coverage_score) — No pockets, straps, or other functional utility details are clearly mentioned.
- `bag` (coverage_score) — No bag is mentioned or implied as a visible styling element.
- `belt` (coverage_score) — No actual belt, sash, waist strap, or harness is described; the waist emphasis comes from draping and knotting, not a belt accessory.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral distinction is described.
- `cultural_reference` (bonus_score) — No clear cultural, historical, or brand grounding is provided.
- `gender_expression` (bonus_score) — The description does not explicitly discuss gender expression or androgyny.
- `brand_alignment` (bonus_score) — No brand identity or brand-language target is mentioned.
- `negation_control` (bonus_score) — The text does not emphasize exclusions or absence of elements.
