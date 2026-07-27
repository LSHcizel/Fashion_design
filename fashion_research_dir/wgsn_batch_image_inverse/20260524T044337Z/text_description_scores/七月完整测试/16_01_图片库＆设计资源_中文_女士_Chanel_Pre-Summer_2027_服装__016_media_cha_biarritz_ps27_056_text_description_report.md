# Text Evaluation Report

- **Source:** 16_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__016_media_cha_biarritz_ps27_056_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.8563 (Strong)
- **Coverage axis:** 0.9444
- **Quality axis (raw / base / penalized):** 0.8269 / 0.8333 / 0.8333
- **Penalties (mean):** 0.1
- **R_content:** 0.826329

## Gates

- Score gate: 0.8563 (threshold 0.7) → **PASS**
- Penalty gate: 0.1 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `bag` | 1.0 | 1 |  | Bag type and carrying method are explicit, and the shape/material are described. |
| `body_coverage` | 1.0 | 1 |  | The text clearly indicates coverage at the neck and exposed arms/shoulders through the sleeveless cut. |
| `color_relationship_logic` | 1.0 | 1 |  | The text provides a clear multicolor floral palette with a dominant red base and supporting accent colors, making the color relationship understandable. |
| `cross_garment_binding` | 1.0 | 1 |  | The description distinguishes which features belong to the top, skirt, and accessories, making the multi-item relations clear. |
| `fabric_family` | 0.0 | 0 |  | The text describes print, structure, and feather-like embellishment, but does not clearly identify the主体材质类别 of the main garment fabric. |
| `functional_detail` | 1.0 | 1 |  | The text clearly mentions functional-style front pocket panels as a salient detail. |
| `garment_category` | 1.0 | 1 |  | The text clearly identifies the main garment category as a coordinated top-and-skirt set. |
| `hardware_embellishment` | 1.0 | 1 |  | Metal ring embellishments are explicitly described and are visually salient. |
| `jewelry` | 1.0 | 1 |  | Visible body adornment is present, including bracelet-like wrist pieces and ring details. |
| `layering` | 1.0 | 1 |  | The look explicitly describes a layered top-over-skirt relationship with a clear separation line. |
| `length_hemline` | 1.0 | 1 |  | The description includes length-related information through the vertical fall of the trim and the skirt’s full front extension. |
| `pattern_type` | 1.0 | 1 |  | The pattern type is clearly identified as floral, with additional motif detail. |
| `primary_color` | 1.0 | 1 |  | Red is clearly established as the dominant primary color. |
| `secondary_color` | 1.0 | 1 |  | Multiple secondary colors are explicitly named and visually anchored in the garment and accents. |
| `shoulder_architecture` | 1.0 | 1 |  | Shoulder design is explicitly described as broad and sleeveless, making the shoulder architecture salient. |
| `silhouette` | 1.0 | 1 |  | It gives a clear structural silhouette for both pieces: fitted/structured on top and slim columnar below. |
| `surface_finish` | 1.0 | 1 |  | The description clearly conveys surface qualities, especially texture and a polished finish. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes the relationship between upper and lower garments, including the waist/hip separation and the slim columnar skirt silhouette. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are bound to the correct entities, and the top/skirt/accessories are clearly distinguished. Minor ambiguity remains in phrases like “feather or petal-like ruffle” and “wrist cuffs or b |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is mostly concentrated on visible garment facts and construction, with only a brief mood closing. It is somewhat verbose, but not essay-like and the main outfit details remain dominant |
| `craft_embellishment_salience` | 1.0 | 1 | 工艺装饰显著度 | Craft and embellishment are clearly specified by type, placement, and visual effect, and they function as major design hooks. |
| `design_distinctiveness` | 1.0 | 1 | 设计独特性 | The look has multiple clear memory points: an unusual neck ruffle/trim, feather-plume pocket accents with ring details, and a vivid floral textile. This is far beyond a formula resort combination. |
| `design_signal_purity` | 0.75 | 1 | 设计信号纯度 | Most of the text is concrete design description, but the closing mood statement adds some non-design framing. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly visual and mostly prompt-ready, with clear garment type, silhouette, layering, and decorative details. It is still somewhat explanatory and verbose, but only needs light cleanup to  |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | 整体按主体造型→上装/下装结构→细节装饰→配饰的顺序展开，主线清楚，能稳定重建服装层级；但中段对领口、胸前装饰、口袋状面板和花纹细节的描述较密集，略有压缩感。 |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The multi-garment relations are mostly clear: the patterned textile, trim, and seam are consistently tied to the top and skirt. There is slight cross-garment ambiguity in the shared central trim conti |
| `reference_clarity` | 1.0 | 1 | 语言清晰度 | References are consistently anchored to clear nouns, and the few pronouns/ellipses are easy to resolve without ambiguity. |
| `silhouette_combination_originality` | 0.75 | 1 | 组合原创性 | The silhouette is coherent and distinctive, especially with the column skirt and central feather trim, though the base top-and-skirt pairing remains relatively straightforward. |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and attachment relationships are clear and imageable, especially the top-over-skirt structure and central trim continuity. Minor ambiguity remains in the feather/petal ruffle description, but |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | The text prioritizes visible, imageable clothing features and accessories. The mood phrase at the end is present but does not overwhelm the concrete outfit description. |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly anchored in visible garment facts and positions, with clear body-zone references and little mood-only prose. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | The top and skirt read as a coherent single look with no trunk-level left-right or material conflicts. |
| `coordination_penalty` | 0.0 | Accessories support the look without creating trunk-level styling conflict; overall coordination is consistent. |
| `formula_template_penalty` | 0.25 | Some runway-essay framing and mood language are present, but the description remains fairly specific and craft-oriented rather than fully formulaic. |
| `generation_content_penalty` | 0.25 | Mostly grounded garment description, but ends with mood/framing language that adds some prompt dilution. |
| `rationality_penalty` | 0.0 | The materials are decorative but still plausible as fashion embellishment; no clear physical impossibility is asserted. |

## Missing coverage (未覆盖)

- **`fabric_family`** — The text describes print, structure, and feather-like embellishment, but does not clearly identify the主体材质类别 of the main garment fabric.

## Skipped metrics (不适用)

- `closure` (coverage_score) — No explicit closure mechanism such as buttons, zipper, ties, or buckle is described.
- `construction_technique` (coverage_score) — It describes texture and trim, but not a specific construction technique with a clear technique-plus-placement pairing.
- `deconstruction` (coverage_score) — No deconstruction, splicing, displacement, or reconstruction is explicitly mentioned.
- `footwear` (coverage_score) — No footwear is mentioned in the text.
- `belt` (coverage_score) — No visible belt, sash, or waist strap is described; the waist seam is structural, not a belt.
- `asymmetry` (coverage_score) — No clear asymmetrical or uneven garment structure is described.
- `quantity_accuracy` (quality_score) — The text does not use explicit counts or quantity relations that need verification.
- `bilateral_coherence` (quality_score) — No explicit left-right asymmetry or bilateral garment differences are described.
- `cultural_reference` (bonus_score) — No cultural, historical, or brand-specific reference is provided.
- `gender_expression` (bonus_score) — The text does not explicitly discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is stated beyond the outfit description.
- `brand_alignment` (bonus_score) — No brand identity or brand-language target is mentioned.
- `negation_control` (bonus_score) — The text does not emphasize exclusions or absence of elements.
