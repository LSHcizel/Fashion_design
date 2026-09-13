"""阶段 A：对 ``phase_a_sft.jsonl`` 做因果 LM 监督微调（仅 assistant 段计损失）。

单独运行或与 ``run_recommended_training.py`` 编排一起使用；完成后将 checkpoint 目录作为
``train_grpo.py`` 的 ``--model``（并由编排脚本将 ``--ref-model`` 指向基座）。
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Any, Dict, List

import torch
from torch.utils.data import Dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    Trainer,
    TrainerCallback,
    TrainingArguments,
)

from plugins.text_description_evaluator.design_text_evaluator_api import default_hf_local_grpo_model

from .data import completion_token_start, load_phase_a_rows, render_chat_text
from .trainer_compat import trainer_processing_kwargs

logger = logging.getLogger(__name__)


class PhaseASftDataset(Dataset):
    def __init__(
        self,
        rows: List[Dict[str, Any]],
        tokenizer,
        max_length: int,
    ) -> None:
        self.rows = rows
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, idx: int) -> Dict[str, Any]:
        messages = self.rows[idx]["messages"]
        text = render_chat_text(messages, self.tokenizer)
        comp_start = completion_token_start(self.tokenizer, messages)
        enc = self.tokenizer(
            text,
            max_length=self.max_length,
            truncation=True,
            return_tensors=None,
        )
        input_ids = enc["input_ids"]
        attn = enc["attention_mask"]
        labels = [-100] * len(input_ids)
        cs = min(comp_start, len(input_ids) - 1)
        for i in range(cs, len(input_ids)):
            if attn[i] == 0:
                continue
            labels[i] = input_ids[i]
        return {
            "input_ids": input_ids,
            "attention_mask": attn,
            "labels": labels,
        }


@torch.no_grad()
def _pad_batch(
    features: List[Dict[str, Any]],
    pad_id: int,
) -> Dict[str, torch.Tensor]:
    max_len = max(len(f["input_ids"]) for f in features)
    b = len(features)
    input_ids = torch.full((b, max_len), pad_id, dtype=torch.long)
    attn = torch.zeros((b, max_len), dtype=torch.long)
    labels = torch.full((b, max_len), -100, dtype=torch.long)
    for i, f in enumerate(features):
        L = len(f["input_ids"])
        input_ids[i, :L] = torch.tensor(f["input_ids"])
        attn[i, :L] = torch.tensor(f["attention_mask"])
        labels[i, :L] = torch.tensor(f["labels"])
    return {"input_ids": input_ids, "attention_mask": attn, "labels": labels}


class SFTDataCollator:
    def __init__(self, pad_token_id: int) -> None:
        self.pad_token_id = pad_token_id

    def __call__(self, features: List[Dict[str, Any]]) -> Dict[str, torch.Tensor]:
        return _pad_batch(features, self.pad_token_id)


class TrainLossPlateauEarlyStopping(TrainerCallback):
    """
    用 Trainer 上报的 **训练 loss**（通常为小批量滑动均值）做指数平滑后，与历史最优比较；
    若连续 ``patience`` 次 logging 均未带来「有意义的」下降，则 ``should_training_stop``，
    作为进入 GRPO 前的 **SFT 平台期早停** 启发式门限。

    有意义的下降定义为::

        best_ema - ema > max(min_abs_delta, min_rel_delta * max(|best_ema|, 1e-8))

    默认 ``min_rel_delta=0.005``（0.5%）、``min_abs_delta=1e-4``、``patience=6``、
    ``min_global_steps=100``（与 ``logging_steps=10`` 配合时，约 ≥100 优化步后才允许早停）。
    """

    def __init__(
        self,
        *,
        patience: int = 6,
        min_rel_delta: float = 0.005,
        min_abs_delta: float = 1e-4,
        min_global_steps: int = 100,
        ema_decay: float = 0.92,
    ) -> None:
        self.patience = max(1, int(patience))
        self.min_rel_delta = float(min_rel_delta)
        self.min_abs_delta = float(min_abs_delta)
        self.min_global_steps = int(min_global_steps)
        self.ema_decay = float(ema_decay)
        self._ema: float | None = None
        self._best: float | None = None
        self._strikes = 0

    def on_log(self, args, state, control, logs=None, **kwargs):  # type: ignore[no-untyped-def]
        if logs is None or "loss" not in logs:
            return control
        loss = float(logs["loss"])
        if self._ema is None:
            self._ema = loss
        else:
            d = self.ema_decay
            self._ema = d * self._ema + (1.0 - d) * loss
        ema = self._ema
        if state.global_step < self.min_global_steps:
            return control
        if self._best is None:
            self._best = ema
            self._strikes = 0
            return control
        thr = max(
            self.min_abs_delta,
            self.min_rel_delta * max(abs(self._best), 1e-8),
        )
        if (self._best - ema) > thr:
            self._best = ema
            self._strikes = 0
        else:
            self._strikes += 1
            if self._strikes >= self.patience:
                logger.info(
                    "SFT 早停（训练 loss 平台）：best_ema=%.6f 当前 ema=%.6f，连续 %d 次 log 未优于 max(%g, %.2f%%×best)。"
                    " 建议在核实 checkpoint 后进入 GRPO。",
                    self._best,
                    ema,
                    self.patience,
                    self.min_abs_delta,
                    100.0 * self.min_rel_delta,
                )
                control.should_training_stop = True
        return control


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    p = argparse.ArgumentParser(description="SFT on phase_a_sft.jsonl")
    p.add_argument("--jsonl", type=Path, required=True, help="phase_a_sft.jsonl")
    p.add_argument(
        "--model",
        type=str,
        default=None,
        help="HF model id 或本地路径；默认读 fashion_config.yaml → grpo.hf-local-training.model",
    )
    p.add_argument("--out", type=Path, required=True, help="output directory")
    p.add_argument("--max-length", type=int, default=2048)
    p.add_argument("--epochs", type=float, default=1.0)
    p.add_argument("--lr", type=float, default=2e-5)
    p.add_argument("--batch", type=int, default=1)
    p.add_argument("--grad-accum", type=int, default=8)
    p.add_argument(
        "--dtype",
        choices=["bf16", "fp16", "fp32"],
        default="bf16",
    )
    p.add_argument(
        "--logging-steps",
        type=int,
        default=10,
        help="与早停联动：每 N 个 optimizer step 记录 loss；patience 按 log 次数计。",
    )
    p.add_argument(
        "--no-early-stop",
        action="store_true",
        help="关闭基于训练 loss 的平台早停（全程跑满 num_train_epochs）。",
    )
    p.add_argument(
        "--early-stop-patience",
        type=int,
        default=6,
        help="连续多少次 logging 未带来足够 loss 下降则早停（默认 6）。",
    )
    p.add_argument(
        "--early-stop-rel-delta",
        type=float,
        default=0.005,
        help="相对门限：相对当前最优 EMA 至少再降该比例才算有改进（默认 0.005=0.5%%）。",
    )
    p.add_argument(
        "--early-stop-abs-delta",
        type=float,
        default=1e-4,
        help="绝对门限：与 rel 取 max；小 loss 时避免数值噪音误触发。",
    )
    p.add_argument(
        "--early-stop-min-steps",
        type=int,
        default=100,
        help="至少经过多少 global_step 后才允许早停，避免首轮噪声。",
    )
    p.add_argument(
        "--early-stop-ema-decay",
        type=float,
        default=0.92,
        help="对 log 中 loss 的 EMA 衰减系数（越大曲线越平滑）。",
    )
    args = p.parse_args()

    model_id = args.model or default_hf_local_grpo_model()
    logger.info("Using HF model: %s", model_id)

    rows = load_phase_a_rows(args.jsonl)
    if not rows:
        raise SystemExit("empty jsonl")

    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    torch_dtype = {"bf16": torch.bfloat16, "fp16": torch.float16, "fp32": torch.float32}[args.dtype]
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        trust_remote_code=True,
        torch_dtype=torch_dtype if args.dtype != "fp32" else None,
    )
    if hasattr(model.config, "use_cache"):
        model.config.use_cache = False

    ds = PhaseASftDataset(rows, tokenizer, args.max_length)
    collator = SFTDataCollator(tokenizer.pad_token_id or 0)

    use_bf16 = args.dtype == "bf16"
    use_fp16 = args.dtype == "fp16"
    ta = TrainingArguments(
        output_dir=str(args.out),
        num_train_epochs=args.epochs,
        learning_rate=args.lr,
        per_device_train_batch_size=args.batch,
        gradient_accumulation_steps=args.grad_accum,
        logging_steps=max(1, int(args.logging_steps)),
        save_steps=500,
        bf16=use_bf16,
        fp16=use_fp16,
        gradient_checkpointing=True,
        report_to=[],
    )

    callbacks = []
    if not args.no_early_stop:
        callbacks.append(
            TrainLossPlateauEarlyStopping(
                patience=args.early_stop_patience,
                min_rel_delta=args.early_stop_rel_delta,
                min_abs_delta=args.early_stop_abs_delta,
                min_global_steps=args.early_stop_min_steps,
                ema_decay=args.early_stop_ema_decay,
            )
        )

    trainer = Trainer(
        model=model,
        args=ta,
        train_dataset=ds,
        data_collator=collator,
        callbacks=callbacks,
        **trainer_processing_kwargs(tokenizer),
    )
    trainer.train()
    trainer.save_model(str(args.out))
    tokenizer.save_pretrained(str(args.out))
    logger.info("Saved to %s", args.out)


if __name__ == "__main__":
    main()
