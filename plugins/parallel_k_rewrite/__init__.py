"""第 1 步改进：同上下文并行 K 份英文改写候选（与既有串行 optimize 流程并存）。"""

from .k_candidate_generator import build_candidate_group_payload, generate_k_parallel_rewrites
from ..text_description_evaluator.design_text_evaluator_api import (
    JudgeConnectionError,
    is_connection_failure,
)

__all__ = [
    "generate_k_parallel_rewrites",
    "build_candidate_group_payload",
    "JudgeConnectionError",
    "is_connection_failure",
]
