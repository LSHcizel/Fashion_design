# Text Evaluation Report

- **Source:** 17_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__017_media_cha_biarritz_ps27_057_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.8672 (Strong)
- **Coverage axis:** 1.0
- **Quality axis (raw / base / penalized):** 0.8214 / 0.8333 / 0.8333
- **Penalties (mean):** 0.1
- **R_content:** 0.836848

## Gates

- Score gate: 0.8672 (threshold 0.7) → **PASS**
- Penalty gate: 0.1 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `bag` | 1.0 | 1 |  | The text clearly gives bag type, shape/structure, and surface/handle details. |
| `closure` | 1.0 | 1 |  | The coat’s opening and buttoned front/cuff details clearly indicate a closure structure. |
| `color_relationship_logic` | 1.0 | 1 |  | The text explains a coherent cool-toned palette with tonal layering and blue-and-white coordination. |
| `cross_garment_binding` | 1.0 | 1 |  | The text distinguishes the coat, handbag, and shoes as separate items and explains how the accessories relate to the main garment. |
| `footwear` | 1.0 | 1 |  | It specifies the shoe family, toe/strap form, and finish/color. |
| `functional_detail` | 1.0 | 1 |  | A functional bag detail and its chain handle are explicitly described. |
| `garment_category` | 1.0 | 1 |  | The main garment category is explicitly identified as a coat/coat-dress. |
| `hardware_embellishment` | 1.0 | 1 |  | Chain hardware and metallic buttons are clearly present as embellishing/structural hardware elements. |
| `length_hemline` | 1.0 | 1 |  | Garment length is explicitly stated. |
| `pattern_type` | 1.0 | 1 |  | The pattern type is explicitly identified as floral. |
| `primary_color` | 1.0 | 1 |  | The dominant color story is clearly blue/aqua. |
| `secondary_color` | 1.0 | 1 |  | Secondary colors are clearly present as aqua and white accents against the blue base. |
| `silhouette` | 1.0 | 1 |  | The text clearly describes the overall silhouette as straight and narrow-column. |
| `surface_finish` | 1.0 | 1 |  | Surface qualities are explicitly described, including gloss on the shoes and plush feather texture on the garment. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes the garment’s vertical silhouette and overall proportion, indicating a slim upper body and elongated lower line. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are clearly attached to the correct entity, including coat details, bag, and shoes. Minor ambiguity remains in phrases like “coat or coat-dress” and the waist/hip feather bands, but th |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is mostly garment-focused and imageable, with clear main-piece, trim, bag, and shoe details. There is some stylistic framing and color-story commentary, but it does not significantly d |
| `craft_embellishment_salience` | 1.0 | 1 | 工艺装饰显著度 | The craft is clearly specified by type, location, and visual effect, and it functions as a main hook of the look. |
| `design_distinctiveness` | 1.0 | 1 | 设计独特性 | The look has multiple clear memory points: unusual feather trim placement, horizontal feather bands, and a vivid floral surface pattern. These are distinctive craft/trim features, not a formula outfit |
| `design_signal_purity` | 1.0 | 1 | 设计信号纯度 | The text is dominated by concrete design facts, materials, placement, and accessories, with essentially no mood or essay-like dilution. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly imageable and already organized around visible garment form, surface treatment, accessories, and footwear, so it is close to a usable prompt. It is still somewhat explanatory and re |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a mostly natural body-to-details order: main garment, then construction details, then accessories and shoes. Minor repetition and some dense embellishment phrasing slightly int |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text keeps the coat, handbag, and footwear mostly distinct and correctly described. There is slight ambiguity around whether the main garment is a coat or coat-dress, but no major cross-item attri |
| `quantity_accuracy` | 0.75 | 1 | 语言清晰度 | Quantities and repeated placements are mostly clear and internally consistent, but some phrasing is slightly dense and requires careful parsing of where the repeated details occur. |
| `reference_clarity` | 0.75 | 1 | 语言清晰度 | References are generally explicit and easy to track, with clear subject shifts between garment and model. Minor complexity comes from long descriptive sentences, but pronouns and omitted subjects rema |
| `silhouette_combination_originality` | 0.75 | 1 | 组合原创性 | The silhouette is coherent and somewhat distinctive due to the coat-dress column shape and ornate surface treatment, though the overall styling remains a fairly polished runway-luxury combination. |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and attachment positions are clearly described and visually coherent, with readable vertical and horizontal placement cues. The spatial logic is strong, though the text remains somewhat descr |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | The text prioritizes visible, dominant surface details and silhouette-defining elements. It includes a small amount of styling summary, but hidden or low-visibility information does not dominate. |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly anchored in visible garment parts and placement, with clear body-zone references and little to no mood essaying. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | No trunk-level left-right or garment-identity conflict; the look reads as one coherent coat-dress, bag, and shoe ensemble. |
| `coordination_penalty` | 0.0 | Color and styling cues are aligned across the main pieces, with no major coordination clash in the trunk garments or footwear. |
| `formula_template_penalty` | 0.25 | A fairly standard runway-description template with coherent garment facts; some formulaic styling language, but not heavily interchangeable or brand-symbol driven. |
| `generation_content_penalty` | 0.25 | Mostly grounded garment description, but the runway framing and styling summary add some evaluative prose beyond pure imaging. |
| `rationality_penalty` | 0.0 | The materials and construction are ornate but still physically plausible as fashion detailing. |

## Skipped metrics (不适用)

- `shoulder_architecture` (coverage_score) — The text mentions a close fit through the shoulders, but not a distinct shoulder design such as padding, drop shoulder, off-shoulder, or similar salient architecture.
- `body_coverage` (coverage_score) — No meaningful skin exposure or cutout/reveal is described; the look is fully covered.
- `fabric_family` (coverage_score) — The text describes color, trim, and tailoring, but does not clearly name the main fabric family.
- `construction_technique` (coverage_score) — No specific fabrication technique like pleating, quilting, embroidery, cut-outs, or engineered panel construction is clearly named.
- `deconstruction` (coverage_score) — The text does not mention deconstruction, splicing, displacement, or reconstruction.
- `jewelry` (coverage_score) — No salient jewelry or body ornament is described.
- `belt` (coverage_score) — No visible belt, sash, waist cincher, or harness is mentioned; the waist emphasis comes from garment cut and trim placement.
- `layering` (coverage_score) — The look is described as a single coat/coat-dress rather than a clear multi-layer outfit with explicit layering relations.
- `asymmetry` (coverage_score) — No asymmetrical construction, one-sided detail, or uneven structure is described.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral distinction is described.
- `cultural_reference` (bonus_score) — No cultural, historical, or brand reference is provided.
- `gender_expression` (bonus_score) — The text does not explicitly discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is stated.
- `brand_alignment` (bonus_score) — No brand language or brand identity is mentioned.
- `negation_control` (bonus_score) — The text does not emphasize exclusions or absence of elements.
