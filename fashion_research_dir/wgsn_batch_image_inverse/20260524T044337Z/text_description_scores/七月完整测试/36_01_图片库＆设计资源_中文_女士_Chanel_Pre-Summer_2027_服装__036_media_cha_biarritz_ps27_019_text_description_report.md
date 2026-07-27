# Text Evaluation Report

- **Source:** 36_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__036_media_cha_biarritz_ps27_019_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.8507 (Strong)
- **Coverage axis:** 0.8333
- **Quality axis (raw / base / penalized):** 0.8571 / 0.8542 / 0.8542
- **Penalties (mean):** 0.1
- **R_content:** 0.820925

## Gates

- Score gate: 0.8507 (threshold 0.7) → **PASS**
- Penalty gate: 0.1 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `body_coverage` | 1.0 | 1 |  | The text clearly notes exposed legs and a visible underlayer, indicating body coverage/reveal. |
| `closure` | 1.0 | 1 |  | A clear front closure is described with buttons. |
| `color_relationship_logic` | 1.0 | 1 |  | The text explains the palette relationship as a dominant pink base with contrasting accent trims and coordinated matching pieces. |
| `construction_technique` | 0.0 | 0 |  | The text mentions trim and texture, but not a specific construction technique with a clear garment zone as required. |
| `cross_garment_binding` | 1.0 | 1 |  | The description clearly distinguishes which details belong to the jacket, skirt, underlayer, and shoes, showing cross-garment attribution. |
| `fabric_family` | 0.0 | 0 |  | The text suggests texture and tailoring, but it does not clearly name the main fabric family of the suit itself. |
| `footwear` | 1.0 | 1 |  | Footwear type, heel height, toe detail, and color/material contrast are clearly specified. |
| `functional_detail` | 1.0 | 1 |  | Pockets are explicitly described on both jacket and skirt. |
| `garment_category` | 1.0 | 1 |  | The main garment category is explicitly identified as a skirt suit with jacket and skirt. |
| `hardware_embellishment` | 1.0 | 1 |  | Visible hardware/metallic embellishment is clearly present. |
| `layering` | 1.0 | 1 |  | The text clearly describes a visible outer layer over an underlayer with readable front-to-back layering. |
| `length_hemline` | 1.0 | 1 |  | Garment lengths and hemline placement are explicitly stated. |
| `pattern_type` | 0.0 | 0 |  | These describe trim texture and speckling, but not a clear garment pattern type for the main look. |
| `primary_color` | 1.0 | 1 |  | The dominant main color is clearly pink. |
| `secondary_color` | 1.0 | 1 |  | Clear secondary/accent colors are described alongside the pink base. |
| `silhouette` | 1.0 | 1 |  | The text clearly describes the overall shape and structural contour. |
| `surface_finish` | 1.0 | 1 |  | It clearly conveys surface qualities: polished and structured/hard-formed, with textured trim. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes the upper and lower proportions and their balance, including jacket length, waist position, and skirt length. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 1.0 | 1 | 属性绑定准确度 | Garment attributes are consistently tied to the correct entities: jacket, skirt, underlayer, and shoes are each described with their own features and no major cross-binding. |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is dense with visible garment facts and construction details, with only a small amount of mood framing at the end. It remains prompt-useful and mostly prioritizes the outfit over prose |
| `craft_embellishment_salience` | 1.0 | 1 | 工艺装饰显著度 | Craft is a main hook here, and the text clearly states the type, placement, and visual role of the trims and edging. |
| `design_distinctiveness` | 1.0 | 1 | 设计独特性 | The look has multiple clear memory points from trim, texture, and pocket treatment, not just a standard suit silhouette. |
| `design_signal_purity` | 1.0 | 1 | 设计信号纯度 | The text is overwhelmingly made of concrete design observations, with minimal mood language and no essay-like drift. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly imageable and organized around visible silhouette, garment types, layering, and styling, so it is close to a usable prompt. It still reads somewhat like a descriptive fashion analys |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a mostly natural hierarchy from overall look to jacket, skirt, palette, and styling details. It is easy to reconstruct the outfit, though some dense pocket/trim details slightl |
| `multi_garment_binding` | 1.0 | 1 | 属性绑定准确度 | Multiple garments are clearly separated and their properties remain attached to the correct item, with coherent layering between jacket, underlayer, skirt, and footwear. |
| `quantity_accuracy` | 0.75 | 1 | 语言清晰度 | The quantity relation is clear and internally consistent, with the four pockets explicitly partitioned into two upper and two lower. Minor complexity comes from the long descriptive sentence, but the  |
| `reference_clarity` | 0.75 | 1 | 语言清晰度 | References are generally well anchored by explicit noun phrases, and pronoun use is minimal. The description is long, but the objects of each clause remain identifiable without serious ambiguity. |
| `silhouette_combination_originality` | 0.75 | 1 | 组合原创性 | The suit combination is polished and specific, with a tailored skirt-suit pairing and decorative trim, though it remains within a recognizable classic runway framework. |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and garment placement are clearly described, with coherent front-opening and hem relationships that are easy to visualize. Minor density and detail accumulation keep it just short of near-per |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | The text foregrounds highly visible, image-dominant elements and keeps hidden or low-visibility details minimal. The brief mood phrase does not overwhelm the garment description. |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly anchored in visible garment facts, with specific placement and construction details throughout. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | The jacket, underlayer, and skirt read as one coherent suit with no trunk-level left-right or identity conflict. |
| `coordination_penalty` | 0.0 | Overall styling is unified and classic; the shoes and bare legs complement the tailored suit rather than clash with it. |
| `formula_template_penalty` | 0.25 | The look is somewhat formulaic and runway-generic, but it still contains specific craft details like braid/fringe trim and patch-pocket construction. |
| `generation_content_penalty` | 0.25 | Mostly grounded garment description, but the closing mood/framing language adds some redundant runway-style commentary. |
| `rationality_penalty` | 0.0 | All described materials and construction details are physically plausible for ordinary fashion wear. |

## Missing coverage (未覆盖)

- **`fabric_family`** — The text suggests texture and tailoring, but it does not clearly name the main fabric family of the suit itself.
- **`pattern_type`** — These describe trim texture and speckling, but not a clear garment pattern type for the main look.
- **`construction_technique`** — The text mentions trim and texture, but not a specific construction technique with a clear garment zone as required.

## Skipped metrics (不适用)

- `shoulder_architecture` (coverage_score) — No prominent shoulder design is described; the text mentions collarless and straight-cut, but not structured shoulders, pads, off-shoulder, or similar cues.
- `deconstruction` (coverage_score) — No deconstruction, splicing, displacement, or reconstruction is mentioned.
- `bag` (coverage_score) — No bag is described or implied as a visual element of the look.
- `jewelry` (coverage_score) — No jewelry or body ornament is mentioned.
- `belt` (coverage_score) — No visible belt, sash, or waist strap is described; the waist emphasis comes from garment cut.
- `asymmetry` (coverage_score) — No asymmetrical or uneven structure is described.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral distinction is described.
- `cultural_reference` (bonus_score) — No explicit cultural, historical, or brand grounding is provided.
- `gender_expression` (bonus_score) — The text does not explicitly discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is stated.
- `brand_alignment` (bonus_score) — No brand identity or brand-language target is mentioned.
- `negation_control` (bonus_score) — The description does not emphasize exclusions or absence of elements as important.
