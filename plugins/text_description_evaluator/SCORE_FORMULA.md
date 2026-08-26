# 文本评分公式说明

> 规范：`fashion_prompt_optimizer_spec.json`（v0.5.0）  
> 代码：`design_text_evaluator_api.py` · `r_content_reward.py` · `score_formula.py` · `training/odin_rm/`

对齐 ODIN：训练吃内容通道，长度不进总分。

---

## 1. 符号

| 符号 | 含义 |
|------|------|
| C | 覆盖度轴：适用 coverage 指标的算术平均 |
| Q_w | 质量模块加权均分 |
| Q | 质量有效分（经 cap，**不含** penalty） |
| w_c, w_q | 覆盖 / 质量轴权重（见 spec） |
| cap_q, cap_t | 质量分上限、总分上限 |
| L | strip 后正文字符数 eval_prose |
| S_fp | 最终综合分，现行等于 s_fp_base |
| P̄ | 惩罚项算术平均 total_penalty |
| γ | 惩罚乘性并入系数 gamma_penalty（现行 0） |
| β | 组内长度修正系数 beta_z_len |
| z_len | 组内 log 长度 z-score |
| τ_s, τ_p | 得分 / 惩罚门限 |
| R_content | RL/GRPO 内容通道 |

---

## 2. 流程（文字）

1. **预处理**：去掉 T2I 固定句、章节标题等，得到 eval_prose。
2. **LLM 评判**：coverage（0/1）、quality（五档 0~1）、penalty（0~1）；不适用项跳过。
3. **质量加权**：六个 quality 子模块按 spec 权重求 Q_w。
4. **质量有效分**：Q = min(Q_w, cap_q)；penalty **不参与** Q 与 S_fp。
5. **内容主分**：s_fp_base = min(w_c·C + w_q·Q, cap_t)。
6. **S_fp**：等于 s_fp_base。长度回归只作诊断，不扣总分。
7. **双门限**：S_fp ≥ τ_s 且 P̄ ≤ τ_p；P̄ 不扣 S_fp。
8. **R_content**：单条等于 s_fp_base；GRPO 同组 K 条再减 β·z_len。组上记录 ρ(R, log_len)。

---

## 3. 关键公式

```
Q_w = Σ(w_i · m_i) / Σ(w_i)

Q = min(Q_w, cap_q)

s_fp_base = min(w_c · C + w_q · Q, cap_t)

S_fp = s_fp_base

score_gate:  S_fp ≥ τ_s
penalty_gate: P̄ ≤ τ_p

单条:     R_content = s_fp_base
GRPO组内: R_content = clip(s_fp_base - β · z_len, 0, 1)
```

---

## 4. 一行总式

```
S_fp = min(w_c·C + w_q·Q, cap_t)

R_content = S_fp                         # 单条
R_content = clip(S_fp - β·z_len, 0, 1)   # GRPO 同组
```

γ = 0 时惩罚不进奖励。档 3 见第 6 节：用 r_Q 替换组内 R_content。

---

## 5. 长度诊断

`holdout_regression.mix_into_score = false`：`a`、`x_0` 只用来对照旧口径，不改分数。

GRPO 同组调用 `apply_group_z_len_r_content` 后，结果里带 `odin_diagnostics`（Pearson）。档 3 采数若把 `odin_stage` 设为 3，则不再减 z_len。

---

## 6. 档 3（双头 RM）

裁判质量轴 `Q` 仍是 0～1，只当老师。本地 RM：

```
r_Q = W_Q · h(x,y)     # 无界
r_L = W_L · h(x,y)
L_RM = −log σ((r_Q+r_L)⁺ − (r_Q+r_L)⁻) + ρ(r_Q,ℓ) − ρ(r_L,ℓ) + |W_Q·W_L|
R_content := r_Q       # GRPO 只用这个；不减 β·z_len
```

入口：`python -m training.odin_rm.run_pipeline --samples <samples.jsonl> --work-dir <dir>`  
然后再跑 `training/hf_grpo/run_recommended_training.py`（phase_a/b 已按 r_Q 算 advantage）。
