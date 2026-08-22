# Text Evaluation Report

- **Source:** look_02.txt
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.1
- **Total score (S_fp):** 0.7289 (Usable)
- **Coverage axis:** 1.0
- **Quality axis (raw / base / penalized):** 0.6833 / 0.6636 / 0.6636
- **Penalties (mean):** 0.1
- **R_content:** 0.703388

## Gates

- Score gate: 0.7289 (threshold 0.7) → **PASS**
- Penalty gate: 0.1 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `belt` | 1.0 | 1 |  | A visible belt is explicitly described with its placement and fastening. |
| `body_coverage` | 1.0 | 1 |  | The text clearly describes visible/revealed body areas and coverage transitions. |
| `closure` | 1.0 | 1 |  | A clear front closure is explicitly described. |
| `color_relationship_logic` | 1.0 | 1 |  | The text explains the color relationship as a coordinated contrast and tonal echo, not just a list of colors. |
| `cross_garment_binding` | 1.0 | 1 |  | Multiple garments are described with clear roles and relations, and the text distinguishes which attributes belong to the jacket, shirt, shorts, belt, and sandals. |
| `fabric_family` | 1.0 | 1 |  | The text clearly names the main fabric families for the key garments. |
| `footwear` | 1.0 | 1 |  | Footwear type and key form/material details are clearly specified. |
| `functional_detail` | 1.0 | 1 |  | Functional garment details are directly mentioned and visually specific. |
| `garment_category` | 1.0 | 1 |  | The text clearly names the main garment categories in the look. |
| `hardware_embellishment` | 1.0 | 1 |  | Visible hardware is salient and clearly described as part of the look. |
| `layering` | 1.0 | 1 |  | The text clearly describes layered relations among jacket, shirt, belt, shorts, and sandals. |
| `length_hemline` | 1.0 | 1 |  | The text gives clear length and hemline information for multiple garments. |
| `pattern_type` | 1.0 | 1 |  | A specific pattern type is clearly identified: stripes. |
| `primary_color` | 1.0 | 1 |  | The dominant palette is clearly established, with navy and white as the main colors. |
| `secondary_color` | 1.0 | 1 |  | There are clear secondary color accents and contrasts supporting the main palette. |
| `shoulder_architecture` | 1.0 | 1 |  | Shoulder design is explicitly described and is visually salient. |
| `silhouette` | 1.0 | 1 |  | It explicitly describes the overall shape and structural contour of the outfit. |
| `surface_finish` | 1.0 | 1 |  | It explicitly describes surface and handling qualities such as structure, drape, polish, and matte finish. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly states the waist position and contrasts a cropped top layer with shorts, establishing top-bottom proportion and silhouette balance. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 1.0 | 1 | 属性绑定准确度 | Attributes are consistently attached to the correct garments and body zones: jacket, shirt, shorts, belt, and sandals are each clearly identified with their own materials and functions, with no confus |
| `core_information_density` | 0.5 | 0 | 信息密度与简洁性 | The description contains substantial concrete garment detail, but repeated mood/transition framing and identity language dilute the prompt efficiency. It is not a four-section template, so the score i |
| `craft_embellishment_salience` | 0.5 | 0 | 工艺装饰显著度 | Craft and construction are present and positioned, but they are described in a fairly generic way rather than as a sharply articulated signature detail with strong visual hierarchy. |
| `design_distinctiveness` | 0.25 | 0 | 设计独特性 | The look is mostly a recognizable cruise-tailoring formula; the Double C is a brand symbol and does not count as a distinct design memory point. Material and proportion details are clear, but the over |
| `design_signal_purity` | 0.25 | 0 | 设计信号纯度 | Design facts are heavily diluted by repeated mood/transition framing and brand-essay language, so the signal is not pure enough for a higher score. |
| `fine_grained_attribute_usage` | 1.0 | 1 | 术语具体度 | Color, fabric, construction, and hardware are described with fine-grained fashion vocabulary and strong visual precision. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly visual, garment-specific, and organized around a coherent single look, so it is close to prompt-ready. It still reads somewhat like polished design prose rather than a direct genera |
| `information_ordering` | 1.0 | 1 | 结构清晰度 | The description is organized from main garment to underlayer, then waist accessories and footwear, making the outfit hierarchy easy to reconstruct. |
| `multi_garment_binding` | 1.0 | 1 | 属性绑定准确度 | Multiple garments are described, but their colors, materials, and structural details remain cleanly assigned to each item, with coherent layering and no notable attribute drift. |
| `reference_clarity` | 1.0 | 1 | 语言清晰度 | References are consistently anchored to clear antecedents, and pronouns/ellipsis do not create ambiguity. The layered garment descriptions remain easy to track throughout. |
| `silhouette_combination_originality` | 0.25 | 0 | 组合原创性 | This is a classic cropped-jacket plus shirt plus tailored short plus belt plus flat sandal resort formula, which the rubric explicitly caps at 0.25. |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering, tuck-in, waist placement, and footwear are clearly described and visually reconstructable. The spatial logic is coherent and imageable, with only minor prose elaboration beyond a direct prom |
| `specific_noun_usage` | 1.0 | 1 | 术语具体度 | Uses highly specific garment names, materials, and accessory terms throughout, creating a clear fashion object. |
| `visibility_priority` | 0.5 | 0 | 信息密度与简洁性 | Visible clothing and silhouette details are generally prioritized, but the text still spends notable space on mood, setting, and identity framing. Hidden or interpretive language does not dominate, ye |
| `visual_observation_grounding` | 0.5 | 0 | 视觉观察 grounded | There are many visible anchors and body-zone references, but the description is repeatedly mixed with mood and identity framing such as salon/daylight/promenade language, which weakens pure observatio |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | The outerwear, shirt, shorts, and sandals read as a coherent single outfit with no trunk-level left-right or material identity conflict. |
| `coordination_penalty` | 0.0 | The styling language is coordinated across layers, with matching tailored, coastal, and polished cues rather than conflicting aesthetics. |
| `formula_template_penalty` | 0.25 | It uses a predictable fashion-description formula with clear section-like progression, but it does not fully hit the stricter fixed-header or bullet-template thresholds. |
| `generation_content_penalty` | 0.25 | The description is mostly grounded, but it repeatedly leans on mood/scene framing and runway-style prose rather than purely image-efficient garment facts. |
| `rationality_penalty` | 0.0 | The materials and construction are physically plausible and consistent with ordinary clothing. |

## Quality issues (质量短板)

- **`core_information_density`** (score 0.5) — The description contains substantial concrete garment detail, but repeated mood/transition framing and identity language dilute the prompt efficiency. It is not a four-section template, so the score is capped by the rubric rather than lower.
- **`visibility_priority`** (score 0.5) — Visible clothing and silhouette details are generally prioritized, but the text still spends notable space on mood, setting, and identity framing. Hidden or interpretive language does not dominate, yet it reduces strict visual priority.
- **`design_distinctiveness`** (score 0.25) — The look is mostly a recognizable cruise-tailoring formula; the Double C is a brand symbol and does not count as a distinct design memory point. Material and proportion details are clear, but the overall combination remains conventional.
- **`visual_observation_grounding`** (score 0.5) — There are many visible anchors and body-zone references, but the description is repeatedly mixed with mood and identity framing such as salon/daylight/promenade language, which weakens pure observational grounding.
- **`craft_embellishment_salience`** (score 0.5) — Craft and construction are present and positioned, but they are described in a fairly generic way rather than as a sharply articulated signature detail with strong visual hierarchy.
- **`silhouette_combination_originality`** (score 0.25) — This is a classic cropped-jacket plus shirt plus tailored short plus belt plus flat sandal resort formula, which the rubric explicitly caps at 0.25.
- **`design_signal_purity`** (score 0.25) — Design facts are heavily diluted by repeated mood/transition framing and brand-essay language, so the signal is not pure enough for a higher score.

## Skipped metrics (不适用)

- `construction_technique` (coverage_score) — No notable named construction technique like quilting, pleating, embroidery, or cut-out architecture is described.
- `deconstruction` (coverage_score) — The text describes tailored layering and contrast, but not deconstruction, splicing, displacement, or reconstruction.
- `bag` (coverage_score) — No bag is described or implied as part of the look.
- `jewelry` (coverage_score) — No jewelry or body ornament is explicitly present.
- `asymmetry` (coverage_score) — No asymmetrical design, one-shoulder, uneven hem, or similar imbalance is described.
- `quantity_accuracy` (quality_score) — The text uses some numeric-like quantity relations implicitly (e.g. 'a second strap'), but there are no problematic counts or conflicting quantity statements to judge.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral garment differences are described.
