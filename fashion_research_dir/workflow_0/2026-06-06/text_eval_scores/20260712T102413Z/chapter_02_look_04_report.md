# Text Evaluation Report

- **Source:** look_04.txt
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.0
- **Total score (S_fp):** 0.709 (Usable)
- **Coverage axis:** 1.0
- **Quality axis (raw / base / penalized):** 0.7167 / 0.6385 / 0.6385
- **Penalties (mean):** 0.15
- **R_content:** 0.671777

## Gates

- Score gate: 0.709 (threshold 0.7) → **PASS**
- Penalty gate: 0.15 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `belt` | 1.0 | 1 |  | A visible waist belt is explicitly described, including its material relation to the dress and how it is worn. |
| `body_coverage` | 1.0 | 1 |  | The text clearly describes layered coverage and partial body reveal. |
| `closure` | 1.0 | 1 |  | The text clearly describes button closure and a tie belt as functional opening/closing details. |
| `color_relationship_logic` | 1.0 | 1 |  | The text explains the color relationship through striped contrast and a dark-underlayer vs striped-overlayer counterpoint. |
| `construction_technique` | 1.0 | 1 |  | A specific construction technique is named and located on the garment, with topstitching on the cuffs and side seams and interfacing in the belt. |
| `cross_garment_binding` | 1.0 | 1 |  | Multiple garments are present and the text clearly distinguishes which attributes belong to the shirt-dress, swim base layer, and sandals. |
| `fabric_family` | 1.0 | 1 |  | The text clearly names the main material families for the garments and footwear. |
| `footwear` | 1.0 | 1 |  | Footwear is clearly specified with type, shape, and color/material details. |
| `functional_detail` | 1.0 | 1 |  | It includes functional garment details such as adjustable sleeves, a self-belt, and wearability options. |
| `garment_category` | 1.0 | 1 |  | The text explicitly names the main garment categories. |
| `layering` | 1.0 | 1 |  | The text clearly describes a layered outfit with explicit over/under relationships and visible reveal points. |
| `length_hemline` | 1.0 | 1 |  | Garment length and hem placement are explicitly stated. |
| `pattern_type` | 1.0 | 1 |  | The pattern type is explicitly identified as stripes. |
| `primary_color` | 1.0 | 1 |  | The dominant palette is clearly stated, with navy as the main color and white as the paired stripe color. |
| `secondary_color` | 1.0 | 1 |  | A clear secondary color is present alongside the primary color, and the sandals also introduce a secondary color option. |
| `shoulder_architecture` | 1.0 | 1 |  | Shoulder construction is clearly specified. |
| `silhouette` | 1.0 | 1 |  | Overall shape and structural contour are clearly described. |
| `surface_finish` | 1.0 | 1 |  | It specifies surface/hand-feel traits including crispness, matte finish, and structured drape. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes vertical proportion and silhouette balance from upper body to hem. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are bound to the correct garments and layers, including the belt, shirt-dress, swim bodysuit, and sandals. Minor ambiguity remains in a few layered descriptions like the belt interacti |
| `core_information_density` | 0.25 | 0 | 信息密度与简洁性 | The description is rich in fashion detail, but it is heavily padded with narrative framing and interpretive language. The core garments are clear, yet the repeated mood-setting and explanatory prose d |
| `craft_embellishment_salience` | 0.75 | 1 | 工艺装饰显著度 | Craft and finish details are clearly located and tied to visual effect, especially the buttons, topstitching, and belt construction. They are supportive rather than the sole main hook, so not a perfec |
| `design_distinctiveness` | 0.75 | 1 | 设计独特性 | The look has a clear memory point in the shirt-dress over swimsuit bodysuit layering, with a crisp striped shirting shell and disciplined swim underlayer. It is distinctive enough to separate from a g |
| `design_signal_purity` | 0.5 | 0 | 设计信号纯度 | There is substantial concrete design information, but it is repeatedly interwoven with mood and narrative language about transition, ease, and identity. The design signal is strong, though not maximal |
| `fine_grained_attribute_usage` | 1.0 | 1 | 术语具体度 | Color, material, construction, and silhouette details are consistently fine-grained and visually precise, supporting strong imageability. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly visual, garment-specific, and already organized as a complete look with clear layering and styling cues, so it is close to prompt-ready. It is still somewhat explanatory and narrati |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description is organized from main garment to underlayer to finishing accessories, so the overall structure is easy to reconstruct. There is some repetition and layered elaboration within each par |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text clearly distinguishes multiple garments and keeps their attributes mostly attached to the correct item. The layering relationship is coherent, with only slight cross-layer complexity from the |
| `reference_clarity` | 1.0 | 1 | 语言清晰度 | References and pronouns are consistently anchored to clear antecedents, and the garment layering remains easy to track throughout. |
| `silhouette_combination_originality` | 0.5 | 0 | 组合原创性 | The combination is coherent and polished, but it remains a fairly legible resort template: striped shirt-dress, swim base, belt, flat sandals. The layering adds interest, yet the overall formula is st |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and attachment relations are clear and imageable, with coherent inside/outside and over/under structure. The description is slightly verbose and interpretive, but the spatial logic remains ea |
| `specific_noun_usage` | 1.0 | 1 | 术语具体度 | Uses highly specific garment and accessory nouns throughout, with clear fashion semantics and little reliance on generic wording. |
| `visibility_priority` | 0.25 | 0 | 信息密度与简洁性 | Visible garment details are present, but a substantial portion of the text focuses on hidden function, lifestyle transition, and abstract mood rather than strictly image-dominant features. This weaken |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly anchored in visible garment parts and readable layering, with multiple concrete placement cues and clear visible/invisible distinctions. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | The trunk garments and footwear are coherent; no left-right or mutually exclusive main-garment conflicts are present. |
| `coordination_penalty` | 0.0 | The palette and styling language are aligned across layers, with no major trunk-level clash between outer layer, base layer, and shoes. |
| `formula_template_penalty` | 0.25 | The text follows a common look-description formula with layered garment-by-garment exposition and repeated mood/transition phrasing, though it is not heavily templated. |
| `generation_content_penalty` | 0.5 | The description spends substantial space on conceptual/runway-style framing and mood language, which reduces prompt efficiency compared with purely imageable garment facts. |
| `rationality_penalty` | 0.0 | The materials and construction are physically plausible and read as ordinary wearable fashion. |

## Quality issues (质量短板)

- **`core_information_density`** (score 0.25) — The description is rich in fashion detail, but it is heavily padded with narrative framing and interpretive language. The core garments are clear, yet the repeated mood-setting and explanatory prose dilute prompt efficiency.
- **`visibility_priority`** (score 0.25) — Visible garment details are present, but a substantial portion of the text focuses on hidden function, lifestyle transition, and abstract mood rather than strictly image-dominant features. This weakens visibility priority for prompt use.
- **`silhouette_combination_originality`** (score 0.5) — The combination is coherent and polished, but it remains a fairly legible resort template: striped shirt-dress, swim base, belt, flat sandals. The layering adds interest, yet the overall formula is still predictable.
- **`design_signal_purity`** (score 0.5) — There is substantial concrete design information, but it is repeatedly interwoven with mood and narrative language about transition, ease, and identity. The design signal is strong, though not maximally pure.

## Skipped metrics (不适用)

- `deconstruction` (coverage_score) — The text describes layered styling and openness, but does not explicitly mention deconstruction, splicing, displacement, or reconstruction as a design method.
- `hardware_embellishment` (coverage_score) — No salient hardware or decorative embellishment such as chains, studs, rings, or crystals is described.
- `bag` (coverage_score) — No bag is described or implied as part of the look.
- `jewelry` (coverage_score) — No jewelry or body ornament is explicitly present.
- `asymmetry` (coverage_score) — No asymmetrical design, one-shoulder, single-sleeve, or uneven structure is described.
- `quantity_accuracy` (quality_score) — The text contains no explicit counts, numerals, or quantity relations that require quantity accuracy judgment.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral asymmetry is described.
- `gender_expression` (bonus_score) — No explicit gender expression or androgyny is mentioned.
