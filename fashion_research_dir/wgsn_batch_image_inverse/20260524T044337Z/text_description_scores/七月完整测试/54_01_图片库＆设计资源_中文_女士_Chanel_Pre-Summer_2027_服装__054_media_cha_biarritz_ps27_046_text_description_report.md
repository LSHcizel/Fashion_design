# Text Evaluation Report

- **Source:** 54_01_图片库＆设计资源_中文_女士_Chanel_Pre-Summer_2027_服装__054_media_cha_biarritz_ps27_046_text_description.md
- **Judge model:** gpt-5.4-mini
- **Spec:** fashion_text_prompt_optimizer v0.2.3
- **Total score (S_fp):** 0.7901 (Strong)
- **Coverage axis:** 0.9474
- **Quality axis (raw / base / penalized):** 0.75 / 0.75 / 0.75
- **Penalties (mean):** 0.2
- **R_content:** 0.734793

## Gates

- Score gate: 0.7901 (threshold 0.7) → **PASS**
- Penalty gate: 0.2 (max 0.5) → **PASS**
- Both passed: **True**

## Coverage metrics (覆盖项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `asymmetry` | 1.0 | 1 |  | The look includes an uneven slit and side/front panel treatment that clearly introduces asymmetrical structure. |
| `body_coverage` | 1.0 | 1 |  | The text clearly describes exposed areas and revealing cut details. |
| `closure` | 1.0 | 1 |  | Clear button closures/fastenings are explicitly described on both jacket and lower piece. |
| `color_relationship_logic` | 1.0 | 1 |  | The text explains the color logic through a dominant red plaid base with black contrast trim and additional white accent panels. |
| `cross_garment_binding` | 1.0 | 1 |  | Multiple garments are described with distinct roles and relations, and the text clearly distinguishes the jacket, inner top, bottom, and draped neck piece. |
| `fabric_family` | 0.0 | 0 |  | The text suggests garment types and construction, but does not clearly name a主体材质类别 such as wool, cotton, leather, silk, or knit. |
| `functional_detail` | 1.0 | 1 |  | The text includes functional/structural details such as a draped scarf-like element and a slit opening. |
| `garment_category` | 1.0 | 1 |  | The text clearly identifies the main garment types: jacket, bodice/top, and bottom/skirt-trouser piece. |
| `hardware_embellishment` | 1.0 | 1 |  | Prominent metallic embellishments are clearly present, including buttons and a ring-like hardware detail. |
| `jewelry` | 1.0 | 1 |  | A salient jewelry item is explicitly present. |
| `layering` | 1.0 | 1 |  | The text clearly describes layered garments and their visible relationship: jacket over bodice, with a draped neck piece over the torso. |
| `length_hemline` | 1.0 | 1 |  | The description explicitly states garment length and hem-related details, including a slit and visible extent. |
| `pattern_type` | 1.0 | 1 |  | The pattern type is clearly identified as plaid/tartan. |
| `primary_color` | 1.0 | 1 |  | Red is clearly established as a main color, paired with black. |
| `secondary_color` | 1.0 | 1 |  | Black is a clear secondary color to the red base, and cream/white appears as a visible contrasting accent on the bodice. |
| `shoulder_architecture` | 1.0 | 1 |  | Shoulder structure is directly described as squared and tailored. |
| `silhouette` | 1.0 | 1 |  | It gives a clear structural silhouette with cropped, tailored, waist-defined proportions. |
| `surface_finish` | 1.0 | 1 |  | Surface qualities are clearly indicated through shine and structured/hard-edged tailoring. |
| `top_bottom_proportion` | 1.0 | 1 |  | The text clearly states the visible vertical framing and the relationship between a cropped top and high-waisted bottom, making the top-bottom proportion explicit. |

## Quality metrics (质量项)

| Metric | Score | Hit | Dimension | Reason |
| --- | ---: | --- | --- | --- |
| `attribute_entity_binding` | 0.75 | 1 | 属性绑定准确度 | Most attributes are bound to the correct garment and body zone, with clear separation between jacket, inner top, and lower piece. Minor ambiguity remains in phrases like 'pocket flaps or scarf-print i |
| `core_information_density` | 0.75 | 1 | 信息密度与简洁性 | The description is packed with visible garment facts and construction details, with only a small amount of styling language. It is efficient overall, though somewhat long and detail-heavy. |
| `craft_embellishment_salience` | 0.75 | 1 | 工艺装饰显著度 | Trim and embellishment are described with decent specificity, including placement and visual effect, though some elements remain interpretive rather than fully certain. |
| `design_distinctiveness` | 0.75 | 1 | 设计独特性 | The look has several memorable anchors, especially the scarf-like lapel/stole and the unusual bust hardware/keyhole detail, though the overall base is still a tailored plaid jacket-and-bottom formula. |
| `design_signal_purity` | 0.75 | 1 | 设计信号纯度 | The text is dominated by concrete design observations, with only a small amount of stylistic framing at the end. |
| `generation_readiness` | 0.75 | 1 | 生成适配度 | The description is highly visual and mostly prompt-ready, with clear garment types, silhouette, colors, and layering. It is slightly more explanatory than a direct generation prompt, but only needs li |
| `information_ordering` | 0.75 | 1 | 结构清晰度 | The description follows a mostly natural top-to-bottom garment order and clearly separates jacket, underlayer, and lower piece. Minor compression and some side-detail insertions interrupt the flow sli |
| `multi_garment_binding` | 0.75 | 1 | 属性绑定准确度 | The text keeps the jacket, inner bodice, and lower garment mostly distinct and correctly related. There is slight cross-item ambiguity around the draped scarf-like element and the hip panels, but the  |
| `reference_clarity` | 0.75 | 1 | 语言清晰度 | References are generally clear and the garment relationships are easy to follow. There is only mild complexity from stacked garment descriptions and layered phrasing, but no serious pronoun or anteced |
| `silhouette_combination_originality` | 0.5 | 0 | 组合原创性 | The combination is more distinctive than a standard formula because of the lingerie-like inner layer and slit bottom, but the core silhouette still reads as a fairly conventional tailored jacket plus  |
| `spatial_coherence` | 0.75 | 1 | 生成适配度 | Layering and attachment positions are clearly described and visually reconstructible. The only minor issue is that some elements are described with alternative possibilities, such as “lapel or stole”  |
| `visibility_priority` | 0.75 | 1 | 信息密度与简洁性 | The text prioritizes visible silhouette, trim, buttons, slit, and layering details that affect the image. There is some lower-priority interpretive wording, but hidden or essay-like content does not d |
| `visual_observation_grounding` | 1.0 | 1 | 视觉观察 grounded | The description is strongly anchored in visible garment facts and body locations, with clear front/waist/bust/hem references and little mood prose. |

## Penalties (扣分项)

| Key | Score | Reason |
| --- | ---: | --- |
| `consistency_penalty` | 0.25 | The inner top is described with two competing identities, and the lower piece is also split between skirt and trouser wording, but the main silhouette remains readable. |
| `coordination_penalty` | 0.25 | The tailored outer jacket and lingerie/swimsuit-like inner layer create a mild styling tension, though it is still presented as an intentional fashion look. |
| `formula_template_penalty` | 0.25 | The look uses a somewhat familiar tailored-cruise formula and relies on generic styling markers, but it still contains specific construction details and is not fully interchangeable. |
| `generation_content_penalty` | 0.25 | Mostly grounded garment description, but ends with some evaluative/styling language and layered symbol listing that slightly dilutes prompt efficiency. |
| `rationality_penalty` | 0.0 | No clearly impossible materials or physically implausible construction are asserted as ordinary wear. |

## Missing coverage (未覆盖)

- **`fabric_family`** — The text suggests garment types and construction, but does not clearly name a主体材质类别 such as wool, cotton, leather, silk, or knit.

## Quality issues (质量短板)

- **`silhouette_combination_originality`** (score 0.5) — The combination is more distinctive than a standard formula because of the lingerie-like inner layer and slit bottom, but the core silhouette still reads as a fairly conventional tailored jacket plus high-waisted lower piece.

## Skipped metrics (不适用)

- `construction_technique` (coverage_score) — No specific fabrication technique like pleating, quilting, embroidery, or engineered cutwork is clearly named.
- `deconstruction` (coverage_score) — The text does not explicitly mention deconstruction, splicing, displacement, or reconstruction.
- `bag` (coverage_score) — No bag is described or implied as a visible styling element.
- `footwear` (coverage_score) — Footwear is not mentioned in the text.
- `belt` (coverage_score) — No visible belt, sash, waist cincher, or harness is described.
- `quantity_accuracy` (quality_score) — The text uses a few quantity-like references such as 'both hips/front sides' and 'rows of shiny gold crest-style buttons,' but it does not present explicit count relations that need verification in the sense of this metric.
- `bilateral_coherence` (quality_score) — No explicit left-right or other bilateral garment differences are described.
- `gender_expression` (bonus_score) — No explicit gender expression or androgyny framing is stated.
- `theme_narrative` (bonus_score) — No series theme or conceptual narrative is provided.
- `brand_alignment` (bonus_score) — No brand identity or brand-language target is mentioned.
- `negation_control` (bonus_score) — The text does not emphasize exclusions or absence of elements.
