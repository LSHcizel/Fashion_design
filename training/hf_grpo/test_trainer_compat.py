"""Trainer 构造参数在新旧 transformers 之间的兼容选择。"""

from __future__ import annotations

import unittest

from training.hf_grpo.trainer_compat import (
    merge_signature_columns,
    trainer_processing_kwargs,
    training_args_keep_extra_columns,
)


class _OldTrainer:
    def __init__(self, model=None, tokenizer=None):
        pass


class _NewTrainer:
    def __init__(self, model=None, processing_class=None):
        pass


class _BothTrainer:
    def __init__(self, model=None, processing_class=None, tokenizer=None):
        pass


class _Subclass(_NewTrainer):
    def __init__(self, extra=None, **kwargs):
        super().__init__(**kwargs)


class TrainerCompatTest(unittest.TestCase):
    def test_old_transformers_uses_tokenizer(self):
        self.assertEqual(
            trainer_processing_kwargs("tok", trainer_cls=_OldTrainer),
            {"tokenizer": "tok"},
        )

    def test_new_transformers_uses_processing_class(self):
        self.assertEqual(
            trainer_processing_kwargs("tok", trainer_cls=_NewTrainer),
            {"processing_class": "tok"},
        )

    def test_prefers_processing_class_when_both_exist(self):
        self.assertEqual(
            trainer_processing_kwargs("tok", trainer_cls=_BothTrainer),
            {"processing_class": "tok"},
        )

    def test_subclass_with_kwargs_walks_mro(self):
        self.assertEqual(
            trainer_processing_kwargs("tok", trainer_cls=_Subclass),
            {"processing_class": "tok"},
        )

    def test_keep_grpo_columns(self):
        kw = training_args_keep_extra_columns()
        if kw:
            self.assertEqual(kw.get("remove_unused_columns"), False)
        self.assertEqual(
            merge_signature_columns(["input_ids"]),
            ["input_ids", "completion_start", "advantage"],
        )


if __name__ == "__main__":
    unittest.main()
