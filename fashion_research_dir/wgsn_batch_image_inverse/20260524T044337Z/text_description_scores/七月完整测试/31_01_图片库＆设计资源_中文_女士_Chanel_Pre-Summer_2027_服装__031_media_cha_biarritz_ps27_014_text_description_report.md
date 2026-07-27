# Text Evaluation Report

- **Source:** 31_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__031_media_cha_biarritz_ps27_014_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.8569 (Strong)
- **Coverage axis:** 0.9444
- **Quality axis (raw / base / penalized):** 0.8269 / 0.8333 / 0.8333
- **Penalties (mean):** 0.1
- **R_content:** 0.826908

## Gates

- Score gate: 0.8569 (threshold 0.7) → **PASS**
- Penalty gate: 0.1 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `body_coverage` | 1.0 | 1 |  | The text includes clear exposure/coverage information, especially the mostly bare feet. |
| `color_relationship_logic` | 1.0 | 1 |  | The text explains the color logic as a strong contrast between top and skirt, with patterned black motifs over a cream base. |
| `construction_technique` | 1.0 | 1 |  | The text names specific construction/craft techniques and their placement on the skirt. |
| `cross_garment_binding` | 1.0 | 1 |  | Multiple garments are present and the description distinguishes their roles and attributes across the outfit, clearly binding properties to the top, skirt, and footwear separately. |
| `fabric_family` | 1.0 | 1 |  | The text clearly identifies the main fabric family as knit for the top and implies a textile/fringed skirt construction. |
| `footwear` | 1.0 | 1 |  | The text clearly identifies the footwear type and functional form, with color/material-like styling cues. |
| `functional_detail` | 1.0 | 1 |  | A functional pocket/opening is explicitly described. |
| `garment_category` | 1.0 | 1 |  | The text clearly identifies the main garment categories: top, skirt, and sandals. |
| `hardware_embellishment` | 0.0 | 0 |  | Jewelry is mentioned, but not the kind of salient hardware/embellishment specified by the metric. |
| `jewelry` | 1.0 | 1 |  | A visible wrist accessory is explicitly mentioned. |
| `layering` | 1.0 | 1 |  | The outfit includes clear garment and trim layering with readable top-over-skirt and fringe-over-fringe relations. |
| `length_hemline` | 1.0 | 1 |  | The text gives clear hem and length information for both the top and skirt. |
| `pattern_type` | 1.0 | 1 |  | It clearly names the pattern types: stripes on the top and abstract vertical motifs on the skirt. |
| `primary_color` | 1.0 | 1 |  | The dominant palette is clearly stated, with black and cream-white as the main visible colors. |
| `secondary_color` | 1.0 | 1 |  | Secondary accent colors are explicitly described and visually anchored to the outfit. |
| `silhouette` | 1.0 | 1 |  | It explicitly describes the overall shape and structural contour of the outfit, especially the skirt silhouette. |
| `surface_finish` | 1.0 | 1 |  | It gives clear surface/handling cues: soft drape, gathered volume, and a textured fringe finish. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly states the waist placement and the relative balance between the fitted/loose top and the voluminous skirt, so the top-bottom proportion is explicitly covered. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are clearly attached to the correct garment or accessory. Minor ambiguity remains in phrases like “printed or appliquéd” and “side pocket or pocket-like opening,” but these do not seri |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description stays mostly on visible garment facts and imageable construction details, with only a brief mood phrase at the end. It is somewhat verbose, but not essay-like and the main outfit infor |
| `craft_embellishment_salience` | 1.0 | 1 | 工艺装饰显著度 | Craft details are explicit, well located, and visually central: fringe trim at the hem and appliqué/print-like motifs across the skirt panels. The text clearly explains both type and placement. |
| `design_distinctiveness` | 0.75 | 1 | 设计独特性 | The look has multiple clear memory points: striped knit, abstract motif treatment, and layered fringe trim. These are distinctive and craft-like, though not so singular as to feel fully exceptional. |
| `design_signal_purity` | 1.0 | 1 | 设计信号纯度 | The text is dominated by concrete design facts, materials, placement, and silhouette. Mood language is limited to a brief closing phrase and does not dilute the design signal. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is already close to a generation prompt: it clearly names the main garments, silhouette, colors, and key surface details. It is slightly more descriptive than prompt-tight, but still highly u |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description moves in a mostly natural order from top to skirt to accessories/footwear, making the outfit easy to reconstruct. There is some detail compression within the skirt section, but the ove |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text keeps attributes mostly separated by item: top, skirt, footwear, and wrist accessory are each described in place. There is slight uncertainty around the skirt’s surface treatment and pocket w |
| `reference_clarity` | 1.0 | 1 | 语言清晰度 | Pronouns and references are clear and consistently anchored to specific garments or the overall look, with no confusing antecedent shifts. |
| `silhouette_combination_originality` | 0.75 | 1 | 组合原创性 | The combination is more original than a standard resort formula because of the voluminous, fringed skirt paired with a relaxed striped knit and thong-heeled sandals. It still remains broadly wearable  |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and placement are visually coherent and easy to image, with clear top-over-skirt and hand-in-pocket relations. Minor ambiguity remains in “pocket or pocket-like opening,” but overall spatial  |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | The text prioritizes highly visible, composition-defining elements such as silhouette, hem treatment, and footwear. There is a small amount of interpretive mood language, but it does not overwhelm the |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly anchored in visible garment facts and placement, with clear references to hem, waist, silhouette, and skirt treatment. Mood language is minimal and does not overwhelm obser |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | No trunk-level left-right conflict or mutually exclusive garment identities; the look reads as a coherent top-skirt-sandal outfit. |
| `coordination_penalty` | 0.0 | Color and texture contrast are deliberate and cohesive rather than clashing; no severe styling mismatch on trunk garments. |
| `formula_template_penalty` | 0.25 | Contains a mild resort-style framing and a familiar top-plus-skirt formula, but still includes specific craft details like appliqué/print and layered fringe. |
| `generation_content_penalty` | 0.25 | Mostly grounded garment description with one mood-led closing phrase; little redundant or essay-like prose. |
| `rationality_penalty` | 0.0 | All described materials and construction remain physically plausible for ordinary fashion wear. |

## Missing coverage (未覆盖)

- **`hardware_embellishment`** — Jewelry is mentioned, but not the kind of salient hardware/embellishment specified by the metric.

## Skipped metrics (不适用)

- `shoulder_architecture` (coverage_score) — No salient shoulder design is described.
- `closure` (coverage_score) — No salient closure detail is mentioned.
- `deconstruction` (coverage_score) — No deconstruction, splicing, displacement, or reconstruction is explicitly described.
- `bag` (coverage_score) — No bag is described or implied as a visual element of the look.
- `belt` (coverage_score) — No visible belt, sash, waist strap, or harness is described.
- `asymmetry` (coverage_score) — No asymmetrical design, one-shoulder, uneven hem, or similar structure is described.
- `quantity_accuracy` (quality_score) — The text does not use explicit counts or quantity relations that need verification.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral garment differences are described.
- `cultural_reference` (bonus_score) — No clear cultural, historical, or brand reference is provided.
- `gender_expression` (bonus_score) — The description does not explicitly discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is stated.
- `brand_alignment` (bonus_score) — There is no explicit brand language or brand identity target.
- `negation_control` (bonus_score) — The text does not emphasize exclusions or absence of elements.
