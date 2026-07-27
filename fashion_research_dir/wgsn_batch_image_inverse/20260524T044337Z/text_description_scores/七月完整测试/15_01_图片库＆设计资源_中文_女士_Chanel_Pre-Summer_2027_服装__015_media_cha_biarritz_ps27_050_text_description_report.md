# Text Evaluation Report

- **Source:** 15_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__015_media_cha_biarritz_ps27_050_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.8168 (Strong)
- **Coverage axis:** 1.0
- **Quality axis (raw / base / penalized):** 0.7857 / 0.7708 / 0.7708
- **Penalties (mean):** 0.1
- **R_content:** 0.788212

## Gates

- Score gate: 0.8168 (threshold 0.7) → **PASS**
- Penalty gate: 0.1 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `bag` | 1.0 | 1 |  | Bag is explicitly present with type, carrying method, and color/material cues. |
| `body_coverage` | 1.0 | 1 |  | The text clearly describes body coverage and reveal through the open jacket and visible underlayer. |
| `closure` | 1.0 | 1 |  | A clear front button closure is described, along with the jacket being worn open. |
| `color_relationship_logic` | 1.0 | 1 |  | The palette is explicitly organized as a burgundy dominant suit with pale contrasting underlayer and light pattern accents, so the color relationship is clearly described. |
| `cross_garment_binding` | 1.0 | 1 |  | The description clearly distinguishes which features belong to the jacket, skirt, and underlayer, making the multi-garment relationships explicit. |
| `fabric_family` | 1.0 | 1 |  | The text identifies the main garment family as a tailored suit and specifies a shirting underlayer, which is enough to infer the fabric family context even without exact fiber content. |
| `functional_detail` | 1.0 | 1 |  | Functional pocket-related details are explicitly mentioned on the jacket. |
| `garment_category` | 1.0 | 1 |  | The text clearly identifies the main garment category as a skirt suit with jacket and skirt. |
| `hardware_embellishment` | 1.0 | 1 |  | Visible metal hardware and embellishment are clearly present. |
| `jewelry` | 1.0 | 1 |  | Salient jewelry is explicitly mentioned. |
| `layering` | 1.0 | 1 |  | Clear multi-layer outfit with readable outer jacket, inner layer, and skirt relationship. |
| `length_hemline` | 1.0 | 1 |  | The text gives clear length and hemline information for both jacket and underlayer. |
| `pattern_type` | 1.0 | 1 |  | The pattern type is clearly specified as a small geometric check/dot micro-pattern. |
| `primary_color` | 1.0 | 1 |  | Burgundy is clearly established as the dominant color of the outfit. |
| `secondary_color` | 1.0 | 1 |  | The text gives clear secondary colors that visibly contrast with the burgundy main suit. |
| `shoulder_architecture` | 1.0 | 1 |  | Shoulder construction is explicitly described as narrow and structured. |
| `silhouette` | 1.0 | 1 |  | Overall shape and structural contour are explicitly described. |
| `surface_finish` | 1.0 | 1 |  | It clearly describes a structured, crisp garment with a tailored silhouette, giving a usable surface/hand impression of firmness rather than drape. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes the relationship between the cropped top and the skirt/underlayer, including where the waistline sits and how the lengths balance. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are clearly tied to the correct garment or accessory, with good separation between jacket, skirt, underlayer, and handbag. Minor ambiguity remains in phrases like “multiple horizontal  |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is dense with visible garment facts and construction details, with only a small amount of styling language at the end. It stays focused on the suit, layers, pattern, trim, and accessor |
| `craft_embellishment_salience` | 0.5 | 0 | 工艺装饰显著度 | Craft and detailing are present and located, but the description stays at a fairly general trim/hardware level rather than a highly specific construction read. |
| `design_distinctiveness` | 0.75 | 1 | 设计独特性 | The look has a clear memory point through the patterned burgundy suit with strong contrast trim and an oversized pointed collar, though it remains within a tailored suit framework. |
| `design_signal_purity` | 1.0 | 1 | 设计信号纯度 | The text is dominated by concrete design facts, with almost no mood or essay-like framing. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly visual and mostly prompt-ready, with clear garment types, layering, silhouette, colors, and accessories. It reads slightly like a descriptive analysis rather than a direct generatio |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a mostly natural progression from overall outfit to jacket, skirt, then accessories. Minor back-and-forth occurs within garment details, but the hierarchy remains easy to track |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text consistently assigns features to the jacket, skirt, underlayer, and accessories without major cross-item confusion. The suit components are well coordinated, and the few descriptive overlaps  |
| `quantity_accuracy` | 1.0 | 1 | 语言清晰度 | The text uses quantities and plural references consistently, with no conflicting counts or unclear side relations. |
| `reference_clarity` | 1.0 | 1 | 语言清晰度 | References are explicit and stable; pronouns are minimal and each garment or accessory is clearly introduced before being described. |
| `silhouette_combination_originality` | 0.5 | 0 | 组合原创性 | The suit silhouette is coherent and polished, with a slightly unusual cropped-over-longer-underlayer proportion, but the overall combination is still a fairly classic tailored look. |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and attachment relationships are clearly described and visually coherent, making the outfit easy to imagine. Minor complexity remains in the dense garment description, but the spatial logic i |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | The text prioritizes visible, image-dominant clothing features and only briefly mentions accessories and overall styling. It does include some lower-priority styling language, but hidden details are n |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is tightly anchored to visible garment parts and layer relationships, with precise placement details and little mood language. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | Main garments read as a coherent suit with no trunk-level left-right or material conflicts. |
| `coordination_penalty` | 0.0 | Overall styling is unified and coordinated; accessories and palette support the suit rather than clash with it. |
| `formula_template_penalty` | 0.25 | A conventional suit formula with some mood language, but still anchored by specific construction details and not heavily template-driven. |
| `generation_content_penalty` | 0.25 | Mostly grounded garment description, but ends with evaluative styling prose that adds little imaging value. |
| `rationality_penalty` | 0.0 | All described materials and construction details are physically plausible for ordinary clothing. |

## Quality issues (质量短板)

- **`craft_embellishment_salience`** (score 0.5) — Craft and detailing are present and located, but the description stays at a fairly general trim/hardware level rather than a highly specific construction read.
- **`silhouette_combination_originality`** (score 0.5) — The suit silhouette is coherent and polished, with a slightly unusual cropped-over-longer-underlayer proportion, but the overall combination is still a fairly classic tailored look.

## Skipped metrics (不适用)

- `construction_technique` (coverage_score) — No notable fabrication technique like pleating, quilting, embroidery, cut-outs, or engineered panel work is clearly described.
- `deconstruction` (coverage_score) — The text does not mention deconstruction, splicing, displacement, or reconstruction.
- `footwear` (coverage_score) — No footwear is described in the text.
- `belt` (coverage_score) — No visible belt, sash, or waist strap is described; the waist emphasis comes from garment cut and layering.
- `asymmetry` (coverage_score) — No asymmetrical design or uneven structure is described.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral asymmetry is described.
- `cultural_reference` (bonus_score) — No cultural, historical, or brand reference is provided.
- `gender_expression` (bonus_score) — The text does not explicitly discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is stated.
- `brand_alignment` (bonus_score) — No brand identity or brand-language target is mentioned.
- `negation_control` (bonus_score) — The text does not emphasize exclusions or absence of elements.
