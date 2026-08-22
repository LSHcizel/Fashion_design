# Text Evaluation Report

- **Source:** 11_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__011_media_cha_biarritz_ps27_033_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.794 (Strong)
- **Coverage axis:** 0.8824
- **Quality axis (raw / base / penalized):** 0.7692 / 0.7708 / 0.7708
- **Penalties (mean):** 0.1
- **R_content:** 0.76621

## Gates

- Score gate: 0.794 (threshold 0.7) → **PASS**
- Penalty gate: 0.1 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `asymmetry` | 1.0 | 1 |  | An uneven, asymmetrical skirt detail is explicitly described through the front slit and side-hanging panel. |
| `bag` | 1.0 | 1 |  | Bag is explicitly described with type, shape, material, and placement. |
| `body_coverage` | 1.0 | 1 |  | The text explicitly describes exposed areas and coverage level. |
| `closure` | 1.0 | 1 |  | An open-front construction and a side tie/panel clearly indicate a visible closure/opening treatment. |
| `color_relationship_logic` | 1.0 | 1 |  | The text explains the palette as coordinated and tightly controlled, establishing a clear tonal/color relationship rather than just listing colors. |
| `construction_technique` | 0.0 | 0 |  | These describe decorative edging and border treatment, but not a clearly named construction technique like quilting, pleating, embroidery, cut-outs, or engineered panel work with a specific garment zo |
| `cross_garment_binding` | 1.0 | 1 |  | Multiple garments are clearly distinguished and their attributes are assigned to the correct item, with coordinated but separate descriptions for the jacket/cardigan, top, and skirt. |
| `functional_detail` | 0.0 | 0 |  | The text mentions accessories, but no clear garment functional details such as pockets, straps, or utility parts on the clothing. |
| `garment_category` | 1.0 | 1 |  | The text clearly names the main garment categories in the look. |
| `jewelry` | 1.0 | 1 |  | Salient jewelry is clearly present and described. |
| `layering` | 1.0 | 1 |  | The text clearly describes layered garments with an outer layer over an inner top, making the layering relation imageable. |
| `length_hemline` | 1.0 | 1 |  | The description includes length and hemline details, including crop length and slit placement. |
| `pattern_type` | 1.0 | 1 |  | The text clearly identifies the print as a dot motif and also describes geometric border patterning. |
| `primary_color` | 1.0 | 1 |  | The dominant color is clearly burgundy, with white as part of the coordinated palette. |
| `secondary_color` | 1.0 | 1 |  | White is a clear secondary color used across the set and top, with gold as an additional accent. |
| `silhouette` | 1.0 | 1 |  | It gives a clear structural silhouette for both the upper and lower garments. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes the upper and lower proportions and their balance, including a cropped top layer over a slim skirt. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are bound to the correct garment or accessory, and the layered outfit is easy to parse. Minor ambiguity remains in phrases like “jacket or cardigan” and “tie or panel,” but these do no |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is mostly garment-focused and imageable, with clear main pieces, patterning, and accessories. There is some stylistic framing (“runway look,” “maximal and bohemian-luxe,” “resort-ready |
| `craft_embellishment_salience` | 0.75 | 1 | 工艺装饰显著度 | The trim is described with type, placement, and visual function, and it clearly acts as a main design hook. The craft is legible, though not deeply technical. |
| `design_distinctiveness` | 0.75 | 1 | 设计独特性 | The look has a clear memory point in the unusual trim system and coordinated dot motif, with a distinctive stepped border and slit treatment. It is more than a generic resort set, though still within  |
| `design_signal_purity` | 0.75 | 1 | 设计信号纯度 | Most of the text is devoted to concrete design facts: garment types, patterning, trim, slit, and accessories. There is some mood language like “maximal and bohemian-luxe” and “resort-ready feel,” but  |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is already close to a usable fashion prompt: it clearly specifies silhouette, garment categories, layering, palette, and accessories. Minor prompt-readiness issues remain because it uses some |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a mostly natural order from overall look to jacket/top, then skirt, then accessories and palette. It is easy to reconstruct the outfit, though some detail clusters are dense an |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text clearly separates the outer layer, top, skirt, jewelry, and bag, with the coordinated pattern and trim consistently attached to the correct garments. There is slight naming ambiguity in a few |
| `reference_clarity` | 1.0 | 1 | 语言清晰度 | References and ellipses are clear throughout; each garment element is anchored to a specific subject, and the description is easy to parse without ambiguity. |
| `silhouette_combination_originality` | 0.5 | 0 | 组合原创性 | The combination is coherent and polished, but it still sits within a familiar resort-luxe formula of cropped layer, simple top, slim skirt, and small bag. The trim adds interest, yet the overall silho |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and attachment positions are mostly clear and visually reconstructable: outer layer over top, diagonal trim along the slit, and a side-hanging tie/panel. The only slight ambiguity is the jack |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | The text prioritizes visible, renderable clothing details and silhouette cues. Mood language is present, but it remains secondary to the clearly observable outfit structure and surface design. |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly anchored in visible garment parts and placement, with clear front-opening, neckline, hem, and slit observations. It reads like a direct visual caption rather than mood pros |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | The trunk garments read coherently with no left-right or mutually exclusive construction conflict. |
| `coordination_penalty` | 0.0 | The outfit’s color and styling language is unified; accessories support rather than clash with the main look. |
| `formula_template_penalty` | 0.25 | The look uses a familiar resort/runway formula, but it remains fairly specific and craft-grounded rather than fully interchangeable. |
| `generation_content_penalty` | 0.25 | Mostly grounded garment description, but the closing styling/mood language adds some conceptual runway prose and accessory stacking that slightly reduces prompt efficiency. |
| `rationality_penalty` | 0.0 | No physically implausible materials or wearing constructions are described. |

## Missing coverage (未覆盖)

- **`functional_detail`** — The text mentions accessories, but no clear garment functional details such as pockets, straps, or utility parts on the clothing.
- **`construction_technique`** — These describe decorative edging and border treatment, but not a clearly named construction technique like quilting, pleating, embroidery, cut-outs, or engineered panel work with a specific garment zone.

## Quality issues (质量短板)

- **`silhouette_combination_originality`** (score 0.5) — The combination is coherent and polished, but it still sits within a familiar resort-luxe formula of cropped layer, simple top, slim skirt, and small bag. The trim adds interest, yet the overall silhouette mix is not highly unexpected.

## Skipped metrics (不适用)

- `shoulder_architecture` (coverage_score) — No salient shoulder construction is described beyond general sleeve and neckline information.
- `fabric_family` (coverage_score) — The text describes color, pattern, and styling, but does not clearly identify the main fabric family/material.
- `surface_finish` (coverage_score) — No clear surface trait such as sheen, matte finish, drape, stiffness, or texture is stated.
- `deconstruction` (coverage_score) — No deconstruction, splicing, displacement, or reconstruction is explicitly described.
- `hardware_embellishment` (coverage_score) — The text mentions jewelry and a handbag, but no salient hardware such as chains, studs, rings, or crystals.
- `footwear` (coverage_score) — No footwear is mentioned.
- `belt` (coverage_score) — No visible belt, sash, or waist strap is described.
- `quantity_accuracy` (quality_score) — The text uses descriptive modifiers and one explicit numeral-free quantity relation, but no actual numbers, counts, or explicit quantity relations that require quantity accuracy scoring.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral asymmetry is described.
- `cultural_reference` (bonus_score) — No specific cultural, historical, or brand reference is grounded in the text.
- `gender_expression` (bonus_score) — The description does not explicitly discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is explicitly stated.
- `brand_alignment` (bonus_score) — No brand identity or brand-language target is mentioned.
- `negation_control` (bonus_score) — The text does not emphasize exclusions or absence of elements.
