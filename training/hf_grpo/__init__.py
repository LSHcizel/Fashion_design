"""
HuggingFace 本地 SFT + GRPO（组相对优势 + 对参考策略的 KL 惩罚）。

安装依赖::

    pip install -r training/hf_grpo/requirements.txt

**推荐顺序（改写器：基座快照 → SFT → GRPO）**：使用编排脚本，一次跑完两段训练（policy=SFT 目录，ref=hf-local-training.ref-model）::

    python training/hf_grpo/run_recommended_training.py --help

分步入口（``--model`` 可省略，默认读 ``fashion_config.yaml`` → ``grpo.hf-local-training.model``）::

    python -m training.hf_grpo.train_sft --help
    python -m training.hf_grpo.train_grpo --help
"""

from .data import (
    build_prompt_only_messages,
    completion_token_start,
    load_phase_a_rows,
    load_phase_b_rows,
    messages_from_phase_b_row,
    phase_b_user_content,
    render_chat_text,
)

__all__ = [
    "build_prompt_only_messages",
    "completion_token_start",
    "load_phase_a_rows",
    "load_phase_b_rows",
    "messages_from_phase_b_row",
    "phase_b_user_content",
    "render_chat_text",
]
