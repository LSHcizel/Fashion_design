"""
ODIN 档 3：蒸馏裁判为本地双头 RM，GRPO 只用 r_Q。

采数仍走裁判 0～1 分。本包在其后插入：

    samples.jsonl → 偏好对 → 训 r_Q/r_L → 用 r_Q 重写 R_content → 导出 phase_a/b

入口::

    python -m training.odin_rm.run_pipeline --samples ... --work-dir ...
"""

from .data import apply_r_q_to_record, teacher_score
from .pairs import build_preference_pairs, pairs_from_group

__all__ = [
    "apply_r_q_to_record",
    "teacher_score",
    "build_preference_pairs",
    "pairs_from_group",
]
