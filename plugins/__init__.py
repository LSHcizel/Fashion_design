"""Plugin package for optional project extensions."""

__all__ = ["CollectionEvaluationAgent", "LookEvaluationAgent"]


def __getattr__(name):
    if name in __all__:
        from .evaluators import CollectionEvaluationAgent, LookEvaluationAgent

        exports = {
            "CollectionEvaluationAgent": CollectionEvaluationAgent,
            "LookEvaluationAgent": LookEvaluationAgent,
        }
        return exports[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
