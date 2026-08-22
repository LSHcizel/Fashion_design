"""阶段 B：``phase_b_grpo.jsonl`` + 预计算 advantage → 组相对策略梯度 + KL(π||π_ref)。"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import torch
import torch.nn as nn
from torch.utils.data import Dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
)

from plugins.text_description_evaluator.design_text_evaluator_api import (
    default_hf_local_grpo_model,
    default_hf_local_grpo_ref_model,
)

from .data import completion_token_start, load_phase_b_rows, messages_from_phase_b_row, render_chat_text
from .modeling import grpo_loss, sequence_completion_log_probs

logger = logging.getLogger(__name__)


class PhaseBGRPODataset(Dataset):
    def __init__(
        self,
        rows: List[Dict[str, Any]],
        tokenizer,
        max_length: int,
        system_prompt: str = "",
    ) -> None:
        self.items: List[Dict[str, Any]] = []
        self.tokenizer = tokenizer
        self.max_length = max_length
        for row in rows:
            adv = row.get("advantage")
            if adv is None:
                continue
            messages = messages_from_phase_b_row(row, system_prompt=system_prompt)
            text = render_chat_text(messages, tokenizer)
            cstart = completion_token_start(tokenizer, messages)
            enc = tokenizer(
                text,
                max_length=self.max_length,
                truncation=True,
                return_tensors=None,
            )
            self.items.append(
                {
                    "input_ids": enc["input_ids"],
                    "attention_mask": enc["attention_mask"],
                    "completion_start": min(cstart, len(enc["input_ids"]) - 1)
                    if len(enc["input_ids"]) > 1
                    else 1,
                    "advantage": float(adv),
                }
            )

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, idx: int) -> Dict[str, Any]:
        return dict(self.items[idx])


def _pad_grpo_batch(
    features: List[Dict[str, Any]],
    pad_id: int,
) -> Dict[str, torch.Tensor]:
    max_len = max(len(f["input_ids"]) for f in features)
    b = len(features)
    input_ids = torch.full((b, max_len), pad_id, dtype=torch.long)
    attn = torch.zeros((b, max_len), dtype=torch.long)
    comp_start = torch.zeros((b,), dtype=torch.long)
    advantage = torch.zeros((b,), dtype=torch.float32)
    for i, f in enumerate(features):
        L = len(f["input_ids"])
        input_ids[i, :L] = torch.tensor(f["input_ids"])
        attn[i, :L] = torch.tensor(f["attention_mask"])
        comp_start[i] = int(f["completion_start"])
        advantage[i] = float(f["advantage"])
    return {
        "input_ids": input_ids,
        "attention_mask": attn,
        "completion_start": comp_start,
        "advantage": advantage,
    }


class GRPOCollator:
    def __init__(self, pad_token_id: int) -> None:
        self.pad_token_id = pad_token_id

    def __call__(self, features: List[Dict[str, Any]]) -> Dict[str, torch.Tensor]:
        return _pad_grpo_batch(features, self.pad_token_id)


class GRPOTrainer(Trainer):
    def __init__(
        self,
        ref_model: nn.Module,
        beta_kl: float = 0.04,
        kl_squared: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.ref_model = ref_model
        self.beta_kl = beta_kl
        self.kl_squared = kl_squared

    def compute_loss(
        self,
        model: nn.Module,
        inputs: Dict[str, torch.Tensor],
        return_outputs: bool = False,
        **_: Any,
    ):
        input_ids = inputs["input_ids"]
        attn = inputs["attention_mask"]
        comp_start = inputs["completion_start"]
        adv = inputs["advantage"].to(model.device)

        dev = input_ids.device
        if next(self.ref_model.parameters()).device != dev:
            self.ref_model.to(dev)

        out = model(input_ids=input_ids, attention_mask=attn)
        logits = out.logits
        self.ref_model.eval()
        with torch.no_grad():
            ref_out = self.ref_model(input_ids=input_ids, attention_mask=attn)
            ref_logits = ref_out.logits

        logp_p = sequence_completion_log_probs(logits, input_ids, comp_start, attn)
        logp_r = sequence_completion_log_probs(ref_logits, input_ids, comp_start, attn)

        loss, pol, kl = grpo_loss(
            logp_p,
            logp_r,
            adv,
            beta_kl=self.beta_kl,
            kl_squared=self.kl_squared,
        )
        if return_outputs:
            return loss, {"policy_term": pol.detach(), "kl_term": kl.detach()}
        return loss


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    p = argparse.ArgumentParser(description="GRPO on phase_b_grpo.jsonl")
    p.add_argument("--jsonl", type=Path, required=True, help="phase_b_grpo.jsonl")
    p.add_argument(
        "--model",
        type=str,
        default=None,
        help="当前策略 π（训练对象）；推荐为阶段 A SFT 保存目录。默认 grpo.hf-local-training.model",
    )
    p.add_argument(
        "--ref-model",
        type=str,
        default="",
        help=(
            "冻结参考策略 π_ref（KL 锚点）。留空时读 grpo.hf-local-training.ref-model（改写器训练前快照）。"
        ),
    )
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--system-prompt-file", type=Path, default=None)
    p.add_argument("--max-length", type=int, default=2048)
    p.add_argument("--epochs", type=float, default=1.0)
    p.add_argument("--lr", type=float, default=1e-6)
    p.add_argument("--batch", type=int, default=1)
    p.add_argument("--grad-accum", type=int, default=8)
    p.add_argument("--beta-kl", type=float, default=0.04)
    p.add_argument(
        "--dtype",
        choices=["bf16", "fp16", "fp32"],
        default="bf16",
    )
    args = p.parse_args()

    model_id = args.model or default_hf_local_grpo_model()
    logger.info("Using HF policy model: %s", model_id)

    sys_prompt = ""
    if args.system_prompt_file and args.system_prompt_file.is_file():
        sys_prompt = args.system_prompt_file.read_text(encoding="utf-8")

    rows = load_phase_b_rows(args.jsonl)
    if not rows:
        raise SystemExit("empty jsonl")

    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    dtype_map = {"bf16": torch.bfloat16, "fp16": torch.float16, "fp32": torch.float32}
    torch_dtype = dtype_map[args.dtype]
    common_kw: Dict[str, Any] = {"trust_remote_code": True}
    if args.dtype != "fp32":
        common_kw["torch_dtype"] = torch_dtype

    policy = AutoModelForCausalLM.from_pretrained(model_id, **common_kw)
    if hasattr(policy.config, "use_cache"):
        policy.config.use_cache = False

    ref_path = args.ref_model.strip() or default_hf_local_grpo_ref_model()
    ref = AutoModelForCausalLM.from_pretrained(ref_path, **common_kw)
    ref.requires_grad_(False)
    ref.eval()

    ds = PhaseBGRPODataset(rows, tokenizer, args.max_length, system_prompt=sys_prompt)
    if len(ds) == 0:
        raise SystemExit("no rows with valid advantage")
    collator = GRPOCollator(tokenizer.pad_token_id or 0)

    use_bf16 = args.dtype == "bf16"
    use_fp16 = args.dtype == "fp16"
    ta = TrainingArguments(
        output_dir=str(args.out),
        num_train_epochs=args.epochs,
        learning_rate=args.lr,
        per_device_train_batch_size=args.batch,
        gradient_accumulation_steps=args.grad_accum,
        logging_steps=10,
        save_steps=500,
        bf16=use_bf16,
        fp16=use_fp16,
        gradient_checkpointing=True,
        report_to=[],
    )

    trainer = GRPOTrainer(
        ref_model=ref,
        beta_kl=args.beta_kl,
        model=policy,
        args=ta,
        train_dataset=ds,
        data_collator=collator,
        tokenizer=tokenizer,
    )
    trainer.train()
    trainer.save_model(str(args.out))
    tokenizer.save_pretrained(str(args.out))
    logger.info("Saved policy to %s", args.out)


if __name__ == "__main__":
    main()
