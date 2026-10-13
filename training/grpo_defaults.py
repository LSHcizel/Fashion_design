"""GRPO 损失的默认系数。不依赖 torch，供各入口共用。"""

# Schulman k3：exp(log π_ref - log π) - (log π_ref - log π) - 1，再对 completion token 平均。
# 采样 token 的对数概率比参考高 0.1 nat 时，k3 ≈ 0.00484，对 log π 的导数约为 0.095。
# beta = 10 时，这个偏离上的 KL 梯度与优势约为 1 的策略项同一量级。
# 旧的 0.001 乘的是整句平均对数概率之差的平方，约束不到 token，会把概率推出词表。
DEFAULT_BETA_KL = 10.0
