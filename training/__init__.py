"""
训练过程数据目录（《改进方案》第 4 步）。

- **runs/**：路径由 ``fashion_config.yaml`` 的 ``grpo.training-data.runs-dir`` 控制，默认 ``training/runs``。
- **hf_grpo/**：可选依赖（PyTorch / transformers）下对 ``phase_a_sft.jsonl``、``phase_b_grpo.jsonl`` 做 **SFT** 与 **GRPO**（仅更新 ``grpo.rewriter-llm`` 改写器权重；基座 judge 冻结）；见 ``pip install -r training/hf_grpo/requirements.txt``。
- 使用 ``TrainingRunLogger`` 追加记录；使用 ``record_builder.summarize_jsonl_file`` 做离线汇总。

**第 5 步（阶段 A / B）**：``grpo_pipeline.export_two_phase_from_samples`` 从 ``samples.jsonl`` 生成
``phase_a_sft.jsonl``（仅文本 K 路组内最优）与 ``phase_b_grpo.jsonl``（组内优势 + 可选排名修正）；数学见 ``grpo_compute``。

**阶段 A（图像逆解析）**：``phase_a_image_inverse`` 多模态逆解析 → 评测 → 写出与上式相同的 SFT 顶层字段，可与 ``phase_a_sft.jsonl`` 合并训练。

**ODIN 档 3（双头 RM）**：``training/odin_rm`` 冷启动一次：造偏好对、训 r_Q/r_L，再用 r_Q 覆盖 ``R_content`` 后导出 phase_a/b。第 2+3 步一条命令：``python -m training.run_coldstart_train``（SFT 一次 + 多轮短 GRPO）；续跑见 ``training.run_next_grpo_round``。

指标与字段说明见 ``record_builder.build_training_record``。
"""

from .grpo_compute import (
    apply_rank_reward_multiplier,
    build_group_training_rows,
    group_baseline_advantages,
    pick_reward_scalar,
    skip_rank_correction_for_group,
)
from .grpo_pipeline import (
    TwoPhaseTrainingPipeline,
    build_sft_record_for_group,
    default_grpo_export_dir,
    export_two_phase_from_samples,
    load_samples_by_group,
)
from .jsonl_logger import TrainingRunLogger, default_runs_root
from .phase_a_image_inverse import (
    IMAGE_INVERSE_MODEL_ENV,
    IMAGE_INVERSE_SOURCE_SCHEMA,
    ImageInverseOutcome,
    append_phase_a_sft_jsonl,
    append_two_phase_a_lines_for_group,
    build_multimodal_user_content,
    build_pair_phase_a_records,
    build_phase_a_sft_record_image_inverse,
    image_path_to_url_part,
    make_vision_judge,
    run_image_inverse_multimodal,
)
from .record_builder import (
    SCHEMA_VERSION,
    build_training_record,
    iter_records_from_parallel_result,
    sha256_text,
    summarize_jsonl_file,
)

__all__ = [
    "SCHEMA_VERSION",
    "TrainingRunLogger",
    "default_runs_root",
    "build_training_record",
    "iter_records_from_parallel_result",
    "sha256_text",
    "summarize_jsonl_file",
    "pick_reward_scalar",
    "group_baseline_advantages",
    "apply_rank_reward_multiplier",
    "skip_rank_correction_for_group",
    "build_group_training_rows",
    "load_samples_by_group",
    "build_sft_record_for_group",
    "default_grpo_export_dir",
    "export_two_phase_from_samples",
    "TwoPhaseTrainingPipeline",
    "IMAGE_INVERSE_MODEL_ENV",
    "IMAGE_INVERSE_SOURCE_SCHEMA",
    "ImageInverseOutcome",
    "append_phase_a_sft_jsonl",
    "append_two_phase_a_lines_for_group",
    "build_multimodal_user_content",
    "build_pair_phase_a_records",
    "build_phase_a_sft_record_image_inverse",
    "image_path_to_url_part",
    "make_vision_judge",
    "run_image_inverse_multimodal",
]
