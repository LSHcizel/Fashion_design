"""阶段 B：``phase_b_grpo.jsonl`` + 预计算 advantage → 组相对策略梯度 + KL(π||π_ref)。

一次优化步只包含同一条原文的 K 个候选。策略项用 completion 的对数概率之和
（再按组内 token 总数平均），不再让长句先除以自己的长度。
"""

from __future__ import annotations

import argparse
import logging
import random
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset, Sampler
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    Trainer,
    TrainerCallback,
    TrainingArguments,
)

from plugins.text_description_evaluator.design_text_evaluator_api import (
    default_hf_local_grpo_model,
    default_hf_local_grpo_ref_model,
)
from training.step_metrics import WindowMeanMetrics

from .data import (
    completion_token_start,
    load_phase_b_rows,
    messages_from_phase_b_row,
    render_chat_text,
    select_grpo_rows,
)
from .model_load import (
    DEFAULT_LORA_ALPHA,
    DEFAULT_LORA_R,
    KL_REF_ADAPTER_NAME,
    active_adapter_name,
    adapter_base_model_path,
    apply_lora,
    attach_frozen_kl_ref,
    freeze_kl_ref_adapter,
    is_peft_adapter_dir,
    load_peft_policy,
    same_model_path,
    should_use_lora,
)
from .metrics_callback import JsonlMetricsCallback
from training.grpo_defaults import DEFAULT_BETA_KL

from .modeling import completion_token_counts, grpo_loss, sampled_token_logprobs, token_kl_k3_sum
from .trainer_compat import (
    merge_signature_columns,
    save_serialization_kwargs,
    trainer_processing_kwargs,
    training_args_keep_extra_columns,
)

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
        self.group_ids: List[str] = []
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
            self.group_ids.append(str(row.get("group_id") or f"row-{len(self.group_ids)}"))

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


class GroupBatchSampler(Sampler[List[int]]):
    """每个 batch 是同一 ``group_id`` 的全部候选，组与组之间打乱。"""

    def __init__(self, group_ids: List[str], seed: int = 0) -> None:
        buckets: Dict[str, List[int]] = {}
        order: List[str] = []
        for i, gid in enumerate(group_ids):
            if gid not in buckets:
                order.append(gid)
                buckets[gid] = []
            buckets[gid].append(i)
        self._order = order
        self._buckets = buckets
        self.seed = int(seed)
        self.epoch = 0

    def set_epoch(self, epoch: int) -> None:
        self.epoch = int(epoch)

    def __iter__(self) -> Iterator[List[int]]:
        rng = random.Random(self.seed + self.epoch)
        keys = list(self._order)
        rng.shuffle(keys)
        for key in keys:
            yield list(self._buckets[key])

    def __len__(self) -> int:
        return len(self._order)


class _GroupEpochCallback(TrainerCallback):
    def __init__(self, sampler: GroupBatchSampler) -> None:
        self.sampler = sampler

    def on_epoch_begin(self, args, state, control, **kwargs):  # type: ignore[no-untyped-def]
        epoch = int(state.epoch or 0)
        self.sampler.set_epoch(epoch)
        return control


def kl_ref_kind_from_flags(
    *,
    ref_is_adapter: bool,
    policy_is_adapter: bool,
    same_base: bool,
) -> str:
    """KL 怎么加载。

    ``frozen_adapter``：参考是一份 LoRA（SFT），挂在同一基座上并冻结。
    ``disable_base``：参考就是 LoRA 的基座，前向时关掉 adapter。
    ``separate_model``：参考是另一份完整权重，单独加载并冻结。
    """
    if ref_is_adapter:
        if not same_base:
            raise SystemExit("KL adapter 的基座与 policy 基座不同，不能挂在同一份 7B 上")
        return "frozen_adapter"
    if policy_is_adapter and same_base:
        return "disable_base"
    return "separate_model"


def forward_frozen_kl_ref(
    model: nn.Module,
    input_ids: torch.Tensor,
    attention_mask: torch.Tensor,
) -> torch.Tensor:
    """用冻结的 ``kl_ref`` adapter 做一次前向，然后切回原来的可训练 adapter。"""
    was_training = bool(model.training)
    previous = active_adapter_name(model)
    model.eval()
    try:
        model.set_adapter(KL_REF_ADAPTER_NAME)  # type: ignore[attr-defined]
        with torch.no_grad():
            logits = model(input_ids=input_ids, attention_mask=attention_mask).logits
    finally:
        model.set_adapter(previous)  # type: ignore[attr-defined]
        freeze_kl_ref_adapter(model)
        if was_training:
            model.train()
    return logits


def drop_kl_ref_keys(state_dict: Optional[Dict[str, torch.Tensor]]) -> Optional[Dict[str, torch.Tensor]]:
    """存 checkpoint 时去掉冻结参考 adapter，避免下一轮把它当成可训练权重读回来。"""
    if state_dict is None:
        return None
    marker = f".{KL_REF_ADAPTER_NAME}."
    return {key: value for key, value in state_dict.items() if marker not in key}


class GRPOCollator:
    def __init__(self, pad_token_id: int) -> None:
        self.pad_token_id = pad_token_id

    def __call__(self, features: List[Dict[str, Any]]) -> Dict[str, torch.Tensor]:
        return _pad_grpo_batch(features, self.pad_token_id)


class GRPOTrainer(Trainer):
    def __init__(
        self,
        ref_model: Optional[nn.Module] = None,
        beta_kl: float = DEFAULT_BETA_KL,
        kl_squared: bool = True,
        share_ref_via_disable_adapter: bool = False,
        frozen_kl_adapter: bool = False,
        trainable_adapter_name: str = "default",
        group_batch_sampler: Optional[GroupBatchSampler] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        if not share_ref_via_disable_adapter and not frozen_kl_adapter and ref_model is None:
            raise ValueError("ref_model required unless KL 用基座或冻结的 SFT adapter")
        self.ref_model = ref_model
        self.beta_kl = beta_kl
        self.kl_squared = kl_squared
        self.share_ref_via_disable_adapter = share_ref_via_disable_adapter
        self.frozen_kl_adapter = frozen_kl_adapter
        self.trainable_adapter_name = trainable_adapter_name
        self.group_batch_sampler = group_batch_sampler
        self._step_metrics = WindowMeanMetrics()

    def _set_signature_columns_if_needed(self):  # type: ignore[override]
        parent = getattr(super(), "_set_signature_columns_if_needed", None)
        if parent is not None:
            parent()
        self._signature_columns = merge_signature_columns(
            getattr(self, "_signature_columns", None)
        )

    def get_train_dataloader(self) -> DataLoader:
        if self.group_batch_sampler is None:
            return super().get_train_dataloader()
        dataset = self.train_dataset
        if dataset is None:
            raise ValueError("Trainer: training requires a train_dataset.")
        loader = DataLoader(
            dataset,
            batch_sampler=self.group_batch_sampler,
            collate_fn=self.data_collator,
            num_workers=0,
            pin_memory=bool(getattr(self.args, "dataloader_pin_memory", True)),
        )
        return self.accelerator.prepare(loader)

    def _pair_logprobs(
        self,
        model: nn.Module,
        inputs: Dict[str, torch.Tensor],
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        input_ids = inputs["input_ids"]
        attn = inputs["attention_mask"]
        comp_start = inputs["completion_start"]
        raw = self.accelerator.unwrap_model(model)
        if self.frozen_kl_adapter:
            raw.set_adapter(self.trainable_adapter_name)  # type: ignore[attr-defined]
        out = model(input_ids=input_ids, attention_mask=attn)
        logits = out.logits
        if self.frozen_kl_adapter:
            ref_logits = forward_frozen_kl_ref(raw, input_ids, attn)
        elif self.share_ref_via_disable_adapter:
            with torch.no_grad():
                with raw.disable_adapter():
                    ref_logits = raw(input_ids=input_ids, attention_mask=attn).logits
        else:
            assert self.ref_model is not None
            self.ref_model.eval()
            ref_dev = next(self.ref_model.parameters()).device
            with torch.no_grad():
                ref_out = self.ref_model(
                    input_ids=input_ids.to(ref_dev),
                    attention_mask=attn.to(ref_dev),
                )
                ref_logits = ref_out.logits.to(device=logits.device, dtype=logits.dtype)
        logp_p, mask = sampled_token_logprobs(logits, input_ids, comp_start, attn)
        logp_r, _mask_r = sampled_token_logprobs(ref_logits, input_ids, comp_start, attn)
        if mask.shape != logp_r.shape:
            width = min(mask.shape[1], logp_r.shape[1], logp_p.shape[1])
            mask = mask[:, :width]
            logp_p = logp_p[:, :width]
            logp_r = logp_r[:, :width]
        token_count = mask.sum(dim=-1).clamp(min=1).to(dtype=logp_p.dtype)
        sum_p = logp_p.sum(dim=-1)
        sum_k3 = token_kl_k3_sum(logp_p, logp_r, mask)
        return sum_p, token_count, sum_k3

    def _save(self, output_dir=None, state_dict=None):  # type: ignore[override]
        if not self.frozen_kl_adapter:
            return super()._save(output_dir, state_dict)
        output_dir = output_dir if output_dir is not None else self.args.output_dir
        raw = self.accelerator.unwrap_model(self.model)
        if hasattr(raw, "set_adapter"):
            raw.set_adapter(self.trainable_adapter_name)
        freeze_kl_ref_adapter(raw)
        save_kw: Dict[str, Any] = save_serialization_kwargs(self.args, raw.save_pretrained)
        if state_dict is not None:
            save_kw["state_dict"] = drop_kl_ref_keys(state_dict)
        raw.save_pretrained(
            output_dir,
            selected_adapters=[self.trainable_adapter_name],
            **save_kw,
        )
        if self.processing_class is not None:
            self.processing_class.save_pretrained(output_dir)
        torch.save(self.args, str(Path(output_dir) / "training_args.bin"))

    def training_step(self, model: nn.Module, inputs: Dict[str, torch.Tensor], *args: Any, **kwargs: Any):
        """一组候选分条前向，梯度累加后再更新。整组一次优化步，显存仍按单条。"""
        model.train()
        inputs = self._prepare_inputs(inputs)
        n = int(inputs["input_ids"].shape[0])
        counts = completion_token_counts(
            inputs["input_ids"], inputs["completion_start"], inputs["attention_mask"]
        )
        total_tokens = counts.sum().clamp(min=1).to(dtype=torch.float32)
        adv_all = inputs["advantage"]
        pol_acc = torch.zeros((), device=adv_all.device)
        kl_acc = torch.zeros((), device=adv_all.device)
        loss_acc = torch.zeros((), device=adv_all.device)
        for start in range(n):
            part = {key: value[start : start + 1] for key, value in inputs.items()}
            sum_p, _count, sum_k3 = self._pair_logprobs(model, part)
            adv = part["advantage"]
            pol = -(adv.detach() * sum_p).sum() / total_tokens.to(dtype=sum_p.dtype)
            kl = sum_k3.to(dtype=sum_p.dtype) / total_tokens.to(dtype=sum_p.dtype)
            loss = pol + float(self.beta_kl) * kl
            self.accelerator.backward(loss)
            pol_acc = pol_acc + pol.detach()
            kl_acc = kl_acc + kl.detach()
            loss_acc = loss_acc + loss.detach()
        self._step_metrics.add(
            policy_term=float(pol_acc),
            kl_term=float(kl_acc),
            grpo_loss=float(loss_acc),
            mean_advantage=float(adv_all.detach().float().mean()),
        )
        return loss_acc.detach()

    def compute_loss(
        self,
        model: nn.Module,
        inputs: Dict[str, torch.Tensor],
        return_outputs: bool = False,
        **_: Any,
    ):
        adv = inputs["advantage"].to(model.device)
        sum_p, token_count, sum_k3 = self._pair_logprobs(model, inputs)
        loss, pol, kl = grpo_loss(
            sum_p,
            sum_p,
            adv,
            beta_kl=self.beta_kl,
            sum_logp_policy=sum_p,
            token_count=token_count,
            token_kl_sum=sum_k3,
        )
        self._step_metrics.add(
            policy_term=float(pol.detach()),
            kl_term=float(kl.detach()),
            grpo_loss=float(loss.detach()),
            mean_advantage=float(adv.detach().mean()),
        )
        if return_outputs:
            return loss, {"policy_term": pol.detach(), "kl_term": kl.detach()}
        return loss

    def log(self, logs, *args, **kwargs):  # type: ignore[override]
        extra = self._step_metrics.flush()
        if extra and isinstance(logs, dict):
            logs.update(extra)
        return super().log(logs, *args, **kwargs)


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
            "冻结参考策略 π_ref。传 SFT 的 LoRA 目录时，KL 从 SFT 之后起算。"
            "留空时读 grpo.hf-local-training.ref-model（训练前基座，前向时关掉 adapter）。"
        ),
    )
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--system-prompt-file", type=Path, default=None)
    p.add_argument("--max-length", type=int, default=2048)
    p.add_argument("--epochs", type=float, default=1.0)
    p.add_argument("--lr", type=float, default=1e-6)
    p.add_argument("--batch", type=int, default=1)
    p.add_argument(
        "--grad-accum",
        type=int,
        default=1,
        help="按组更新时忽略。一次优化步就是同一原文的全部候选。",
    )
    p.add_argument(
        "--min-reward-std",
        type=float,
        default=0.05,
        help="组内 R_content 标准差低于此值则整组不训（避免把噪声标准化成 ±1）",
    )
    p.add_argument("--beta-kl", type=float, default=DEFAULT_BETA_KL)
    p.add_argument(
        "--dtype",
        choices=["bf16", "fp16", "fp32"],
        default="bf16",
    )
    p.add_argument("--lora-r", type=int, default=DEFAULT_LORA_R)
    p.add_argument("--lora-alpha", type=int, default=DEFAULT_LORA_ALPHA)
    p.add_argument(
        "--full-finetune",
        action="store_true",
        help="关闭 LoRA。全参 policy + 第二份 ref 在 24G 通常 OOM。",
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
    rows, group_summary = select_grpo_rows(rows, min_reward_std=args.min_reward_std)
    logger.info("GRPO 组过滤: %s", group_summary)
    if not rows:
        raise SystemExit("过滤后没有可训练的组：组内奖励差太小，或每组不足 2 条")

    tok_src = model_id
    adapter_tok = Path(model_id)
    if is_peft_adapter_dir(model_id) and not (
        (adapter_tok / "tokenizer.json").is_file()
        or (adapter_tok / "tokenizer_config.json").is_file()
    ):
        tok_src = adapter_base_model_path(model_id)
    tokenizer = AutoTokenizer.from_pretrained(tok_src, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    dtype_map = {"bf16": torch.bfloat16, "fp16": torch.float16, "fp32": torch.float32}
    torch_dtype = dtype_map[args.dtype]
    common_kw: Dict[str, Any] = {"trust_remote_code": True}
    if args.dtype != "fp32":
        common_kw["torch_dtype"] = torch_dtype

    ref_path = args.ref_model.strip() or default_hf_local_grpo_ref_model()
    policy_is_adapter = is_peft_adapter_dir(model_id)
    ref_is_adapter = is_peft_adapter_dir(ref_path)
    will_lora = (not policy_is_adapter) and should_use_lora(
        full_finetune=args.full_finetune, lora_r=args.lora_r
    )
    policy_base = adapter_base_model_path(model_id) if policy_is_adapter else model_id
    if ref_is_adapter:
        same_base = same_model_path(policy_base, adapter_base_model_path(ref_path))
    else:
        same_base = same_model_path(policy_base, ref_path)
    kind = kl_ref_kind_from_flags(
        ref_is_adapter=ref_is_adapter,
        policy_is_adapter=policy_is_adapter or will_lora,
        same_base=same_base,
    )
    share_ref = kind == "disable_base"
    frozen_kl = kind == "frozen_adapter"
    ref: Optional[nn.Module] = None
    trainable_adapter_name = "default"

    if policy_is_adapter:
        logger.info("从 LoRA 目录加载 policy=%s base=%s", model_id, policy_base)
        policy = AutoModelForCausalLM.from_pretrained(policy_base, **common_kw)
        if hasattr(policy.config, "use_cache"):
            policy.config.use_cache = False
        policy = load_peft_policy(policy, model_id)
    else:
        policy = AutoModelForCausalLM.from_pretrained(model_id, **common_kw)
        if hasattr(policy.config, "use_cache"):
            policy.config.use_cache = False
        if will_lora:
            logger.info("在全量 policy 上新挂 LoRA r=%s", args.lora_r)
            policy = apply_lora(policy, lora_r=args.lora_r, lora_alpha=args.lora_alpha)

    if frozen_kl:
        trainable_adapter_name = attach_frozen_kl_ref(policy, ref_path)
        logger.info(
            "KL 冻在 SFT adapter %s（同一份基座上的 %s，不更新，不再加载第二份 7B）",
            ref_path,
            KL_REF_ADAPTER_NAME,
        )
    elif share_ref:
        logger.info("KL 用 disable_adapter（基座 %s，不再加载第二份 7B ref）", ref_path)
    else:
        logger.info("独立 ref 放到 CPU: %s", ref_path)
        ref = AutoModelForCausalLM.from_pretrained(ref_path, **common_kw)
        ref.requires_grad_(False)
        ref.eval()
        if torch.cuda.is_available():
            ref.to("cpu")
            logger.info("独立 ref 放 CPU，避免与 policy 同时占满 24G")

    ds = PhaseBGRPODataset(rows, tokenizer, args.max_length, system_prompt=sys_prompt)
    if len(ds) == 0:
        raise SystemExit("no rows with valid advantage")
    group_sampler = GroupBatchSampler(ds.group_ids, seed=0)
    logger.info(
        "GRPO 按组更新：%s 组、%s 条。gradient_accumulation_steps=1（传入的 --grad-accum=%s 不跨组累积）",
        len(group_sampler),
        len(ds),
        args.grad_accum,
    )
    collator = GRPOCollator(tokenizer.pad_token_id or 0)

    use_bf16 = args.dtype == "bf16"
    use_fp16 = args.dtype == "fp16"
    ta = TrainingArguments(
        output_dir=str(args.out),
        num_train_epochs=args.epochs,
        learning_rate=args.lr,
        lr_scheduler_type="constant",
        per_device_train_batch_size=args.batch,
        gradient_accumulation_steps=1,
        logging_steps=10,
        save_steps=500,
        bf16=use_bf16,
        fp16=use_fp16,
        gradient_checkpointing=True,
        report_to=[],
        **training_args_keep_extra_columns(),
    )

    trainer = GRPOTrainer(
        ref_model=ref,
        beta_kl=args.beta_kl,
        share_ref_via_disable_adapter=share_ref,
        frozen_kl_adapter=frozen_kl,
        trainable_adapter_name=trainable_adapter_name,
        group_batch_sampler=group_sampler,
        model=policy,
        args=ta,
        train_dataset=ds,
        data_collator=collator,
        callbacks=[
            _GroupEpochCallback(group_sampler),
            JsonlMetricsCallback(
                args.out / "metrics.jsonl",
                stage="grpo",
                summary_keys=("loss", "grpo_loss", "policy_term", "kl_term", "mean_advantage"),
            )
        ],
        **trainer_processing_kwargs(tokenizer, trainer_cls=GRPOTrainer),
    )
    trainer.train()
    trainer.save_model(str(args.out))
    tokenizer.save_pretrained(str(args.out))
    logger.info("Saved policy to %s", args.out)


if __name__ == "__main__":
    main()
