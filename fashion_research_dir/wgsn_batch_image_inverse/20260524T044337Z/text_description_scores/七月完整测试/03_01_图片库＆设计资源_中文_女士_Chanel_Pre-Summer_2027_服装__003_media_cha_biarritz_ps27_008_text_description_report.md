# Text Evaluation Report

- **Source:** 03_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__003_media_cha_biarritz_ps27_008_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.1
- **Total score (S_fp):** 0.8294 (Strong)
- **Coverage axis:** 1.0
- **Quality axis (raw / base / penalized):** 0.7969 / 0.7864 / 0.7864
- **Penalties (mean):** 0.05
- **R_content:** 0.814886

## Gates

- Score gate: 0.8294 (threshold 0.7) → **PASS**
- Penalty gate: 0.05 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `bag` | 1.0 | 1 |  | Bag is a salient look element and the text covers type/carry method, shape, and material/color details. |
| `body_coverage` | 1.0 | 1 |  | The text describes coverage and reveal through layering and cropped framing, making body exposure/coverage relevant. |
| `closure` | 1.0 | 1 |  | Clear button-front closure is explicitly described. |
| `color_relationship_logic` | 1.0 | 1 |  | The text explains the palette as a muted earthy scheme and shows a coordinated tonal relationship between grey and tan with accent colors. |
| `cross_garment_binding` | 1.0 | 1 |  | Multiple garments are present and their relationships are clearly assigned: open jacket over inner layer, then top/vest over skirt. |
| `deconstruction` | 1.0 | 1 |  | The text explicitly frames the look as deconstructed, supported by frayed, reconstructed detailing. |
| `fabric_family` | 1.0 | 1 |  | The text clearly identifies fabric family/surface as woven and textile-like, with a soft crumpled bag surface. |
| `functional_detail` | 1.0 | 1 |  | Multiple functional details are named, including pockets and a shoulder strap. |
| `garment_category` | 1.0 | 1 |  | The text clearly identifies the main garment categories: jacket, inner layer/top, skirt, and bag. |
| `hardware_embellishment` | 1.0 | 1 |  | Visible hardware and metallic embellishment are clearly present. |
| `layering` | 1.0 | 1 |  | The text clearly describes a layered outfit with an outer jacket over an inner layer and a skirt beneath, with readable stacking order. |
| `length_hemline` | 1.0 | 1 |  | The text gives multiple clear length and hemline references for the garments. |
| `pattern_type` | 1.0 | 1 |  | A clear pattern type is specified: narrow vertical stripes. |
| `primary_color` | 1.0 | 1 |  | The main palette is explicitly stated, with pale grey and khaki/tan as dominant colors. |
| `secondary_color` | 1.0 | 1 |  | Distinct secondary accent colors are clearly described on trims, bag panels, and hardware. |
| `shoulder_architecture` | 1.0 | 1 |  | Shoulder construction is explicitly salient through dropped shoulders and sleeve placement. |
| `silhouette` | 1.0 | 1 |  | Overall shape and structural trend are explicitly described for both the jacket and skirt. |
| `surface_finish` | 1.0 | 1 |  | It gives clear surface traits including coarse texture, relaxed structure, and a soft crumpled finish. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes the overall vertical proportion and the relative lengths of the jacket and skirt, making the top-bottom balance imageable. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are clearly attached to the correct garment or accessory, with good separation between jacket, inner layer, skirt, and bag. Minor ambiguity remains in phrases like "utility-like top or |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is packed with concrete garment facts and mostly prioritizes the visible outfit. There is some stylistic framing at the end, but not enough to seriously dilute the core clothing inform |
| `craft_embellishment_salience` | 0.75 | 1 | 工艺装饰显著度 | Craft and trim are clearly identified with type and placement, and they function as major visual hooks. The only limitation is that the description is still somewhat broad rather than deeply technical |
| `design_distinctiveness` | 0.75 | 1 | 设计独特性 | The look has clear non-formula memory points through frayed trim, fringed edging, and coarse woven texture. It is distinctive, though not so singular or structurally unusual as to merit 1.0. |
| `design_signal_purity` | 1.0 | 1 | 设计信号纯度 | The text is dominated by concrete design facts—shape, trim, layers, materials, and placement—with only a brief mood phrase at the end. Design signal clearly outweighs narrative framing. |
| `fine_grained_attribute_usage` | 1.0 | 1 | 术语具体度 | Color, material, and construction details are very fine-grained and layered, with precise texture, trim, closure, and palette descriptions that strongly support visual reconstruction. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly visual, garment-specific, and already close to a prompt, with clear silhouette, layering, materials, and palette. It is slightly less than perfect because it reads like a detailed f |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a mostly natural top-down order from overall framing to jacket, inner layer, skirt, and bag. The structure is easy to reconstruct, though some detail clusters are dense and sli |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text consistently distinguishes multiple items and generally keeps their colors, trims, and structures bound to the right piece. There is slight uncertainty around whether the inner layer is a top |
| `quantity_accuracy` | 0.75 | 1 | 语言清晰度 | Quantity and side references are mostly clear and internally consistent, with only minor density from multiple garment descriptions. |
| `reference_clarity` | 0.75 | 1 | 语言清晰度 | Pronouns and omitted subjects are generally easy to resolve; the description stays coherent despite several successive garment references. |
| `silhouette_combination_originality` | 0.5 | 0 | 组合原创性 | The silhouette is coherent and layered, but the overall combination remains fairly safe and familiar: oversized jacket over tailored tan separates with a shoulder bag. It is more textured than formula |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and attachment positions are clearly described and imageable, with coherent front-to-back and over/under relations. Minor ambiguity remains in the exact identity of the inner layer as “top or |
| `specific_noun_usage` | 1.0 | 1 | 术语具体度 | The description uses highly specific fashion nouns and garment terms throughout, with clear references to jacket, inner layer, skirt, shoulder bag, collar, sleeves, pockets, and buttons. |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | The text emphasizes visible, image-dominant details and crop-relevant garment structure. The mood phrase at the end is secondary and does not overpower the outfit description. |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly anchored in visible garment parts and placements, with clear layer reading and specific edge/collar/hem observations. It reads like a direct runway caption rather than mood |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | The outer jacket, inner layer, and skirt read as a coherent layered look without direct left-right or material identity conflicts on trunk garments. |
| `coordination_penalty` | 0.0 | The palette and styling language are coordinated overall; the bag adds contrast but does not create trunk-level styling conflict. |
| `formula_template_penalty` | 0.0 | The text is a single continuous description rather than a fixed template or formulaic sectioned prompt. |
| `generation_content_penalty` | 0.25 | Mostly imageable garment description with some conceptual mood language and color summary, but not enough redundancy or essay-like framing to warrant a higher penalty. |
| `rationality_penalty` | 0.0 | All described materials and construction details are physically plausible for ordinary fashion wear. |

## Quality issues (质量短板)

- **`silhouette_combination_originality`** (score 0.5) — The silhouette is coherent and layered, but the overall combination remains fairly safe and familiar: oversized jacket over tailored tan separates with a shoulder bag. It is more textured than formulaic, yet not highly unpredictable.

## Skipped metrics (不适用)

- `construction_technique` (coverage_score) — No specific fabrication technique like quilting, pleating, embroidery, or engineered panel work is clearly identified.
- `footwear` (coverage_score) — No footwear is described in the text.
- `jewelry` (coverage_score) — No jewelry or body ornament is explicitly mentioned.
- `belt` (coverage_score) — No visible belt, sash, or waist strap/harness is described.
- `asymmetry` (coverage_score) — No clear asymmetrical design, one-shoulder, uneven hem, or similar structure is described.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral asymmetry is described.
- `cultural_reference` (bonus_score) — No cultural, historical, or brand-specific reference is provided.
- `gender_expression` (bonus_score) — No explicit gender expression or androgyny is mentioned.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is stated beyond general mood.
- `brand_alignment` (bonus_score) — No brand language or brand identity is referenced.
- `negation_control` (bonus_score) — The text does not emphasize exclusions or absence of elements.
