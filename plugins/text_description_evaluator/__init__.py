"""Standalone text-description evaluator plugin for fashion prompts."""

from .design_text_evaluator_api import DesignTextEvaluator, load_default_evaluator

__all__ = ["DesignTextEvaluator", "load_default_evaluator"]
