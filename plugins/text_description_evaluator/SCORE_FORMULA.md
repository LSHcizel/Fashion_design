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
3. **质量加权**：七个 quality 子模块按 spec 权重求 Q_w。信息密度、可见性优先级、生成适配的权重都是 5。信息密度只给「识别锚点还在、每句新增可成像事实」加分，不按字数加分，删掉识别锚点最高 0.5。这三项的裁判 prompt 带 few-shot 模板，按最近例打分。
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
r_Q + r_L 还原 S_fp
gap_s = S_fp⁺ − S_fp⁻
|gap_s| < 0.20：
  gap_t = gap_s          # 整段留在 r_Q
  t_L = 0                # 两侧都不扣
  u = 1，w_gap = 1
|gap_s| ≥ 0.20：
  w_ex = 0                            # |ℓ⁺−ℓ⁻| ≤ 0.10 nat
       = (|Δℓ|−0.10) / (ln2−0.10)    # 其间
       = 1                            # |Δℓ| ≥ ln 2，超长
  w_rl = 1                            # |r_L⁺−r_L⁻| ≤ 0.10
       = 0                            # |r_L⁺−r_L⁻| ≥ 0.20
  w_hi = 0                            # ℓ⁺−ℓ⁻ ≤ 0.10：高分不更长
       = (ℓ⁺−ℓ⁻−0.10) / (ln2−0.10)   # 高分一侧更长
       = 1                            # 高分一侧长到约两倍
  w_gap = max(1 − w_ex, w_rl, w_hi)
  gap_t = max(gap_s − 0.20·w_hi, 0)  # 高分过长时缩小分差
  t_L(长) = 0.20 · w_ex               # 短侧目标是 0；不超长时两边都是 0
  u = 1
L_RM = Σ u · ((r_Q + r_L − S_fp)²) / Σ u
     + Σ w_gap · (gap_q − gap_t)² / Σ w_gap
     + mean((r_L − t_L)²)
R_content := r_Q
```

比较对只在同一 `group_id` 内两两构造，不跨组。组内分差不到 0.20 时，`r_Q` 分差对齐原始分差，偏大偏小都算损失，两侧 `r_L` 收到 0。固定扣 0.20 会把这条分差收成 0，所以这一档不扣。分差达到 0.20 之后，`r_L` 才在一侧超长时取到最多 0.20。句长差在 0.10 nat 以内，或两侧 `r_L` 仍接近时，`r_Q` 分差继续对齐 `S_fp` 分差。高分一侧明显更长时，对齐的目标改为把 `S_fp` 分差缩小，长到约两倍时缩小 0.20。高分一侧更短时不缩小。策略训练只取 `r_Q`。GRPO 丢掉组内标准差低于 0.01 的组。

入口：`python -m training.odin_rm.run_pipeline --samples <samples.jsonl> --work-dir <dir>`  
然后再跑 `training/hf_grpo/run_recommended_training.py`（phase_a/b 已按 r_Q 算 advantage）。
