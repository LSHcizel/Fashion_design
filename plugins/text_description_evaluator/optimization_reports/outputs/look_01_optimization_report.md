# Text Description Optimization Report

## Summary
- 来源文件：`look_01.txt`
- 双门限同时满足：`True`
- 原始总分：`0.775`
- 优化后总分：`0.9375`
- 总分变化：`0.1625`
- 原始质量分：`0.625`
- 优化后质量分：`0.8958`
- 原始分档：`Strong`
- 优化后分档：`Excellent`
- 原始·得分门限：加权值 `0.775` / 阈值 `0.75` / 通过 `True`
- 原始·惩罚门限：total_penalty `0.625` / 阈值 `0.15` / 通过 `False`
- 优化后·得分门限：加权值 `0.9375` / 阈值 `0.75` / 通过 `True`
- 优化后·惩罚门限：total_penalty `0.0625` / 阈值 `0.15` / 通过 `True`
- 已执行优化轮数：`3`（默认最大 `max_rounds=5`，可能因双门限通过或停滞早停而提前结束）

## Penalty Comparison
- `generation_content_penalty`: `0.75` -> `0.25` (`-0.5`)
- `consistency_penalty`: `0.75` -> `0.0` (`-0.75`)
- `coordination_penalty`: `0.5` -> `0.0` (`-0.5`)
- `rationality_penalty`: `0.5` -> `0.0` (`-0.5`)
- `total_penalty`: `0.625` -> `0.0625` (`-0.5625`)

## Penalty Repair Details
### `generation_content_penalty`
- 优化前分值：`0.75`
- 优化后分值：`0.25`
- 修复结果：已缓解，下降 `0.5`。
- 优化前原因：The description is heavily essay-like and conceptual, with repeated thematic framing and hidden/low-visibility material details taking substantial space, which reduces prompt efficiency.
- 优化后原因：Mostly imageable garment description, but it includes a dense list of tailoring details that adds some prompt overhead without changing the core silhouette.
- 优化前证据：“societal constraints… emerging rebellion”; “The Secret: The left lining consists entirely of mercury morph paillettes…”; “Prison-bar grayscale dominates… hidden vermilion blazer lining flashes”
- 优化后证据：structured and coherent; single functional middle button, oxidized brass buttons, a button-on collar, single-button surgeon’s cuffs

### `consistency_penalty`
- 优化前分值：`0.75`
- 优化后分值：`0.0`
- 修复结果：已缓解，下降 `0.75`。
- 优化前原因：Multiple trunk-level left-right splits are stacked on the same look across blazer shoulders, lapels, and shirt sleeves, creating strong internal inconsistency despite the intentional deconstruction framing.
- 优化后原因：The blazer, shirt, trousers, and shoes read as a coherent suit-based look; no trunk-level left-right or identity conflict is present.
- 优化前证据：“right sleeve head is dramatically raised… while the opposite side remains softly unpadded”; “right side contrast with a deconstructed 5" shawl lapel on the left”; “One sleeve extends 18"… while the other remains cropped at mid-bicep”
- 优化后证据：tailored charcoal wool pinstripe blazer; high-waisted pinstripe wool trousers; platform Oxfords in polished black calfskin with white piping

### `coordination_penalty`
- 优化前分值：`0.5`
- 优化后分值：`0.0`
- 修复结果：已缓解，下降 `0.5`。
- 优化前原因：The overall styling language is intentionally split between rigid tailoring and fluid distortion, and the footwear is coherent, but the upper-body language still reads as only partially unified rather than fully coordinated.
- 优化后原因：The asymmetries are limited to accessories and lining accents, while the main outfit language remains coordinated and unified.
- 优化前证据：“structured above the waist dissolving into fluidity below”; “one shoulder extends aggressively… opposite side remains softly unpadded”; “The Shoe: Chunky 2" platform Oxfords… anchors the unstable upper silhouette”
- 优化后证据：restrained vermilion lining flash when it opens; off-center at the left hip; single silver thumb ring on the right hand and matte black leather half-gloves

### `rationality_penalty`
- 优化前分值：`0.5`
- 优化后分值：`0.0`
- 修复结果：已缓解，下降 `0.5`。
- 优化前原因：Most tailoring is plausible, but the mercury-based lining and the claim of permanently shifting body weight from shoe construction push the description toward physically implausible fashion facts.
- 优化后原因：All materials and garment constructions are physically plausible for ordinary wear.
- 优化前证据：“left lining consists entirely of mercury morph paillettes”; “thermochromatic silk that shifts from gray to pearl-white when touched”; “Weight shifted permanently onto left leg due to shoe construction”
- 优化后证据：stiff starched white cotton shirt; matte calfskin belt with an oxidized brass buckle; matte black leather half-gloves


## Round History
### Round `1`
- 分数变化：`0.775` -> `0.825` (`0.05`)
- 质量变化：`0.625` -> `0.7083` (`0.0833`)
- 重点 penalty：generation_content_penalty; consistency_penalty; coordination_penalty; rationality_penalty
- 重点 metric：bilateral_coherence; core_information_density; visibility_priority; generation_readiness; spatial_coherence; attribute_entity_binding
- 重点模块：ConcisenessAndDensity; GenerationReadiness; BindingAccuracy; LanguageClarity
- 策略备注：当前为第 `1` 轮优化。; 压缩冗余、无关与分析性表述，提升可直接生成的视觉信息密度。; 优先修复主干单品的一致性与同物件冲突绑定问题。; 重点收敛上身过度不协调的结构与材质对撞，统一造型语气后再保留有限不对称。; 优先修复不符合客观规律或现实穿着条件的表达。
- 本轮附加修复目标：【多轮核心目标】以得分门与惩罚门同时通过为首要目的；择优时优先保留使任一门通过、或使 total_penalty 下降、或使得分门加权值上升的改写，不必以总分为唯一标准。; 逐项核查材质、结构、功能和穿着关系，消除不符合现实条件或物理逻辑的设定。; 如果保留左右差异，确保差异在材质、色调和造型语言上仍然可统一识别。; 减少次要配件和概念性补充，提升主体服装信息占比。; 主体单品的可见廓形、材质、颜色和外部造型必须优先于隐藏内里和局部弱可见细节。; 把文本收束成可直接生成的 prompt 句式，减少说明性和编辑性表达。; 明确内外、上下、前后、叠搭和附着位置，避免空间关系模糊。; 把属性和单品绑定写得更集中，避免一个句子跨多个实体切换。; 主干拒绝不对称：外套、内搭、下装、鞋履必须左右同类同源。; 若同一物件被描述成多个互斥状态，优先保留最稳定的一种绑定关系。; 衣、裤、鞋作为主干必须对称与稳定，禁止主类别左右切换。; 通过统一主色、主材质和主轮廓增强收束感，不保留主干不对称。; 【consistency·本轮】主干左右对撞（如双袖极端）：以合并为一句轻描、统一袖线/廓形为主，不优先删整侧极端。; 清理与整体风格明显违和的搭配，确保鞋履、配件和主体服装在气质上互相衬托。; 优先消除单件上装左右互斥的风格场域（精裁西装式半侧 vs 对侧泡袖露肩高光泽丝绸等），统一为可成像的单一上装语法或明确分层。; 去掉不符合现实材质条件或穿着逻辑的主体设定，避免模型生成不可成立的服装。; 【删除闸门】以下 penalty keys 尚未完成两次 rewrite，不允许删除导向：['consistency_penalty', 'coordination_penalty', 'generation_content_penalty', 'rationality_penalty']。 本轮仅允许改写（rewrite）路径；重写（rewrite-again）后仍无法消除的 penalty 才可进入删除步骤。

### Round `2`
- 分数变化：`0.825` -> `0.85` (`0.025`)
- 质量变化：`0.7083` -> `0.75` (`0.0417`)
- 重点 penalty：coordination_penalty
- 重点 metric：bilateral_coherence; core_information_density; visibility_priority; attribute_entity_binding; multi_garment_binding; quantity_accuracy
- 重点模块：ConcisenessAndDensity; GenerationReadiness; BindingAccuracy; LanguageClarity
- 策略备注：当前为第 `2` 轮优化。; 压缩冗余、无关与分析性表述，提升可直接生成的视觉信息密度。; 优先修复主干单品的一致性与同物件冲突绑定问题。; 重点收敛上身过度不协调的结构与材质对撞，统一造型语气后再保留有限不对称。; 优先修复不符合客观规律或现实穿着条件的表达。
- 本轮附加修复目标：【多轮核心目标】以得分门与惩罚门同时通过为首要目的；择优时优先保留使任一门通过、或使 total_penalty 下降、或使得分门加权值上升的改写，不必以总分为唯一标准。; 如果保留左右差异，确保差异在材质、色调和造型语言上仍然可统一识别。; 减少次要配件和概念性补充，提升主体服装信息占比。; 主体单品的可见廓形、材质、颜色和外部造型必须优先于隐藏内里和局部弱可见细节。; 把属性和单品绑定写得更集中，避免一个句子跨多个实体切换。; 多单品描述时按单品分段组织，减少同一句里左右腿、左右脚、上装和配件混写。; 保留关键数字，但避免过多并列尺寸细节影响主结构识别。; 主干拒绝不对称：外套、内搭、下装、鞋履必须左右同类同源。; 若同一物件被描述成多个互斥状态，优先保留最稳定的一种绑定关系。; 衣、裤、鞋作为主干必须对称与稳定，禁止主类别左右切换。; 通过统一主色、主材质和主轮廓增强收束感，不保留主干不对称。; 清理与整体风格明显违和的搭配，确保鞋履、配件和主体服装在气质上互相衬托。; 优先消除单件上装左右互斥的风格场域（精裁西装式半侧 vs 对侧泡袖露肩高光泽丝绸等），统一为可成像的单一上装语法或明确分层。; 去掉不符合现实材质条件或穿着逻辑的主体设定，避免模型生成不可成立的服装。; 本轮比上一轮更强调收束：若主干元素仍存在左右分叉，优先统一主干，再保留边缘层差异。; 惩罚门仍未通过：在 grounded 范围内可牺牲部分 avant-garde 细节以换取更低 total_penalty，不必保留全部原始解构强度。; 【删除闸门】以下 penalty keys 尚未完成两次 rewrite，不允许删除导向：['consistency_penalty', 'coordination_penalty', 'generation_content_penalty', 'rationality_penalty']。 本轮仅允许改写（rewrite）路径；重写（rewrite-again）后仍无法消除的 penalty 才可进入删除步骤。

### Round `3`
- 分数变化：`0.85` -> `0.9375` (`0.0875`)
- 质量变化：`0.75` -> `0.8958` (`0.1458`)
- 重点 penalty：generation_content_penalty
- 重点 metric：core_information_density; visibility_priority; attribute_entity_binding; multi_garment_binding; quantity_accuracy; reference_clarity
- 重点模块：ConcisenessAndDensity; BindingAccuracy; LanguageClarity; StructuralClarity
- 策略备注：当前为第 `3` 轮优化。; 压缩冗余、无关与分析性表述，提升可直接生成的视觉信息密度。; 优先修复主干单品的一致性与同物件冲突绑定问题。; 重点收敛上身过度不协调的结构与材质对撞，统一造型语气后再保留有限不对称。; 上一轮质量提升有限，本轮优先处理未改善的质量项。
- 本轮附加修复目标：【多轮核心目标】以得分门与惩罚门同时通过为首要目的；择优时优先保留使任一门通过、或使 total_penalty 下降、或使得分门加权值上升的改写，不必以总分为唯一标准。; 多轮次·三步策略：对拉高 penalty、矛盾或难成像的表述，先改写、再重写同一证据片段；仅当两次改写后仍无法消除问题时再删除最小必要片段。; 进一步合并重复、去除解释性措辞并删除弱可见与无关稀释，提高主体可视化信息占比。; 减少次要配件和概念性补充，提升主体服装信息占比。; 主体单品的可见廓形、材质、颜色和外部造型必须优先于隐藏内里和局部弱可见细节。; 把属性和单品绑定写得更集中，避免一个句子跨多个实体切换。; 多单品描述时按单品分段组织，减少同一句里左右腿、左右脚、上装和配件混写。; 保留关键数字，但避免过多并列尺寸细节影响主结构识别。; 减少代词、省略和跳跃指代，直接点名对应单品和部位。; 压缩重复与解释性表述：先改写为紧凑 prompt 句式；仍占篇幅且弱成像的再删除弱可见、无关与元指令类内容。; 主干拒绝不对称：外套、内搭、下装、鞋履必须左右同类同源。; 若同一物件被描述成多个互斥状态，优先保留最稳定的一种绑定关系。; 衣、裤、鞋作为主干必须对称与稳定，禁止主类别左右切换。; 通过统一主色、主材质和主轮廓增强收束感，不保留主干不对称。; 【consistency·本轮】先穷尽合并/轻描 flagged 主干对撞，再删仍拉高惩罚的解构符号。; 清理与整体风格明显违和的搭配，确保鞋履、配件和主体服装在气质上互相衬托。; 优先消除单件上装左右互斥的风格场域（精裁西装式半侧 vs 对侧泡袖露肩高光泽丝绸等），统一为可成像的单一上装语法或明确分层。; 【coordination·本轮】合并优先；仍冲突时删较弱主干分支上的极端气质符号。; 本轮比上一轮更强调收束：若主干元素仍存在左右分叉，优先统一主干，再保留边缘层差异。; 后续轮次·强收敛解构：在不过度编造前提下，显著弱化左右袖/袖型极端对撞、裤腿开衩露内搭或第二裤型、单侧超长拖袖尾等非常规结构，改写为统一、易成像的轮廓。; 惩罚门仍未通过：在 grounded 范围内可牺牲部分 avant-garde 细节以换取更低 total_penalty，不必保留全部原始解构强度。; 上一轮质量提升有限，本轮优先解决仍未改善的低质量区域，而不是继续补充新信息。; 【强制·consistency】第2轮结束后当前最优稿仍 consistency>0 且裁判原因含不对称：本轮必须二选一——同一主干（含外套里布/裤装内衬若原文已写）禁止并列互斥左右或壳衬对撞；统一为单一可读结构或删较弱 grounded 分支，不得同时保留对打的双袖/双驳领等。


## Round Texts（各轮优化全文）
### Round `1` · 输入（本轮优化前）

```
**Look textual description**

**Look 1: Chrysalis Constraint**

**1. The Outerwear: Distorted Pinstripe Blazer**
A sharply tailored wool pinstripe blazer with intentional asymmetrical disruptions that challenge traditional suiting norms. The structured silhouette embodies societal constraints, while its manipulated proportions suggest emerging rebellion.

    *   **The Shoulder:** One shoulder extends aggressively with 2" shoulder pads creating dramatic angularity, while the opposite side remains softly unpadded to slope naturally. The right sleeve head is dramatically raised with internal boning.

    *   **The Lapel:** Standard 3.5" notched lapels on the right side contrast with a deconstructed 5" shawl lapel on the left, unfinished edges revealing silver paillette lining. The asymmetry creates tension when worn open.

    *   **The Closure:** Only the middle of three oxidized brass buttons functions, forcing the jacket to drape unevenly when fastened at a diagonal. The non-functional buttons are slightly misaligned to enhance the distorted effect.

    *   **The Length & Cut:** Standard 28" blazer length at back, but the front right panel extends an extra 3" into a sharp point. Internal canvas structure maintains form despite the visual distortion.

    *   **The Secret:** The left lining consists entirely of mercury morph paillettes suspended on conductive organza threads, flashing between silver and gold with movement - visible only when jacket flares open.

**2. The Foundation: Constraint Contrast Set**
Bodily contrasts emphasized through opposing fabric treatments and silhouettes between top and bottom.

    *   **The Shirt/Top:** Stiff 120s starched cotton shirt with button-on collar (detachable via hidden magnets). One sleeve extends 18" beyond normal proportions into a scarf-like tail, while the other remains cropped at mid-bicep.

    *   **The Trouser/Bottom:** High-waisted (12" rise) pinstripe wool trousers mirroring blazer fabric, cut with traditional forward pleats but sliced open along outer seams from mid-thigh down to reveal liquid jersey culottes lining in institutional gray.

    *   **The Fit & Line:** Creates a broken column silhouette - structured above the waist dissolving into fluidity below. The extended shirt sleeve counterbalances the trouser's weighty wool draping.

**3. The Details: Materiality & Hardware**
Precision interventions that reveal the collection's themes upon closer inspection.

    *   **The Cuffs:** Shirt features single-button surgeon's cuffs on the normal sleeve only. The extended sleeve remains uncuffed, raw edge revealing thermochromatic silk that shifts from gray to pearl-white when touched.

    *   **The Waist:** 1.5" wide matte calfskin belt with oxidized brass buckle positioned off-center at left hip. The belt loops are asymmetrical - three on right side only, emphasizing bodily distortion.

    *   **The Hands:** No jewelry except a single silver thumb ring on the dominant hand (right). Matte black leather half-gloves cover only the extended shirt sleeve's hand, leaving the other bare.

    *   **Additional Details:** All buttons are slightly mismatched - shirt features matte horn while jacket displays polished brass. Hidden inside collar stay pocket: miniature mirror engraved with "QUIS?" ("Who?" in Latin).

**4. The Finish: Footwear & Stance**
Grounding the look with weighted contrast to the upper distortions.

    *   **The Shoe:** Chunky 2" platform Oxfords in polished black calfskin with contrasting white piping. The exaggerated sole weight anchors the unstable upper silhouette.

    *   **The Stance:** Weight shifted permanently onto left leg due to shoe construction, creating a dynamic imbalance. The right foot rests lightly on its toe to accommodate extended trouser drape.

    *   **The Palette:** Prison-bar grayscale dominates (charcoal pinstripe, starched white shirt, black shoes) with calculated bursts - the hidden vermilion blazer lining flashes during movement like a warning signal.
```

### Round `1` · 输出（本轮 LLM 改写）

```
A sharply tailored wool pinstripe blazer with a broken-column silhouette, paired with a stiff starched white cotton shirt, high-waisted pinstripe wool trousers, and chunky 2" platform Oxfords in polished black calfskin with white piping. The blazer is 28" long at the back with a front right panel extending 3" into a sharp point, has a single functional middle button, oxidized brass buttons, and a visible silver paillette lining at the unfinished lapel edges; keep the overall tailoring coherent and structured, with only subtle asymmetry in the lapel and hem. The shirt has a button-on collar, single-button surgeon’s cuffs, and one sleeve that extends into a scarf-like tail while the other is cropped at mid-bicep, but the sleeve treatment should read as one unified deconstructed shirt design. The trousers are high-waisted with a 12" rise, forward pleats, and outer seams sliced open from mid-thigh down to reveal institutional-gray liquid jersey culotte lining. A 1.5" matte calfskin belt with an oxidized brass buckle sits off-center at the left hip, with three belt loops on the right side only. Accessories include a single silver thumb ring on the right hand and matte black leather half-gloves. The palette is prison-bar grayscale—charcoal pinstripe, starched white shirt, black shoes—with a restrained vermilion lining flash only when the blazer opens.
```

### Round `2` · 输入（本轮优化前）

```
A sharply tailored wool pinstripe blazer with a broken-column silhouette, paired with a stiff starched white cotton shirt, high-waisted pinstripe wool trousers, and chunky 2" platform Oxfords in polished black calfskin with white piping. The blazer is 28" long at the back with a front right panel extending 3" into a sharp point, has a single functional middle button, oxidized brass buttons, and a visible silver paillette lining at the unfinished lapel edges; keep the overall tailoring coherent and structured, with only subtle asymmetry in the lapel and hem. The shirt has a button-on collar, single-button surgeon’s cuffs, and one sleeve that extends into a scarf-like tail while the other is cropped at mid-bicep, but the sleeve treatment should read as one unified deconstructed shirt design. The trousers are high-waisted with a 12" rise, forward pleats, and outer seams sliced open from mid-thigh down to reveal institutional-gray liquid jersey culotte lining. A 1.5" matte calfskin belt with an oxidized brass buckle sits off-center at the left hip, with three belt loops on the right side only. Accessories include a single silver thumb ring on the right hand and matte black leather half-gloves. The palette is prison-bar grayscale—charcoal pinstripe, starched white shirt, black shoes—with a restrained vermilion lining flash only when the blazer opens.
```

### Round `2` · 输出（本轮 LLM 改写）

```
A sharply tailored wool pinstripe blazer, stiff starched white cotton shirt, high-waisted pinstripe wool trousers, and chunky 2" platform Oxfords in polished black calfskin with white piping. The blazer is 28" long at the back with a front right panel extending 3" into a sharp point, a single functional middle button, oxidized brass buttons, and visible silver paillette lining at the unfinished lapel edges; keep the tailoring coherent and structured with subtle asymmetry only in the lapel and hem. The shirt has a button-on collar and single-button surgeon’s cuffs. The trousers are high-waisted with a 12" rise and forward pleats. A 1.5" matte calfskin belt with an oxidized brass buckle sits off-center at the left hip, with three belt loops on the right side only. Accessories include a single silver thumb ring on the right hand and matte black leather half-gloves. The palette is charcoal pinstripe, starched white, and black, with a restrained vermilion lining flash when the blazer opens.
```

### Round `3` · 输入（本轮优化前）

```
A sharply tailored wool pinstripe blazer, stiff starched white cotton shirt, high-waisted pinstripe wool trousers, and chunky 2" platform Oxfords in polished black calfskin with white piping. The blazer is 28" long at the back with a front right panel extending 3" into a sharp point, a single functional middle button, oxidized brass buttons, and visible silver paillette lining at the unfinished lapel edges; keep the tailoring coherent and structured with subtle asymmetry only in the lapel and hem. The shirt has a button-on collar and single-button surgeon’s cuffs. The trousers are high-waisted with a 12" rise and forward pleats. A 1.5" matte calfskin belt with an oxidized brass buckle sits off-center at the left hip, with three belt loops on the right side only. Accessories include a single silver thumb ring on the right hand and matte black leather half-gloves. The palette is charcoal pinstripe, starched white, and black, with a restrained vermilion lining flash when the blazer opens.
```

### Round `3` · 输出（本轮 LLM 改写）

```
A tailored charcoal wool pinstripe blazer over a stiff starched white cotton shirt, paired with high-waisted pinstripe wool trousers and chunky 2-inch platform Oxfords in polished black calfskin with white piping. The blazer is structured and coherent, with a single functional middle button, oxidized brass buttons, a button-on collar, single-button surgeon’s cuffs, and a restrained vermilion lining flash when it opens. The trousers have a 12-inch rise and forward pleats. A 1.5-inch matte calfskin belt with an oxidized brass buckle sits off-center at the left hip, and the look is finished with a single silver thumb ring on the right hand and matte black leather half-gloves.
```


## Module Comparison
| Module | Before Score | After Score | Delta | Before Hits | After Hits | Before Applicable | After Applicable |
|---|---:|---:|---:|---:|---:|---:|---:|
| `BindingAccuracy` | `0.75` | `1.0` | `0.25` | `2` | `2` | `2` | `2` |
| `Composition` | `1.0` | `1.0` | `0.0` | `3` | `3` | `3` | `3` |
| `ConceptBonus` | `1.0` | `1.0` | `0.0` | `4` | `1` | `4` | `1` |
| `ConcisenessAndDensity` | `0.25` | `0.75` | `0.5` | `0` | `2` | `2` | `2` |
| `ConstructionDetail` | `1.0` | `1.0` | `0.0` | `4` | `2` | `4` | `2` |
| `GarmentCore` | `1.0` | `1.0` | `0.0` | `4` | `2` | `4` | `2` |
| `GenerationReadiness` | `0.4167` | `0.75` | `0.3333` | `0` | `3` | `3` | `3` |
| `LanguageClarity` | `0.75` | `1.0` | `0.25` | `2` | `2` | `2` | `2` |
| `MaterialColor` | `1.0` | `1.0` | `0.0` | `5` | `5` | `5` | `5` |
| `Specificity` | `1.0` | `1.0` | `0.0` | `2` | `2` | `2` | `2` |
| `StructuralClarity` | `0.75` | `1.0` | `0.25` | `1` | `1` | `1` | `1` |
| `StylingSet` | `1.0` | `1.0` | `0.0` | `4` | `4` | `4` | `4` |

## Metric Comparison
| Metric | Axis | Before Applicable | After Applicable | Before Hit | After Hit | Before Score | After Score | Delta |
|---|---|---|---|---|---|---:|---:|---:|
| `aesthetic_vocabulary` | `bonus_score` | `yes` | `yes` | `1` | `1` | `1.0` | `1.0` | `0.0` |
| `asymmetry` | `coverage_score` | `yes` | `yes` | `1` | `1` | `1.0` | `1.0` | `0.0` |
| `attribute_entity_binding` | `quality_score` | `yes` | `yes` | `1` | `1` | `0.75` | `1.0` | `0.25` |
| `bag` | `coverage_score` | `no` | `no` | `N/A` | `N/A` | `N/A` | `N/A` | `N/A` |
| `belt` | `coverage_score` | `yes` | `yes` | `1` | `1` | `1.0` | `1.0` | `0.0` |
| `bilateral_coherence` | `quality_score` | `yes` | `yes` | `0` | `1` | `0.25` | `0.75` | `0.5` |
| `body_coverage` | `coverage_score` | `yes` | `no` | `1` | `N/A` | `1.0` | `N/A` | `N/A` |
| `brand_alignment` | `bonus_score` | `no` | `no` | `N/A` | `N/A` | `N/A` | `N/A` | `N/A` |
| `closure` | `coverage_score` | `yes` | `yes` | `1` | `1` | `1.0` | `1.0` | `0.0` |
| `core_information_density` | `quality_score` | `yes` | `yes` | `0` | `1` | `0.25` | `0.75` | `0.5` |
| `cross_garment_binding` | `coverage_score` | `yes` | `yes` | `1` | `1` | `1.0` | `1.0` | `0.0` |
| `cultural_reference` | `bonus_score` | `yes` | `no` | `1` | `N/A` | `1.0` | `N/A` | `N/A` |
| `deconstruction` | `coverage_score` | `yes` | `no` | `1` | `N/A` | `1.0` | `N/A` | `N/A` |
| `fabric_family` | `coverage_score` | `yes` | `yes` | `1` | `1` | `1.0` | `1.0` | `0.0` |
| `fine_grained_attribute_usage` | `quality_score` | `yes` | `yes` | `1` | `1` | `1.0` | `1.0` | `0.0` |
| `footwear` | `coverage_score` | `yes` | `yes` | `1` | `1` | `1.0` | `1.0` | `0.0` |
| `functional_detail` | `coverage_score` | `yes` | `no` | `1` | `N/A` | `1.0` | `N/A` | `N/A` |
| `garment_category` | `coverage_score` | `yes` | `yes` | `1` | `1` | `1.0` | `1.0` | `0.0` |
| `gender_expression` | `bonus_score` | `no` | `no` | `N/A` | `N/A` | `N/A` | `N/A` | `N/A` |
| `generation_readiness` | `quality_score` | `yes` | `yes` | `0` | `1` | `0.5` | `0.75` | `0.25` |
| `hardware_embellishment` | `coverage_score` | `yes` | `yes` | `1` | `1` | `1.0` | `1.0` | `0.0` |
| `information_ordering` | `quality_score` | `yes` | `yes` | `1` | `1` | `0.75` | `1.0` | `0.25` |
| `jewelry` | `coverage_score` | `yes` | `yes` | `1` | `1` | `1.0` | `1.0` | `0.0` |
| `layering` | `coverage_score` | `yes` | `yes` | `1` | `1` | `1.0` | `1.0` | `0.0` |
| `length_hemline` | `coverage_score` | `yes` | `no` | `1` | `N/A` | `1.0` | `N/A` | `N/A` |
| `multi_garment_binding` | `quality_score` | `yes` | `yes` | `1` | `1` | `0.75` | `1.0` | `0.25` |
| `negation_control` | `bonus_score` | `yes` | `no` | `1` | `N/A` | `1.0` | `N/A` | `N/A` |
| `pattern_type` | `coverage_score` | `yes` | `yes` | `1` | `1` | `1.0` | `1.0` | `0.0` |
| `primary_color` | `coverage_score` | `yes` | `yes` | `1` | `1` | `1.0` | `1.0` | `0.0` |
| `quantity_accuracy` | `quality_score` | `yes` | `yes` | `1` | `1` | `0.75` | `1.0` | `0.25` |
| `reference_clarity` | `quality_score` | `yes` | `yes` | `1` | `1` | `0.75` | `1.0` | `0.25` |
| `secondary_color` | `coverage_score` | `yes` | `yes` | `1` | `1` | `1.0` | `1.0` | `0.0` |
| `silhouette` | `coverage_score` | `yes` | `yes` | `1` | `1` | `1.0` | `1.0` | `0.0` |
| `spatial_coherence` | `quality_score` | `yes` | `yes` | `0` | `1` | `0.5` | `0.75` | `0.25` |
| `specific_noun_usage` | `quality_score` | `yes` | `yes` | `1` | `1` | `1.0` | `1.0` | `0.0` |
| `surface_finish` | `coverage_score` | `yes` | `yes` | `1` | `1` | `1.0` | `1.0` | `0.0` |
| `theme_narrative` | `bonus_score` | `yes` | `no` | `1` | `N/A` | `1.0` | `N/A` | `N/A` |
| `top_bottom_proportion` | `coverage_score` | `yes` | `yes` | `1` | `1` | `1.0` | `1.0` | `0.0` |
| `visibility_priority` | `quality_score` | `yes` | `yes` | `0` | `1` | `0.25` | `0.75` | `0.5` |

## Changed Metric Details
### `aesthetic_vocabulary`
- 规则：`适度加入设计风格词汇`
- 优化前：applicable=`yes`，hit=`1`，score=`1.0`
- 优化后：applicable=`yes`，hit=`1`，score=`1.0`
- 优化前原因：The description uses explicit style and design vocabulary to frame the look.
- 优化后原因：The description uses explicit style and design vocabulary that frames the look aesthetically.
- 优化前命中证据："sharply tailored wool pinstripe blazer"; "structured silhouette"; "broken column silhouette"
- 优化后命中证据："tailored charcoal wool pinstripe blazer"; "structured and coherent"

### `asymmetry`
- 规则：`不对称设计存在时应被提到`
- 优化前：applicable=`yes`，hit=`1`，score=`1.0`
- 优化后：applicable=`yes`，hit=`1`，score=`1.0`
- 优化前原因：Asymmetry is a central design feature and is repeatedly specified across the blazer, shirt sleeve, and closure details.
- 优化后原因：The look includes explicit asymmetrical placement details, especially the off-center belt and right-hand-only ring.
- 优化前命中证据：“intentional asymmetrical disruptions”; “One shoulder extends ... while the opposite side remains softly unpadded”; “standard ... lapels on the right side contrast with a deconstructed ... lapel on the left”
- 优化后命中证据：“a single silver thumb ring on the right hand”; “matte black leather half-gloves”; “sits off-center at the left hip”

### `attribute_entity_binding`
- 规则：`属性必须绑定到正确实体；腰带、腿带、harness、护臂/护手等须明确归属外套、裤装或身体附件，避免腰胯多重束系指代漂移`
- 优化前：applicable=`yes`，hit=`1`，score=`0.75`
- 优化后：applicable=`yes`，hit=`1`，score=`1.0`
- 优化前原因：Most attributes are clearly tied to their intended entities and sides, with good separation between blazer, shirt, trousers, belt, gloves, and shoes. Minor complexity comes from heavy asymmetry and nested details, but the bindings remain interpretable and stable.
- 优化后原因：Attributes are consistently attached to the correct garments or body accessories, with clear left/right placement only where stated (e.g. right hand thumb ring, left hip belt).
- 优化前命中证据："matte calfskin belt with oxidized brass buckle positioned off-center at left hip"; "Matte black leather half-gloves cover only the extended shirt sleeve's hand"; "one shoulder extends... while the opposite side remains softly unpadded"
- 优化后命中证据："charcoal wool pinstripe blazer"; "matte black leather half-gloves"

### `bag`
- 规则：`整套 Look 中若包袋重要应被提到`
- 优化前：applicable=`no`，hit=`N/A`，score=`N/A`
- 优化后：applicable=`no`，hit=`N/A`，score=`N/A`
- 优化前原因：No bag or handbag is mentioned in the look description.
- 优化后原因：No bag is mentioned in the full look.
- 优化前命中证据：N/A
- 优化后命中证据：N/A

### `belt`
- 规则：`腰部强调明显时应被提到；若同时存在宽腰带、腰下固定点与腿带/吊带 harness 等多套腰胯束系，须说明与大衣/裤装的内外、上下与附着关系，避免腰胯层次不可成像`
- 优化前：applicable=`yes`，hit=`1`，score=`1.0`
- 优化后：applicable=`yes`，hit=`1`，score=`1.0`
- 优化前原因：A belt is explicitly included and visually emphasized at the waist.
- 优化后原因：A belt is explicitly present and emphasized with placement details.
- 优化前命中证据：1.5" wide matte calfskin belt; positioned off-center at left hip
- 优化后命中证据：“A 1.5-inch matte calfskin belt”; “sits off-center at the left hip”

### `bilateral_coherence`
- 规则：`当文本显式区分左右脚、左右腿、左右袖、左右肩或左右手配件时：若差异落在外穿/内搭/裤/鞋等主干上（含内外层上装），须有明确设计逻辑且与 penalty 一致（主干互斥应对齐或删）。**禁止**在 prompt 中同时堆叠多处主干左右对撞（多袖态+双腿异料+双脚异鞋等）仍声称一体解构而不收束——此类视为 bilateral 质量与生成导向双重风险，须低分直至合并或删支。若差异仅落在配饰/小附件且为轻度，而所有主干衣裤鞋已统一，质量分从宽。禁止无叙事支撑的「一侧重装金属护臂/高光护甲、对侧普通皮手套」等与主干对撞，除非文本给出统一的解构或主题设定`
- 优化前：applicable=`yes`，hit=`0`，score=`0.25`
- 优化后：applicable=`yes`，hit=`1`，score=`0.75`
- 优化前原因：The look stacks multiple left-right asymmetries across trunk garments and hands/sleeves, creating a highly complex bilateral structure that is difficult to translate cleanly into a single coherent image prompt without simplification.
- 优化后原因：The only explicit left-right distinctions are on accessories and small details, not on the main trunk garments. The outfit remains visually unified overall, so bilateral coherence is strong with only mild asymmetry.
- 优化前命中证据：“One shoulder extends aggressively ... while the opposite side remains softly unpadded”; “right sleeve head is dramatically raised”; “One sleeve extends 18" ... while the other remains cropped”; “single-button surgeon's cuffs on the normal sleeve only”; “Matte black leather half-gloves cover only the extended shirt sleeve's hand”
- 优化后命中证据：“off-center at the left hip”; “single silver thumb ring on the right hand”; “matte black leather half-gloves”

### `body_coverage`
- 规则：`文本需描述显著裸露或包裹区域`
- 优化前：applicable=`yes`，hit=`1`，score=`1.0`
- 优化后：applicable=`no`，hit=`N/A`，score=`N/A`
- 优化前原因：It clearly specifies exposed and covered body areas, including a cropped sleeve and one bare hand.
- 优化后原因：The text does not describe notable exposure, cutouts, or body-reveal coverage details.
- 优化前命中证据："one sleeve extends 18" beyond normal proportions into a scarf-like tail"; "the other remains cropped at mid-bicep"; "Matte black leather half-gloves cover only the extended shirt sleeve's hand, leaving the other bare"
- 优化后命中证据：N/A

### `brand_alignment`
- 规则：`仅在品牌任务中加入品牌语言`
- 优化前：applicable=`no`，hit=`N/A`，score=`N/A`
- 优化后：applicable=`no`，hit=`N/A`，score=`N/A`
- 优化前原因：No brand identity or brand-language target is explicitly mentioned.
- 优化后原因：No brand identity or brand-language target is mentioned.
- 优化前命中证据：N/A
- 优化后命中证据：N/A

### `closure`
- 规则：`显著开合方式应被提到`
- 优化前：applicable=`yes`，hit=`1`，score=`1.0`
- 优化后：applicable=`yes`，hit=`1`，score=`1.0`
- 优化前原因：The text clearly describes a salient button closure and how it functions.
- 优化后原因：The text clearly specifies multiple closure details, including button closure on the blazer and a buckle on the belt.
- 优化前命中证据："Only the middle of three oxidized brass buttons functions"; "fastened at a diagonal"
- 优化后命中证据：“single functional middle button”; “oxidized brass buttons”; “1.5-inch matte calfskin belt with an oxidized brass buckle”

### `core_information_density`
- 规则：`服装主体信息应占主要篇幅；多风格符号（军装肩章、大翻领、东方领型、金属护臂、腿带等）并列时须先确立可成像的主干轮廓与品类，再写配件，避免符号堆砌稀释 prompt 主干`
- 优化前：applicable=`yes`，hit=`0`，score=`0.25`
- 优化后：applicable=`yes`，hit=`1`，score=`0.75`
- 优化前原因：The description contains many vivid garment details, but it is heavily expanded with conceptual framing, section headers, and numerous low-priority hidden/internal details. The main wearable silhouette is present, yet the prompt is cluttered and the core outfit is diluted by excessive sub-detail.
- 优化后原因：The prompt is tightly packed with strong garment-defining details and keeps the main outfit readable. However, it includes several secondary construction details and accessory specifics that slightly reduce concision, so it is dense but not maximally streamlined.
- 优化前命中证据：“Look 1: Chrysalis Constraint”; “The Secret: The left lining consists entirely of mercury morph paillettes...”; “Hidden inside collar stay pocket: miniature mirror engraved with ‘QUIS?’”
- 优化后命中证据：“tailored charcoal wool pinstripe blazer”; “high-waisted pinstripe wool trousers”; “chunky 2-inch platform Oxfords”; “single silver thumb ring”

### `cross_garment_binding`
- 规则：`多单品时应能区分属性属于哪件单品`
- 优化前：applicable=`yes`，hit=`1`，score=`1.0`
- 优化后：applicable=`yes`，hit=`1`，score=`1.0`
- 优化前原因：Multiple garments are clearly separated and attributed, with distinct descriptions for blazer, shirt, trousers, belt, gloves, and shoes.
- 优化后原因：Multiple garments are clearly distinguished and their attributes are assigned to specific items, making the outfit composition coherent.
- 优化前命中证据：“The Outerwear”; “The Foundation: Constraint Contrast Set”; “The Shirt/Top” ... “The Trouser/Bottom”
- 优化后命中证据：“blazer over a stiff starched white cotton shirt”; “paired with high-waisted pinstripe wool trousers”; “A 1.5-inch matte calfskin belt ... sits off-center at the left hip”

### `cultural_reference`
- 规则：`仅在用户提供相关背景时加入文化或历史引用`
- 优化前：applicable=`yes`，hit=`1`，score=`1.0`
- 优化后：applicable=`no`，hit=`N/A`，score=`N/A`
- 优化前原因：It includes grounded cultural/linguistic references and institutional imagery.
- 优化后原因：No clear cultural, historical, or brand reference is provided.
- 优化前命中证据："Prison-bar grayscale"; "QUIS? ("Who?" in Latin)"; "institutional gray"
- 优化后命中证据：N/A

### `deconstruction`
- 规则：`存在解构设计时应被提到`
- 优化前：applicable=`yes`，hit=`1`，score=`1.0`
- 优化后：applicable=`no`，hit=`N/A`，score=`N/A`
- 优化前原因：The look strongly features deconstructed and reconstructed garment treatment.
- 优化后原因：The description presents a coherent tailored look and does not mention deconstruction, splicing, displacement, or reconstruction.
- 优化前命中证据："intentional asymmetrical disruptions"; "deconstructed 5\" shawl lapel"; "sliced open along outer seams"
- 优化后命中证据：N/A

### `fabric_family`
- 规则：`文本需给出主体材质类别`
- 优化前：applicable=`yes`，hit=`1`，score=`1.0`
- 优化后：applicable=`yes`，hit=`1`，score=`1.0`
- 优化前原因：The text clearly specifies the main fabric families for the outfit components.
- 优化后原因：The text clearly names the main fabric families for the garments and accessories.
- 优化前命中证据：“wool pinstripe blazer”; “starched cotton shirt”; “pinstripe wool trousers”; “polished black calfskin”
- 优化后命中证据：charcoal wool pinstripe blazer; white cotton shirt; pinstripe wool trousers; polished black calfskin

### `fine_grained_attribute_usage`
- 规则：`颜色、材质、结构词应尽量细粒度`
- 优化前：applicable=`yes`，hit=`1`，score=`1.0`
- 优化后：applicable=`yes`，hit=`1`，score=`1.0`
- 优化前原因：Attributes are extremely fine-grained across color, material, construction, and structure, with strong visual precision and imageability.
- 优化后原因：Color, material, fit, and structural details are rendered at a very fine grain, and the garment relationships are visually coherent and imageable.
- 优化前命中证据：“2" shoulder pads”; “3.5" notched lapels”; “oxidized brass buttons”; “thermochromatic silk”; “liquid jersey culottes lining”; “white piping”
- 优化后命中证据：“charcoal wool pinstripe”; “stiff starched white cotton”; “single functional middle button”; “single-button surgeon’s cuffs”; “vermilion lining flash”; “12-inch rise”

### `footwear`
- 规则：`整套 Look 中若鞋履重要应被提到`
- 优化前：applicable=`yes`，hit=`1`，score=`1.0`
- 优化后：applicable=`yes`，hit=`1`，score=`1.0`
- 优化前原因：Footwear is explicitly described and is a salient part of the full look.
- 优化后原因：Footwear is explicitly described and is a salient part of the outfit.
- 优化前命中证据：Chunky 2" platform Oxfords; polished black calfskin with contrasting white piping
- 优化后命中证据：“chunky 2-inch platform Oxfords”; “polished black calfskin with white piping”

### `functional_detail`
- 规则：`显著口袋、挂带或功能细节应被提到`
- 优化前：applicable=`yes`，hit=`1`，score=`1.0`
- 优化后：applicable=`no`，hit=`N/A`，score=`N/A`
- 优化前原因：Functional construction details are explicitly mentioned, including magnets and a hidden pocket.
- 优化后原因：No pockets, straps, or comparable utility-focused functional parts are described.
- 优化前命中证据："hidden magnets"; "Hidden inside collar stay pocket"
- 优化后命中证据：N/A

### `garment_category`
- 规则：`文本需明确给出服装主体品类`
- 优化前：applicable=`yes`，hit=`1`，score=`1.0`
- 优化后：applicable=`yes`，hit=`1`，score=`1.0`
- 优化前原因：The text explicitly names the main garment categories: blazer, shirt, trousers, and shoes.
- 优化后原因：The text clearly names the main garment categories and outfit components.
- 优化前命中证据："Distorted Pinstripe Blazer"; "shirt/top"; "trouser/bottom"; "Chunky 2" platform Oxfords"
- 优化后命中证据：“tailored charcoal wool pinstripe blazer”; “high-waisted pinstripe wool trousers”; “white cotton shirt”

### `gender_expression`
- 规则：`仅在描述明确需要时加入性别气质表达`
- 优化前：applicable=`no`，hit=`N/A`，score=`N/A`
- 优化后：applicable=`no`，hit=`N/A`，score=`N/A`
- 优化前原因：No explicit gender expression or androgyny is stated as a goal.
- 优化后原因：The text does not explicitly discuss gender expression or androgyny.
- 优化前命中证据：N/A
- 优化后命中证据：N/A

### `generation_readiness`
- 规则：`文本应可直接转为图像生成 prompt；须以可见廓形、品类与层次为先，多文化/多时代风格符号混用时应能收束为单一 look 身份，否则视为生成导向不足`
- 优化前：applicable=`yes`，hit=`0`，score=`0.5`
- 优化后：applicable=`yes`，hit=`1`，score=`0.75`
- 优化前原因：The text is rich in garment, silhouette, material, and styling detail, so it is usable as prompt material. However, it reads more like a design brief/concept essay than a clean generation prompt, with heavy explanatory language and many nested sub-notes that would need condensation.
- 优化后原因：The text is highly imageable and already close to a fashion prompt, with clear garment hierarchy, materials, colors, and styling details. It is still somewhat descriptive and detail-dense rather than fully prompt-optimized, but only minor cleanup would be needed.
- 优化前命中证据：“Look 1: Chrysalis Constraint”; “A sharply tailored wool pinstripe blazer”; “Chunky 2" platform Oxfords”
- 优化后命中证据：“A tailored charcoal wool pinstripe blazer over a stiff starched white cotton shirt”; “paired with high-waisted pinstripe wool trousers and chunky 2-inch platform Oxfords”; “single functional middle button… single-button surgeon’s cuffs… off-center at the left hip”

### `hardware_embellishment`
- 规则：`存在显著五金或装饰时应被提到`
- 优化前：applicable=`yes`，hit=`1`，score=`1.0`
- 优化后：applicable=`yes`，hit=`1`，score=`1.0`
- 优化前原因：The description includes prominent hardware and embellishment elements such as metal buttons and a ring.
- 优化后原因：The text includes clearly visible hardware and metallic embellishment elements.
- 优化前命中证据："oxidized brass buttons"; "silver thumb ring"; "white piping"
- 优化后命中证据：“oxidized brass buttons”; “oxidized brass buckle”; “single silver thumb ring”

### `information_ordering`
- 规则：`描述应按主体到细节的顺序组织`
- 优化前：applicable=`yes`，hit=`1`，score=`0.75`
- 优化后：applicable=`yes`，hit=`1`，score=`1.0`
- 优化前原因：The description is organized in a clear主体→结构→细节→完成度 sequence, making the outfit easy to reconstruct. There is some internal density and occasional cross-referencing between sections, but the overall ordering remains strong and readable.
- 优化后原因：The description moves in a clear主体→搭配→细节→配饰→收尾 order. Garments are introduced first, then structural details, then accessories and finishing touches, making the outfit easy to reconstruct visually.
- 优化前命中证据：“1. The Outerwear”; “2. The Foundation”; “3. The Details”; “4. The Finish”
- 优化后命中证据：“A tailored charcoal wool pinstripe blazer over a stiff starched white cotton shirt”; “paired with high-waisted pinstripe wool trousers and chunky 2-inch platform Oxfords”; “The blazer is structured and coherent”; “The trousers have a 12-inch rise and forward pleats”; “A 1.5-inch matte calfskin belt ... and the look is finished with ...”

### `jewelry`
- 规则：`显著首饰或身体装饰应被提到`
- 优化前：applicable=`yes`，hit=`1`，score=`1.0`
- 优化后：applicable=`yes`，hit=`1`，score=`1.0`
- 优化前原因：A clearly stated piece of jewelry is present and identifiable.
- 优化后原因：A clear piece of jewelry/body ornament is present and visible.
- 优化前命中证据：a single silver thumb ring; No jewelry except
- 优化后命中证据：“a single silver thumb ring”

### `layering`
- 规则：`多层叠搭时应给出层次关系；外套、内搭、腰带、腿带与裤装之间的遮盖与固定顺序应可还原为可见层次，服务生成导向`
- 优化前：applicable=`yes`，hit=`1`，score=`1.0`
- 优化后：applicable=`yes`，hit=`1`，score=`1.0`
- 优化前原因：The text clearly describes multiple garment layers and their visible relationships, including outerwear over shirt and trousers with revealed lining.
- 优化后原因：The text clearly describes layered garments and their visible relationship.
- 优化前命中证据：Outerwear: Distorted Pinstripe Blazer; The Foundation: Constraint Contrast Set; sliced open along outer seams ... to reveal liquid jersey culottes lining
- 优化后命中证据：“blazer over a stiff starched white cotton shirt”; “The blazer ... opens”; “a restrained vermilion lining flash”

### `length_hemline`
- 规则：`文本需给出长度或下摆信息`
- 优化前：applicable=`yes`，hit=`1`，score=`1.0`
- 优化后：applicable=`no`，hit=`N/A`，score=`N/A`
- 优化前原因：The description gives explicit garment length and hemline/extension details.
- 优化后原因：No garment length or hemline information is explicitly described.
- 优化前命中证据："front right panel extends an extra 3" into a sharp point"; "standard 28" blazer length"; "one sleeve extends 18" beyond normal proportions"
- 优化后命中证据：N/A

### `multi_garment_binding`
- 规则：`多单品描述时不得将属性归错单品`
- 优化前：applicable=`yes`，hit=`1`，score=`0.75`
- 优化后：applicable=`yes`，hit=`1`，score=`1.0`
- 优化前原因：The description cleanly separates multiple garments and generally assigns colors, materials, and structural details to the correct item. There is some dense cross-referencing across layers, but no major garment-to-garment attribute confusion.
- 优化后原因：Multiple garments are described with stable, unambiguous bindings for material, color, structure, and accessories; no major cross-item attribute drift is present.
- 优化前命中证据："The Outerwear: Distorted Pinstripe Blazer"; "The Shirt/Top"; "The Trouser/Bottom"; "The Shoe"
- 优化后命中证据："blazer over a stiff starched white cotton shirt"; "paired with high-waisted pinstripe wool trousers and chunky 2-inch platform Oxfords"

### `negation_control`
- 规则：`需要强调排除项时，明确说明没有什么`
- 优化前：applicable=`yes`，hit=`1`，score=`1.0`
- 优化后：applicable=`no`，hit=`N/A`，score=`N/A`
- 优化前原因：The text explicitly uses exclusions and absence to define the look.
- 优化后原因：The text does not emphasize exclusions or absence of elements.
- 优化前命中证据："No jewelry except a single silver thumb ring"; "The non-functional buttons"; "visible only when jacket flares open"
- 优化后命中证据：N/A

### `pattern_type`
- 规则：`有图案时需给出图案类型`
- 优化前：applicable=`yes`，hit=`1`，score=`1.0`
- 优化后：applicable=`yes`，hit=`1`，score=`1.0`
- 优化前原因：A clear pattern type is present: pinstripe.
- 优化后原因：The text explicitly identifies the pattern type as pinstripe.
- 优化前命中证据：“pinstripe blazer”; “pinstripe wool trousers”
- 优化后命中证据：pinstripe blazer; pinstripe wool trousers

### `primary_color`
- 规则：`文本需给出主色`
- 优化前：applicable=`yes`，hit=`1`，score=`1.0`
- 优化后：applicable=`yes`，hit=`1`，score=`1.0`
- 优化前原因：The dominant color palette is clearly stated as grayscale, with charcoal, white, and black as the main colors.
- 优化后原因：The look has clearly stated main colors, especially charcoal, white, and black.
- 优化前命中证据：“Prison-bar grayscale dominates”; “charcoal pinstripe, starched white shirt, black shoes”
- 优化后命中证据：charcoal; white cotton shirt; polished black calfskin

### `quantity_accuracy`
- 规则：`数量词应准确且不冲突`
- 优化前：applicable=`yes`，hit=`1`，score=`0.75`
- 优化后：applicable=`yes`，hit=`1`，score=`1.0`
- 优化前原因：Quantities are abundant and mostly internally consistent, with clear side-specific references. A few dense measurements and layered comparisons add slight reading load, but the numeric relations remain stable and understandable.
- 优化后原因：All explicit quantities and side references are internally consistent and easy to parse; no conflicting counts or ambiguous quantity relations appear.
- 优化前命中证据："2" shoulder pads; "three" oxidized brass buttons; "18"" beyond normal proportions; "12" rise
- 优化后命中证据：“single functional middle button”; “single silver thumb ring on the right hand”; “1.5-inch matte calfskin belt”

### `reference_clarity`
- 规则：`代词和省略指向必须清晰`
- 优化前：applicable=`yes`，hit=`1`，score=`0.75`
- 优化后：applicable=`yes`，hit=`1`，score=`1.0`
- 优化前原因：Pronouns and omitted subjects are generally clear, and side references are usually explicit. The description is long and highly segmented, so some references require brief re-parsing, but overall the antecedents remain recoverable.
- 优化后原因：Pronouns and omitted references are clear from context, and each clause cleanly attaches to the correct garment or accessory.
- 优化前命中证据："One shoulder extends... while the opposite side remains"; "the normal sleeve only"; "The extended sleeve remains uncuffed"; "the other bare"
- 优化后命中证据：“The blazer is structured and coherent”; “when it opens”; “the look is finished with”

### `secondary_color`
- 规则：`有明显副色时需描述；若为大衣内里、开衩内衬等高对比色块，应说明可见条件（如行走、开片时）或与主色区的衔接，避免孤立撞色无锚点、不利生成`
- 优化前：applicable=`yes`，hit=`1`，score=`1.0`
- 优化后：applicable=`yes`，hit=`1`，score=`1.0`
- 优化前原因：Distinct secondary accent colors are clearly described, including silver/gold, gray lining, and vermilion flashes with movement.
- 优化后原因：A distinct accent color is present, with vermilion as a visible lining flash and white piping as an additional contrast detail.
- 优化前命中证据：“silver paillette lining”; “flashing between silver and gold”; “institutional gray”; “hidden vermilion blazer lining flashes during movement”
- 优化后命中证据：restrained vermilion lining flash; white piping; oxidized brass buttons

### `silhouette`
- 规则：`文本需给出整体轮廓或结构趋势`
- 优化前：applicable=`yes`，hit=`1`，score=`1.0`
- 优化后：applicable=`yes`，hit=`1`，score=`1.0`
- 优化前原因：It clearly describes the overall shape and structural trend of the look.
- 优化后原因：It gives a clear structural silhouette through tailored, structured, high-waisted, pleated tailoring.
- 优化前命中证据："structured silhouette"; "broken column silhouette"; "dissolving into fluidity below"
- 优化后命中证据：“structured and coherent”; “high-waisted”; “12-inch rise and forward pleats”

### `spatial_coherence`
- 规则：`层次、前后、内外、上下、附着位置等空间关系必须清晰且视觉上合理；大衣与腰带、腰下吊带、腿带/harness 与裤管之间的遮盖、穿入与固定点须可还原，禁止腰胯多层束系含糊不可成像`
- 优化前：applicable=`yes`，hit=`0`，score=`0.5`
- 优化后：applicable=`yes`，hit=`1`，score=`0.75`
- 优化前原因：Most spatial relations are understandable and imageable, especially the open seams, lining reveal, and hidden pocket. Still, the description is dense and layered, with several concealed or conditional details that reduce immediate prompt clarity.
- 优化后原因：Layering and attachment positions are clearly stated and visually reconstructable. The spatial relations are coherent and imageable, though the text is still more specification-like than compositionally explicit.
- 优化前命中证据：“left lining consists entirely of mercury morph paillettes ... visible only when jacket flares open”; “sliced open along outer seams from mid-thigh down to reveal liquid jersey culottes lining”; “belt loops are asymmetrical - three on right side only”; “Hidden inside collar stay pocket”
- 优化后命中证据：“blazer over a stiff starched white cotton shirt”; “when it opens”; “belt… sits off-center at the left hip”

### `specific_noun_usage`
- 规则：`使用具体服装或配件名词而非泛词`
- 优化前：applicable=`yes`，hit=`1`，score=`1.0`
- 优化后：applicable=`yes`，hit=`1`，score=`1.0`
- 优化前原因：Uses highly specific garment nouns, materials, and footwear terms throughout, with clear fashion semantics and little reliance on generic wording.
- 优化后原因：The description uses highly specific garment names, materials, colors, and construction terms throughout, with clear fashion semantics and little reliance on generic wording.
- 优化前命中证据：“pinstripe blazer”; “starched cotton shirt”; “high-waisted pinstripe wool trousers”; “Chunky 2" platform Oxfords”
- 优化后命中证据：“tailored charcoal wool pinstripe blazer”; “stiff starched white cotton shirt”; “high-waisted pinstripe wool trousers”; “chunky 2-inch platform Oxfords”; “oxidized brass buttons”

### `surface_finish`
- 规则：`文本需给出光泽、哑光、垂坠或硬挺等表面性质`
- 优化前：applicable=`yes`，hit=`1`，score=`1.0`
- 优化后：applicable=`yes`，hit=`1`，score=`1.0`
- 优化前原因：Multiple surface traits are explicitly described, including stiffness, matte finish, polish, and drape.
- 优化后原因：Multiple surface traits are explicitly described, including stiffness, polish, and matte finish.
- 优化前命中证据：“sharply tailored”; “stiff 120s starched cotton”; “matte calfskin belt”; “polished black calfskin”; “fluidity below”
- 优化后命中证据：stiff starched; structured and coherent; polished black calfskin; matte calfskin belt; matte black leather half-gloves

### `theme_narrative`
- 规则：`仅在系列主题任务中加入叙事表达`
- 优化前：applicable=`yes`，hit=`1`，score=`1.0`
- 优化后：applicable=`no`，hit=`N/A`，score=`N/A`
- 优化前原因：The look is clearly built around a conceptual narrative and theme.
- 优化后原因：No series theme or conceptual narrative is stated.
- 优化前命中证据："Chrysalis Constraint"; "societal constraints"; "emerging rebellion"
- 优化后命中证据：N/A

### `top_bottom_proportion`
- 规则：`明显上下比例关系应被提到；长外套、阔腿或宽松下装、厚底鞋与腿带/harness 等叠加时，应交代主干剪影主次，避免仅堆砌元素导致下盘过重、prompt 失焦`
- 优化前：applicable=`yes`，hit=`1`，score=`1.0`
- 优化后：applicable=`yes`，hit=`1`，score=`1.0`
- 优化前原因：The text explicitly describes upper-versus-lower body proportion and visual balance, including waist emphasis and silhouette relationship.
- 优化后原因：The text clearly specifies a top-and-bottom outfit with waist placement and footwear that affects overall silhouette balance.
- 优化前命中证据：“broken column silhouette - structured above the waist dissolving into fluidity below”; “High-waisted ... trousers”; “The extended shirt sleeve counterbalances the trouser's weighty wool draping”
- 优化后命中证据：“high-waisted pinstripe wool trousers”; “chunky 2-inch platform Oxfords”; “A tailored charcoal wool pinstripe blazer over a stiff starched white cotton shirt”

### `visibility_priority`
- 规则：`可见且决定成像结果的主体信息应优先于隐藏、内部或低可见度细节，避免不可见信息喧宾夺主`
- 优化前：applicable=`yes`，hit=`0`，score=`0.25`
- 优化后：applicable=`yes`，hit=`1`，score=`0.75`
- 优化前原因：Several emphasized details are hidden, internal, or only visible in motion, which reduces prompt efficiency for image generation. The visible outer silhouette is described, but too much attention is given to low-visibility elements relative to what will dominate the image.
- 优化后原因：The description prioritizes visible trunk pieces and footwear, which are image-dominant and useful for generation. A few lower-visibility details like lining flash, collar construction, cuffs, and belt placement are included, but they do not overwhelm the main visible silhouette.
- 优化前命中证据：“visible only when jacket flares open”; “Hidden inside collar stay pocket”; “The Secret: The left lining...”
- 优化后命中证据：“tailored charcoal wool pinstripe blazer”; “high-waisted pinstripe wool trousers”; “chunky 2-inch platform Oxfords”; “restrained vermilion lining flash when it opens”


## Original Text

**Look textual description**

**Look 1: Chrysalis Constraint**

**1. The Outerwear: Distorted Pinstripe Blazer**
A sharply tailored wool pinstripe blazer with intentional asymmetrical disruptions that challenge traditional suiting norms. The structured silhouette embodies societal constraints, while its manipulated proportions suggest emerging rebellion.

    *   **The Shoulder:** One shoulder extends aggressively with 2" shoulder pads creating dramatic angularity, while the opposite side remains softly unpadded to slope naturally. The right sleeve head is dramatically raised with internal boning.

    *   **The Lapel:** Standard 3.5" notched lapels on the right side contrast with a deconstructed 5" shawl lapel on the left, unfinished edges revealing silver paillette lining. The asymmetry creates tension when worn open.

    *   **The Closure:** Only the middle of three oxidized brass buttons functions, forcing the jacket to drape unevenly when fastened at a diagonal. The non-functional buttons are slightly misaligned to enhance the distorted effect.

    *   **The Length & Cut:** Standard 28" blazer length at back, but the front right panel extends an extra 3" into a sharp point. Internal canvas structure maintains form despite the visual distortion.

    *   **The Secret:** The left lining consists entirely of mercury morph paillettes suspended on conductive organza threads, flashing between silver and gold with movement - visible only when jacket flares open.

**2. The Foundation: Constraint Contrast Set**
Bodily contrasts emphasized through opposing fabric treatments and silhouettes between top and bottom.

    *   **The Shirt/Top:** Stiff 120s starched cotton shirt with button-on collar (detachable via hidden magnets). One sleeve extends 18" beyond normal proportions into a scarf-like tail, while the other remains cropped at mid-bicep.

    *   **The Trouser/Bottom:** High-waisted (12" rise) pinstripe wool trousers mirroring blazer fabric, cut with traditional forward pleats but sliced open along outer seams from mid-thigh down to reveal liquid jersey culottes lining in institutional gray.

    *   **The Fit & Line:** Creates a broken column silhouette - structured above the waist dissolving into fluidity below. The extended shirt sleeve counterbalances the trouser's weighty wool draping.

**3. The Details: Materiality & Hardware**
Precision interventions that reveal the collection's themes upon closer inspection.

    *   **The Cuffs:** Shirt features single-button surgeon's cuffs on the normal sleeve only. The extended sleeve remains uncuffed, raw edge revealing thermochromatic silk that shifts from gray to pearl-white when touched.

    *   **The Waist:** 1.5" wide matte calfskin belt with oxidized brass buckle positioned off-center at left hip. The belt loops are asymmetrical - three on right side only, emphasizing bodily distortion.

    *   **The Hands:** No jewelry except a single silver thumb ring on the dominant hand (right). Matte black leather half-gloves cover only the extended shirt sleeve's hand, leaving the other bare.

    *   **Additional Details:** All buttons are slightly mismatched - shirt features matte horn while jacket displays polished brass. Hidden inside collar stay pocket: miniature mirror engraved with "QUIS?" ("Who?" in Latin).

**4. The Finish: Footwear & Stance**
Grounding the look with weighted contrast to the upper distortions.

    *   **The Shoe:** Chunky 2" platform Oxfords in polished black calfskin with contrasting white piping. The exaggerated sole weight anchors the unstable upper silhouette.

    *   **The Stance:** Weight shifted permanently onto left leg due to shoe construction, creating a dynamic imbalance. The right foot rests lightly on its toe to accommodate extended trouser drape.

    *   **The Palette:** Prison-bar grayscale dominates (charcoal pinstripe, starched white shirt, black shoes) with calculated bursts - the hidden vermilion blazer lining flashes during movement like a warning signal.

## Optimized Text

A tailored charcoal wool pinstripe blazer over a stiff starched white cotton shirt, paired with high-waisted pinstripe wool trousers and chunky 2-inch platform Oxfords in polished black calfskin with white piping. The blazer is structured and coherent, with a single functional middle button, oxidized brass buttons, a button-on collar, single-button surgeon’s cuffs, and a restrained vermilion lining flash when it opens. The trousers have a 12-inch rise and forward pleats. A 1.5-inch matte calfskin belt with an oxidized brass buckle sits off-center at the left hip, and the look is finished with a single silver thumb ring on the right hand and matte black leather half-gloves.
