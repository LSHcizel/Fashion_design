"""品牌调性改写：评分之前，只处理已经生成的 description。"""

from .rewriter import MODEL_NAME, rewrite_generated_description

__all__ = ["MODEL_NAME", "rewrite_generated_description"]
