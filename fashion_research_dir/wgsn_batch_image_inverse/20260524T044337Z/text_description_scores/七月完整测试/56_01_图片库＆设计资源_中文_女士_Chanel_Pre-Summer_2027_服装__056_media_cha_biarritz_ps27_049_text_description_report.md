# Text Evaluation Report

- **Source:** 56_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__056_media_cha_biarritz_ps27_049_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.8207 (Strong)
- **Coverage axis:** 0.9333
- **Quality axis (raw / base / penalized):** 0.7885 / 0.7917 / 0.7917
- **Penalties (mean):** 0.1
- **R_content:** 0.791975

## Gates

- Score gate: 0.8207 (threshold 0.7) → **PASS**
- Penalty gate: 0.1 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `asymmetry` | 1.0 | 1 |  | The look includes uneven, side-specific construction and hanging panels, which clearly establish asymmetrical design elements. |
| `body_coverage` | 1.0 | 1 |  | The description includes visible coverage and exposure boundaries, especially at the neckline and torso framing. |
| `color_relationship_logic` | 1.0 | 1 |  | The text gives a clear layered color logic: warm ivory/cream base with black graphic contrast, supported by brown inner layering and gold accents. |
| `cross_garment_binding` | 1.0 | 1 |  | The description distinguishes which features belong to the top, outer layer, and skirt, so the multi-garment relations are clearly assigned. |
| `fabric_family` | 0.0 | 0 |  | The text suggests construction and handfeel, but it does not clearly name a主体材质类别 such as wool, silk, cotton, leather, denim, etc. |
| `garment_category` | 1.0 | 1 |  | The text clearly identifies the main garment types: a tailored layered outfit with an outer layer, top, and skirt. |
| `hardware_embellishment` | 1.0 | 1 |  | Chain trim and chain details are clear hardware/embellishment elements. |
| `jewelry` | 1.0 | 1 |  | Visible chain accents function as jewelry/body ornament details and are explicitly present. |
| `layering` | 1.0 | 1 |  | The text clearly describes a layered outfit with readable inner top, outer layer, and hanging side panels. |
| `length_hemline` | 1.0 | 1 |  | The text gives clear length information and hemline details. |
| `primary_color` | 1.0 | 1 |  | The main color story is clearly stated, with cream/ivory as the dominant light tone and black as the key contrast. |
| `secondary_color` | 1.0 | 1 |  | Secondary colors are explicitly present and anchored to visible garment parts, especially the brown inner top plus black and gold accents. |
| `silhouette` | 1.0 | 1 |  | It explicitly describes the overall shape and structural contour of the look. |
| `surface_finish` | 1.0 | 1 |  | Surface traits are clearly described, including smoothness, drape, and a textured/embellished finish. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes the upper-to-lower body framing and the relationship between the fitted top and knee-length skirt, making the top-bottom proportion visually explicit. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are clearly attached to the correct garment, and the layering is coherent. Minor ambiguity remains around some decorative black bands and chain trim, but there is no major cross-bindin |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is compact and heavily garment-focused, with clear visible construction details and little mood prose. There is some stylistic framing (“runway look,” “polished, graphic, and dressy”), |
| `craft_embellishment_salience` | 0.75 | 1 | 工艺装饰显著度 | Craft and embellishment are clearly identified by type and placement, and they function as visible accents, though the description is more detailed than deeply technical. |
| `design_distinctiveness` | 0.75 | 1 | 设计独特性 | The look has clear non-formula memory points through graphic banding, chain trim, and layered side panels, though it is still within a polished tailored framework rather than highly radical. |
| `design_signal_purity` | 1.0 | 1 | 设计信号纯度 | The text is dominated by concrete design observations, with very little mood or essay-like framing, so the design signal remains highly pure. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly imageable and already organized around visible silhouette, garment types, layering, palette, and trim details, so it is close to a usable generation prompt. It is still somewhat exp |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description moves in a mostly natural order from overall framing to main layers, then top, bottom, and finishing details. Structure is easy to reconstruct, though some later embellishment details  |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text distinguishes top, outer layer, and skirt well, with their colors and structural details mostly bound to the right items. A few details like the black bands and chain accents require careful  |
| `reference_clarity` | 1.0 | 1 | 语言清晰度 | References and spatial relations are consistently anchored to clear nouns, with no confusing pronoun chains or ambiguous omissions. |
| `silhouette_combination_originality` | 0.5 | 0 | 组合原创性 | The combination is coherent and somewhat distinctive through the open layered outer piece and skirt construction, but it remains a fairly safe tailored-luxury silhouette rather than a highly unexpecte |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering, openings, hem framing, and hanging side panels are described in a visually coherent way that should be easy to image. The spatial relations are clear overall, with only minor complexity from |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | The text prioritizes visible silhouette, layering, trim, and hem details that would matter in an image. It includes a few lower-salience details like chain trim, but these remain secondary to the main |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly anchored in visible garment facts and precise locations, with clear layering and edge details that read like direct runway observation. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | The main garments read as a coherent layered look without trunk-level left-right contradictions or mutually exclusive identities. |
| `coordination_penalty` | 0.0 | Color, trim, and silhouette are coordinated into one unified graphic palette; no major styling clash across trunk garments. |
| `formula_template_penalty` | 0.25 | Some generic fashion-prose phrasing is present, but the description still contains specific craft and construction details rather than a fully interchangeable formula. |
| `generation_content_penalty` | 0.25 | Mostly grounded garment description, but ends with some evaluative styling language that slightly dilutes prompt efficiency. |
| `rationality_penalty` | 0.0 | All described materials and construction details are physically plausible as ordinary fashion design. |

## Missing coverage (未覆盖)

- **`fabric_family`** — The text suggests construction and handfeel, but it does not clearly name a主体材质类别 such as wool, silk, cotton, leather, denim, etc.

## Quality issues (质量短板)

- **`silhouette_combination_originality`** (score 0.5) — The combination is coherent and somewhat distinctive through the open layered outer piece and skirt construction, but it remains a fairly safe tailored-luxury silhouette rather than a highly unexpected formula.

## Skipped metrics (不适用)

- `shoulder_architecture` (coverage_score) — No prominent shoulder construction is described.
- `pattern_type` (coverage_score) — No explicit print or pattern type is described; the black bands read as construction lines/edging rather than a pattern.
- `closure` (coverage_score) — No explicit closure mechanism such as buttons, zipper, ties, or buckle is described.
- `functional_detail` (coverage_score) — The text does not clearly mention pockets, straps, or other functional utility details.
- `construction_technique` (coverage_score) — No notable fabrication technique is explicitly identified; the description stays at the level of silhouette, trim, and paneling.
- `deconstruction` (coverage_score) — The text does not mention deconstruction, splicing, displacement, or reconstruction.
- `bag` (coverage_score) — No bag is described or implied as a visual element of the look.
- `footwear` (coverage_score) — The text stops at the knees and does not mention any shoes.
- `belt` (coverage_score) — No actual belt, sash, waist strap, or harness is described; the waist shaping comes from garment cut.
- `quantity_accuracy` (quality_score) — The text contains no explicit counts or quantity relations that need verification.
- `bilateral_coherence` (quality_score) — No explicit left-right bilateral difference is described for sleeves, legs, shoes, shoulders, or hand accessories.
- `cultural_reference` (bonus_score) — No cultural, historical, or brand reference is provided.
- `gender_expression` (bonus_score) — The description does not explicitly discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is stated.
- `brand_alignment` (bonus_score) — No brand identity or brand-language target is mentioned.
- `negation_control` (bonus_score) — The text does not emphasize exclusions or absence of elements.
