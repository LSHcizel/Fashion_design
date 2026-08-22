# Text Evaluation Report

- **Source:** 10_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__010_media_cha_biarritz_ps27_031_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.0
- **Total score (S_fp):** 0.8146 (Strong)
- **Coverage axis:** 0.8947
- **Quality axis (raw / base / penalized):** 0.8167 / 0.7936 / 0.7936
- **Penalties (mean):** 0.1
- **R_content:** 0.786089

## Gates

- Score gate: 0.8146 (threshold 0.7) → **PASS**
- Penalty gate: 0.1 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `asymmetry` | 1.0 | 1 |  | Asymmetry is explicitly stated and is a visible design feature of the inner striped layer. |
| `belt` | 1.0 | 1 |  | A visible waist-crossing belt/tab detail is explicitly mentioned. |
| `body_coverage` | 1.0 | 1 |  | The text clearly describes visible exposure at the chest and layered coverage beneath. |
| `color_relationship_logic` | 1.0 | 1 |  | The text explains the color logic as a contrast between the neutral textured outer coat and the vivid graphic striped underlayer, i.e. explicit color blocking and layered contrast. |
| `construction_technique` | 1.0 | 1 |  | The text clearly describes a specific surface-making technique/texture treatment and locates it on the coat body. |
| `cross_garment_binding` | 1.0 | 1 |  | The description clearly distinguishes which features belong to the coat, the black layer, and the striped inner piece, so multi-garment attribution is well covered. |
| `fabric_family` | 0.0 | 0 |  | The text describes texture and surface quality, but does not clearly identify a fabric family such as wool, silk, leather, denim, or knit. |
| `functional_detail` | 1.0 | 1 |  | A visible tab/belt-like functional detail is mentioned, along with trim that reads as a construction detail. |
| `garment_category` | 1.0 | 1 |  | The text clearly identifies the main garment types, especially a coat as the outer statement piece. |
| `jewelry` | 1.0 | 1 |  | Prominent earrings are explicitly described as a salient accessory. |
| `layering` | 1.0 | 1 |  | The text clearly describes multiple visible layers and their order from outer coat to inner garments. |
| `length_hemline` | 1.0 | 1 |  | The text gives clear length information for the coat and layered look. |
| `pattern_type` | 1.0 | 1 |  | Pattern types are clearly identified: chevron-like waves on the coat and stripes on the inner garment. |
| `primary_color` | 1.0 | 1 |  | The dominant outer coat color reads as golden beige/cream with dark flecks, which establishes the primary color family. |
| `secondary_color` | 1.0 | 1 |  | Secondary colors are clearly present in the trim and especially the visible striped underlayer, with the contrast anchored to the open-front coat and exposed inner piece. |
| `shoulder_architecture` | 0.0 | 0 |  | Shoulder structure is not explicitly defined; collar and front opening are mentioned, but not a salient shoulder design. |
| `silhouette` | 1.0 | 1 |  | The overall shape and structural trend are explicitly described. |
| `surface_finish` | 1.0 | 1 |  | Surface traits are clearly given: tactile, shaggy/fringed, and a straight drape. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes overall vertical proportion and silhouette balance, with a long outer coat and elongated layered structure. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are clearly attached to the correct entities, including coat trim, waist detail on the inner striped piece, and earrings. There is only slight ambiguity in the phrase “belt or tab deta |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The main garment stack is clearly established and visually rich, with coat, underlayer, and striped inner piece prioritized. There is some descriptive redundancy and texture elaboration, but the core  |
| `craft_embellishment_salience` | 0.75 | 1 | 工艺装饰显著度 | Craft and surface treatment are clearly salient and positioned on the coat edges and body, though the description is more texture-focused than technique-specific. |
| `design_distinctiveness` | 1.0 | 1 | 设计独特性 | The look has multiple strong memory anchors: an unusual shaggy chevron-wave coat texture and a highly graphic multicolor striped underlayer. The combination is clearly distinctive rather than formulai |
| `design_signal_purity` | 0.75 | 1 | 设计信号纯度 | Most of the text is devoted to concrete design facts, with only a small amount of mood language like “polished runway mood” and “maximal texture and color blocking.” |
| `fine_grained_attribute_usage` | 1.0 | 1 | 术语具体度 | Color, texture, and construction are described in fine-grained, imageable terms with strong material and structural specificity. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly visual and mostly prompt-ready, with clear garment hierarchy, silhouette, colors, and styling. It still reads somewhat like a descriptive analysis rather than a concise generation p |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a mostly natural top-down structure from main outer garment to inner layers and then accessories, making the outfit easy to reconstruct. Minor compression and dense detail stac |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text distinguishes multiple garments and generally keeps their attributes separated correctly: outer coat, black layer, and striped inner piece. Minor ambiguity remains around the waist detail and |
| `reference_clarity` | 0.75 | 1 | 语言清晰度 | References are mostly clear and sequential, with pronouns like "it" and "The inner striped piece" pointing unambiguously to the coat and underlayer. Minor density from layered descriptions, but no ser |
| `silhouette_combination_originality` | 0.75 | 1 | 组合原创性 | The layered silhouette is specific and visually interesting, but it still sits within a recognizable runway formula of statement coat plus tailored inner layer plus graphic underlayer. |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and attachment relationships are clearly described and imageable, with coherent front-open and underlayer structure. The only slight weakness is that some lower-body continuation is described |
| `specific_noun_usage` | 1.0 | 1 | 术语具体度 | Uses highly specific garment and accessory nouns with clear fashion semantics, plus structural descriptors that make the look easy to visualize. |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | The description mostly prioritizes visible, image-defining clothing and silhouette details. Accessories and mood are present but secondary, with only minor extra emphasis on styling details that do no |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is anchored in visible garment parts and layering relationships, with clear references to collar, front edges, neckline, and visible lower area. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | The coat, inner layer, and striped underlayer read as a coherent stacked outfit without trunk-level left-right contradictions or mutually exclusive garment identities. |
| `coordination_penalty` | 0.0 | The look is stylistically unified as a layered runway ensemble; the contrast is intentional and the accessories do not disrupt trunk coordination. |
| `formula_template_penalty` | 0.25 | The description follows a common fashion-prompt formula of silhouette + material + color + styling mood, with some reusable runway phrasing, though it is not heavily templated. |
| `generation_content_penalty` | 0.25 | Mostly imageable garment description, but ends with runway-style mood language and broad styling summary that adds some conceptual padding. |
| `rationality_penalty` | 0.0 | All described materials and construction remain physically plausible for fashion imagery; no impossible garment structure is asserted. |

## Missing coverage (未覆盖)

- **`shoulder_architecture`** — Shoulder structure is not explicitly defined; collar and front opening are mentioned, but not a salient shoulder design.
- **`fabric_family`** — The text describes texture and surface quality, but does not clearly identify a fabric family such as wool, silk, leather, denim, or knit.

## Skipped metrics (不适用)

- `closure` (coverage_score) — No explicit closure mechanism such as buttons, zipper, ties, or buckle is described.
- `deconstruction` (coverage_score) — The text does not explicitly mention deconstruction, splicing, displacement, or reconstruction.
- `hardware_embellishment` (coverage_score) — No salient hardware or metallic embellishment such as chains, studs, rings, or crystals is described.
- `bag` (coverage_score) — No bag is mentioned or implied as a visible styling element.
- `footwear` (coverage_score) — Footwear is not described in the text.
- `quantity_accuracy` (quality_score) — No explicit counts, numerals, or quantity relations are used.
- `bilateral_coherence` (quality_score) — No explicit left-right, bilateral, or paired-side differences are described.
- `cultural_reference` (bonus_score) — No cultural, historical, or brand-specific reference is provided.
- `gender_expression` (bonus_score) — The description does not explicitly discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is explicitly stated.
- `brand_alignment` (bonus_score) — No brand identity or brand-language target is mentioned.
- `negation_control` (bonus_score) — The text does not emphasize exclusions or absence of elements.
