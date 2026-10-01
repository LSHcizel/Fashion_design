# Text Evaluation Report

- **Source:** 77_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__077_media_cha_biarritz_ps27_074_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.813 (Strong)
- **Coverage axis:** 0.8947
- **Quality axis (raw / base / penalized):** 0.7857 / 0.7917 / 0.7917
- **Penalties (mean):** 0.1
- **R_content:** 0.784545

## Gates

- Score gate: 0.813 (threshold 0.7) → **PASS**
- Penalty gate: 0.1 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `asymmetry` | 1.0 | 1 |  | Asymmetry is explicitly stated and reinforced by the irregular hem and uneven drape. |
| `bag` | 1.0 | 1 |  | The text clearly identifies the bag, its carry method, and its material/finish cues, satisfying at least two required facets. |
| `body_coverage` | 1.0 | 1 |  | The text clearly indicates exposed upper chest/neckline area and coverage across the chest and torso. |
| `color_relationship_logic` | 1.0 | 1 |  | The text explains the color logic as a light blue floral base contrasted with black framing and edging. |
| `cross_garment_binding` | 1.0 | 1 |  | The description distinguishes multiple items and assigns their attributes clearly to the dress, bag, and footwear. |
| `fabric_family` | 0.0 | 0 |  | The text describes drape and silhouette but does not clearly name the main fabric family. |
| `footwear` | 0.0 | 0 |  | Footwear is mentioned, but the description does not clearly specify a shoe family or enough functional/material detail beyond color and pointed toe. |
| `functional_detail` | 1.0 | 1 |  | A carried bag with a strap/chain is a functional accessory detail clearly described. |
| `garment_category` | 1.0 | 1 |  | The main garment is clearly identified as a dress. |
| `hardware_embellishment` | 1.0 | 1 |  | The chain and beaded-looking surface count as visible embellishment/hardware details. |
| `layering` | 1.0 | 1 |  | The text describes a clear overlay and an underlying/edge layer relationship that is visually reconstructible. |
| `length_hemline` | 1.0 | 1 |  | Length and hem behavior are clearly stated. |
| `pattern_type` | 1.0 | 1 |  | The pattern type is clearly specified as botanical floral print. |
| `primary_color` | 1.0 | 1 |  | The main color is clearly identified as powder blue. |
| `secondary_color` | 1.0 | 1 |  | Black is a salient secondary color used as trim and contrasting panels. |
| `shoulder_architecture` | 1.0 | 1 |  | Shoulder/sleeve construction is explicitly described, including the shoulder-origin drape and sleeve type. |
| `silhouette` | 1.0 | 1 |  | The text explicitly describes the overall shape and structural fall of the garment. |
| `surface_finish` | 1.0 | 1 |  | The garment’s surface behavior is clearly described through drape and fluidity. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes the overall vertical proportion and balance of the dress, including a long upper-to-lower silhouette and emphasized lower hem movement. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are bound to the correct entities, and the dress, bag, and footwear are clearly distinguished. Minor ambiguity remains in phrases like “cape-like or ruffled bib effect” and “either an  |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description stays focused on the garment and visible styling details, with clear silhouette, print, trim, hem, bag, and shoes. There is some interpretive phrasing like “reads as” and “Overall mood |
| `craft_embellishment_salience` | 0.75 | 1 | 工艺装饰显著度 | The trim and structural detailing are clearly located and described in visual terms, especially the border framing and repeated edging. The craft is salient, though the exact construction method remai |
| `design_distinctiveness` | 0.75 | 1 | 设计独特性 | The look has a clear non-formula memory point through the cape-like bib overlay, graphic black edging, and asymmetric hem treatment. It is distinctive, though not so complex as to merit the top score. |
| `design_signal_purity` | 1.0 | 1 | 设计信号纯度 | The text is dominated by concrete design facts rather than mood essay or identity framing. Any mood language is brief and secondary to the garment description. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly imageable and mostly prompt-ready, with clear garment type, silhouette, color, trim, bag, and footwear. It is slightly less than perfect because it includes interpretive phrasing li |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a mostly natural order from overall garment to silhouette, print, construction details, hem, and accessories. It is clear and easy to reconstruct, though some layering and mate |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text separates multiple items well and generally keeps their attributes attached to the correct garment or accessory. There is slight uncertainty around the black contrasting lower sides/hem being |
| `quantity_accuracy` | 0.75 | 1 | 语言清晰度 | The text uses a few quantity-like descriptors and side/placement relations, but they remain internally consistent and easy to parse. There is slight ambiguity in phrases like “from one hand” and “eith |
| `reference_clarity` | 0.75 | 1 | 语言清晰度 | References are generally clear and well anchored to the dress or model. A few phrases introduce mild ambiguity, especially “either an underlayer or integrated border panels,” but overall the pronouns  |
| `silhouette_combination_originality` | 0.75 | 1 | 组合原创性 | The overall combination is more original than a standard formula look because of the loose shoulder-falling dress, asymmetric hem, and graphic trim. It still remains within a broadly wearable dress-an |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | The layering and attachment relationships are mostly clear and visually reconstructable, especially the front overlay, center-front border, hem contrast, and bag carry method. Minor ambiguity remains  |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | The text prioritizes visible, image-dominant features such as neckline, sleeves, hem treatment, and footwear. It includes some lower-priority interpretive language, but hidden or speculative details d |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly anchored in visible garment facts and specific body/garment zones, with clear observations about neckline, sleeves, chest overlay, hem, and footwear. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | Single coherent dress silhouette with no clear trunk-level left-right or garment-identity conflict. |
| `coordination_penalty` | 0.0 | The black trim, footwear, and floral dress read as coordinated within one styling language rather than clashing. |
| `formula_template_penalty` | 0.25 | Some mood-led runway prose and generic styling language are present, but the description remains fairly specific and not strongly formulaic. |
| `generation_content_penalty` | 0.25 | Mostly grounded garment description, but includes some interpretive/analytical phrasing and a few redundant read-as qualifiers that slightly dilute prompt efficiency. |
| `rationality_penalty` | 0.0 | No physically implausible materials or construction claims; the outfit is wearable and realistic. |

## Missing coverage (未覆盖)

- **`fabric_family`** — The text describes drape and silhouette but does not clearly name the main fabric family.
- **`footwear`** — Footwear is mentioned, but the description does not clearly specify a shoe family or enough functional/material detail beyond color and pointed toe.

## Skipped metrics (不适用)

- `closure` (coverage_score) — No explicit closure detail such as buttons, zipper, ties, or buckle is mentioned.
- `construction_technique` (coverage_score) — The text describes drape, overlay, and trim, but not a specific construction technique like pleating, quilting, embroidery, or engineered panel work with clear placement.
- `deconstruction` (coverage_score) — The text does not explicitly mention deconstruction, splicing, displacement, or reconstruction.
- `jewelry` (coverage_score) — No jewelry or body ornament is explicitly present.
- `belt` (coverage_score) — No visible belt, sash, waist cincher, or harness is described.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral distinction is described.
- `cultural_reference` (bonus_score) — No clear cultural, historical, or brand grounding is provided.
- `gender_expression` (bonus_score) — The description does not explicitly discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is explicitly stated.
- `brand_alignment` (bonus_score) — No brand identity or brand-language target is mentioned.
- `negation_control` (bonus_score) — The text does not emphasize exclusions or absence of elements.
