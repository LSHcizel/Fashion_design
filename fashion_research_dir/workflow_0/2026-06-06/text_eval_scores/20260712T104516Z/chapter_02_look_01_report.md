# Text Evaluation Report

- **Source:** look_01.txt
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.1
- **Total score (S_fp):** 0.7365 (Usable)
- **Coverage axis:** 1.0
- **Quality axis (raw / base / penalized):** 0.7188 / 0.6727 / 0.6727
- **Penalties (mean):** 0.1
- **R_content:** 0.710723

## Gates

- Score gate: 0.7365 (threshold 0.7) → **PASS**
- Penalty gate: 0.1 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `belt` | 1.0 | 1 |  | A visible belt is explicitly described, including its attachment to the waist loops. |
| `body_coverage` | 1.0 | 1 |  | The text describes visible exposure/coverage at the neckline, cuffs, and shoe back. |
| `closure` | 1.0 | 1 |  | The text clearly describes both button front closure and a belt closure detail. |
| `color_relationship_logic` | 1.0 | 1 |  | The text explains the color logic through tonal variation, accent contrast, and matte-vs-gloss interplay. |
| `construction_technique` | 1.0 | 1 |  | The garment construction is described through seam work and seam treatment, with clear placement on the jacket body. |
| `cross_garment_binding` | 1.0 | 1 |  | The description clearly distinguishes which details belong to the jacket, trousers, base layer, belt, and shoes, keeping multi-item relations coherent. |
| `fabric_family` | 1.0 | 1 |  | The text clearly names the main fabric families for the garments. |
| `footwear` | 1.0 | 1 |  | Footwear is clearly specified with type, toe shape, heel height, and material/color. |
| `functional_detail` | 1.0 | 1 |  | Functional pocket details are explicitly described, along with pocket-related hardware. |
| `garment_category` | 1.0 | 1 |  | The text clearly names the main garment categories. |
| `hardware_embellishment` | 1.0 | 1 |  | The look includes clearly described decorative hardware elements. |
| `layering` | 1.0 | 1 |  | The text clearly describes layered garments and their visible order: base layer under jacket, with trousers below. |
| `length_hemline` | 1.0 | 1 |  | The text gives clear length and hem/cuff information. |
| `primary_color` | 1.0 | 1 |  | The dominant palette is clearly anchored by navy and black, with navy functioning as the main color. |
| `secondary_color` | 1.0 | 1 |  | Secondary colors are clearly present, especially pale blue accents against navy and black supporting elements. |
| `shoulder_architecture` | 1.0 | 1 |  | Shoulder structure is directly specified. |
| `silhouette` | 1.0 | 1 |  | Overall shape and structural contour are explicitly described. |
| `surface_finish` | 1.0 | 1 |  | Multiple surface traits are explicitly described, including matte, washed, softened, and polished finishes. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes the relationship between the cropped top and the lower garment, including waist placement and overall silhouette balance. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are clearly tied to the correct garment or body area, and the layering is coherent. Minor complexity comes from dense multi-garment phrasing, but there is no major misbinding. |
| `core_information_density` | 0.5 | 0 | 信息密度与简洁性 | The description contains substantial concrete garment detail, but it is diluted by repeated mood/identity/transition framing and salon/coastal narrative language. Core clothing facts remain usable, ye |
| `craft_embellishment_salience` | 0.75 | 1 | 工艺装饰显著度 | Craft and trim are described with decent specificity, including type and placement. The details are not the main hook of the look, but they are clearly localized and visually legible. |
| `design_distinctiveness` | 0.5 | 0 | 设计独特性 | There are some distinctive touches in the washed canvas, pearl-finished snaps, and seam abrasion, but the overall look still reads as a fairly safe cropped jacket + trouser + belt + slingback combinat |
| `design_signal_purity` | 0.5 | 0 | 设计信号纯度 | Most of the text is concrete garment description, but repeated narrative framing and identity/mood language dilute the design signal somewhat. |
| `fine_grained_attribute_usage` | 1.0 | 1 | 术语具体度 | Attributes are finely differentiated across color, fabric, finish, construction, and silhouette, giving a precise and imageable fashion description. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly imageable and organized around visible garments, layers, and styling, so it is close to a usable prompt. It is still somewhat essay-like and interpretive in places, which keeps it j |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a clear主体→下装→内搭/配件→鞋履 progression, making the outfit easy to reconstruct. There is some lyrical elaboration and repeated thematic framing, but the overall ordering remains natu |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text keeps jacket, trousers, base layer, belt, and shoes mostly separated and correctly attributed. There is some density, but the garment-to-attribute mapping remains stable and imageable. |
| `quantity_accuracy` | 1.0 | 1 | 语言清晰度 | The text uses quantities and count-like descriptors consistently, with no conflicting numbers or ambiguous quantity relations. |
| `reference_clarity` | 1.0 | 1 | 语言清晰度 | Pronouns and omitted subjects remain easy to track; each sentence clearly ties back to the jacket, trousers, or full look without reference confusion. |
| `silhouette_combination_originality` | 0.25 | 0 | 组合原创性 | The silhouette is coherent but close to a familiar cropped-jacket-plus-trouser-plus-belt-plus-heeled-shoe formula. The styling is polished, yet not especially original in combination. |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and attachment relations are clearly described and visually reconstructable, including jacket-over-base-layer, belt-through-loops, and shoe structure. The spatial logic is coherent and imagea |
| `specific_noun_usage` | 1.0 | 1 | 术语具体度 | The text uses highly specific garment, material, color, and footwear nouns throughout, with clear fashion terminology and little reliance on generic wording. |
| `visibility_priority` | 0.5 | 0 | 信息密度与简洁性 | Visible garment features are present and fairly detailed, but the text repeatedly foregrounds mood, identity, and narrative atmosphere alongside the clothing. That reduces priority on directly image-d |
| `visual_observation_grounding` | 0.75 | 1 | 视觉观察 grounded | The description is strongly anchored in visible garment zones and layering, with clear references to neckline, cuffs, pockets, waist, and hemline. There is some mood language, but it does not overwhel |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | The jacket, trousers, base layer, and shoes read as a coherent single outfit with no left-right or trunk-level contradictions. |
| `coordination_penalty` | 0.0 | The materials and styling cues are coordinated into one unified navy/black look; no major trunk-garment or footwear clash is present. |
| `formula_template_penalty` | 0.25 | The text uses a somewhat templated fashion-description progression, but it does not hit the stricter fixed-header or bullet-list formula triggers. |
| `generation_content_penalty` | 0.25 | Mostly grounded garment description, but it includes some conceptual/runway-style phrasing and brand-coded commentary that slightly reduces prompt efficiency. |
| `rationality_penalty` | 0.0 | All described materials and garment constructions are physically plausible for ordinary wear. |

## Quality issues (质量短板)

- **`core_information_density`** (score 0.5) — The description contains substantial concrete garment detail, but it is diluted by repeated mood/identity/transition framing and salon/coastal narrative language. Core clothing facts remain usable, yet the prose is not highly dense.
- **`visibility_priority`** (score 0.5) — Visible garment features are present and fairly detailed, but the text repeatedly foregrounds mood, identity, and narrative atmosphere alongside the clothing. That reduces priority on directly image-dominant facts.
- **`design_distinctiveness`** (score 0.5) — There are some distinctive touches in the washed canvas, pearl-finished snaps, and seam abrasion, but the overall look still reads as a fairly safe cropped jacket + trouser + belt + slingback combination.
- **`silhouette_combination_originality`** (score 0.25) — The silhouette is coherent but close to a familiar cropped-jacket-plus-trouser-plus-belt-plus-heeled-shoe formula. The styling is polished, yet not especially original in combination.
- **`design_signal_purity`** (score 0.5) — Most of the text is concrete garment description, but repeated narrative framing and identity/mood language dilute the design signal somewhat.

## Skipped metrics (不适用)

- `pattern_type` (coverage_score) — No explicit pattern or print is described.
- `deconstruction` (coverage_score) — The text does not mention deconstruction, splicing, displacement, or reconstruction.
- `bag` (coverage_score) — No bag is described or implied as part of the look.
- `jewelry` (coverage_score) — No jewelry or body ornament is explicitly present.
- `asymmetry` (coverage_score) — No asymmetrical design or uneven structure is described.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral asymmetry is described.
