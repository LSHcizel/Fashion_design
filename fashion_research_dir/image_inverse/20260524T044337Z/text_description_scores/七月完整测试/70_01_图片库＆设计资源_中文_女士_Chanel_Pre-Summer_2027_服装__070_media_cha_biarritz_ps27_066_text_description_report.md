# Text Evaluation Report

- **Source:** 70_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__070_media_cha_biarritz_ps27_066_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.8342 (Strong)
- **Coverage axis:** 1.0
- **Quality axis (raw / base / penalized):** 0.7857 / 0.7917 / 0.7917
- **Penalties (mean):** 0.1
- **R_content:** 0.805003

## Gates

- Score gate: 0.8342 (threshold 0.7) → **PASS**
- Penalty gate: 0.1 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `asymmetry` | 1.0 | 1 |  | The garment includes uneven hem treatment and an off-balance visible-hand detail, which supports asymmetry. |
| `bag` | 1.0 | 1 |  | Bag is clearly present with category, shape, and decorative finish described. |
| `body_coverage` | 1.0 | 1 |  | The text clearly describes strong body coverage with limited arm exposure. |
| `color_relationship_logic` | 1.0 | 1 |  | 文本交代了配色逻辑：以黑色为主，辅以金属金和浅粉红红色作为配饰点缀，属于明确的主次色关系。 |
| `construction_technique` | 1.0 | 1 |  | A clear fabrication technique is described, with pleating/frayed layered construction and its placement on the upper body and hips. |
| `cross_garment_binding` | 1.0 | 1 |  | Multiple items are present and the text distinguishes them clearly from the dress, showing which attributes belong to each accessory or garment. |
| `fabric_family` | 1.0 | 1 |  | 主体材质/面料家族可明确推断为以轻薄织物为基础的层叠褶皱、荷叶边/流苏式装饰面料，属于可识别的服装材质描述。 |
| `footwear` | 1.0 | 1 |  | Footwear is explicitly identified with shoe type, toe shape, and color/accent detail. |
| `garment_category` | 1.0 | 1 |  | The main garment is explicitly identified as a dress. |
| `hardware_embellishment` | 1.0 | 1 |  | The look includes salient metallic embellishment in the form of a spiked necklace and gold accent hardware-like detailing. |
| `jewelry` | 1.0 | 1 |  | A prominent necklace/body ornament is clearly described. |
| `length_hemline` | 1.0 | 1 |  | Garment length and hem behavior are explicitly stated. |
| `primary_color` | 1.0 | 1 |  | 主色非常明确，为黑色。 |
| `secondary_color` | 1.0 | 1 |  | 存在清晰副色与点缀色：金色与浅粉红/红色配件，与主黑色形成可见辅助色块。 |
| `shoulder_architecture` | 1.0 | 1 |  | The shoulder area is visually emphasized through structured volume and layered construction. |
| `silhouette` | 1.0 | 1 |  | The text clearly describes the overall shape and structural contour. |
| `surface_finish` | 1.0 | 1 |  | 文本明确给出表面性质：强纹理、褶皱、飘动与毛边感，足以覆盖表面质感。 |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes overall vertical proportion and balance between upper volume and a narrower lower skirt. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are clearly tied to the correct entities, including dress, necklace, clutch, and shoes. Minor ambiguity remains in phrases like “sleeves appear long or fully integrated” and “one hand  |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is dense with visible garment facts and styling details, with the main dress clearly foregrounded. There is some extra mood language at the end, but it does not overwhelm the core fash |
| `craft_embellishment_salience` | 0.75 | 1 | 工艺装饰显著度 | Craft and embellishment are clearly identified and tied to placement and effect, especially the layered frayed/pleated strips that define the dress. The necklace and shoe accent are secondary, but the |
| `design_distinctiveness` | 0.75 | 1 | 设计独特性 | The look has a clear non-formula memory point through its heavily textured tiered ruffle construction and unusual straight-to-cocoon silhouette. It is distinctive, though the palette and accessories r |
| `design_signal_purity` | 1.0 | 1 | 设计信号纯度 | The text is dominated by concrete design information: silhouette, texture, hem, accessories, and color relationships. Mood language is minimal and does not dilute the design signal. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly visual, garment-centered, and mostly prompt-ready, with clear silhouette, materials, accessories, and styling. It reads slightly like a descriptive analysis rather than a compact ge |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a mostly natural order from main garment to construction details, then neckline/sleeves/hem, and finally accessories and styling. It is clear and easy to reconstruct, though so |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text cleanly separates multiple items and their attributes, with color and material cues attached to the correct garment or accessory. There is slight looseness in the dress sleeve/arm description |
| `quantity_accuracy` | 0.75 | 1 | 语言清晰度 | The explicit quantity relation is clear and consistent, with only minor ambiguity around the optional phrasing “clutch or minaudière,” which does not materially confuse the count. |
| `reference_clarity` | 0.75 | 1 | 语言清晰度 | References are mostly clear and the subject remains stable, though a few phrases use hedging (“appear,” “or”) that slightly reduce precision without making the description hard to follow. |
| `silhouette_combination_originality` | 0.75 | 1 | 组合原创性 | The silhouette combination is unusual and sculptural, especially the cocooning column shape with heavy volume at the upper body and hips. It is not a standard formula template, though the footwear and |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and attachment relations are mostly clear and imageable, especially the neckline, necklace placement, and the dress’s volume versus exposed lower legs. The text is coherent, though some phras |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | Most of the text prioritizes visible, imageable elements of the look. A few lower-priority phrases like the mood statement are present, but they do not dominate or obscure the outfit description. |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly anchored in visible garment facts and body zones, with precise observations of neckline, sleeves, hem, footwear, and accessories. It reads like a direct runway caption rath |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | Single coherent trunk garment with no left-right or multi-garment identity conflict. |
| `coordination_penalty` | 0.0 | Accessories and footwear are coordinated with the dress; no trunk-level styling clash. |
| `formula_template_penalty` | 0.25 | Readable and specific, but slightly formulaic runway prose with mood framing layered over the garment facts. |
| `generation_content_penalty` | 0.25 | Mostly grounded in a clear dress description, but ends with evaluative mood language that slightly dilutes prompt efficiency. |
| `rationality_penalty` | 0.0 | All described materials and worn items are physically plausible. |

## Skipped metrics (不适用)

- `pattern_type` (coverage_score) — 未描述明确图案或印花，仅有纹理与层叠结构。
- `closure` (coverage_score) — No explicit closure detail such as buttons, zipper, ties, or buckle is mentioned.
- `functional_detail` (coverage_score) — The text does not describe pockets, straps, utility parts, or similar functional garment details.
- `deconstruction` (coverage_score) — The text does not explicitly mention deconstruction, splicing, displacement, or reconstruction.
- `belt` (coverage_score) — No visible belt, sash, waist cincher, or harness is mentioned; only silhouette shaping is described.
- `layering` (coverage_score) — The text describes a single dress with internal textural construction, not a clear multi-garment layering relation.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral contrast is described.
- `cultural_reference` (bonus_score) — No clear cultural, historical, or brand reference is provided.
- `gender_expression` (bonus_score) — The description does not explicitly discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is explicitly stated.
- `brand_alignment` (bonus_score) — The text does not explicitly target a brand identity or brand language.
- `negation_control` (bonus_score) — The description does not emphasize exclusions or absence of elements as important.
