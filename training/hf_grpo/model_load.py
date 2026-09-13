"""7B 在 24G 上的加载 / LoRA 约定。"""

from __future__ import annotations

from pathlib import Path
from typing import Any, List, Sequence, Union

DEFAULT_LORA_R = 16
DEFAULT_LORA_ALPHA = 32
DEFAULT_LORA_DROPOUT = 0.05
DEFAULT_LORA_TARGETS: tuple[str, ...] = (
    "q_proj",
    "k_proj",
    "v_proj",
    "o_proj",
    "gate_proj",
    "up_proj",
    "down_proj",
)


def is_peft_adapter_dir(path: Union[str, Path]) -> bool:
    p = Path(path)
    return p.is_dir() and (p / "adapter_config.json").is_file()


def should_use_lora(*, full_finetune: bool, lora_r: int) -> bool:
    return (not full_finetune) and int(lora_r) > 0


def lora_cli_args(*, lora_r: int, lora_alpha: int, full_finetune: bool) -> List[str]:
    if not should_use_lora(full_finetune=full_finetune, lora_r=lora_r):
        return ["--full-finetune"]
    return ["--lora-r", str(int(lora_r)), "--lora-alpha", str(int(lora_alpha))]


def same_model_path(a: Union[str, Path], b: Union[str, Path]) -> bool:
    pa, pb = Path(str(a)), Path(str(b))
    if pa.exists() and pb.exists():
        return pa.resolve() == pb.resolve()
    return pa.as_posix().rstrip("/") == pb.as_posix().rstrip("/")


def require_peft() -> Any:
    try:
        import peft  # noqa: F401
    except ImportError as exc:  # pragma: no cover
        raise SystemExit(
            "7B 全参 SFT/GRPO 在 24G 会 OOM，需要 LoRA。请安装: pip install peft"
        ) from exc
    return __import__("peft")


def apply_lora(
    model: Any,
    *,
    lora_r: int = DEFAULT_LORA_R,
    lora_alpha: int = DEFAULT_LORA_ALPHA,
    lora_dropout: float = DEFAULT_LORA_DROPOUT,
    target_modules: Sequence[str] = DEFAULT_LORA_TARGETS,
) -> Any:
    peft = require_peft()
    cfg = peft.LoraConfig(
        r=int(lora_r),
        lora_alpha=int(lora_alpha),
        lora_dropout=float(lora_dropout),
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=list(target_modules),
    )
    model = peft.get_peft_model(model, cfg)
    prepare_lora_for_checkpointing(model)
    return model


def prepare_lora_for_checkpointing(model: Any) -> None:
    if hasattr(model, "enable_input_require_grads"):
        model.enable_input_require_grads()
    if hasattr(model, "config") and hasattr(model.config, "use_cache"):
        model.config.use_cache = False


def load_peft_policy(base_model: Any, adapter_dir: Union[str, Path]) -> Any:
    peft = require_peft()
    model = peft.PeftModel.from_pretrained(
        base_model, str(adapter_dir), is_trainable=True
    )
    prepare_lora_for_checkpointing(model)
    return model


def adapter_base_model_path(adapter_dir: Union[str, Path]) -> str:
    peft = require_peft()
    cfg = peft.PeftConfig.from_pretrained(str(adapter_dir))
    return str(cfg.base_model_name_or_path)
