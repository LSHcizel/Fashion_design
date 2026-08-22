# Text Evaluation Report

- **Source:** 25_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__025_media_cha_biarritz_ps27_001_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.8077 (Strong)
- **Coverage axis:** 0.8667
- **Quality axis (raw / base / penalized):** 0.7885 / 0.7917 / 0.7917
- **Penalties (mean):** 0.1
- **R_content:** 0.77943

## Gates

- Score gate: 0.8077 (threshold 0.7) → **PASS**
- Penalty gate: 0.1 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `asymmetry` | 1.0 | 1 |  | Asymmetry is explicitly stated and reinforced by the uneven hem and overlapping panel structure. |
| `body_coverage` | 1.0 | 1 |  | The text clearly describes both exposed and covered body areas. |
| `color_relationship_logic` | 1.0 | 1 |  | The text explains the color logic as a monochrome black-and-white base with a small red contrast accent. |
| `cross_garment_binding` | 1.0 | 1 |  | The text distinguishes multiple items and clearly assigns them to different parts of the look, making the garment relationships readable. |
| `footwear` | 0.0 | 0 |  | Footwear is mentioned, but only in a generic way; no shoe type, shape, heel/sole form, or material/finish is given. |
| `garment_category` | 1.0 | 1 |  | The主体品类 is explicitly identified as a dress. |
| `layering` | 0.0 | 0 |  | The text mentions a dress and a separately carried coat, but not a clear worn layering relationship with visible overlap, attachment, or ordering that can be reconstructed as layered styling. |
| `length_hemline` | 1.0 | 1 |  | Garment length and hemline are explicitly stated. |
| `pattern_type` | 1.0 | 1 |  | The linework functions as a clear stripe/pinstripe-like pattern type. |
| `primary_color` | 1.0 | 1 |  | The main color is clearly black. |
| `secondary_color` | 1.0 | 1 |  | There are clear secondary accent colors: white line detailing and a small red accent. |
| `shoulder_architecture` | 1.0 | 1 |  | Shoulder design is salient and clearly described. |
| `silhouette` | 1.0 | 1 |  | The text clearly describes the overall shape and structural contour. |
| `surface_finish` | 1.0 | 1 |  | It clearly conveys a fluid, draped surface quality. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes overall vertical balance and proportion, including the dress silhouette, hem length, and the added long outerwear volume. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are clearly attached to the correct entities, and the left-hand carried coat is distinguished from the dress. Minor ambiguity remains in phrases like “outerwear piece or coat” and the  |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is mostly concentrated on visible garment structure, silhouette, and surface detailing, with only a small amount of styling/context language. It is detailed but still efficient and pro |
| `craft_embellishment_salience` | 0.75 | 1 | 工艺装饰显著度 | The text clearly identifies a salient linear treatment and seam/panel structure with location and visual effect, though it does not specify a named craft technique. |
| `design_distinctiveness` | 0.75 | 1 | 设计独特性 | The look has a clear non-formula memory point in the starburst linear treatment and asymmetrical draped paneling, though it is still anchored by a relatively simple black dress silhouette. |
| `design_signal_purity` | 1.0 | 1 | 设计信号纯度 | The text is dominated by concrete design observations, with minimal mood language and no essay-like framing that would dilute the garment facts. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly imageable and mostly prompt-ready, with clear garment type, silhouette, color, and surface detailing. It is slightly weakened by explanatory phrasing and some ambiguity (“piece or c |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a mostly natural order from main garment to silhouette, detailing, color/finish, then accessory and styling. It is clear and imageable, though some later clauses are dense and  |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text keeps the dress, carried outerwear, and footwear separate, so multi-item binding is mostly stable. There is slight uncertainty in the coat phrasing and the accessory placement, but no major c |
| `reference_clarity` | 0.75 | 1 | 语言清晰度 | References are generally clear and stable, with the dress as the main subject and the left-hand coat clearly anchored. Minor complexity comes from the long descriptive sentence structure, but pronouns |
| `silhouette_combination_originality` | 0.75 | 1 | 组合原创性 | The combination is more distinctive than a standard formula because of the column-to-draped asymmetry and the carried outerwear volume, though the core dress remains a fairly legible black midi base. |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Spatial relations are mostly clear and visually reconstructable: front-facing placement, panel overlap, line convergence, and the carried outerwear’s position beside the body are all understandable. M |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | The text prioritizes highly visible, image-dominant features of the dress and styling. It does mention a carried coat and a small head/ear accent, but these do not overwhelm the main look, so visibili |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly grounded in visible garment facts with precise body-part and placement references, and it reads like a runway caption rather than a mood essay. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | No trunk-level left-right conflict or mutually exclusive garment identities; the look reads as a coherent dress with carried outerwear. |
| `coordination_penalty` | 0.0 | Overall styling is unified and the small red accent does not create trunk-level coordination conflict. |
| `formula_template_penalty` | 0.25 | Some runway-essay framing and generic style language are present, but the description remains specific and craft-grounded rather than fully formulaic. |
| `generation_content_penalty` | 0.25 | Mostly grounded garment description, but includes runway/editorial framing and evaluative phrasing that slightly reduces prompt efficiency. |
| `rationality_penalty` | 0.0 | The described construction is physically plausible as ordinary fashion design. |

## Missing coverage (未覆盖)

- **`footwear`** — Footwear is mentioned, but only in a generic way; no shoe type, shape, heel/sole form, or material/finish is given.
- **`layering`** — The text mentions a dress and a separately carried coat, but not a clear worn layering relationship with visible overlap, attachment, or ordering that can be reconstructed as layered styling.

## Skipped metrics (不适用)

- `fabric_family` (coverage_score) — The text describes silhouette, drape, and linework, but does not clearly name the main fabric family.
- `closure` (coverage_score) — No explicit closure such as buttons, zipper, ties, or buckle is mentioned.
- `functional_detail` (coverage_score) — No pockets, straps, or other functional utility details are described.
- `construction_technique` (coverage_score) — The text describes drape, asymmetry, and line placement, but not a clearly named construction technique like pleating, quilting, embroidery, cut-outs, or engineered panel work.
- `deconstruction` (coverage_score) — Although the look is described as asymmetrical and draped, it does not explicitly mention deconstruction, splicing, displacement, or reconstruction.
- `hardware_embellishment` (coverage_score) — No salient hardware or embellishment such as chains, studs, rings, or crystals is mentioned.
- `bag` (coverage_score) — No bag is described; the carried item is explicitly a coat/outerwear piece, not a bag.
- `jewelry` (coverage_score) — No jewelry or body ornament is explicitly present.
- `belt` (coverage_score) — No visible belt, sash, waist strap, or harness is described.
- `quantity_accuracy` (quality_score) — The text does not use explicit counts or quantity relations that need verification.
- `bilateral_coherence` (quality_score) — No explicit left-right garment or accessory contrast is described beyond a general runway view and a single hand holding an item.
- `cultural_reference` (bonus_score) — No cultural, historical, or brand grounding is provided.
- `gender_expression` (bonus_score) — The description does not explicitly discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is stated.
- `brand_alignment` (bonus_score) — No brand identity or brand-language target is mentioned.
- `negation_control` (bonus_score) — The text does not emphasize exclusions in a way that requires negation control.
