# Text Evaluation Report

- **Source:** 10_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__010_media_cha_biarritz_ps27_031_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.1
- **Total score (S_fp):** 0.8388 (Strong)
- **Coverage axis:** 0.9444
- **Quality axis (raw / base / penalized):** 0.8281 / 0.8114 / 0.8114
- **Penalties (mean):** 0.15
- **R_content:** 0.794763

## Gates

- Score gate: 0.8388 (threshold 0.7) → **PASS**
- Penalty gate: 0.15 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `asymmetry` | 1.0 | 1 |  | Asymmetry is explicitly stated and is part of the visible inner layer. |
| `belt` | 1.0 | 1 |  | A visible waist-crossing belt/tab accessory is mentioned. |
| `body_coverage` | 1.0 | 1 |  | The text clearly mentions exposed chest/neckline coverage and layered reveal. |
| `color_relationship_logic` | 1.0 | 1 |  | The text explains the palette relationship: a warm neutral outer coat contrasted with a vivid multicolor striped underlayer. |
| `construction_technique` | 1.0 | 1 |  | The text clearly identifies a specific surface-making technique and its placement on the coat body. |
| `cross_garment_binding` | 1.0 | 1 |  | The description clearly distinguishes multiple garments and their relationships: outer coat, black layer, and striped inner piece. |
| `fabric_family` | 0.0 | 0 |  | The text describes texture and surface feel, but does not clearly identify a material family such as wool, knit, leather, silk, or denim. |
| `functional_detail` | 1.0 | 1 |  | A functional waist detail is explicitly mentioned, along with trim that reads as a construction detail. |
| `garment_category` | 1.0 | 1 |  | The text clearly identifies the main garment categories, especially the coat and layered clothing underneath. |
| `jewelry` | 1.0 | 1 |  | Salient earrings are explicitly described as part of the styling. |
| `layering` | 1.0 | 1 |  | The text clearly reconstructs a multi-layer outfit with coat, underlayer, and inner striped piece. |
| `length_hemline` | 1.0 | 1 |  | The text gives clear length information for the coat and inner layer. |
| `pattern_type` | 1.0 | 1 |  | Pattern types are explicitly identified as chevron-like waves and stripes with directional banding. |
| `primary_color` | 1.0 | 1 |  | The main outer coat is centered in golden beige/cream tones, making the primary color readable. |
| `secondary_color` | 1.0 | 1 |  | Secondary colors are clearly present in the trim and especially the visible striped underlayer, with the contrast anchored by the open coat. |
| `silhouette` | 1.0 | 1 |  | It explicitly describes the overall silhouette and structural relationship between outer and inner layers. |
| `surface_finish` | 1.0 | 1 |  | Surface qualities are clearly described as tactile, shaggy, textured, and flatter, which supports finish/hand-feel coverage. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes overall vertical proportion and silhouette balance, with a long outer coat, layered torso, and elongated shape. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are correctly tied to the coat, the black underlayer, and the striped inner piece. The only slight ambiguity is the “belt or tab detail,” which is described as crossing near the waist  |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The text prioritizes visible garment structure and surface detail, with only a small amount of styling/mood language. It is somewhat layered and descriptive, but not essay-like or template-driven. |
| `craft_embellishment_salience` | 0.75 | 1 | 工艺装饰显著度 | Craft and surface treatment are clearly described by type and placement, especially the textured coat surface and edge trim, though the functional visual role is implied rather than fully unpacked. |
| `design_distinctiveness` | 0.75 | 1 | 设计独特性 | The look has at least one clear memory point in the shaggy chevron-textured coat, plus a strong graphic striped underlayer and trim contrast. It is distinctive without reading as a generic formula. |
| `design_signal_purity` | 1.0 | 1 | 设计信号纯度 | The text is dominated by concrete design facts, materials, structure, color, and placement, with only a brief mood phrase at the end. |
| `fine_grained_attribute_usage` | 1.0 | 1 | 术语具体度 | Attributes are richly and precisely specified across color, texture, structure, and pattern, giving a highly detailed and imageable fashion description. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly visual and already organized around silhouette, garment hierarchy, and material/color contrasts, so it is close to a usable generation prompt. It is still somewhat explanatory and r |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a mostly natural top-level-to-detail order: outer coat, underlayer, inner striped piece, then accessories and styling. It is clear and easy to reconstruct, though some material |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text clearly distinguishes multiple garments and generally keeps their attributes separated: coat, black layer, and striped inner piece. There is minor cross-layer complexity around the chest open |
| `quantity_accuracy` | 1.0 | 1 | 语言清晰度 | The text uses quantity/size relations clearly and consistently; there are no conflicting counts or ambiguous numerical references. |
| `reference_clarity` | 0.75 | 1 | 语言清晰度 | References are mostly clear and sequential, with each layer explicitly anchored, though the dense layering description creates slight reading load. |
| `silhouette_combination_originality` | 0.75 | 1 | 组合原创性 | The combination is more specific and layered than a standard formula, with an oversized textured coat over a tailored open chest layer and graphic inner piece. It is still somewhat legible and wearabl |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and attachment relationships are clearly described and visually reconstructable. The only minor issue is that some inner-layer structure is described in a dense, interpretive way, but the ove |
| `specific_noun_usage` | 1.0 | 1 | 术语具体度 | Uses highly specific fashion nouns and garment terms throughout, with clear references to coat, lapels, neckline, underlayer, and earrings. |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | The description foregrounds the most visible, image-defining elements of the outfit. There is some less-critical styling language, but it does not overpower the clothing facts. |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is tightly anchored to visible garment zones and layered structure, with clear observations of collar, front edges, neckline, waist detail, and texture. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.25 | There is a mild trunk-level tension between the tailored black layer and the asymmetric striped underlayer, but no strong left-right split or mutually exclusive garment identities. |
| `coordination_penalty` | 0.25 | The look is broadly coherent, but the outer coat’s shaggy texture and the sharp graphic underlayer create a moderate styling contrast rather than a fully unified mood. |
| `formula_template_penalty` | 0.0 | The text is a compact prose description without obvious template headers or formulaic sectioning. |
| `generation_content_penalty` | 0.25 | Mostly imageable garment description with a clear trunk; only mild runway-style framing and evaluative wording reduce prompt efficiency. |
| `rationality_penalty` | 0.0 | The described materials and construction are stylized but physically plausible for fashion imagery. |

## Missing coverage (未覆盖)

- **`fabric_family`** — The text describes texture and surface feel, but does not clearly identify a material family such as wool, knit, leather, silk, or denim.

## Skipped metrics (不适用)

- `shoulder_architecture` (coverage_score) — No prominent shoulder construction such as pads, off-shoulder, or strapless design is described.
- `closure` (coverage_score) — No explicit closure mechanism such as buttons, zipper, ties, or buckle is described.
- `deconstruction` (coverage_score) — The text does not explicitly describe deconstruction, splicing, displacement, or reconstruction.
- `hardware_embellishment` (coverage_score) — No salient hardware or metallic embellishment such as chains, studs, rings, or crystals is described.
- `bag` (coverage_score) — No bag is mentioned or implied as a visible styling element.
- `footwear` (coverage_score) — No footwear is described.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral distinction is described.
- `cultural_reference` (bonus_score) — No clear cultural, historical, or brand reference is provided.
- `gender_expression` (bonus_score) — The description does not explicitly discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is explicitly stated.
- `brand_alignment` (bonus_score) — The text does not target a specific brand identity or brand language.
- `negation_control` (bonus_score) — The text does not emphasize exclusions or absence of elements.
