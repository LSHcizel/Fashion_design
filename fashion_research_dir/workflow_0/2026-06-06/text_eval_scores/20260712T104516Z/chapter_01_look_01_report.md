# Text Evaluation Report

- **Source:** look_01.txt
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.1
- **Total score (S_fp):** 0.6854 (Usable)
- **Coverage axis:** 1.0
- **Quality axis (raw / base / penalized):** 0.6406 / 0.6091 / 0.6091
- **Penalties (mean):** 0.25
- **R_content:** 0.625428

## Gates

- Score gate: 0.6854 (threshold 0.7) → **FAIL**
- Penalty gate: 0.25 (max 0.5) → **PASS**
- Both passed: **False**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `belt` | 1.0 | 1 |  | A visible belt is explicitly present and its attachment at the waist is described. |
| `body_coverage` | 1.0 | 1 |  | The text clearly describes exposed and covered body areas, especially at the midriff and cuffs. |
| `closure` | 1.0 | 1 |  | Multiple explicit closure elements are described, including placket, button, and belt buckle. |
| `color_relationship_logic` | 1.0 | 1 |  | It explains the palette logic as a white base with navy and sand-beige accents, including tonal contrast and softening relationships. |
| `cross_garment_binding` | 1.0 | 1 |  | The description distinguishes how the jacket, shirt, shorts, belt, and footwear relate to each other, making cross-garment roles and interactions clear. |
| `fabric_family` | 1.0 | 1 |  | The text clearly names the main fabric families for the garments. |
| `footwear` | 1.0 | 1 |  | Footwear is clearly specified with type and material/finish details. |
| `functional_detail` | 1.0 | 1 |  | Clear functional details are named, especially pocketing and side-entry construction. |
| `garment_category` | 1.0 | 1 |  | The text clearly names the main garment categories in the outfit. |
| `hardware_embellishment` | 1.0 | 1 |  | Visible hardware is clearly present and described as a notable design element. |
| `layering` | 1.0 | 1 |  | The text clearly describes layered garments and their visible order/relationship. |
| `length_hemline` | 1.0 | 1 |  | Length and hem placement are directly specified for the jacket and shorts. |
| `pattern_type` | 1.0 | 1 |  | A clear stripe pattern is specified. |
| `primary_color` | 1.0 | 1 |  | White is the dominant primary color across the look. |
| `secondary_color` | 1.0 | 1 |  | The text clearly includes secondary colors that complement and contrast with the white base. |
| `shoulder_architecture` | 1.0 | 1 |  | The shoulder structure is explicitly called out and is visually salient. |
| `silhouette` | 1.0 | 1 |  | It explicitly describes the overall shape and structural contour of the look. |
| `surface_finish` | 1.0 | 1 |  | It explicitly describes surface qualities including structure, polish, and matte finish. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly states the top-to-bottom proportion and waist break, with explicit balance between cropped jacket and high-waisted shorts. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are clearly attached to the correct garment or body zone, including the belt at the waist and the lining on the jacket. Minor complexity comes from layered references around the jacket |
| `core_information_density` | 0.5 | 0 | 信息密度与简洁性 | The description contains substantial concrete garment detail, but repeated mood/identity framing and scenic language dilute prompt efficiency. It is not a four-section template, so the score is capped |
| `craft_embellishment_salience` | 0.75 | 1 | 工艺装饰显著度 | Craft details are clearly named and located, with visible function and placement, though some elements remain somewhat generalized. |
| `design_distinctiveness` | 0.25 | 0 | 设计独特性 | The look is mostly a recognizable resort/luxury formula; the Double C is not counted as a distinctiveness anchor, and the remaining details are refined but not strongly non-formula. |
| `design_signal_purity` | 0.25 | 0 | 设计信号纯度 | Design facts are repeatedly diluted by mood/scene language, with several essay-like transitions and atmospheric phrases reducing signal purity. |
| `fine_grained_attribute_usage` | 1.0 | 1 | 术语具体度 | Colors, fabrics, construction details, and structural features are described at a fine-grained level, making the look highly imageable and technically precise. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly imageable and already organized like a prompt, with clear garment categories, materials, colors, and silhouette logic. It is slightly over-explanatory and essay-like in places, so i |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a clear主体→内搭→腰部配件→鞋履→整体完成度的顺序, making the outfit easy to reconstruct. Minor repetition and interpretive prose slightly interrupt the flow, but the main structure remains strong |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text distinguishes multiple garments and generally keeps each attribute with the right item: jacket, shirt, shorts, belt, and sandals are separately described. There is some dense cross-referencin |
| `quantity_accuracy` | 0.75 | 1 | 语言清晰度 | Quantities and side relations are mostly clear and stable, with only minor density from multiple garment references. The single-pocket count is explicit, and the rest of the numeric/relative descripti |
| `reference_clarity` | 0.75 | 1 | 语言清晰度 | Pronouns and references are generally well anchored to nearby nouns, and the garment chain is easy to follow. There is slight referential load from repeated 'the jacket,' 'the shirt,' and 'their,' but |
| `silhouette_combination_originality` | 0.25 | 0 | 组合原创性 | This is a classic cropped jacket + striped shirt + tailored short + belt + flat sandal combination, which falls squarely into the capped formula template. |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and attachment relations are clear and visually coherent, including jacket-over-shirt-over-shorts and visible lining. Minor issues remain because some motion-based visibility is described nar |
| `specific_noun_usage` | 1.0 | 1 | 术语具体度 | The description uses highly specific garment, material, and accessory nouns throughout, with clear fashion terminology and little reliance on generic wording. |
| `visibility_priority` | 0.5 | 0 | 信息密度与简洁性 | Visible clothing facts are present and mostly prioritized, but the text spends notable space on atmosphere, stance, and implied narrative. Hidden/interior detail is mentioned, though not dominant, so  |
| `visual_observation_grounding` | 0.5 | 0 | 视觉观察 grounded | There are solid visible anchors and layer relations, but they are mixed with mood-heavy phrasing like promenade/sea light/seaworthy, reducing pure observational grounding. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | The trunk garments and footwear read as a coherent outfit with no left-right or mutually exclusive structural conflicts. |
| `coordination_penalty` | 0.0 | The palette and styling language are coordinated across jacket, shirt, shorts, and sandals; no major trunk-level aesthetic clash is present. |
| `formula_template_penalty` | 0.75 | The text follows a predictable four-part fashion-description template with repeated mood/essay phrasing and brand-symbol emphasis, making it formulaic. |
| `generation_content_penalty` | 0.5 | The description repeatedly shifts into essay-like mood and conceptual framing rather than staying purely image-driven, with multiple promenade/sea/light/confidence style sentences that reduce prompt efficiency. |
| `rationality_penalty` | 0.0 | All materials and garment constructions are physically plausible and described as ordinary wearable fashion. |

## Quality issues (质量短板)

- **`core_information_density`** (score 0.5) — The description contains substantial concrete garment detail, but repeated mood/identity framing and scenic language dilute prompt efficiency. It is not a four-section template, so the score is capped at 0.5 rather than lower.
- **`visibility_priority`** (score 0.5) — Visible clothing facts are present and mostly prioritized, but the text spends notable space on atmosphere, stance, and implied narrative. Hidden/interior detail is mentioned, though not dominant, so this remains moderate rather than strong.
- **`design_distinctiveness`** (score 0.25) — The look is mostly a recognizable resort/luxury formula; the Double C is not counted as a distinctiveness anchor, and the remaining details are refined but not strongly non-formula.
- **`visual_observation_grounding`** (score 0.5) — There are solid visible anchors and layer relations, but they are mixed with mood-heavy phrasing like promenade/sea light/seaworthy, reducing pure observational grounding.
- **`silhouette_combination_originality`** (score 0.25) — This is a classic cropped jacket + striped shirt + tailored short + belt + flat sandal combination, which falls squarely into the capped formula template.
- **`design_signal_purity`** (score 0.25) — Design facts are repeatedly diluted by mood/scene language, with several essay-like transitions and atmospheric phrases reducing signal purity.

## Skipped metrics (不适用)

- `construction_technique` (coverage_score) — The text describes tailoring and finishing, but not a salient named craft technique like quilting, pleating, cut-outs, or engineered panel work.
- `deconstruction` (coverage_score) — No deconstruction, splicing, displacement, or reconstruction is explicitly mentioned.
- `bag` (coverage_score) — No bag is mentioned or implied as part of the look.
- `jewelry` (coverage_score) — No jewelry or body ornament is described.
- `asymmetry` (coverage_score) — No clear asymmetrical design or uneven structural feature is described.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral garment differences are described.
