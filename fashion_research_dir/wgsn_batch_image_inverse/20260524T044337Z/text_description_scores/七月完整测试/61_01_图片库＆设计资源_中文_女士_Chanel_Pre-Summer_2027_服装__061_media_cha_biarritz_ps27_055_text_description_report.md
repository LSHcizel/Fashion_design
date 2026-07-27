# Text Evaluation Report

- **Source:** 61_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__061_media_cha_biarritz_ps27_055_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.8333 (Strong)
- **Coverage axis:** 0.9545
- **Quality axis (raw / base / penalized):** 0.8036 / 0.8021 / 0.8021
- **Penalties (mean):** 0.1
- **R_content:** 0.804134

## Gates

- Score gate: 0.8333 (threshold 0.7) → **PASS**
- Penalty gate: 0.1 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `asymmetry` | 1.0 | 1 |  | Asymmetry is explicitly stated and reinforced by the irregular hem and side/front tie detail. |
| `bag` | 1.0 | 1 |  | The bag is clearly described by type, carrying method, shape/structure, and hardware/material cues. |
| `body_coverage` | 1.0 | 1 |  | The text explicitly notes visible body exposure through the bare legs and open neckline. |
| `closure` | 1.0 | 1 |  | The dress clearly has an open front opening, which functions as a visible closure/placket detail even though buttons or zippers are not named. |
| `color_relationship_logic` | 1.0 | 1 |  | The text gives a clear color relationship: a pale ground with darker printed elements, establishing a printed-on-base contrast. |
| `construction_technique` | 1.0 | 1 |  | A clear construction technique is described: layered raw-edged ruffle treatment with a specific placement along the collar/front opening and hem. |
| `cross_garment_binding` | 1.0 | 1 |  | The text distinguishes the main dress from separate accessories and clearly assigns attributes to each item. |
| `deconstruction` | 1.0 | 1 |  | The text explicitly states a deconstructed finish, so this metric is directly covered. |
| `fabric_family` | 0.0 | 0 |  | The text describes silhouette, print, and finish, but does not clearly name the main fabric family (e.g. cotton, silk, denim). |
| `functional_detail` | 1.0 | 1 |  | The text describes functional waist details and utility-like elements that read as construction features rather than pure decoration. |
| `garment_category` | 1.0 | 1 |  | The main garment category is explicitly identified as a shirt dress. |
| `hardware_embellishment` | 1.0 | 1 |  | Metal ring/chain hardware is explicitly mentioned and qualifies as salient hardware embellishment. |
| `jewelry` | 1.0 | 1 |  | Salient jewelry is explicitly present and described. |
| `layering` | 1.0 | 1 |  | The text describes visible layered construction and its placement across the garment in a coherent, imageable way. |
| `length_hemline` | 1.0 | 1 |  | Garment length and hemline are explicitly stated. |
| `pattern_type` | 1.0 | 1 |  | The pattern type is clearly identified as a newspaper/collage-style graphic print. |
| `primary_color` | 1.0 | 1 |  | The main color is explicitly stated. |
| `secondary_color` | 1.0 | 1 |  | Black functions as a clear secondary color within the print against the pale grey-green ground. |
| `shoulder_architecture` | 1.0 | 1 |  | Shoulder construction is clearly specified through dropped shoulders and sleeve treatment. |
| `silhouette` | 1.0 | 1 |  | The text clearly describes the overall shape as loose and shirt-like, giving a readable silhouette. |
| `surface_finish` | 1.0 | 1 |  | The description clearly conveys a washed, distressed, raw-edged surface with a relaxed drape-like feel. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes the garment length, waist treatment, and visible lower-body balance, so top-bottom proportion is salient. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are clearly attached to the correct entities, including the dress, its waist treatment, and the handbag. Minor ambiguity remains in phrases like “gathered or tied” and the exact placem |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is mostly packed with visible garment facts and construction details, with only a brief mood wrap-up. It is efficient overall, though slightly verbose in places. |
| `craft_embellishment_salience` | 1.0 | 1 | 工艺装饰显著度 | The craft is clearly specified by type, placement, and visual effect, and it functions as a main hook of the look. |
| `design_distinctiveness` | 0.75 | 1 | 设计独特性 | The look has clear non-formula memory points: an unusual graphic print plus a deconstructed ruffle treatment with diagonal placement and asymmetrical hem. Strongly distinctive, though not quite at the |
| `design_signal_purity` | 0.75 | 1 | 设计信号纯度 | Most of the text is devoted to concrete design facts, with only a brief mood summary at the end. The design signal remains dominant. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly imageable and mostly prompt-ready, with clear garment type, silhouette, surface treatment, and styling. It is slightly less than perfect because it still reads like a descriptive fa |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a mostly natural order from main garment to construction details, then styling/accessories and finishing mood. It is easy to reconstruct the look, though some detail clusters a |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text cleanly separates the main garment from accessories and does not confuse their attributes. There is slight looseness in describing the waist details and styling, but no major cross-garment at |
| `quantity_accuracy` | 0.75 | 1 | 语言清晰度 | The text uses a few quantity-like relations and they are mostly clear and internally consistent. There is no major conflict in counts or side references, though some measurements are approximate rathe |
| `reference_clarity` | 1.0 | 1 | 语言清晰度 | References are stable and easy to track. Pronouns and omitted subjects do not create ambiguity, and each descriptive clause clearly attaches to the dress or styling elements. |
| `silhouette_combination_originality` | 0.75 | 1 | 组合原创性 | The combination is more specific and expressive than a standard formula look, especially with the shirt-dress base plus deconstructed ruffle treatment. Some elements remain familiar, so it is strong b |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and attachment positions are clearly described and visually coherent, making the look easy to reconstruct. Minor uncertainty remains in phrases like “gathered or tied” and the loose handling  |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | The main dress silhouette and surface details are prioritized clearly, and accessories are secondary. There is some mood language, but it does not overwhelm the visible clothing information. |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is tightly anchored to visible garment zones and readable details, with clear separation of what is seen versus what is uncertain, such as the footwear. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | No trunk-level left-right conflict or mutually exclusive garment identities are described; the look reads as one coherent dress silhouette. |
| `coordination_penalty` | 0.0 | Accessories support the dress without creating a conflicting styling language on the main garment or footwear. |
| `formula_template_penalty` | 0.25 | The prompt is fairly grounded, but it uses a somewhat reusable fashion-formula structure centered on silhouette + wash + texture + mood, with limited craft-specific anchors. |
| `generation_content_penalty` | 0.25 | Mostly grounded in a single dress description, but ends with mood-summary language that adds some conceptual framing beyond the visual trunk. |
| `rationality_penalty` | 0.0 | All described materials and construction details are physically plausible for ordinary fashion wear. |

## Missing coverage (未覆盖)

- **`fabric_family`** — The text describes silhouette, print, and finish, but does not clearly name the main fabric family (e.g. cotton, silk, denim).

## Skipped metrics (不适用)

- `footwear` (coverage_score) — Footwear is explicitly not shown, so this metric does not apply.
- `belt` (coverage_score) — No actual belt, sash, waist strap, or harness is described; the waist is only gathered/tied by fabric tabs.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral contrast is described.
- `gender_expression` (bonus_score) — No explicit gender expression or androgyny is mentioned.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative task is stated.
- `brand_alignment` (bonus_score) — No brand language or brand identity target is provided.
