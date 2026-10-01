# Text Evaluation Report

- **Source:** 66_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__066_media_cha_biarritz_ps27_062_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.8339 (Strong)
- **Coverage axis:** 1.0
- **Quality axis (raw / base / penalized):** 0.7885 / 0.7917 / 0.7917
- **Penalties (mean):** 0.1
- **R_content:** 0.804713

## Gates

- Score gate: 0.8339 (threshold 0.7) → **PASS**
- Penalty gate: 0.1 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `asymmetry` | 1.0 | 1 |  | Asymmetry is directly stated in the waistband/front panel and reinforced by the angled inner-piece construction. |
| `body_coverage` | 1.0 | 1 |  | The text clearly describes exposed and covered body areas through a plunging, cutout-like inner layer. |
| `closure` | 1.0 | 1 |  | The text clearly describes button closures as salient front fastening details. |
| `color_relationship_logic` | 1.0 | 1 |  | The text explains the palette as a strong dark base with contrasting light bands and warm metallic accents, making the color relationship imageable. |
| `construction_technique` | 1.0 | 1 |  | The text identifies a clear cutout/engineered panel construction at the chest with a specific location. |
| `cross_garment_binding` | 1.0 | 1 |  | The description clearly distinguishes how each garment relates to the others, making the multi-item outfit structure readable. |
| `fabric_family` | 1.0 | 1 |  | The text clearly identifies the main garment family as suiting, with an inner bodysuit/top. |
| `functional_detail` | 1.0 | 1 |  | Functional garment details are explicitly named, especially pockets and a wrap-like waistband/front panel. |
| `garment_category` | 1.0 | 1 |  | The text clearly names the main garment categories: blazer, trousers, and an inner top/bodysuit. |
| `hardware_embellishment` | 1.0 | 1 |  | Metallic ornamental hardware is clearly present and visually salient. |
| `jewelry` | 1.0 | 1 |  | A prominent necklace is clearly described as a salient accessory. |
| `layering` | 1.0 | 1 |  | The text clearly describes a layered outfit with an outer blazer over an inner top/bodysuit, with visible relationship between layers. |
| `primary_color` | 1.0 | 1 |  | The dominant palette is clearly dark black/charcoal. |
| `secondary_color` | 1.0 | 1 |  | A clear secondary color contrast is present in the off-white/cream bands against the dark main look, with gold accents as additional color detail. |
| `shoulder_architecture` | 1.0 | 1 |  | Shoulder structure is prominently and specifically described. |
| `silhouette` | 1.0 | 1 |  | It explicitly describes the overall shape and structural silhouette of the look. |
| `surface_finish` | 1.0 | 1 |  | It gives surface/structure traits such as looseness and relaxed volume, plus the blazer is described as tailored and padded, implying a structured finish. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text explicitly describes the upper-lower silhouette balance and proportion between the broad-shouldered top and relaxed trousers. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are bound to the correct garment or body area, and the layering is generally coherent. Minor ambiguity remains in phrases like “top or bodysuit” and “clasp or medallion,” but these do  |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is mostly garment-focused and imageable, with clear trunk details prioritized. There is some stylistic framing and a few interpretive phrases, but not enough to significantly dilute th |
| `craft_embellishment_salience` | 0.75 | 1 | 工艺装饰显著度 | The embellishment and structural detailing are clearly located and described in visual terms, especially the clasp/medallion and decorative buttons. The craft language is still somewhat general, but t |
| `design_distinctiveness` | 0.75 | 1 | 设计独特性 | The look has several clear non-formula anchors: exaggerated shoulders, a lingerie-like contrast bodice with angled bands and clasp, and an asymmetrical trouser waistband. These are distinctive structu |
| `design_signal_purity` | 1.0 | 1 | 设计信号纯度 | The text is dominated by concrete design facts: garment types, proportions, closures, color blocking, and accessory description. Mood language is minimal and does not dilute the design signal. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly visual and mostly prompt-ready, with clear garment hierarchy, silhouette, and material/color cues. It is slightly less than perfect because it includes some interpretive phrasing an |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a mostly natural top-down structure: overall look, blazer/inner layer, trousers, then accessories and styling. It is easy to reconstruct the outfit, though the sentence is dens |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text clearly separates blazer, inner bodice/top, trousers, and necklace, with most properties attached to the right item. There is slight uncertainty in the inner layer naming, but no major cross- |
| `reference_clarity` | 0.75 | 1 | 语言清晰度 | References are mostly clear and the garment subjects are easy to track, with only minor complexity from long layered descriptions and repeated modifiers. |
| `silhouette_combination_originality` | 0.75 | 1 | 组合原创性 | The combination is more original than a standard tailored look because it mixes broad-shouldered suiting, a cutout lingerie-like underlayer, relaxed trousers, and a heavy statement necklace. It is sti |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and attachment relationships are clearly described and imageable, especially the bodice framing and blazer-over-top structure. Minor ambiguity remains in the exact identity of the inner piece |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | Visible, decisive outfit elements are foregrounded, and the text explicitly notes what is not visible. A few lower-visibility details are mentioned, but they do not dominate the prompt. |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly anchored in visible garment parts and spatial relations, and it explicitly marks what is not visible. It reads like a careful runway observation rather than mood prose. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | The main garments read coherently; no strong trunk-level left-right or mutually exclusive construction conflict is present. |
| `coordination_penalty` | 0.0 | The look is stylistically mixed but still coordinated through a consistent dark tailored palette and matching suit language. |
| `formula_template_penalty` | 0.25 | The description is grounded, but it uses some generic runway styling language and a familiar tailored-look formula that is somewhat transferable. |
| `generation_content_penalty` | 0.25 | Mostly concrete garment description, but it includes some runway-style framing and evaluative summary that slightly reduces prompt efficiency. |
| `rationality_penalty` | 0.0 | All described elements are physically plausible fashion construction; no unrealistic material or wearing condition is asserted. |

## Skipped metrics (不适用)

- `length_hemline` (coverage_score) — No clear garment length or hemline detail is given beyond general fit and the note that full trouser length is not visible.
- `pattern_type` (coverage_score) — No pattern or print is described.
- `deconstruction` (coverage_score) — The text does not explicitly mention deconstruction, splicing, displacement, or reconstruction.
- `bag` (coverage_score) — No bag is mentioned or implied as part of the look.
- `footwear` (coverage_score) — Footwear is explicitly not visible, so this metric is not applicable.
- `belt` (coverage_score) — No visible belt, sash, waist cincher, or harness is described; the waist emphasis comes from garment cut.
- `quantity_accuracy` (quality_score) — The text contains no explicit counts or quantity relations that need verification.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral garment differences are described.
- `cultural_reference` (bonus_score) — No clear cultural, historical, or brand reference is provided.
- `gender_expression` (bonus_score) — The description does not explicitly discuss gender expression or androgyny as a concept.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is stated.
- `brand_alignment` (bonus_score) — No explicit brand language or brand identity target is mentioned.
