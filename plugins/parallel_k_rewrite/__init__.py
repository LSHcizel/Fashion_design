"""第 1 步改进：同上下文并行 K 份英文改写候选（与既有串行 optimize 流程并存）。"""

from .k_candidate_generator import (
    REWRITE_ELEMENT_RECONSTRUCTION,
    REWRITE_LOCAL_EDITS_ALLOWED,
    REWRITE_STYLE_CONCEPT_LOCK,
    build_candidate_group_payload,
    build_rewrite_user_prompt,
    generate_k_parallel_rewrites,
)
from .select_best import pick_rewrite_if_better, rank_key
from ..text_description_evaluator.design_text_evaluator_api import (
    JudgeConnectionError,
    is_connection_failure,
)

__all__ = [
    "REWRITE_ELEMENT_RECONSTRUCTION",
    "REWRITE_LOCAL_EDITS_ALLOWED",
    "REWRITE_STYLE_CONCEPT_LOCK",
    "generate_k_parallel_rewrites",
    "build_candidate_group_payload",
    "build_rewrite_user_prompt",
    "pick_rewrite_if_better",
    "rank_key",
    "JudgeConnectionError",
    "is_connection_failure",
]
