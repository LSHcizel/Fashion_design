# Text Evaluation Report

- **Source:** 74_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__074_media_cha_biarritz_ps27_072_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.851 (Strong)
- **Coverage axis:** 1.0
- **Quality axis (raw / base / penalized):** 0.8036 / 0.8125 / 0.8125
- **Penalties (mean):** 0.1
- **R_content:** 0.821215

## Gates

- Score gate: 0.851 (threshold 0.7) → **PASS**
- Penalty gate: 0.1 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `bag` | 1.0 | 1 |  | The bag is explicitly identified, with carrying method and material/texture details clearly described. |
| `belt` | 1.0 | 1 |  | A visible belt is clearly present and described as cinching the waist. |
| `closure` | 1.0 | 1 |  | A clear opening/closure structure is described, along with a belt fastening the waist. |
| `color_relationship_logic` | 1.0 | 1 |  | The text explains the palette relationship as a strong contrast between black and the red/red-orange accents. |
| `construction_technique` | 1.0 | 1 |  | It names specific surface/assembly techniques and locates them on the garment body, sleeves, and hem. |
| `cross_garment_binding` | 1.0 | 1 |  | The description distinguishes the main garment from accessories and assigns attributes to each item clearly. |
| `fabric_family` | 1.0 | 1 |  | The text gives plausible主体材质/面料类别 cues for the main garment. |
| `footwear` | 1.0 | 1 |  | Footwear type and toe shape are specified, along with color contrast and surface detail. |
| `functional_detail` | 1.0 | 1 |  | The text includes a functional carried accessory with straps, which counts as a functional detail. |
| `garment_category` | 1.0 | 1 |  | The main garment category is explicitly identified. |
| `hardware_embellishment` | 1.0 | 1 |  | Chains and metal jewelry are explicitly mentioned as visible embellishment/hardware. |
| `jewelry` | 1.0 | 1 |  | Earrings are explicitly mentioned as visible jewelry. |
| `layering` | 1.0 | 1 |  | The text describes a wearable layered/structured relation between the main outer garment and the belt, making the outfit’s attachment and silhouette readable. |
| `length_hemline` | 1.0 | 1 |  | Garment length and hemline are directly specified. |
| `pattern_type` | 1.0 | 1 |  | A clear pattern type is described, even if offered as alternatives. |
| `primary_color` | 1.0 | 1 |  | The dominant main color is clearly black. |
| `secondary_color` | 1.0 | 1 |  | Distinct secondary accent colors are explicitly stated. |
| `shoulder_architecture` | 1.0 | 1 |  | Shoulder structure is explicitly emphasized. |
| `silhouette` | 1.0 | 1 |  | The text clearly describes the overall structural silhouette. |
| `surface_finish` | 1.0 | 1 |  | It clearly describes surface qualities: textured, shaggy/fringed, and structured. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes vertical proportion and balance through waist definition, upper-body structure, and lower-length silhouette. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are clearly attached to the correct entities, including the belt on the coat-dress, the handbag in hand, and the pumps on the feet. Minor ambiguity remains in phrases like “coat-dress  |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is packed with visible garment facts and keeps the main look clear. There is some extra elaboration on texture, silhouette, and styling, but it remains fashion-specific rather than ess |
| `craft_embellishment_salience` | 1.0 | 1 | 工艺装饰显著度 | The embellishment type, placement, and visual effect are clearly specified and function as a main design hook. |
| `design_distinctiveness` | 0.75 | 1 | 设计独特性 | The look has a clear memory point in the heavy fringe treatment and textured surface, which are more distinctive than a formula coat-dress. |
| `design_signal_purity` | 1.0 | 1 | 设计信号纯度 | The text is dominated by concrete design facts, materials, placement, and silhouette details rather than mood or essay-like framing. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly visual and mostly prompt-ready, with clear garment type, silhouette, surface, and styling details. It is slightly less than perfect because it offers some alternative naming (“coat- |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a mostly natural order from main garment to construction details, then surface texture, fringe placement, silhouette, and finally accessories. It is clear and easy to reconstru |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text includes multiple items, but their attributes are mostly bound correctly: the main garment, handbag, and shoes are distinguished clearly. There is slight ambiguity in the main-garment naming, |
| `quantity_accuracy` | 0.75 | 1 | 语言清晰度 | The text uses a few explicit quantity relations and they are mostly clear and internally consistent. There is minor density in the description, but no serious conflict in counts or side references. |
| `reference_clarity` | 0.75 | 1 | 语言清晰度 | References are generally well anchored to the main garment and styling items, with clear subject continuity. The prose is somewhat long and layered, but pronouns and omitted subjects remain understand |
| `silhouette_combination_originality` | 0.75 | 1 | 组合原创性 | The silhouette is coherent and somewhat unusual because of the coat-dress/long-jacket ambiguity plus fringe-driven lower volume, though it still sits within a tailored luxury framework. |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | The layering and attachment logic is clear enough to visualize: a main coat-dress/jacket, belt at the waist, and fringe placed along front, cuffs, and hem. Minor ambiguity remains in the garment namin |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | The text prioritizes the dominant, image-defining elements of the outfit and accessories. It does include some lower-visibility texture interpretation like “reads as lace, jacquard, or embossed,” but  |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly anchored to visible garment zones and reads like direct runway observation with only light inference language. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | No trunk-level left-right conflict or mutually exclusive garment identities are described; the look reads as one coherent coat-dress/jacket silhouette. |
| `coordination_penalty` | 0.0 | The styling elements are coordinated around a single dark tailored look with controlled color accents; no major trunk-level aesthetic clash is present. |
| `formula_template_penalty` | 0.25 | The look uses a somewhat familiar tailored runway formula, but it is still anchored by specific fringe and texture details rather than being fully interchangeable or mood-only. |
| `generation_content_penalty` | 0.25 | Main garment is still clear and imageable, but the description adds some analytical hedging and accessory styling that slightly dilutes the core garment prompt. |
| `rationality_penalty` | 0.0 | All described materials and construction remain physically plausible for fashion imagery; no implausible garment physics or impossible wear conditions are asserted. |

## Skipped metrics (不适用)

- `body_coverage` (coverage_score) — The text does not describe notable skin exposure or cutouts; coverage is implied but not a salient reveal.
- `deconstruction` (coverage_score) — No deconstruction, splicing, displacement, or reconstruction is explicitly described.
- `asymmetry` (coverage_score) — No asymmetrical or uneven garment structure is described.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral asymmetry is described.
- `cultural_reference` (bonus_score) — No cultural, historical, or brand reference is explicitly grounded in the text.
- `gender_expression` (bonus_score) — The description does not explicitly discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is explicitly stated.
- `brand_alignment` (bonus_score) — The text does not target a specific brand identity or brand language.
- `negation_control` (bonus_score) — The description does not emphasize exclusions or absence of elements as important.
