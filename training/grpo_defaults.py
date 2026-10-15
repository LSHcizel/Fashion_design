"""GRPO 损失的默认系数。不依赖 torch，供各入口共用。"""

import math

# Schulman k3：exp(log π_ref - log π) - (log π_ref - log π) - 1，再对 completion token 平均。
# 小偏离时 k3 ≈ (1/2) (log ratio)^2。预算 0.005 对应 |log ratio| = 0.1 nat。
# 比率截断取 exp(±0.1)，与这个预算是同一个界限，不是 PPO 论文里的 0.8/1.2。
# 约 0.2 nat 时 k3 ≈ 0.02。动态系数从预算处的 0 按超出比例的平方升到上限。
KL_TARGET = 0.005
KL_SEVERE = 0.02
LOG_RATIO_BUDGET = math.sqrt(2.0 * KL_TARGET)
DEFAULT_BETA_KL = 10.0


def dynamic_kl_coefficient(kl: float, beta_max: float) -> float:
    """正常偏离不束缚；越出 0.1 nat 之后才逐渐加到 ``beta_max``。"""
    if beta_max <= 0.0 or kl <= KL_TARGET:
        return 0.0
    frac = (float(kl) - KL_TARGET) / (KL_SEVERE - KL_TARGET)
    if frac >= 1.0:
        return float(beta_max)
    return float(beta_max) * frac * frac
