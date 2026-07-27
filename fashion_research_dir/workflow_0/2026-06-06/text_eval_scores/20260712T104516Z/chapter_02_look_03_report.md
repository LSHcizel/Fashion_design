# Text Evaluation Report

- **Source:** look_03.txt
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.1
- **Total score (S_fp):** 0.7463 (Usable)
- **Coverage axis:** 1.0
- **Quality axis (raw / base / penalized):** 0.7344 / 0.6864 / 0.6864
- **Penalties (mean):** 0.15
- **R_content:** 0.707119

## Gates

- Score gate: 0.7463 (threshold 0.7) → **PASS**
- Penalty gate: 0.15 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `belt` | 1.0 | 1 |  | A visible waist belt is explicitly described, including its material and function at the waist. |
| `body_coverage` | 1.0 | 1 |  | The text clearly indicates exposed collarbone and partial coverage by layered garments. |
| `closure` | 1.0 | 1 |  | The text clearly describes the jacket’s button front closure and also mentions a tied belt closure at the waist. |
| `color_relationship_logic` | 1.0 | 1 |  | The text explains the palette as a coordinated marine scheme with clear relationships between base, accents, and linking details. |
| `cross_garment_binding` | 1.0 | 1 |  | The description explicitly distinguishes how details belong to specific garments and how they relate across the outfit, making the multi-garment binding clear. |
| `fabric_family` | 1.0 | 1 |  | The text clearly names the main fabric families for the jacket, trousers, top, and shoes. |
| `footwear` | 1.0 | 1 |  | Footwear is clearly specified with shoe type, heel height, toe shape, and material/finish. |
| `functional_detail` | 1.0 | 1 |  | Multiple functional elements are explicitly described, including pockets and utility strap tabs. |
| `garment_category` | 1.0 | 1 |  | The text clearly names the main garment categories and footwear. |
| `hardware_embellishment` | 1.0 | 1 |  | The text clearly includes notable metal hardware used as visible embellishment. |
| `layering` | 1.0 | 1 |  | The text clearly describes layered garments and their visible order: jacket over top over trousers, with tuck and overlap relations. |
| `length_hemline` | 1.0 | 1 |  | The text gives clear length and hem/cuff information for the jacket and trousers. |
| `primary_color` | 1.0 | 1 |  | The dominant palette is clearly stated, led by navy with supporting neutral tones. |
| `secondary_color` | 1.0 | 1 |  | Distinct secondary colors are present and tied to visible garment details. |
| `shoulder_architecture` | 1.0 | 1 |  | Shoulder structure is explicitly described. |
| `silhouette` | 1.0 | 1 |  | It explicitly describes the overall shape and structural contour of the outfit. |
| `surface_finish` | 1.0 | 1 |  | Multiple surface qualities are explicitly described, including washed, matte, smooth, and glazed finishes. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes the relationship between the cropped jacket and the trouser rise/waistband, establishing top-bottom proportion and visual balance. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are clearly tied to the correct garment or accessory, including the jacket, trousers, belt, and shoes. Minor complexity comes from layered references like lining, cuff flashes, and ove |
| `core_information_density` | 0.5 | 0 | 信息密度与简洁性 | The text contains substantial concrete garment detail, but it is repeatedly wrapped in mood/identity framing and interpretive prose, which reduces prompt efficiency. It is not a four-section template, |
| `craft_embellishment_salience` | 0.75 | 1 | 工艺装饰显著度 | Craft details are clearly identified by type and placement, and they contribute meaningfully to the look. The description is still somewhat broad in places, but the main construction accents are legib |
| `design_distinctiveness` | 0.75 | 1 | 设计独特性 | The look has several concrete non-formula anchors in trim and finishing, especially the cuff snaps, contrast piping, and self-belt. It is still grounded in a fairly wearable tailored template, so it i |
| `design_signal_purity` | 0.5 | 0 | 设计信号纯度 | Design facts are substantial, but they are repeatedly interwoven with mood and identity framing. The result is balanced rather than purely observational, with noticeable essay-like phrasing. |
| `fine_grained_attribute_usage` | 1.0 | 1 | 术语具体度 | Attributes are richly and precisely specified across color, material, construction, and finish, producing a highly imageable and technically detailed description. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly visual, garment-specific, and organized as a coherent full look with clear layers, materials, and silhouette cues, making it close to prompt-ready. It is still somewhat essay-like a |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a clear top-to-bottom outfit order: jacket, then trousers and top, then accessories/finishing footwear. Minor compression and repeated thematic commentary slightly reduce clari |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text describes multiple garments with their own materials, closures, and finishing details, and these are generally assigned to the correct item. There is some dense cross-referencing across layer |
| `quantity_accuracy` | 1.0 | 1 | 语言清晰度 | Quantities are explicit and consistent, with clear singular/plural references and no conflicting counts. |
| `reference_clarity` | 1.0 | 1 | 语言清晰度 | Pronouns and omitted subjects are easy to resolve; each sentence keeps a stable, readable reference chain. |
| `silhouette_combination_originality` | 0.25 | 0 | 组合原创性 | The outfit follows a recognizable cropped-jacket-plus-tailored-trouser-plus-loafer formula, even with refined material choices and a wrap top. The combination is polished but remains close to a common |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and attachment relationships are clearly described and visually reconstructible, including jacket-over-top-over-trouser and cuff lining visibility. The only slight weakness is that the prose  |
| `specific_noun_usage` | 1.0 | 1 | 术语具体度 | Uses highly specific garment and accessory nouns throughout, with clear fashion semantics and little reliance on generic terms. |
| `visibility_priority` | 0.5 | 0 | 信息密度与简洁性 | Visible clothing facts are present and fairly detailed, but they are consistently interleaved with stance, mood, and lifestyle narration. The imageable garment description remains usable, yet the essa |
| `visual_observation_grounding` | 0.75 | 1 | 视觉观察 grounded | The description is strongly anchored in visible garment zones and readable construction details. There is some mood language, but the text mostly reads like a grounded visual caption rather than an es |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | The trunk garments and shoes read as a coherent outfit with no direct left-right or mutually exclusive garment identity conflict. |
| `coordination_penalty` | 0.0 | The styling language is coordinated around a consistent workwear-marine-tailoring theme, with no major trunk-level clash. |
| `formula_template_penalty` | 0.25 | The text follows a predictable staged outfit-description formula, but it does not use fixed section headers or bullet templates. |
| `generation_content_penalty` | 0.5 | The description is heavily essayistic and mood-driven, with repeated conceptual framing around salon/coastal/marine polish rather than a compact imaging prompt. |
| `rationality_penalty` | 0.0 | Materials and garment construction are physically plausible and described in ordinary wearable terms. |

## Quality issues (质量短板)

- **`core_information_density`** (score 0.5) — The text contains substantial concrete garment detail, but it is repeatedly wrapped in mood/identity framing and interpretive prose, which reduces prompt efficiency. It is not a four-section template, so the score is capped at 0.5 rather than lower.
- **`visibility_priority`** (score 0.5) — Visible clothing facts are present and fairly detailed, but they are consistently interleaved with stance, mood, and lifestyle narration. The imageable garment description remains usable, yet the essay-like framing prevents a higher score.
- **`silhouette_combination_originality`** (score 0.25) — The outfit follows a recognizable cropped-jacket-plus-tailored-trouser-plus-loafer formula, even with refined material choices and a wrap top. The combination is polished but remains close to a common luxury/resort template.
- **`design_signal_purity`** (score 0.5) — Design facts are substantial, but they are repeatedly interwoven with mood and identity framing. The result is balanced rather than purely observational, with noticeable essay-like phrasing.

## Skipped metrics (不适用)

- `pattern_type` (coverage_score) — No explicit pattern or print is described.
- `construction_technique` (coverage_score) — The text mentions tailoring and topstitching, but not a salient specialized construction technique of the type required by the metric.
- `deconstruction` (coverage_score) — No explicit deconstruction, splicing, displacement, or reconstruction is described.
- `bag` (coverage_score) — No bag is described or implied as part of the look.
- `jewelry` (coverage_score) — No salient jewelry or body ornament is present.
- `asymmetry` (coverage_score) — No clear asymmetrical design or uneven structure is described.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral garment differences are described.
