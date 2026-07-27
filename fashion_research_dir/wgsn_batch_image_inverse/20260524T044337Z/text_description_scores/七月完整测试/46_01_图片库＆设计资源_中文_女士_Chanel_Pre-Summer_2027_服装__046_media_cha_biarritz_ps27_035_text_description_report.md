# Text Evaluation Report

- **Source:** 46_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__046_media_cha_biarritz_ps27_035_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.8296 (Strong)
- **Coverage axis:** 0.95
- **Quality axis (raw / base / penalized):** 0.8036 / 0.7986 / 0.7986
- **Penalties (mean):** 0.1
- **R_content:** 0.800564

## Gates

- Score gate: 0.8296 (threshold 0.7) → **PASS**
- Penalty gate: 0.1 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `bag` | 0.0 | 0 |  | A held object is mentioned, but it is not clearly identifiable as a bag, nor are bag type, shape, and material/finish covered. |
| `body_coverage` | 1.0 | 1 |  | The text explicitly mentions a reveal/exposure area at the lower front, so body coverage is applicable and covered. |
| `closure` | 1.0 | 1 |  | A clear front button closure is described, along with the jacket opening at the front. |
| `color_relationship_logic` | 1.0 | 1 |  | The palette is readable as a black dominant look with metallic gold accent contrast. |
| `construction_technique` | 1.0 | 1 |  | The description includes visible fabrication/finish techniques and their placement on the jacket neckline and skirt surface. |
| `cross_garment_binding` | 1.0 | 1 |  | Multiple garments are present and the description distinguishes their roles and relationships, making it clear which attributes belong to the jacket, underlayer, and skirt. |
| `fabric_family` | 1.0 | 1 |  | The main fabric family is clearly identified as tweed-style/tweed. |
| `functional_detail` | 1.0 | 1 |  | The text explicitly mentions pocket details, which are salient functional garment features. |
| `garment_category` | 1.0 | 1 |  | The text clearly identifies the main garment categories: jacket and skirt, forming a skirt suit. |
| `hardware_embellishment` | 1.0 | 1 |  | The look clearly features prominent metallic embellishment and hardware-like accents. |
| `jewelry` | 1.0 | 1 |  | Visible jewelry/body ornament is explicitly present and salient. |
| `layering` | 1.0 | 1 |  | The text clearly describes a visible layered relationship between jacket and underlayer. |
| `length_hemline` | 1.0 | 1 |  | The text includes length-related information for sleeves and skirt hem extent, satisfying hemline/length coverage. |
| `pattern_type` | 1.0 | 1 |  | A stripe-like surface pattern is explicitly described. |
| `primary_color` | 1.0 | 1 |  | Black is the dominant color across the suit and underlayer. |
| `secondary_color` | 1.0 | 1 |  | Gold/metallic accents function as a clear secondary color against the black base. |
| `shoulder_architecture` | 1.0 | 1 |  | Shoulder structure is explicitly described as strong and narrow, making shoulder architecture salient. |
| `silhouette` | 1.0 | 1 |  | The description gives a clear structural silhouette: tailored, fitted, narrow-shouldered, and close through the waist and hips. |
| `surface_finish` | 1.0 | 1 |  | The text gives clear surface traits: textured/frayed, reflective, and irregular light-catching sparkle. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly describes the top-to-bottom silhouette and waist placement, giving a readable proportion relationship between the fitted jacket and high-waisted skirt. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are clearly tied to the correct garment or body area, and the jacket/skirt distinction is stable. Minor ambiguity remains in a few decorative details like the held gold object/chain an |
| `bilateral_coherence` | 1.0 | 1 | 生成适配度 | The only explicit bilateral detail is a symmetric shoulder embellishment, which is coherent and accessory-like rather than a conflicting trunk split. No problematic left-right mismatch on sleeves, leg |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is packed with visible garment facts and construction details, with only a small amount of mood framing at the end. It is somewhat dense and efficient, though a bit verbose in places. |
| `craft_embellishment_salience` | 0.75 | 1 | 工艺装饰显著度 | Craft and embellishment are clearly located and described, especially the trim and shoulder embellishments, though the visual function is somewhat less elaborated than a full craft caption. |
| `design_distinctiveness` | 0.75 | 1 | 设计独特性 | The look has clear non-formula memory points through the frayed trim, shoulder safety-pin embellishments, and irregular sparkle, though the base suit silhouette remains fairly classic. |
| `design_signal_purity` | 1.0 | 1 | 设计信号纯度 | The text is dominated by concrete design facts, materials, placement, and construction details, with only a light mood note at the end. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The text is highly imageable and organized around visible silhouette, garment type, layering, and surface details, so it is close to a usable generation prompt. It is still somewhat explanatory and st |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a mostly natural garment-to-detail order: main outfit, jacket structure, skirt, then styling/accessories. There is some compression and a few detail clusters within long senten |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text consistently separates jacket, underlayer, and skirt, and attributes texture, buttons, and trim to the jacket while carrying the fabric description onto the skirt appropriately. There is slig |
| `reference_clarity` | 1.0 | 1 | 语言清晰度 | References are clear and stable throughout; pronouns and omitted subjects do not create ambiguity. |
| `silhouette_combination_originality` | 0.5 | 0 | 组合原创性 | The combination is polished and coherent, but it stays within a recognizable tailored skirt-suit formula rather than a highly unexpected silhouette mix. |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and reveal relationships are clearly described and visually reconstructible. Minor ambiguity remains in some low-visibility details and the cropped skirt length, but overall the spatial logic |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | The text prioritizes highly visible, image-dominant clothing details and surface effects. The mood phrase at the end is present but does not overwhelm the garment description. |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly anchored to visible garment zones and reads like direct observation of the look, with clear placement and layering details. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.0 | The trunk garments read coherently with no left-right or garment-identity conflict. |
| `coordination_penalty` | 0.0 | Styling language is unified and polished; accessories do not create trunk-level coordination conflict. |
| `formula_template_penalty` | 0.25 | A familiar tailored-look template is present, but it remains fairly specific and craft-anchored rather than fully formulaic. |
| `generation_content_penalty` | 0.25 | Mostly grounded garment description, but the closing mood/framing language slightly dilutes prompt efficiency. |
| `rationality_penalty` | 0.0 | All described materials and construction details are plausible in ordinary fashion imagery. |

## Missing coverage (未覆盖)

- **`bag`** — A held object is mentioned, but it is not clearly identifiable as a bag, nor are bag type, shape, and material/finish covered.

## Quality issues (质量短板)

- **`silhouette_combination_originality`** (score 0.5) — The combination is polished and coherent, but it stays within a recognizable tailored skirt-suit formula rather than a highly unexpected silhouette mix.

## Skipped metrics (不适用)

- `deconstruction` (coverage_score) — No explicit deconstruction, splicing, displacement, or reconstruction is mentioned.
- `footwear` (coverage_score) — No footwear is described in the text.
- `belt` (coverage_score) — No visible belt, sash, waist cincher, or harness is described.
- `asymmetry` (coverage_score) — No clear asymmetrical garment design is described; the look reads as largely symmetrical and tailored.
- `quantity_accuracy` (quality_score) — The text contains no explicit counts or quantity relations that need verification.
- `cultural_reference` (bonus_score) — No clear cultural, historical, or brand reference is provided.
- `gender_expression` (bonus_score) — The description does not explicitly discuss gender expression or androgyny.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is stated beyond general styling mood.
- `brand_alignment` (bonus_score) — No brand identity or brand-language target is mentioned.
- `negation_control` (bonus_score) — The text does not emphasize exclusions or absence of elements as a meaningful design requirement.
