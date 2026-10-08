# Stage 1 · Multi-Agent Look Generation · 真实案例插图说明

供后续 **GPT Images 2** 绘制论文用 flowchart。  
范围：**仅左上角 Stage A（Multi-Agent Look Generation）**，不画 Evaluator / Rewrite / T2I。  
视觉语言对齐 PromptEnhancer Fig.2 / 既有生成主干图：分区圆角容器、蓝实心 Agent、虚线框中间产物、三列层级。

---

## 0. 真实案例一句话

> **Chanel Cruise 2027「Sous le Salon la Plage」→ Theme Analysis 分裂为 2 个子主题 → 展开「The Artistic Revolution」→ Design Elements → `look_01.txt`。**

案例来源：`fashion_config.yaml`（design-target / theme / description）。  
已真实调用远程 API（`gpt-4o-mini` @ ohmygpt）跑通 Stage A；产物目录：

`fashion_research_dir/workflow_0/stage1_figure_case/2026-10-02/`

运行脚本：`scripts/run_stage1_case_for_figure.py`

---

## 1. 图中应出现的真实中间产物（已截短，供虚线框）

### 1.1 输入（Collection-level）

| 框标签 | 图中展示文案（英文，尽量短） |
|--------|------------------------------|
| `# Design target prompt` | `Analyze the theme of Chanel Cruise 2027 collection Sous le Salon la Plage for fashion design development` |
| `# Theme description` | `Sous le Salon la Plage` + 一行补充：`Away from the Paris salon, Chanel found in Biarritz a new way of being…`（省略号截断即可） |

### 1.2 Theme Analysis 后（Concept divergence）

虚线框 **Theme analysis**（可只显示 Theme 首句）：

> Sous le Salon la Plage — fluidity between haute couture and beachwear; Biarritz heritage × contemporary rebellion.

虚线框 **Sub-themes**（两个并列小框）：

1. `The Artistic Revolution`
2. `The Coastal Elegance`

（真实文件：`theme_analysis.txt`；解析时忽略模型误写的字面 “Sub-theme title:”，图中只用标题。）

可选小字旁注（不必占主框）：上游还产出 `description_key_elements.txt`（Heritage / Biarritz / Blazy / Basque stripes…），图中可不展开。

### 1.3 Concept Brainstorming（Sub-theme-level）

输入虚线：`Sub-theme: The Artistic Revolution`  
输出虚线 **Chapter concept**（短句）：

> Structure × fluidity as canvases of rebellion; iridescent organza cape, brushstroke trench, oceanic blue / coral / lime.

（真实文件：`chapter_01/design_chapter.txt`）

### 1.4 Design Elements → Look Description（Look-level）

虚线框 **Candidate elements**（三条短标签即可）：

- `Iridescent Organza Layering`
- `Geometric Fluidity Visual`
- `Abstract Brushstroke Prints`

（真实文件：`chapter_01/design_element&concept.txt`）

虚线框 **`look_01.txt` — real case**（一篇成段短描述，勿贴相机约束前缀）：

> A tailored beach cover-up trench with abstract brushstrokes in oceanic blue and coral, worn open over a lime-green silk mini-dress; sculpted lapels, beaded sleeve fringes, strappy sandals.

（真实文件：`chapter_01/look_01.txt`）

---

## 2. 建议图结构（仅 Stage A，横向三列）

对齐参考图左上：三列层级 + 顶栏概念进程。

```
┌──────────────────────────────── Stage 1: Multi-Agent Look Generation ────────────────────────────────┐
│                                                                                                      │
│   Collection-level          Sub-theme-level                 Look-level                               │
│   Concept divergence    →   Concept exploration         →   Feature convergence + verbalization      │
│                                                                                                      │
│  [# Design target]          [Sub-theme n]                   [Design context]                         │
│  [# Theme desc.]                 │                          [Look feature sampling]                  │
│         │                        │                                   │                               │
│   ┌──────────────┐         ┌──────────────────┐          ┌─────────────┐   ┌────────────────┐      │
│   │Theme Analysis│ ──────► │Concept           │ ───────► │Design       │ → │Look Description│      │
│   │   (agent)    │         │Brainstorming     │          │Elements     │   │    (agent)     │      │
│   └──────────────┘         └──────────────────┘          └─────────────┘   └────────────────┘      │
│         │                        │                                   │              │                │
│  [Theme analysis]          [Chapter concept]              [Candidate elements]                      │
│  [The Artistic Revolution] [The Artistic Revolution…]                                               │
│  [The Coastal Elegance]                                              └─► [look_01.txt real case]    │
└──────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

要点：

- 左列：目标 + 主题描述 → Theme Analysis → 分析摘要 + **两个**子主题虚线框（体现 divergence）。
- 中列：只把 **The Artistic Revolution** 送入 Concept Brainstorming（另一子主题虚线悬置，示意未展开）。
- 右列：Design Elements → Look Description → `look_01.txt`。
- Agent 盒右上角可加小齿轮图标（与参考图一致）；本图 **不要** ❄️（Stage A 是可训练/可调用的生成 agents，非冻结 judge）。

---

## 3. 各块英文标注（出图用）

### Panel title
`Stage 1: Multi-Agent Look Generation`

### Column headers（顶）
| 列 | 层级 | 进程 |
|----|------|------|
| Left | `Collection-level` | `Concept divergence` |
| Mid | `Sub-theme-level` | `Concept exploration` |
| Right | `Look-level` | `Feature convergence + verbalization` |

### Agent boxes（实心蓝）
1. `Theme Analysis`
2. `Concept Brainstorming`
3. `Design Elements`
4. `Look Description`

### Case strip（可选顶栏小条，证明真实案例）
`Case: Chanel Cruise 2027 · Sous le Salon la Plage`

---

## 4. 视觉规范（与主干图一致）

| 元素 | 规范 |
|------|------|
| 画幅 | 横向单图；**只画 Stage A 一个浅蓝大容器**（不要画 B/C） |
| 背景 | 白底 |
| Stage 容器 | 浅蓝 fill `#EAF1F8` + 蓝边 `#6E96C0`，圆角；标题蓝粗斜体 |
| Agent 盒 | 实心中蓝 / 浅蓝圆角矩形（或轻微梯形，贴近参考图） |
| 中间产物 | **灰虚线圆角框**；正文 1–3 行，字号小于 Agent 标题 |
| 主路径 | 实心蓝箭头（左→右） |
| 未展开子主题 | 虚线框 + 浅灰，无粗箭头引出即可 |
| 字体 | 无衬线；图内主标注英文 |
| 禁止 | Evaluator、Dual Gate、Rewriter、T2I、❄️、火焰、GRPO/SFT、训练红虚线、紫渐变、3D |

---

## 5. GPT Images 2 出图提示词

```text
Create a clean scientific paper flowchart (single figure, landscape, white background, high resolution) in the visual style of PromptEnhancer Figure 2 / multi-agent fashion pipeline diagrams.

SCOPE: ONLY the top-left stage. Title (italic bold blue): "Stage 1: Multi-Agent Look Generation".
Do NOT draw Stage B (DesignTextEvaluator), Stage C (rewrite/T2I), dual gates, snowflakes, training loops, GRPO, or SFT.

REAL CASE banner under the title (small): "Case: Chanel Cruise 2027 · Sous le Salon la Plage"

Layout: ONE large light-blue rounded panel (#EAF1F8 fill, #6E96C0 border) divided into THREE vertical columns with headers:
1) Collection-level — Concept divergence
2) Sub-theme-level — Concept exploration
3) Look-level — Feature convergence + verbalization

Color palette: white background, soft blue fills, medium-blue solid agent boxes with white titles, grey dashed boxes for intermediate artifacts. Sans-serif. No purple, no 3D, no clutter.

LEFT COLUMN:
- Two dashed input boxes:
  "# Design target prompt" with text: "Analyze the theme of Chanel Cruise 2027 collection Sous le Salon la Plage for fashion design development"
  "# Theme description" with text: "Sous le Salon la Plage — Away from the Paris salon, Chanel found in Biarritz a new way of being…"
- Solid blue agent box: "Theme Analysis" (tiny gear icon optional)
- Dashed output: short theme summary "haute couture × beachwear; Biarritz heritage × rebellion"
- Two dashed sub-theme boxes: "The Artistic Revolution" and "The Coastal Elegance"

MIDDLE COLUMN:
- Arrow from "The Artistic Revolution" into solid blue agent "Concept Brainstorming"
- Dashed outputs: "Chapter concept" with short text "structure × fluidity; organza cape; brushstroke trench; oceanic blue / coral / lime"
- Keep "The Coastal Elegance" unexpanded (no strong arrow)

RIGHT COLUMN:
- Solid blue agents in sequence: "Design Elements" → "Look Description"
- Dashed "Candidate elements": "Iridescent Organza Layering · Geometric Fluidity · Abstract Brushstroke Prints"
- Final dashed box labeled "look_01.txt — real case" containing:
  "A tailored beach cover-up trench with abstract brushstrokes in oceanic blue and coral, worn open over a lime-green silk mini-dress; sculpted lapels, beaded sleeve fringes, strappy sandals."

Solid blue arrows for the main left-to-right path. Balanced whitespace, paper-figure aesthetic, high readability, no watermark, no logo.
```

### 出图检查清单

- [ ] 仅 Stage A，无 Evaluator / Rewrite / T2I  
- [ ] 三列：Collection / Sub-theme / Look + 顶栏 divergence → exploration → convergence  
- [ ] 真实案例文案已嵌入虚线框（Chanel / Biarritz / 两子主题 / look_01）  
- [ ] Agent 实心蓝；产物虚线框  
- [ ] 无训练元素、无 ❄️  

---

## 6. 机读结构（可选）

```json
{
  "figure": "stage1_multi_agent_look_generation_real_case",
  "case": {
    "brand": "Chanel",
    "theme": "Sous le Salon la Plage",
    "season": "Cruise 2027",
    "artifact_dir": "fashion_research_dir/workflow_0/stage1_figure_case/2026-10-02"
  },
  "columns": [
    {
      "level": "Collection-level",
      "progress": "Concept divergence",
      "agent": "Theme Analysis",
      "inputs": ["design-target-prompt", "theme description"],
      "outputs": [
        "theme analysis summary",
        "The Artistic Revolution",
        "The Coastal Elegance"
      ]
    },
    {
      "level": "Sub-theme-level",
      "progress": "Concept exploration",
      "agent": "Concept Brainstorming",
      "selected_subtheme": "The Artistic Revolution",
      "outputs": ["chapter concept"]
    },
    {
      "level": "Look-level",
      "progress": "Feature convergence + verbalization",
      "agents": ["Design Elements", "Look Description"],
      "outputs": [
        "candidate elements",
        "look_01.txt"
      ]
    }
  ]
}
```

---

## 7. 产物路径速查

| 阶段 | 文件 |
|------|------|
| Description 关键要素 | `.../description_key_elements.txt` |
| Theme Analysis | `.../theme_analysis.txt` |
| Chapter concept | `.../chapter_01/design_chapter.txt` |
| Design elements | `.../chapter_01/design_element&concept.txt` |
| Look 描述 | `.../chapter_01/look_01.txt` |
| 输入快照 | `.../_case_inputs.md` |

路径前缀：`fashion_research_dir/workflow_0/stage1_figure_case/2026-10-02/`

---

## 8. 相关材料

| 材料 | 用途 |
|------|------|
| 本文 | Stage A 真实案例插图 brief |
| `汇报/生成工作流主干_论文流程图说明.md` | 全链路主干图（A+B+C） |
| 用户提供的 PromptEnhancer Fig.2 风格参考图 | 视觉语言母版 |
| `fashion_config.yaml` L4–31 | 案例输入 |
| `scripts/run_stage1_case_for_figure.py` | 复现 API 跑通 |
