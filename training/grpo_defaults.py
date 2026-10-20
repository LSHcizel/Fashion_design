"""GRPO 损失的默认系数。不依赖 torch，供各入口共用。"""

import math

# Schulman k3：exp(log π_ref - log π) - (log π_ref - log π) - 1，再对 completion token 平均。
# 比率截断仍用 0.005 对应的 ±0.1 nat。KL 系数本身是常数，对齐 PromptEnhancer 的 0.001。
KL_TARGET = 0.005
LOG_RATIO_BUDGET = math.sqrt(2.0 * KL_TARGET)
DEFAULT_BETA_KL = 0.001
# 8 组 × 每组 8 条 = 64 条，对齐 PromptEnhancer 的 global batch。
GROUPS_PER_UPDATE = 8
