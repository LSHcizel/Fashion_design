"""
HuggingFace 本地 SFT + GRPO（组相对优势 + 对参考策略的 KL 惩罚）。

安装依赖::

    pip install -r training/hf_grpo/requirements.txt

**推荐顺序（冷启动一次）**：双头 RM 见 ``training.odin_rm``。本包 **SFT 只跑一次**，随后 **多轮短 GRPO**（policy 链式更新，ref 冻在 ``hf-local-training.ref-model``）::

    python training/hf_grpo/run_recommended_training.py --help

后续新 K 路样本不要再 SFT / 不要再训双头，用 ``python -m training.run_next_grpo_round``。

分步入口（``--model`` 可省略，默认读 ``fashion_config.yaml`` → ``grpo.hf-local-training.model``）::

    python -m training.hf_grpo.train_sft --help
    python -m training.hf_grpo.train_grpo --help

档 3 先跑 ``python -m training.odin_rm.run_pipeline``，再用本包训改写器（phase_a/b 的 advantage 来自 r_Q）。
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
