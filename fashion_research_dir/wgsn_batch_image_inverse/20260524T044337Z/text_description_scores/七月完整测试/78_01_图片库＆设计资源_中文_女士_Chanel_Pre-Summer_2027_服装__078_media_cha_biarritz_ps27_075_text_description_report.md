# Text Evaluation Report

- **Source:** 78_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__078_media_cha_biarritz_ps27_075_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.7903 (Strong)
- **Coverage axis:** 0.95
- **Quality axis (raw / base / penalized):** 0.75 / 0.75 / 0.75
- **Penalties (mean):** 0.3
- **R_content:** 0.707318

## Gates

- Score gate: 0.7903 (threshold 0.7) → **PASS**
- Penalty gate: 0.3 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `asymmetry` | 1.0 | 1 |  | The front-split trailing layer introduces an uneven, asymmetrical structure that is explicitly described. |
| `bag` | 1.0 | 1 |  | Bag is clearly present with category, shape, and finish/hardware described. |
| `body_coverage` | 1.0 | 1 |  | The text describes a visible front opening and a long trailing underlayer, which clearly indicate coverage and reveal. |
| `closure` | 1.0 | 1 |  | A clear buttoned front opening is described, so the closure detail is explicitly covered. |
| `color_relationship_logic` | 1.0 | 1 |  | The palette is described as a dark base with lighter flecks and metallic accents, plus a contrasting black printed underlayer, giving a clear multi-tone color relationship. |
| `construction_technique` | 0.0 | 0 |  | The text describes texture and fraying, but not a clearly named construction technique with a specific garment zone as required. |
| `cross_garment_binding` | 1.0 | 1 |  | The description clearly distinguishes which attributes belong to the jacket/top, skirt, underlayer, and accessories, showing cross-garment attribution. |
| `fabric_family` | 1.0 | 1 |  | The main fabric family is clearly identified as tweed, with bouclé texture reinforcing the material category. |
| `footwear` | 1.0 | 1 |  | Footwear type and key form/finish details are explicitly covered. |
| `functional_detail` | 1.0 | 1 |  | Pocket-flap areas are a functional garment detail and are directly mentioned. |
| `garment_category` | 1.0 | 1 |  | The text clearly identifies the main garment category as a tweed ensemble / skirt suit. |
| `hardware_embellishment` | 1.0 | 1 |  | Multiple prominent metal embellishments are clearly described on the garment. |
| `layering` | 1.0 | 1 |  | The text clearly describes a layered relationship between the skirt and a trailing underlayer, with readable front/back and overlap order. |
| `length_hemline` | 1.0 | 1 |  | The text gives clear length and hemline information for both the jacket/top and skirt. |
| `pattern_type` | 1.0 | 1 |  | The text clearly specifies pattern types: floral motifs and logo-like emblems. |
| `primary_color` | 1.0 | 1 |  | The dominant color is clearly dark charcoal-black / black. |
| `secondary_color` | 1.0 | 1 |  | Secondary accent colors are explicitly present as grey, white, and gold/metallic details against the dark base. |
| `silhouette` | 1.0 | 1 |  | It explicitly describes the overall shape as boxy on top and slim pencil-skirt below, with a compact suit silhouette. |
| `surface_finish` | 1.0 | 1 |  | The text clearly describes surface qualities: dense bouclé, rough texture, and frayed finish. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes the upper-to-lower silhouette balance and waist placement, including a cropped top, high-waisted skirt, and a trailing lower layer. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are bound to the correct entities, with clear separation between jacket/top, skirt, clutch, and shoes. Minor ambiguity remains in phrases like “jacket or top” and “long black fluid pan |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is dense with visible garment facts and construction details, with only a small amount of interpretive framing. It stays mostly focused on the outfit rather than essay-like mood prose. |
| `craft_embellishment_salience` | 0.75 | 1 | 工艺装饰显著度 | Craft and embellishment are clearly tied to specific zones and visual effect, especially the hardware placement and raw frayed edges. The description is strong, though not fully technical in construct |
| `design_distinctiveness` | 0.75 | 1 | 设计独特性 | The look has multiple non-formula memory points: textured tweed/bouclé, frayed cuffs, gold-tone hardware, and a dramatic printed trailing underlayer. It is distinctive without relying on brand symbols |
| `design_signal_purity` | 0.75 | 1 | 设计信号纯度 | The text is dominated by concrete design facts, materials, placement, and layering. The final styling sentence adds some interpretive framing, but it does not overwhelm the garment description. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly visual and mostly prompt-ready, with clear garment types, silhouette, materials, and styling. It is slightly less than perfect because it uses some interpretive phrasing like “appea |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description generally follows a clear subject-to-detail order: overall look, top, skirt, layered panel, then accessories and footwear. There is some compression and a few long, information-dense s |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text keeps most multi-item relations coherent: the tweed jacket/top matches the skirt, the trailing panel is clearly positioned behind/beneath the skirt, and accessories are separately identified. |
| `quantity_accuracy` | 0.75 | 1 | 语言清晰度 | The text uses a few quantity-like descriptors and alternatives, but they remain mostly coherent. There is some mild ambiguity from paired options like “buttons or eyelet-like hardware” and “flats or s |
| `reference_clarity` | 0.75 | 1 | 语言清晰度 | Pronoun and referent tracking is generally clear: the jacket/top, skirt, and trailing underlayer are introduced in sequence and then referenced consistently. Minor ambiguity exists in phrases like “ap |
| `silhouette_combination_originality` | 0.75 | 1 | 组合原创性 | The combination is more unusual than a standard cropped-jacket-and-skirt formula because of the trailing split underlayer and the contrast between tailored tweed and fluid panel. Still, the core suit  |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and front/back relationships are clearly described and visually imageable. The structure is coherent overall, though the phrasing leaves some ambiguity about whether the trailing panel is a s |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | The text prioritizes clearly visible, image-dominant clothing elements and accessories. There is some interpretive language, but it does not overwhelm the concrete visual description. |
| `visual_observation_grounding` | 0.75 | 1 | 视觉观察 grounded | The description is strongly anchored in visible garment parts and placement, with clear layering and hem details. There is some interpretive phrasing, but the observation remains mostly runway-caption |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.25 | The main suit is coherent, but the trailing underlayer introduces a second garment identity that is not fully integrated into the skirt-suit silhouette. |
| `coordination_penalty` | 0.25 | Overall styling is mostly aligned, but the dress-like trailing layer and embellished flats slightly shift the look away from the tailored tweed suit language. |
| `formula_template_penalty` | 0.5 | The look follows a predictable suit-plus-accessories template and is somewhat diluted by runway commentary and symbol stacking, though it is not fully generic. |
| `generation_content_penalty` | 0.5 | The description is fairly imageable, but it spends notable space on evaluative runway prose and repeated decorative inventory, which dilutes the prompt trunk. |
| `rationality_penalty` | 0.0 | The materials and construction are unusual but still physically plausible as fashion design. |

## Missing coverage (未覆盖)

- **`construction_technique`** — The text describes texture and fraying, but not a clearly named construction technique with a specific garment zone as required.

## Skipped metrics (不适用)

- `shoulder_architecture` (coverage_score) — No prominent shoulder construction is described.
- `deconstruction` (coverage_score) — No explicit deconstruction, splicing, displacement, or reconstruction is stated.
- `jewelry` (coverage_score) — No salient jewelry or body ornament is described; the gold details are on garments/accessories, not worn jewelry.
- `belt` (coverage_score) — No visible belt, sash, waist strap, or harness is mentioned; waist emphasis comes from garment cut and silhouette only.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral distinction is described.
- `cultural_reference` (bonus_score) — No clear cultural, historical, or brand grounding is provided.
- `gender_expression` (bonus_score) — The description does not explicitly discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is explicitly stated beyond garment description.
- `brand_alignment` (bonus_score) — No explicit brand language or brand identity target is mentioned.
- `negation_control` (bonus_score) — The text does not emphasize exclusions or absences that require negation control.
