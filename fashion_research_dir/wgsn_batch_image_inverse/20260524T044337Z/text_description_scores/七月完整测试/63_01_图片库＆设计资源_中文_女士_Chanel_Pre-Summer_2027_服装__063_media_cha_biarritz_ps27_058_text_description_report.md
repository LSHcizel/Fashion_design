# Text Evaluation Report

- **Source:** 63_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__063_media_cha_biarritz_ps27_058_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.8511 (Strong)
- **Coverage axis:** 1.0
- **Quality axis (raw / base / penalized):** 0.8393 / 0.8125 / 0.8125
- **Penalties (mean):** 0.1
- **R_content:** 0.821311

## Gates

- Score gate: 0.8511 (threshold 0.7) → **PASS**
- Penalty gate: 0.1 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `bag` | 1.0 | 1 |  | Bag is a visible styling element and the text covers category/carry method plus shape and color/material details. |
| `body_coverage` | 1.0 | 1 |  | The text clearly describes both covered and exposed body areas. |
| `closure` | 1.0 | 1 |  | The coat’s opening mechanism is explicitly described and visually salient. |
| `color_relationship_logic` | 1.0 | 1 |  | The text gives a clear color relationship: a black dominant outerwear look with contrasting light footwear and black toe caps. |
| `construction_technique` | 1.0 | 1 |  | The text names a clear construction technique and its placement across the coat body. |
| `cross_garment_binding` | 1.0 | 1 |  | The text distinguishes multiple items and their attributes clearly across garments and accessories, making item-to-item binding unambiguous. |
| `fabric_family` | 1.0 | 1 |  | The main garment’s material family is clearly indicated as leather-like. |
| `footwear` | 1.0 | 1 |  | Footwear is clearly described with shoe type, functional form, and color/detail finish. |
| `functional_detail` | 1.0 | 1 |  | A functional carrying strap and bag details are clearly mentioned. |
| `garment_category` | 1.0 | 1 |  | The main garment category is clearly identified as a coat. |
| `hardware_embellishment` | 1.0 | 1 |  | Visible metallic hardware is explicitly described and is part of the garment’s design. |
| `jewelry` | 1.0 | 1 |  | Earrings are explicitly present and salient enough to count as jewelry. |
| `layering` | 1.0 | 1 |  | The text describes multiple worn and carried elements with clear attachment/placement relations, making the layered arrangement imageable. |
| `length_hemline` | 1.0 | 1 |  | Garment length and hem position are clearly stated. |
| `pattern_type` | 1.0 | 1 |  | The pattern type is explicitly identified as diamond quilting. |
| `primary_color` | 1.0 | 1 |  | Black is clearly stated as the dominant color of the main look. |
| `secondary_color` | 1.0 | 1 |  | Multiple secondary colors are clearly present in the bags and footwear. |
| `shoulder_architecture` | 1.0 | 1 |  | The shoulder treatment is explicitly described, even if subtle rather than exaggerated. |
| `silhouette` | 1.0 | 1 |  | The text explicitly describes the overall silhouette and structural contour. |
| `surface_finish` | 1.0 | 1 |  | The text explicitly describes surface qualities: sheen and quilted texture. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes the garment length and the visible lower-leg proportion, giving a readable top-to-bottom balance. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 1.0 | 1 | 属性绑定准确度 | Attributes are consistently tied to the correct entities: coat, bags, and footwear are clearly separated, with no major cross-binding or left-right confusion. |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is compact and heavily garment-focused, with most space devoted to visible clothing, silhouette, texture, closure, accessories, and shoes. There is some styling/context wording, but no |
| `craft_embellishment_salience` | 0.75 | 1 | 工艺装饰显著度 | The quilting is a salient craft feature and its allover placement is clear. The buttons and sheen support the construction read, though the craft language is not highly elaborate. |
| `design_distinctiveness` | 0.75 | 1 | 设计独特性 | The quilted coat gives a clear craft/texture anchor, and the lattice pumps with black toe caps add a second memorable visual point. The overall look is still fairly luxury-classic, but it is not a gen |
| `design_signal_purity` | 1.0 | 1 | 设计信号纯度 | The text is dominated by concrete design facts—materials, silhouette, closure, and accessories—with essentially no mood or essay framing. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly visual, garment-specific, and mostly prompt-ready, with clear silhouette, materials, and accessories. It reads slightly more like a detailed description than a compact generation pr |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a mostly natural body-to-detail progression: main garment, then styling/accessories, then bags, then footwear. It is clear and imageable, though somewhat dense and slightly com |
| `multi_garment_binding` | 1.0 | 1 | 属性绑定准确度 | Multiple garments and accessories are described with stable, coherent bindings; each set of attributes stays attached to its own item. |
| `quantity_accuracy` | 1.0 | 1 | 语言清晰度 | Quantity and directional relations are explicit and internally consistent; no conflicting counts or ambiguous quantity references. |
| `reference_clarity` | 1.0 | 1 | 语言清晰度 | References are clear and stable throughout, with unambiguous subjects and no confusing pronoun or ellipsis chains. |
| `silhouette_combination_originality` | 0.5 | 0 | 组合原创性 | The combination is coherent and polished, but it remains within a recognizable luxury runway template: structured coat, accessories, and decorative pumps. The bag layering adds interest, but not enoug |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and attachment relations are mostly clear and imageable, especially for the coat closure and stacked bags. The spatial description is coherent enough for generation, though the bag arrangemen |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | The text prioritizes highly visible, image-dominant elements: coat silhouette, quilting, buttons, hem length, exposed legs, bags, and shoes. Minor styling details like sunglasses and earrings are pres |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly anchored in visible garment parts, placement, and silhouette details, with clear front-facing spatial reading and little mood prose. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | No trunk-level left-right conflict or mutually exclusive garment identities; the look reads as a single coherent outerwear outfit. |
| `coordination_penalty` | 0.0 | The coat, bags, and shoes are stylistically aligned into a polished runway look without major coordination clash. |
| `formula_template_penalty` | 0.25 | Slightly template-like runway phrasing and styling-summary language, but the description remains fairly specific and craft-grounded. |
| `generation_content_penalty` | 0.25 | Mostly grounded garment description, but includes some styling/accessory detail that is secondary to the main coat and shoe read. |
| `rationality_penalty` | 0.0 | Materials and construction are plausible as described; no physically implausible garment construction is asserted. |

## Quality issues (质量短板)

- **`silhouette_combination_originality`** (score 0.5) — The combination is coherent and polished, but it remains within a recognizable luxury runway template: structured coat, accessories, and decorative pumps. The bag layering adds interest, but not enough to feel highly unpredictable.

## Skipped metrics (不适用)

- `deconstruction` (coverage_score) — No deconstruction, splicing, displacement, or reconstruction is mentioned.
- `belt` (coverage_score) — No visible belt, sash, waist cincher, or harness is described.
- `asymmetry` (coverage_score) — No asymmetrical or uneven garment structure is described.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral garment differences are described.
- `cultural_reference` (bonus_score) — No cultural, historical, or brand-specific reference is provided.
- `gender_expression` (bonus_score) — The description does not explicitly discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is stated.
- `brand_alignment` (bonus_score) — The text does not target a brand identity or brand language.
- `negation_control` (bonus_score) — The description does not emphasize exclusions or absence as a meaningful design point.
