# Text Evaluation Report

- **Source:** look_02.txt
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.0
- **Total score (S_fp):** 0.7701 (Strong)
- **Coverage axis:** 1.0
- **Quality axis (raw / base / penalized):** 0.7812 / 0.7154 / 0.7154
- **Penalties (mean):** 0.15
- **R_content:** 0.72967

## Gates

- Score gate: 0.7701 (threshold 0.7) → **PASS**
- Penalty gate: 0.15 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `asymmetry` | 1.0 | 1 |  | The wrap-front top is explicitly one-sided, creating a clear asymmetrical closure. |
| `belt` | 1.0 | 1 |  | A visible waist belt is explicitly described and its relation to the wrap layer is clear. |
| `body_coverage` | 1.0 | 1 |  | The text clearly describes exposed and covered body areas, especially at the waist and collarbone. |
| `closure` | 1.0 | 1 |  | Multiple clear closure methods are described for the jacket and top. |
| `color_relationship_logic` | 1.0 | 1 |  | The text explains the color logic through contrast and tonal coordination across layers. |
| `cross_garment_binding` | 1.0 | 1 |  | The text distinguishes how different elements belong to different garments and how they interact across the outfit, making the multi-garment relationships clear. |
| `fabric_family` | 1.0 | 1 |  | The text clearly names the main fabric families for the garments. |
| `footwear` | 1.0 | 1 |  | Footwear is clearly specified with type, shape, and materials/finish. |
| `functional_detail` | 1.0 | 1 |  | The text explicitly mentions pockets and functional strap/hardware details. |
| `garment_category` | 1.0 | 1 |  | The text clearly names the main garment categories: jacket, top, trouser, and footwear. |
| `hardware_embellishment` | 1.0 | 1 |  | Visible hardware is clearly present and described as a notable design element. |
| `layering` | 1.0 | 1 |  | The text clearly describes a jacket over a wrap-front top over trousers, with readable layering relations. |
| `length_hemline` | 1.0 | 1 |  | The text gives clear length and hemline information for the jacket and trouser. |
| `primary_color` | 1.0 | 1 |  | The dominant palette is clearly navy/indigo. |
| `secondary_color` | 1.0 | 1 |  | Secondary colors are clearly present and tied to specific garment details. |
| `shoulder_architecture` | 1.0 | 1 |  | Shoulder structure is explicitly stated and visually salient. |
| `silhouette` | 1.0 | 1 |  | The overall shape and structural contour are explicitly described. |
| `surface_finish` | 1.0 | 1 |  | Surface qualities are explicitly described, including washed/softened, matte, and sheen-related finishes. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes upper-lower proportion and waist visibility, with a cropped jacket balancing the trouser line. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are clearly attached to the correct garment or accessory, with good separation between jacket, top, trouser, belt, and footwear. Minor complexity comes from layered waist details and m |
| `core_information_density` | 0.5 | 0 | 信息密度与简洁性 | The text contains strong, imageable garment information and a clear outfit structure, but it is also heavily elaborated with stylistic interpretation and repeated atmospheric framing. Core clothing de |
| `craft_embellishment_salience` | 0.75 | 1 | 工艺装饰显著度 | Craft and trim are clearly identified with placement and visual effect, though the text uses several embellishment details rather than one singular dominant craft signature. |
| `design_distinctiveness` | 0.75 | 1 | 设计独特性 | The look has a clear memory anchor in the workwear-meets-couture hardware mix and the maritime-luxury treatment, though the base silhouette remains fairly familiar. |
| `design_signal_purity` | 0.5 | 0 | 设计信号纯度 | There is substantial design detail, but it is repeatedly interwoven with mood, metaphor, and stance language that dilutes pure garment signal. |
| `fine_grained_attribute_usage` | 1.0 | 1 | 术语具体度 | Color, material, construction, and silhouette details are consistently fine-grained and precise, producing a highly imageable and technically specific fashion description. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly imageable and already organized like a fashion prompt with clear garments, colors, materials, and silhouette logic. It is slightly verbose and explanatory, but only needs light edit |
| `information_ordering` | 1.0 | 1 | 结构清晰度 | The description is organized from main garment to layered pieces, then accessories/hardware, then footwear and overall pose. The hierarchy is clear and easy to reconstruct, with only minor elaboration |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text handles multiple garments and accessories with mostly clear ownership and layering. There is some dense cross-referencing across jacket, wrap top, trouser, belt, and hardware, but no major mi |
| `quantity_accuracy` | 1.0 | 1 | 语言清晰度 | Quantity expressions are modest and internally consistent; the text uses clear, non-conflicting counts and relations without ambiguity. |
| `reference_clarity` | 1.0 | 1 | 语言清晰度 | Pronouns and references are consistently anchored to clear antecedents, and the description remains easy to track throughout. |
| `silhouette_combination_originality` | 0.5 | 0 | 组合原创性 | The combination is coherent and polished, but it still reads as a fairly safe luxury/workwear formula with recognizable components. |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and attachment positions are clearly described and visually coherent, making the outfit easy to reconstruct. Minor complexity comes from the many layered details, but the spatial logic remain |
| `specific_noun_usage` | 1.0 | 1 | 术语具体度 | The description uses highly specific garment names, materials, closures, and footwear terms throughout, with clear fashion semantics and little reliance on generic wording. |
| `visibility_priority` | 0.5 | 0 | 信息密度与简洁性 | Most of the description focuses on visible silhouette, fabric, closures, and footwear, which supports image generation. However, some attention goes to lower-visibility or interpretive details such as |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly anchored to visible garment zones and readable layering, with multiple concrete placement cues. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | The jacket, top, trouser, and shoes read as a coherent layered outfit without trunk-level left-right conflicts or mutually exclusive garment identities. |
| `coordination_penalty` | 0.0 | Material and styling language are coordinated around a unified nautical-workwear palette; no strong trunk-level aesthetic clash is present. |
| `formula_template_penalty` | 0.25 | The text follows a fairly standard fashion-description formula with sequential item-by-item coverage and recurring mood/stance language, though it is not strongly templated or symbol-only. |
| `generation_content_penalty` | 0.5 | The description leans heavily into conceptual, evaluative, and mood-driven prose rather than compact imageable garment facts, with repeated salon/shore/couture framing that reduces prompt efficiency. |
| `rationality_penalty` | 0.0 | The described construction is physically plausible and consistent with ordinary garment making and wear. |

## Quality issues (质量短板)

- **`core_information_density`** (score 0.5) — The text contains strong, imageable garment information and a clear outfit structure, but it is also heavily elaborated with stylistic interpretation and repeated atmospheric framing. Core clothing details remain present and organized, yet the density is only moderate because descriptive commentary and symbolic language dilute the prompt efficiency.
- **`visibility_priority`** (score 0.5) — Most of the description focuses on visible silhouette, fabric, closures, and footwear, which supports image generation. However, some attention goes to lower-visibility or interpretive details such as hidden closures and metaphorical effects, so visible priorities are good but not fully optimized.
- **`silhouette_combination_originality`** (score 0.5) — The combination is coherent and polished, but it still reads as a fairly safe luxury/workwear formula with recognizable components.
- **`design_signal_purity`** (score 0.5) — There is substantial design detail, but it is repeatedly interwoven with mood, metaphor, and stance language that dilutes pure garment signal.

## Skipped metrics (不适用)

- `pattern_type` (coverage_score) — No explicit pattern or print is described.
- `construction_technique` (coverage_score) — No salient named fabrication technique like quilting, embroidery, cut-outs, or engineered pleating is described.
- `deconstruction` (coverage_score) — The text does not mention deconstruction, splicing, displacement, or reconstruction.
- `bag` (coverage_score) — No bag is described or implied as part of the look.
- `jewelry` (coverage_score) — No salient jewelry or body ornament is present.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral garment differences are described.
- `gender_expression` (bonus_score) — The text describes a woman, but does not explicitly discuss gender expression or androgyny as a design goal.
