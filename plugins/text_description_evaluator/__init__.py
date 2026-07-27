"""Standalone text-description evaluator plugin for fashion prompts."""

from .design_text_evaluator_api import (
    DEFAULT_HF_LOCAL_GRPO_MODEL,
    DesignTextEvaluator,
    default_hf_local_grpo_model,
    grpo_config,
    grpo_design_text_evaluator_config,
    grpo_hf_local_training_config,
    grpo_parallel_k_rewrite_config,
    grpo_training_data_config,
    load_default_evaluator,
)
from .r_content_reward import (
    apply_group_z_len_r_content,
    apply_length_disentangle,
    build_r_content_payload,
    fit_holdout_length_centered,
    fit_holdout_length_regression,
)

__all__ = [
    "DEFAULT_HF_LOCAL_GRPO_MODEL",
    "DesignTextEvaluator",
    "load_default_evaluator",
    "default_hf_local_grpo_model",
    "grpo_config",
    "grpo_design_text_evaluator_config",
    "grpo_hf_local_training_config",
    "grpo_parallel_k_rewrite_config",
    "grpo_training_data_config",
    "apply_group_z_len_r_content",
    "apply_length_disentangle",
    "build_r_content_payload",
    "fit_holdout_length_centered",
    "fit_holdout_length_regression",
]
