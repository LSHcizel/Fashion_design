# Text Evaluation Report

- **Source:** 69_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__069_media_cha_biarritz_ps27_064_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.8506 (Strong)
- **Coverage axis:** 1.0
- **Quality axis (raw / base / penalized):** 0.8077 / 0.8125 / 0.8125
- **Penalties (mean):** 0.15
- **R_content:** 0.805944

## Gates

- Score gate: 0.8506 (threshold 0.7) → **PASS**
- Penalty gate: 0.15 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `asymmetry` | 1.0 | 1 |  | Asymmetry is explicitly stated and visually grounded in the sash bow placement and hanging ends. |
| `bag` | 1.0 | 1 |  | The text clearly identifies the bag type/holding method and gives its color/pattern, satisfying the coverage requirement. |
| `belt` | 1.0 | 1 |  | A visible waist sash functions as a belt-like accessory and its placement/attachment is clearly described. |
| `body_coverage` | 1.0 | 1 |  | The text clearly indicates body coverage and partial transparency. |
| `closure` | 1.0 | 1 |  | The text clearly describes closure details via buttons and a waist tie/bow. |
| `color_relationship_logic` | 1.0 | 1 |  | The text explains the color relationship as a coordinated plaid with a warm ground, strong red blocks, and dark linear checks, which makes the palette reconstructible. |
| `construction_technique` | 1.0 | 1 |  | The text names a specific construction treatment—pleated panels—and gives its placement on the skirt. |
| `cross_garment_binding` | 1.0 | 1 |  | The description distinguishes which attributes belong to the dress, sash, bag, and shoes, making multi-garment relations clear. |
| `fabric_family` | 1.0 | 1 |  | The main garment is clearly a shirt-dress, and the semi-sheer description supports a lightweight woven fabric family, even if the exact fiber is not named. |
| `footwear` | 1.0 | 1 |  | It specifies the footwear family and material/finish, plus a clear decorative form detail. |
| `functional_detail` | 1.0 | 1 |  | A functional carry detail is described for the bag, and the sash is a clear functional waist detail. |
| `garment_category` | 1.0 | 1 |  | The main garment category is explicitly identified as a shirt-dress/dress. |
| `jewelry` | 1.0 | 1 |  | A salient piece of jewelry is explicitly mentioned. |
| `layering` | 1.0 | 1 |  | The text describes visible garment relations and overlay/attachment at the waist, making the layered structure imageable. |
| `length_hemline` | 1.0 | 1 |  | Garment length and hemline are explicitly stated. |
| `pattern_type` | 1.0 | 1 |  | The pattern type is clearly identified as plaid/tartan. |
| `primary_color` | 1.0 | 1 |  | The dominant palette is explicitly stated, with red/tan/black/dark navy as the main colors. |
| `secondary_color` | 1.0 | 1 |  | Secondary accent colors are clearly present and described as part of the overall palette and sash details. |
| `silhouette` | 1.0 | 1 |  | The text clearly describes the overall shape and fit structure. |
| `surface_finish` | 1.0 | 1 |  | The text gives clear surface/handling traits, including translucency and fluid drape with pleating. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes upper-versus-lower silhouette balance and waist emphasis, including torso fit and skirt length. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are bound to the correct entities, including the sash, bag, and shoes. Minor ambiguity remains in phrases like “shoes or sandals,” but it does not seriously disrupt the overall binding |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is packed with visible garment facts and mostly prioritizes the main look, with only light stylistic framing. It is somewhat verbose, but not essay-like or dominated by mood language. |
| `craft_embellishment_salience` | 0.75 | 1 | 工艺装饰显著度 | Craft and embellishment are clearly described with type and placement, especially the sash bow and sculptural shoe decoration. The visual role is understandable, though not deeply technical. |
| `design_distinctiveness` | 0.75 | 1 | 设计独特性 | The look has multiple memorable anchors: semi-sheer plaid construction, an oversized off-center waist bow, and sculptural gold footwear. These are clearly more distinctive than a standard shirt-dress. |
| `design_signal_purity` | 1.0 | 1 | 设计信号纯度 | The text is dominated by concrete design facts, materials, placement, and silhouette details, with essentially no mood-essay dilution. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly visual and mostly prompt-ready, with clear garment type, silhouette, colors, and accessory details. It still reads somewhat like a descriptive fashion analysis rather than a tightly |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a mostly natural progression from overall silhouette to garment details, then lower-body shape and accessories. It is clear and easy to reconstruct, though there is some densit |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text clearly separates the dress, sash, bag, and footwear, with attributes mostly attached to the correct item. There is slight looseness in the footwear wording and some dense multi-item descript |
| `reference_clarity` | 1.0 | 1 | 语言清晰度 | References are consistently anchored to clear subjects, with no confusing pronouns or ambiguous omissions. |
| `silhouette_combination_originality` | 0.75 | 1 | 组合原创性 | The combination is more specific than a formula look because the shirt-dress is pushed into an asymmetric, bow-accented tartan statement. Still, the base silhouette remains relatively familiar. |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | The layering and attachment logic is clear and imageable, especially the waist wrap and bow placement. Minor complexity remains in the dense description, but the spatial relationships are coherent and |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | The text emphasizes highly visible, image-dominant details of the dress, sash, and shoes. Accessories and styling are present, but they do not overwhelm the core outfit description. |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly grounded in visible, imageable details with precise body and garment anchors, and it reads like direct runway observation rather than mood prose. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | No trunk-level left-right or mutually exclusive garment conflicts; the look reads as one coherent dress-based silhouette. |
| `coordination_penalty` | 0.25 | Overall coordinated, but the sheer plaid dress, casual striped bag, and ornate gold footwear create a mild mixed-language styling tension. |
| `formula_template_penalty` | 0.25 | Some runway-essay framing and generic styling language, but the description remains mostly specific and grounded. |
| `generation_content_penalty` | 0.25 | Mostly grounded garment description, but ends with evaluative styling language that adds some prompt noise. |
| `rationality_penalty` | 0.0 | All described elements are physically plausible fashion details. |

## Skipped metrics (不适用)

- `shoulder_architecture` (coverage_score) — No salient shoulder architecture is described beyond short sleeves and a collar.
- `deconstruction` (coverage_score) — No deconstruction, splicing, displacement, or reconstruction is explicitly described.
- `hardware_embellishment` (coverage_score) — No salient hardware or metal embellishment such as chains, studs, rings, or crystals is described.
- `quantity_accuracy` (quality_score) — The text contains no explicit counts or quantity relations that need verification.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral contrast is described.
- `cultural_reference` (bonus_score) — No explicit cultural, historical, or brand grounding is provided.
- `gender_expression` (bonus_score) — The description does not discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is stated.
- `brand_alignment` (bonus_score) — No brand language or brand identity target is mentioned.
- `negation_control` (bonus_score) — The text does not emphasize exclusions or absence of elements.
