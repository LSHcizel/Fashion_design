# Text Evaluation Report

- **Source:** 39_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__039_media_cha_biarritz_ps27_021_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.8067 (Strong)
- **Coverage axis:** 0.9474
- **Quality axis (raw / base / penalized):** 0.7857 / 0.7708 / 0.7708
- **Penalties (mean):** 0.1
- **R_content:** 0.778465

## Gates

- Score gate: 0.8067 (threshold 0.7) → **PASS**
- Penalty gate: 0.1 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `bag` | 0.0 | 0 |  | A bag is mentioned, but only as a glimpse; the text does not clearly cover category/holding style plus shape and material sufficiently for a hit. |
| `body_coverage` | 1.0 | 1 |  | The text describes visible coverage and exposure zones, including the cropped hem and open neckline. |
| `closure` | 1.0 | 1 |  | Clear button closures are explicitly described on both the jacket and the knit top. |
| `color_relationship_logic` | 1.0 | 1 |  | 文本交代了明确的配色逻辑：浅色上装与深棕下装形成主次分区，并以金色五金作点缀。 |
| `cross_garment_binding` | 1.0 | 1 |  | Multiple garments are clearly distinguished and their attributes are assigned to the correct item. |
| `fabric_family` | 1.0 | 1 |  | 主体材质类别明确，包含针织、皮革/仿皮，以及外套面料的服装描述。 |
| `functional_detail` | 1.0 | 1 |  | Functional garment details are present, especially the pocket openings and inset side details. |
| `garment_category` | 1.0 | 1 |  | The text clearly names the main garment categories: jacket, knit top/cardigan, and trousers. |
| `hardware_embellishment` | 1.0 | 1 |  | Metal hardware is a salient visual feature throughout the outfit. |
| `jewelry` | 1.0 | 1 |  | Salient jewelry is explicitly present and clearly described. |
| `layering` | 1.0 | 1 |  | Clear layered outfit structure is described with outer layer over inner layer and trousers beneath. |
| `length_hemline` | 1.0 | 1 |  | The text gives clear length and hemline information for the jacket and the framing of the look. |
| `pattern_type` | 1.0 | 1 |  | 存在明确图案/装饰类型，为黑色交错环状图案。 |
| `primary_color` | 1.0 | 1 |  | 主色清晰，以象牙白/奶油色与棕色为主。 |
| `secondary_color` | 1.0 | 1 |  | 存在明显副色与点缀色，金色、黑色都作为可见对比元素出现。 |
| `shoulder_architecture` | 1.0 | 1 |  | Shoulder structure is explicitly salient through the padded-looking shoulders and tailored jacket construction. |
| `silhouette` | 1.0 | 1 |  | Overall shape and structural contour are explicitly described for both the outer layer and bottoms. |
| `surface_finish` | 1.0 | 1 |  | 文本明确给出光泽与挺括/结构感等表面性质。 |
| `top_bottom_proportion` | 1.0 | 1 |  | The text explicitly describes waist placement and the resulting top-bottom proportion. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are clearly attached to the correct garment, with color, hardware, and silhouette consistently bound. Minor ambiguity remains in phrases like "top or cardigan" and "leather or leather- |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is packed with concrete garment facts and mostly prioritizes visible clothing structure, silhouette, and hardware. There is some stylistic framing at the end, but it does not overwhelm |
| `craft_embellishment_salience` | 0.75 | 1 | 工艺装饰显著度 | The hardware is clearly located and repeated as a design feature, though it is still hardware rather than a more elaborate craft technique. |
| `design_distinctiveness` | 0.75 | 1 | 设计独特性 | The look has at least one clear memory point beyond a formula outfit: the chest motif and sailor-style button arrangement create a recognizable structure. |
| `design_signal_purity` | 0.75 | 1 | 设计信号纯度 | Most of the text is devoted to concrete design facts, with only a brief mood phrase at the end. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly imageable and already organized around visible silhouette, garment layers, materials, and styling, so it is close to a usable prompt. It is still slightly explanatory and verbose ra |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a clear body-to-detail progression: overall view, outer layer, inner layer, bottoms, then accessories/styling. Minor compression and dense modifier stacking reduce smoothness s |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The description separates jacket, inner top, trousers, and accessories well, and their attributes are mostly assigned to the correct items. Small uncertainty in garment naming and material wording sli |
| `quantity_accuracy` | 1.0 | 1 | 语言清晰度 | Quantities and spatial extents are explicit and internally consistent; no conflicting counts or ambiguous quantity relations. |
| `reference_clarity` | 1.0 | 1 | 语言清晰度 | References and ellipses are clear, with each garment layer and accessory introduced unambiguously and easy to track. |
| `silhouette_combination_originality` | 0.5 | 0 | 组合原创性 | The silhouette is coherent and somewhat specific, but it still sits within a fairly familiar cropped-jacket-plus-tailored-trouser luxury formula. |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and placement are clearly described, with coherent top-under-jacket and trouser-under-jacket relations. The spatial structure is easy to visualize, though some details remain slightly interpr |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | Visible, image-dominant details are foregrounded, and low-visibility items are only lightly mentioned. The mood phrase at the end is present, but it does not dominate the description. |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly anchored in visible garment details, placement, and layer relationships, with little mood-only language. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | The main garments read coherently; no strong trunk-level left-right or mutually exclusive construction conflict is present. |
| `coordination_penalty` | 0.0 | The palette, hardware, and silhouette cues are aligned into one coherent styling direction. |
| `formula_template_penalty` | 0.25 | There is some formulaic cruise/resort-adjacent styling language and mood framing, but the description still contains specific craft and garment details. |
| `generation_content_penalty` | 0.25 | Mostly grounded garment description, but includes some runway/mood framing and stylistic summary that slightly dilutes prompt efficiency. |
| `rationality_penalty` | 0.0 | All described materials and construction details are physically plausible as ordinary fashion wear. |

## Missing coverage (未覆盖)

- **`bag`** — A bag is mentioned, but only as a glimpse; the text does not clearly cover category/holding style plus shape and material sufficiently for a hit.

## Quality issues (质量短板)

- **`silhouette_combination_originality`** (score 0.5) — The silhouette is coherent and somewhat specific, but it still sits within a fairly familiar cropped-jacket-plus-tailored-trouser luxury formula.

## Skipped metrics (不适用)

- `construction_technique` (coverage_score) — No notable named construction technique such as quilting, pleating architecture, embroidery, or cut-out work is clearly described.
- `deconstruction` (coverage_score) — The text does not explicitly mention deconstruction, splicing, displacement, or reconstruction.
- `footwear` (coverage_score) — No footwear is described.
- `belt` (coverage_score) — No visible belt, sash, or waist strap is described; the waist emphasis comes from garment cut and high-waisted trousers.
- `asymmetry` (coverage_score) — No clear asymmetry, one-shoulder, uneven hem, or similar design is described.
- `bilateral_coherence` (quality_score) — No explicit left-right, bilateral, or side-specific garment differences are described.
- `cultural_reference` (bonus_score) — No explicit cultural, historical, or brand grounding is provided.
- `gender_expression` (bonus_score) — The description does not discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is stated.
- `brand_alignment` (bonus_score) — No brand identity or brand-language target is mentioned.
- `negation_control` (bonus_score) — The text does not emphasize exclusions or absence of elements.
