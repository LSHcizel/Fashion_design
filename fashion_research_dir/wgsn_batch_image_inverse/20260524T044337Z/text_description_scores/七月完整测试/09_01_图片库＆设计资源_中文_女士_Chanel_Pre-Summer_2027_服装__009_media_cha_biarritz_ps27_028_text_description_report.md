# Text Evaluation Report

- **Source:** 09_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__009_media_cha_biarritz_ps27_028_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.1
- **Total score (S_fp):** 0.848 (Strong)
- **Coverage axis:** 0.9444
- **Quality axis (raw / base / penalized):** 0.8333 / 0.8227 / 0.8227
- **Penalties (mean):** 0.05
- **R_content:** 0.83316

## Gates

- Score gate: 0.848 (threshold 0.7) → **PASS**
- Penalty gate: 0.05 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `asymmetry` | 1.0 | 1 |  | An uneven/off-center structural detail is explicitly stated, so asymmetry is present and covered. |
| `body_coverage` | 1.0 | 1 |  | The text clearly describes exposed body areas: chest/neckline and leg reveal. |
| `closure` | 1.0 | 1 |  | A clear button-front closure is described, along with additional buttoned pocket details. |
| `color_relationship_logic` | 1.0 | 1 |  | 文本明确交代了主次色与强对比配色逻辑，属于奶油色主体配黑色与金色点缀的关系。 |
| `cross_garment_binding` | 1.0 | 1 |  | The description clearly distinguishes which attributes belong to the jacket, inner top, and skirt, satisfying multi-garment binding. |
| `fabric_family` | 1.0 | 1 |  | 主体材质类别明确为tweed（粗花呢）. |
| `functional_detail` | 1.0 | 1 |  | The text explicitly mentions functional pocket details and a skirt slit. |
| `garment_category` | 1.0 | 1 |  | The text clearly names the main garment categories: jacket, top, and skirt. |
| `hardware_embellishment` | 0.0 | 0 |  | Buttons are present, but the text does not clearly describe the kind of salient hardware embellishment targeted by this metric, such as chains, studs, rings, or crystals. |
| `jewelry` | 1.0 | 1 |  | A salient jewelry item is explicitly present and visually emphasized. |
| `layering` | 1.0 | 1 |  | The text clearly describes a layered outfit with an outer jacket over an inner top and a skirt below. |
| `length_hemline` | 1.0 | 1 |  | The text gives clear length and hemline information, including a slit. |
| `primary_color` | 1.0 | 1 |  | 主色清晰为米白/奶油色。 |
| `secondary_color` | 1.0 | 1 |  | 存在明确副色黑色，并伴随金色点缀。 |
| `shoulder_architecture` | 1.0 | 1 |  | Dropped sleeves indicate salient shoulder construction. |
| `silhouette` | 1.0 | 1 |  | Overall shape and structural contour are explicitly described. |
| `surface_finish` | 1.0 | 1 |  | 文本给出了明显的表面/质感信息，包括纹理、光泽与挺括感。 |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes the upper and lower silhouette relationship, including an oversized jacket versus a fitted high-waisted skirt, so proportion is explicitly covered. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are clearly tied to the correct garment or accessory, and the layering is understandable. There is only minor ambiguity in phrases like “scarf-like black panels or lapels,” but it does |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is compact and heavily centered on visible garment structure, materials, and silhouette. There is some stylistic framing at the end, but it does not overwhelm the clothing facts. |
| `craft_embellishment_salience` | 0.75 | 1 | 工艺装饰显著度 | Craft and detail are clearly located and visually relevant, though the description relies more on trim, buttons, and piping than on a deeply articulated construction technique. |
| `design_distinctiveness` | 0.75 | 1 | 设计独特性 | The look has clear non-formula anchors: textured tweed, strong black trim/piping contrast, and an off-center slit. Distinctive, though not highly experimental. |
| `design_signal_purity` | 1.0 | 1 | 设计信号纯度 | The text is dominated by concrete design facts, materials, placement, and structure, with minimal mood language. |
| `fine_grained_attribute_usage` | 1.0 | 1 | 术语具体度 | Attributes are described with fine-grained color, material, construction, and structural detail, making the look highly imageable and precise. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly visual, garment-specific, and already close to a prompt. It clearly states silhouette, layers, materials, colors, and key details, though it still reads a bit like a descriptive fas |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a mostly natural order from overall look to jacket, inner top, skirt, and accessories/color finish. Structure is easy to reconstruct, though some detail clusters are dense and  |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text keeps jacket, inner top, skirt, and accessories mostly distinct, with their colors and details attached to the right items. The only slight risk is some overlap in describing the jacket/front |
| `reference_clarity` | 1.0 | 1 | 语言清晰度 | References are consistently anchored to clear garment subjects, and the layering sequence is easy to follow without pronoun confusion. |
| `silhouette_combination_originality` | 0.75 | 1 | 组合原创性 | The combination is coherent and somewhat distinctive, especially with the oversized jacket over a fitted deep-V top and slit skirt, but it remains within a polished luxury tailoring framework. |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and attachment relationships are clear and imageable, with coherent front opening, underlayer, and skirt slit placement. Minor ambiguity remains in phrases like “scarf-like panels or lapels,” |
| `specific_noun_usage` | 1.0 | 1 | 术语具体度 | Uses highly specific fashion nouns and garment names, with clear material and accessory terminology throughout. |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | Most details are image-dominant and directly visible. A few lower-priority interpretive phrases like “reads polished, structured, and couture-like” are present, but they do not dominate the prompt. |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | Highly grounded in visible garment observations with precise body/garment anchors and clear layering description. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | The jacket, inner top, and skirt are coherent and do not present trunk-level left-right or garment-identity conflicts. |
| `coordination_penalty` | 0.0 | The palette and accessories are coordinated; no major trunk-level styling clash is present. |
| `formula_template_penalty` | 0.0 | No fixed four-section template, bullet formula, or brand-symbol stacking is present. |
| `generation_content_penalty` | 0.25 | Mostly imageable garment description, but it includes runway/editorial framing and evaluative styling language that slightly reduces prompt efficiency. |
| `rationality_penalty` | 0.0 | The described materials and construction are physically plausible as ordinary fashion garments. |

## Missing coverage (未覆盖)

- **`hardware_embellishment`** — Buttons are present, but the text does not clearly describe the kind of salient hardware embellishment targeted by this metric, such as chains, studs, rings, or crystals.

## Skipped metrics (不适用)

- `pattern_type` (coverage_score) — 未描述具体图案或印花。
- `construction_technique` (coverage_score) — No specific fabrication technique like quilting, pleating, embroidery, or engineered panel work is clearly identified.
- `deconstruction` (coverage_score) — The text does not mention deconstruction, splicing, displacement, or reconstruction.
- `bag` (coverage_score) — No bag is mentioned or implied as a visible styling element.
- `footwear` (coverage_score) — No footwear is described.
- `belt` (coverage_score) — No visible belt, sash, waist cincher, or harness is described.
- `quantity_accuracy` (quality_score) — The text uses a few quantities like "small gold-tone buttons" and "long bright red drop earrings," but there are no explicit count relations or ambiguous numerical references that need quantity verification.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral asymmetry is described.
- `cultural_reference` (bonus_score) — No cultural, historical, or brand reference is provided.
- `gender_expression` (bonus_score) — The text does not explicitly discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is stated.
- `brand_alignment` (bonus_score) — No brand identity or brand-language target is mentioned.
- `negation_control` (bonus_score) — The description does not emphasize exclusions or absence of elements.
