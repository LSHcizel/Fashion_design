# SFT / GRPO 超参表 · 论文表说明

供后续 **GPT Images** 或 LaTeX/`booktabs` 绘制论文超参表。  
版式对齐参考图：**Table 2: Key hyperparameters for the SFT and GRPO training stages.**  
三线表、无竖线；左列左对齐，SFT/GRPO 列居中；不适用项写 **N/A**。

数值以仓库**现行默认**为准（不传 CLI 覆盖时）：  
`fashion_config.yaml` → `grpo.hf-local-training` / `parallel-k-rewrite`，  
以及 `training/hf_grpo/train_sft.py`、`train_grpo.py`、`model_load.py`。

---

## 0. 一句话

> **只训改写器 `Qwen2.5-7B-Rewriter`（LoRA）；基座 Instruct 作冻结 judge，不进 SFT/GRPO。**  
> 冷启动：SFT 一次 → 同口径短 GRPO 一轮；在线续跑由 `run_next_grpo_round` 再采样再 GRPO，KL 仍锚初始改写器快照。

---

## 1. 主表（论文用 · 英文定稿）

**Table 2: Key hyperparameters for the SFT and GRPO training stages.**

| Hyperparameter | SFT Stage | GRPO Stage |
| :--- | :---: | :---: |
| Base Model | Qwen2.5-7B-Rewriter | SFT-tuned Rewriter |
| Learning Rate | \(2.0 \times 10^{-5}\) | \(1.0 \times 10^{-6}\) |
| LR Scheduler | Linear | Constant |
| Warmup Ratio | 0.0 | N/A |
| Epochs | 1 | 1 |
| Effective Batch Size | 8 | 8 |
| Precision | bfloat16 | bfloat16 |
| Rollout Samples (\(N\)) | N/A | 8 |
| KL Coefficient | N/A | 0.001 |

**题注（英文）**

> Base model is the rewriter copy of Qwen2.5-7B-Instruct; the frozen Instruct checkpoint is used only as LLM-as-judge and is not updated.  
> SFT effective batch = `per_device_train_batch_size × gradient_accumulation_steps` = \(1×8\).  
> GRPO updates once per source group of \(N=K=8\) rollouts (`gradient_accumulation_steps=1`).  
> Default training uses LoRA (\(r=16\), \(\alpha=32\)); max sequence length 2048.  
> SFT may stop early on training-loss plateau; GRPO runs the scheduled epoch.

**题注（中文速查）**

> 基座为改写器副本；Instruct 只做冻结评判。SFT 有效 batch=8；GRPO 每组 \(K=8\) 一次更新。默认 LoRA r=16 / α=32；最大长度 2048。SFT 可早停；GRPO 跑满设定 epoch。

---

## 2. 字段释义与代码锚点

| 行 | 含义 | SFT 证据 | GRPO 证据 |
|---|---|---|---|
| Base Model | 训练对象 | `fashion_config.yaml` `hf-local-training.model` | Policy 接 SFT/上轮 ckpt；`ref-model` 冷冻锚点同 rewriter 初始路径 |
| Learning Rate | 优化器学习率 | `train_sft.py` `--lr` 默认 `2e-5` | `train_grpo.py` `--lr` 默认 `1e-6`；yaml 注释对齐 PromptEnhancer |
| LR Scheduler | 学习率日程 | 未显式设置 → HF `TrainingArguments` 默认 **linear** | 显式 `lr_scheduler_type="constant"` |
| Warmup Ratio | 预热比例 | 未设置 → HF 默认 **0.0** | Constant 日程下标 **N/A** |
| Epochs | 训练轮数 | 默认 `1.0`（可早停） | 每轮默认 `1.0`（`grpo-epochs-per-round`） |
| Effective Batch Size | 一次更新所见样本当量 | \(1×8=8\) | 一组 \(K=8\) 候选 = 一步；强制 `grad_accum=1` |
| Precision | 计算精度 | 默认 `bf16` | 默认 `bf16` |
| Rollout Samples \(N\) | 组内采样条数 | 监督阶段无 rollout | `parallel-k-rewrite.k: 8` |
| KL Coefficient | \(\beta_{\mathrm{KL}}\) | 无 KL 项 | `--beta-kl` 默认 `0.001` |

### 2.1 表外但应写入题注的训练设定

| 项 | SFT | GRPO |
|---|---|---|
| LoRA \(r\) / \(\alpha\) / dropout | 16 / 32 / 0.05 | 同左 |
| LoRA targets | q/k/v/o/gate/up/down_proj | 同左 |
| Max length | 2048 | 2048 |
| Gradient checkpointing | True | True |
| Min reward std（组过滤） | N/A | 0.05 |
| 早停 | patience=6 等（可 `--no-early-stop`） | N/A |

---

## 3. 版式规范（对齐参考 Table 2）

1. **三线表**：顶粗线 · 表头下细线 · 底粗线；**无竖线**、无斑马纹（可极浅灰，但参考图为纯白）  
2. **题注在表上方**：`Table 2: Key hyperparameters for the SFT and GRPO training stages.`  
3. **列**：Hyperparameter（左对齐）| SFT Stage（居中）| GRPO Stage（居中）  
4. **学习率**：科学计数 \(a \times 10^{b}\)；不要写成 `2e-5` 进终稿图  
5. **不适用**：粗体或常规 **N/A**（与参考图一致）  
6. **字体**：学术衬线（Times / Computer Modern 风格）；英文 only  
7. **禁止**：把 ODIN-RM、vLLM 端口、GPU 编号、早停细参画进主表（进题注或附录）

---

## 4. Markdown 可粘贴定稿表

```markdown
**Table 2: Key hyperparameters for the SFT and GRPO training stages.**

| Hyperparameter | SFT Stage | GRPO Stage |
| :--- | :---: | :---: |
| Base Model | Qwen2.5-7B-Rewriter | SFT-tuned Rewriter |
| Learning Rate | $2.0 \times 10^{-5}$ | $1.0 \times 10^{-6}$ |
| LR Scheduler | Linear | Constant |
| Warmup Ratio | 0.0 | N/A |
| Epochs | 1 | 1 |
| Effective Batch Size | 8 | 8 |
| Precision | bfloat16 | bfloat16 |
| Rollout Samples ($N$) | N/A | 8 |
| KL Coefficient | N/A | 0.001 |
```

---

## 5. GPT Images Prompt 包

```text
Academic paper table, English only, booktabs three-line style (thick top rule, thin mid rule under header, thick bottom rule). No vertical lines. White background, black text, serif font like Times New Roman.

Title centered above the table:
"Table 2: Key hyperparameters for the SFT and GRPO training stages."

Three columns, header row: Hyperparameter | SFT Stage | GRPO Stage
First column left-aligned; second and third columns center-aligned.
Header text not bold; clean academic look.

Exact rows (9 data rows):
Base Model | Qwen2.5-7B-Rewriter | SFT-tuned Rewriter
Learning Rate | 2.0 × 10^-5 | 1.0 × 10^-6
LR Scheduler | Linear | Constant
Warmup Ratio | 0.0 | N/A
Epochs | 1 | 1
Effective Batch Size | 8 | 8
Precision | bfloat16 | bfloat16
Rollout Samples (N) | N/A | 8
KL Coefficient | N/A | 0.001

Render Learning Rate with proper scientific notation (a × 10^b), not "2e-5".
Write N/A exactly where shown. No icons, no shadows, no colored cells.
Optional tiny footnote under table in gray:
"Rewriter LoRA r=16, α=32; max length 2048. Frozen Qwen2.5-7B-Instruct used only as judge."
```

---

## 6. 与参考图 / 历史跑次的差异（勿混用）

| 来源 | 说法 | 本表是否采用 |
|---|---|---|
| 用户参考 Table 2（他文） | SFT lr \(1×10^{-5}\)，warmup 0.1，epoch 2，batch 128 | **否**（他文超参） |
| 本仓库现行默认 | SFT lr **\(2×10^{-5}\)**，warmup **0.0**，epoch **1**，batch **8**；GRPO lr \(1×10^{-6}\)，constant，\(\beta=0.001\)，\(N=8\) | **是** |
| 部分旧汇报 / 过时 docstring | GRPO 0.25 epoch × 多轮、\(\beta=0.04\) 等 | **否**（历史实验，与现行默认不一致） |

---

## 7. 更新规则

1. 改默认超参时，同步改 §1、§4、§5，并核对 `train_sft.py` / `train_grpo.py` / `fashion_config.yaml`。  
2. 若某次论文报告的是**覆盖后的实跑**（非默认），在题注写清 run-id，勿静默改主表。  
3. 主表保持与参考图**同行集合**；LoRA / max length / 早停只放题注或附录表。
