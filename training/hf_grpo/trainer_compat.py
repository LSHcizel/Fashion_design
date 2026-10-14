"""兼容不同 transformers 版本的 Trainer 构造参数。"""

from __future__ import annotations

import inspect
from typing import Any, Dict, Iterable, List


def trainer_processing_kwargs(tokenizer: Any, trainer_cls: Any = None) -> Dict[str, Any]:
    """
    新版 Hugging Face Trainer 用 ``processing_class``，旧版用 ``tokenizer``。
    按当前已安装版本的 ``__init__`` 签名选一个，避免 unexpected keyword。
    """
    if trainer_cls is None:
        from transformers import Trainer

        trainer_cls = Trainer
    # 子类常只声明 **kwargs，要沿 MRO 找到真正接收 tokenizer 的基类。
    for cls in getattr(trainer_cls, "__mro__", (trainer_cls,)):
        try:
            params = inspect.signature(cls.__init__).parameters
        except (TypeError, ValueError):
            continue
        if "processing_class" in params:
            return {"processing_class": tokenizer}
        if "tokenizer" in params:
            return {"tokenizer": tokenizer}
    return {}


def save_serialization_kwargs(training_args: Any, save_fn: Any = None) -> Dict[str, Any]:
    """
    transformers 4 用 ``TrainingArguments.save_safetensors`` 决定是否写 safetensors。
    transformers 5 删掉了该字段，``save_pretrained`` 也不再接受 ``safe_serialization``。
    """
    if not hasattr(training_args, "save_safetensors"):
        return {}
    kw = {"safe_serialization": bool(training_args.save_safetensors)}
    if save_fn is None:
        return kw
    try:
        params = inspect.signature(save_fn).parameters
    except (TypeError, ValueError):
        return kw
    if any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params.values()):
        return kw
    return {key: value for key, value in kw.items() if key in params}


def training_args_keep_extra_columns() -> Dict[str, Any]:
    """
    Trainer 默认按 model.forward 签名丢掉自定义列。
    GRPO 需要保留 ``completion_start`` / ``advantage``。
    """
    try:
        from transformers import TrainingArguments

        params = inspect.signature(TrainingArguments.__init__).parameters
    except Exception:
        return {"remove_unused_columns": False}
    if "remove_unused_columns" in params:
        return {"remove_unused_columns": False}
    return {}


GRPO_EXTRA_COLUMNS = ("completion_start", "advantage")


def merge_signature_columns(existing: Iterable[str] | None, extra: Iterable[str] = GRPO_EXTRA_COLUMNS) -> List[str]:
    cols = list(existing or [])
    for name in extra:
        if name not in cols:
            cols.append(name)
    return cols
