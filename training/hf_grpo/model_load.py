"""7B 在 24G 上的加载 / LoRA 约定。"""

from __future__ import annotations

from pathlib import Path
from typing import Any, List, Sequence, Union

DEFAULT_LORA_R = 16
DEFAULT_LORA_ALPHA = 32
# 与正在训练的 adapter 分开。只用于 KL，不进优化器，也不写入 GRPO 的 checkpoint。
KL_REF_ADAPTER_NAME = "kl_ref"
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


def active_adapter_name(model: Any) -> str:
    """当前生效的 adapter。PEFT 在不同版本里把它放在字符串或列表上。"""
    name = getattr(model, "active_adapter", None)
    if isinstance(name, str) and name:
        return name
    adapters = getattr(model, "active_adapters", None)
    if isinstance(adapters, str) and adapters:
        return adapters
    if isinstance(adapters, (list, tuple)) and adapters:
        return str(adapters[0])
    if isinstance(name, (list, tuple)) and name:
        return str(name[0])
    return "default"


def freeze_kl_ref_adapter(model: Any) -> None:
    """``set_adapter`` 会把当前 adapter 重新设成可训练，参考 adapter 每次切回来都要再冻上。"""
    marker = f".{KL_REF_ADAPTER_NAME}."
    for name, param in model.named_parameters():
        if marker in name:
            param.requires_grad_(False)


def attach_frozen_kl_ref(model: Any, ref_adapter_dir: Union[str, Path]) -> str:
    """在可训练 LoRA 旁边再挂一份冻结的参考 adapter，并切回可训练的那份。

    参考权重来自 ``ref_adapter_dir``（冷启动里是 SFT 目录）。随后策略 adapter 继续更新，
    这份参考不动，所以 KL 从 SFT 之后起算，而不是从训练前的基座起算。
    """
    trainable = active_adapter_name(model)
    if trainable == KL_REF_ADAPTER_NAME:
        raise ValueError("可训练 adapter 不能占用 kl_ref 这个名字")
    try:
        model.load_adapter(
            str(ref_adapter_dir),
            adapter_name=KL_REF_ADAPTER_NAME,
            is_trainable=False,
        )
    except TypeError:
        model.load_adapter(str(ref_adapter_dir), adapter_name=KL_REF_ADAPTER_NAME)
    freeze_kl_ref_adapter(model)
    model.set_adapter(trainable)
    freeze_kl_ref_adapter(model)
    return trainable


def adapter_base_model_path(adapter_dir: Union[str, Path]) -> str:
    peft = require_peft()
    cfg = peft.PeftConfig.from_pretrained(str(adapter_dir))
    return str(cfg.base_model_name_or_path)
