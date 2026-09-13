"""兼容不同 transformers 版本的 Trainer 构造参数。"""

from __future__ import annotations

import inspect
from typing import Any, Dict


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
