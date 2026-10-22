"""训 ODIN 双头 RM。默认解开基座最后两层，其余冻住；按留出集 acc_q 保存最好的权重。"""

from __future__ import annotations

import argparse
import json
import logging
import math
import random
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from plugins.text_description_evaluator.design_text_evaluator_api import (
    default_odin_rm_model,
    grpo_odin_rm_config,
)
from training.step_metrics import append_metrics, progress_summary

from .data import messages_from_record, response_token_count
from .modeling import (
    LAMBDA_GAP,
    LAMBDA_L,
    LAMBDA_O,
    MIN_SCORE_GAP,
    DualHeadRewardModel,
    batch_pearson,
    last_token_from_inner,
    load_tuned_layers,
    odin_rm_loss,
    set_suffix_train,
    tuned_layer_state,
    unfreeze_last_layers,
)
from .pairs import build_preference_pairs, pair_in_rm_training

logger = logging.getLogger(__name__)

HEADS_NAME = "odin_heads.pt"
RM_CONFIG_NAME = "odin_rm_config.json"
DEFAULT_UNFREEZE_LAYERS = 2
DEFAULT_LAYER_LR = 1e-5
DEFAULT_PATIENCE_EVALS = 15
DEFAULT_MIN_EPOCHS = 1.0


def _dtype(name: str):
    return {"bf16": torch.bfloat16, "fp16": torch.float16, "fp32": torch.float32}[name]


def _tokenize_side(tokenizer, rec_side: Dict[str, Any], max_length: int, system_prompt: str):
    wrap = {
        "context": rec_side.get("context") or {},
        "completion": rec_side.get("completion") or "",
    }
    messages = messages_from_record(wrap, system_prompt=system_prompt)
    from ..hf_grpo.data import render_chat_text

    text = render_chat_text(messages, tokenizer)
    enc = tokenizer(
        text,
        max_length=max_length,
        truncation=True,
        padding=False,
        return_tensors=None,
    )
    return enc["input_ids"], enc["attention_mask"]


def _pad_ids(batch_ids: List[List[int]], pad_id: int) -> Tuple[torch.Tensor, torch.Tensor]:
    max_len = max(len(x) for x in batch_ids)
    b = len(batch_ids)
    ids = torch.full((b, max_len), pad_id, dtype=torch.long)
    mask = torch.zeros((b, max_len), dtype=torch.long)
    for i, row in enumerate(batch_ids):
        ids[i, : len(row)] = torch.tensor(row, dtype=torch.long)
        mask[i, : len(row)] = 1
    return ids, mask


def _side_key(side: Dict[str, Any]) -> str:
    return f"{side.get('group_id')}#{side.get('candidate_index')}"


def _collect_unique_sides(pairs: Sequence[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    uniq: Dict[str, Dict[str, Any]] = {}
    for p in pairs:
        for name in ("chosen", "rejected"):
            side = p[name]
            uniq[_side_key(side)] = side
    return uniq


@torch.no_grad()
def encode_hidden_cache(
    rm: DualHeadRewardModel,
    tokenizer,
    sides: Dict[str, Dict[str, Any]],
    *,
    max_length: int,
    device: torch.device,
    system_prompt: str,
    encode_batch: int = 1,
) -> Dict[str, torch.Tensor]:
    """key → CPU float32 hidden（last token）。"""
    rm.backbone.eval()
    keys = list(sides.keys())
    cache: Dict[str, torch.Tensor] = {}
    pad_id = tokenizer.pad_token_id or 0
    for start in range(0, len(keys), max(1, encode_batch)):
        chunk = keys[start : start + max(1, encode_batch)]
        id_rows: List[List[int]] = []
        for k in chunk:
            ids, _ = _tokenize_side(tokenizer, sides[k], max_length, system_prompt)
            id_rows.append(ids)
        input_ids, attn = _pad_ids(id_rows, pad_id)
        input_ids = input_ids.to(device)
        attn = attn.to(device)
        hidden = rm.pool_hidden(input_ids, attn).float().cpu()
        for i, k in enumerate(chunk):
            cache[k] = hidden[i].contiguous()
        if (start // max(1, encode_batch)) % 20 == 0:
            logger.info("encoded %s / %s completions", min(start + len(chunk), len(keys)), len(keys))
    return cache


def _stack_cached(
    cache: Dict[str, torch.Tensor],
    pairs: Sequence[Dict[str, Any]],
    which: str,
    device: torch.device,
) -> torch.Tensor:
    rows = [cache[_side_key(p[which])] for p in pairs]
    return torch.stack(rows, dim=0).to(device)


def _attach_token_counts(pairs: Sequence[Dict[str, Any]], tokenizer) -> None:
    """把回复 token 数写到两侧。同一段文本只分词一次。"""
    cache: Dict[str, int] = {}
    for pair in pairs:
        for name in ("chosen", "rejected"):
            side = pair[name]
            text = str(side.get("completion") or "")
            if text not in cache:
                cache[text] = response_token_count(tokenizer, text)
            side["n_tokens"] = cache[text]


def _token_counts(pairs: Sequence[Dict[str, Any]], which: str, device: torch.device) -> torch.Tensor:
    vals = [float(p[which].get("n_tokens") or 0.0) for p in pairs]
    return torch.tensor(vals, dtype=torch.float32, device=device)


def _teacher_scores(pairs: Sequence[Dict[str, Any]], which: str, device: torch.device) -> torch.Tensor:
    vals = [float(p[which]["teacher_score"]) for p in pairs]
    return torch.tensor(vals, dtype=torch.float32, device=device)


def _mean_stats(rows: List[Dict[str, float]]) -> Dict[str, float]:
    if not rows:
        return {}
    keys = rows[0].keys()
    return {k: sum(r[k] for r in rows) / len(rows) for k in keys}


def _remember_side_score(
    bucket: Dict[str, Tuple[float, float, float]],
    side: Dict[str, Any],
    r_q: torch.Tensor,
    r_l: torch.Tensor,
) -> None:
    bucket[_side_key(side)] = (
        float(r_q.detach()),
        float(r_l.detach()),
        float(side.get("n_tokens") or 0.0),
    )


def write_full_set_rho(stats: Dict[str, float], sides: Dict[str, Tuple[float, float, float]]) -> None:
    """用整份去重后的稿算一次 Pearson，盖掉按 batch 平均的 ρ。"""
    if len(sides) < 2:
        return
    rows = list(sides.values())
    r_q = torch.tensor([row[0] for row in rows])
    r_l = torch.tensor([row[1] for row in rows])
    length = torch.tensor([row[2] for row in rows])
    stats["rho_q"] = float(batch_pearson(r_q, length))
    stats["rho_l"] = float(batch_pearson(r_l, length))


@torch.no_grad()
def eval_pairs_cached(
    rm: DualHeadRewardModel,
    cache: Dict[str, torch.Tensor],
    pairs: Sequence[Dict[str, Any]],
    *,
    device: torch.device,
    lambda_l: float,
    lambda_o: float,
    lambda_gap: float,
    batch: int,
) -> Dict[str, float]:
    if not pairs:
        return {}
    rm.eval()
    stats_rows: List[Dict[str, float]] = []
    sides: Dict[str, Tuple[float, float, float]] = {}
    for start in range(0, len(pairs), batch):
        chunk = pairs[start : start + batch]
        h_w = _stack_cached(cache, chunk, "chosen", device)
        h_l = _stack_cached(cache, chunk, "rejected", device)
        rqw, rlw = rm.scores_from_hidden(h_w)
        rql, rll = rm.scores_from_hidden(h_l)
        nw = _token_counts(chunk, "chosen", device)
        nl = _token_counts(chunk, "rejected", device)
        tw = _teacher_scores(chunk, "chosen", device)
        tl = _teacher_scores(chunk, "rejected", device)
        _, stats = odin_rm_loss(
            rqw, rlw, rql, rll, nw, nl, tw, tl,
            head_q=rm.head_q, head_l=rm.head_l,
            lambda_l=lambda_l, lambda_o=lambda_o, lambda_gap=lambda_gap,
        )
        stats_rows.append(stats)
        for i, pair in enumerate(chunk):
            _remember_side_score(sides, pair["chosen"], rqw[i], rlw[i])
            _remember_side_score(sides, pair["rejected"], rql[i], rll[i])
    summary = _mean_stats(stats_rows)
    write_full_set_rho(summary, sides)
    return summary


def save_rm(
    rm: DualHeadRewardModel,
    out_dir: Path,
    *,
    backbone_path: str,
    freeze_backbone: bool,
    extra: Optional[Dict[str, Any]] = None,
    tuned_names: Optional[Sequence[str]] = None,
    unfreeze_layers: int = 0,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    blob = rm.heads_state_dict()
    blob["backbone_path"] = backbone_path
    blob["freeze_backbone"] = freeze_backbone
    tuned = tuned_layer_state(rm.backbone, list(tuned_names) if tuned_names is not None else None)
    if tuned:
        blob["tuned_layers"] = tuned
        blob["unfreeze_layers"] = int(unfreeze_layers)
    torch.save(blob, out_dir / HEADS_NAME)
    cfg = {
        "backbone_path": backbone_path,
        "freeze_backbone": freeze_backbone,
        "hidden_size": rm.hidden_size,
        **(extra or {}),
    }
    (out_dir / RM_CONFIG_NAME).write_text(
        json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    if not freeze_backbone:
        rm.backbone.save_pretrained(out_dir / "backbone")


def load_rm(
    ckpt_dir: Path,
    *,
    device: torch.device,
    dtype: torch.dtype,
    backbone_override: str = "",
) -> DualHeadRewardModel:
    cfg_path = Path(ckpt_dir) / RM_CONFIG_NAME
    cfg = json.loads(cfg_path.read_text(encoding="utf-8")) if cfg_path.is_file() else {}
    heads_path = Path(ckpt_dir) / HEADS_NAME
    try:
        heads = torch.load(heads_path, map_location="cpu", weights_only=False)
    except TypeError:
        heads = torch.load(heads_path, map_location="cpu")
    backbone_path = backbone_override or cfg.get("backbone_path") or heads.get("backbone_path")
    freeze = bool(cfg.get("freeze_backbone", heads.get("freeze_backbone", True)))
    if not freeze and (Path(ckpt_dir) / "backbone").is_dir():
        backbone_path = str(Path(ckpt_dir) / "backbone")
    backbone = AutoModelForCausalLM.from_pretrained(
        backbone_path,
        trust_remote_code=True,
        torch_dtype=dtype if dtype != torch.float32 else None,
    )
    if hasattr(backbone.config, "use_cache"):
        backbone.config.use_cache = False
    rm = DualHeadRewardModel(backbone, hidden_size=int(heads.get("hidden_size") or 0) or None)
    rm.load_heads_state_dict(heads)
    tuned = heads.get("tuned_layers") or {}
    if tuned:
        load_tuned_layers(rm.backbone, tuned)
    if freeze or tuned:
        rm.freeze_backbone()
    rm.to(device)
    rm.eval()
    return rm


def train_heads_cached(
    rm: DualHeadRewardModel,
    cache: Dict[str, torch.Tensor],
    train_pairs: List[Dict[str, Any]],
    hold_pairs: List[Dict[str, Any]],
    *,
    device: torch.device,
    epochs: float,
    batch: int,
    lr: float,
    lambda_l: float,
    lambda_o: float,
    lambda_gap: float,
    log_every: int,
    seed: int,
    metrics_path: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    rng = random.Random(seed)
    opt = AdamWBf16State(
        [p for p in list(rm.head_q.parameters()) + list(rm.head_l.parameters()) if p.requires_grad],
        lr=lr,
    )
    if int(batch) < 2:
        logger.warning("batch=%s 时同一侧只有一条稿，长度损失为 0。", batch)
    n = len(train_pairs)
    steps_per_epoch = max(1, math.ceil(n / max(1, batch)))
    total_steps = max(1, int(round(float(epochs) * steps_per_epoch)))
    history: List[Dict[str, Any]] = []
    step = 0
    rm.head_q.train()
    rm.head_l.train()
    while step < total_steps:
        order = list(range(n))
        rng.shuffle(order)
        for start in range(0, n, max(1, batch)):
            if step >= total_steps:
                break
            idx = order[start : start + max(1, batch)]
            chunk = [train_pairs[i] for i in idx]
            h_w = _stack_cached(cache, chunk, "chosen", device)
            h_l = _stack_cached(cache, chunk, "rejected", device)
            rqw, rlw = rm.scores_from_hidden(h_w)
            rql, rll = rm.scores_from_hidden(h_l)
            nw = _token_counts(chunk, "chosen", device)
            nl = _token_counts(chunk, "rejected", device)
            tw = _teacher_scores(chunk, "chosen", device)
            tl = _teacher_scores(chunk, "rejected", device)
            loss, stats = odin_rm_loss(
                rqw, rlw, rql, rll, nw, nl, tw, tl,
                head_q=rm.head_q, head_l=rm.head_l,
                lambda_l=lambda_l, lambda_o=lambda_o, lambda_gap=lambda_gap,
            )
            opt.zero_grad(set_to_none=True)
            loss.backward()
            opt.step()
            step += 1
            if step % max(1, log_every) == 0 or step == 1 or step == total_steps:
                hold = eval_pairs_cached(
                    rm, cache, hold_pairs, device=device,
                    lambda_l=lambda_l, lambda_o=lambda_o, lambda_gap=lambda_gap,
                    batch=max(1, batch),
                )
                row = {"step": step, "train": stats, "holdout": hold}
                history.append(row)
                if metrics_path is not None:
                    append_metrics(
                        metrics_path,
                        {
                            "stage": "rm",
                            "event": "step",
                            "global_step": step,
                            **{f"train_{k}": v for k, v in stats.items()},
                            **{f"holdout_{k}": v for k, v in hold.items()},
                        },
                    )
                logger.info("step %s train=%s holdout=%s", step, stats, hold)
                rm.head_q.train()
                rm.head_l.train()
    return history


def update_holdout_watch(
    acc: Optional[float],
    best_acc: Optional[float],
    stale: int,
    *,
    step: int,
    min_step: int,
    patience: int,
) -> Tuple[Optional[float], int, bool, bool]:
    """返回 (best_acc, stale, should_stop, improved)。耐心只在 min_step 之后生效。"""
    if acc is None:
        return best_acc, stale, False, False
    improved = best_acc is None or float(acc) > float(best_acc)
    if improved:
        return float(acc), 0, False, True
    stale = int(stale) + 1
    stop = int(patience) > 0 and int(step) >= int(min_step) and stale >= int(patience)
    return best_acc, stale, stop, False


def _token_id_cache(
    tokenizer,
    sides: Dict[str, Dict[str, Any]],
    *,
    max_length: int,
    system_prompt: str,
) -> Dict[str, List[int]]:
    cache: Dict[str, List[int]] = {}
    for key, side in sides.items():
        ids, _ = _tokenize_side(tokenizer, side, max_length, system_prompt)
        cache[key] = list(ids)
    logger.info("tokenized %s completions", len(cache))
    return cache


class AdamWBf16State(torch.optim.Optimizer):
    """AdamW。动量和方差用 bf16 存放，这一步的更新仍在 fp32 里算完再写回。"""

    def __init__(
        self,
        params,
        lr: float = 1e-3,
        betas: Tuple[float, float] = (0.9, 0.999),
        eps: float = 1e-8,
        weight_decay: float = 0.01,
    ) -> None:
        super().__init__(params, {"lr": lr, "betas": betas, "eps": eps, "weight_decay": weight_decay})

    @torch.no_grad()
    def step(self, closure=None):
        loss = None
        if closure is not None:
            with torch.enable_grad():
                loss = closure()
        for group in self.param_groups:
            beta1, beta2 = group["betas"]
            lr = float(group["lr"])
            eps = float(group["eps"])
            weight_decay = float(group["weight_decay"])
            for param in group["params"]:
                grad = param.grad
                if grad is None:
                    continue
                if grad.is_sparse:
                    raise RuntimeError("AdamWBf16State 不支持稀疏梯度")
                state = self.state[param]
                if len(state) == 0:
                    state["step"] = 0
                    state["exp_avg"] = torch.zeros_like(param, dtype=torch.bfloat16)
                    state["exp_avg_sq"] = torch.zeros_like(param, dtype=torch.bfloat16)
                state["step"] += 1
                step = int(state["step"])
                exp_avg = state["exp_avg"].float()
                exp_avg_sq = state["exp_avg_sq"].float()
                grad_f = grad.detach().float()
                exp_avg.mul_(beta1).add_(grad_f, alpha=1.0 - beta1)
                exp_avg_sq.mul_(beta2).addcmul_(grad_f, grad_f, value=1.0 - beta2)
                state["exp_avg"].copy_(exp_avg)
                state["exp_avg_sq"].copy_(exp_avg_sq)
                bias_correction1 = 1.0 - beta1 ** step
                bias_correction2 = 1.0 - beta2 ** step
                denom = exp_avg_sq.sqrt().div_(bias_correction2 ** 0.5).add_(eps)
                updated = param.detach().float()
                if weight_decay != 0.0:
                    updated.mul_(1.0 - lr * weight_decay)
                updated.addcdiv_(exp_avg, denom, value=-(lr / bias_correction1))
                param.copy_(updated.to(dtype=param.dtype))
        return loss


def _scores_for_pairs(
    rm: DualHeadRewardModel,
    token_cache: Dict[str, List[int]],
    pairs: Sequence[Dict[str, Any]],
    *,
    device: torch.device,
    pad_id: int,
    n_unfreeze: int,
) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    rows: List[List[int]] = []
    for pair in pairs:
        rows.append(token_cache[_side_key(pair["chosen"])])
        rows.append(token_cache[_side_key(pair["rejected"])])
    input_ids, attn = _pad_ids(rows, pad_id)
    hidden = last_token_from_inner(
        rm, input_ids.to(device), attn.to(device), n_unfreeze,
    )
    r_q, r_l = rm.scores_from_hidden(hidden)
    return r_q[0::2], r_l[0::2], r_q[1::2], r_l[1::2]


@torch.no_grad()
def eval_pairs_tokens(
    rm: DualHeadRewardModel,
    token_cache: Dict[str, List[int]],
    pairs: Sequence[Dict[str, Any]],
    *,
    device: torch.device,
    pad_id: int,
    n_unfreeze: int,
    lambda_l: float,
    lambda_o: float,
    lambda_gap: float,
    batch: int,
) -> Dict[str, float]:
    if not pairs:
        return {}
    rm.head_q.eval()
    rm.head_l.eval()
    set_suffix_train(rm.backbone, n_unfreeze, train=False)
    stats_rows: List[Dict[str, float]] = []
    sides: Dict[str, Tuple[float, float, float]] = {}
    for start in range(0, len(pairs), max(1, batch)):
        chunk = pairs[start : start + max(1, batch)]
        rqw, rlw, rql, rll = _scores_for_pairs(
            rm, token_cache, chunk, device=device, pad_id=pad_id, n_unfreeze=n_unfreeze,
        )
        _, stats = odin_rm_loss(
            rqw, rlw, rql, rll,
            _token_counts(chunk, "chosen", device),
            _token_counts(chunk, "rejected", device),
            _teacher_scores(chunk, "chosen", device),
            _teacher_scores(chunk, "rejected", device),
            head_q=rm.head_q, head_l=rm.head_l,
            lambda_l=lambda_l, lambda_o=lambda_o, lambda_gap=lambda_gap,
        )
        stats_rows.append(stats)
        for i, pair in enumerate(chunk):
            _remember_side_score(sides, pair["chosen"], rqw[i], rlw[i])
            _remember_side_score(sides, pair["rejected"], rql[i], rll[i])
    summary = _mean_stats(stats_rows)
    write_full_set_rho(summary, sides)
    return summary


def _restore_best(
    rm: DualHeadRewardModel,
    best: Dict[str, Any],
) -> None:
    rm.load_heads_state_dict(best)
    load_tuned_layers(rm.backbone, best.get("tuned_layers") or {})


def train_unfrozen_suffix(
    rm: DualHeadRewardModel,
    token_cache: Dict[str, List[int]],
    train_pairs: List[Dict[str, Any]],
    hold_pairs: List[Dict[str, Any]],
    *,
    device: torch.device,
    pad_id: int,
    n_unfreeze: int,
    tuned_names: Sequence[str],
    epochs: float,
    batch: int,
    lr: float,
    layer_lr: float,
    lambda_l: float,
    lambda_o: float,
    lambda_gap: float,
    log_every: int,
    patience_evals: int,
    min_epochs: float,
    seed: int,
    metrics_path: Optional[Path] = None,
    checkpoint_dir: Optional[Path] = None,
    backbone_path: str = "",
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """最后 n 层和两个头一起训。留出 acc_q 变好就落盘，耐心用尽则停并恢复最好的一次。"""
    rng = random.Random(seed)
    head_params = [p for p in list(rm.head_q.parameters()) + list(rm.head_l.parameters()) if p.requires_grad]
    layer_params = [p for p in rm.backbone.parameters() if p.requires_grad]
    opt = AdamWBf16State(
        [
            {"params": head_params, "lr": lr},
            {"params": layer_params, "lr": layer_lr},
        ],
        lr=lr,
    )
    n = len(train_pairs)
    steps_per_epoch = max(1, math.ceil(n / max(1, batch)))
    total_steps = max(1, int(round(float(epochs) * steps_per_epoch)))
    min_step = max(1, int(round(float(min_epochs) * steps_per_epoch)))
    history: List[Dict[str, Any]] = []
    step = 0
    best_acc: Optional[float] = None
    best_step = 0
    stale = 0
    best_blob: Optional[Dict[str, Any]] = None
    if int(batch) < 2:
        logger.warning("batch=%s 时同一侧只有一条稿，长度损失为 0。", batch)
    logger.info(
        "解开最后 %s 层：头 lr=%s 层 lr=%s，动量和方差用 bf16 存放。最多 %s 步，%s 步后连续 %s 次留出评估不升就停",
        n_unfreeze, lr, layer_lr, total_steps, min_step, patience_evals,
    )

    def _remember(acc: float) -> None:
        nonlocal best_blob
        best_blob = {
            "head_q": {k: v.detach().cpu().clone() for k, v in rm.head_q.state_dict().items()},
            "head_l": {k: v.detach().cpu().clone() for k, v in rm.head_l.state_dict().items()},
            "tuned_layers": tuned_layer_state(rm.backbone, list(tuned_names)),
        }
        if checkpoint_dir is not None:
            save_rm(
                rm, checkpoint_dir,
                backbone_path=backbone_path,
                freeze_backbone=True,
                tuned_names=tuned_names,
                unfreeze_layers=n_unfreeze,
                extra={
                    "unfreeze_layers": n_unfreeze,
                    "best_step": step,
                    "best_holdout_acc_q": acc,
                    "layer_lr": layer_lr,
                },
            )

    while step < total_steps:
        order = list(range(n))
        rng.shuffle(order)
        for start in range(0, n, max(1, batch)):
            if step >= total_steps:
                break
            set_suffix_train(rm.backbone, n_unfreeze, train=True)
            rm.head_q.train()
            rm.head_l.train()
            idx = order[start : start + max(1, batch)]
            chunk = [train_pairs[i] for i in idx]
            rqw, rlw, rql, rll = _scores_for_pairs(
                rm, token_cache, chunk, device=device, pad_id=pad_id, n_unfreeze=n_unfreeze,
            )
            loss, stats = odin_rm_loss(
                rqw, rlw, rql, rll,
                _token_counts(chunk, "chosen", device),
                _token_counts(chunk, "rejected", device),
                _teacher_scores(chunk, "chosen", device),
                _teacher_scores(chunk, "rejected", device),
                head_q=rm.head_q, head_l=rm.head_l,
                lambda_l=lambda_l, lambda_o=lambda_o, lambda_gap=lambda_gap,
            )
            opt.zero_grad(set_to_none=True)
            loss.backward()
            opt.step()
            step += 1
            if step % max(1, log_every) != 0 and step != 1 and step != total_steps:
                continue
            hold = eval_pairs_tokens(
                rm, token_cache, hold_pairs,
                device=device, pad_id=pad_id, n_unfreeze=n_unfreeze,
                lambda_l=lambda_l, lambda_o=lambda_o, lambda_gap=lambda_gap,
                batch=max(1, batch),
            )
            acc = hold.get("acc_q")
            best_acc, stale, stop, improved = update_holdout_watch(
                acc, best_acc, stale, step=step, min_step=min_step, patience=patience_evals,
            )
            if improved and acc is not None:
                best_step = step
                _remember(float(acc))
                logger.info("留出 acc_q=%.4f，保存 step %s", float(acc), step)
            row = {"step": step, "train": stats, "holdout": hold, "best_step": best_step, "best_acc_q": best_acc}
            history.append(row)
            if metrics_path is not None:
                append_metrics(
                    metrics_path,
                    {
                        "stage": "rm",
                        "event": "step",
                        "global_step": step,
                        "best_step": best_step,
                        "best_holdout_acc_q": best_acc,
                        **{f"train_{k}": v for k, v in stats.items()},
                        **{f"holdout_{k}": v for k, v in hold.items()},
                    },
                )
            logger.info("step %s train=%s holdout=%s", step, stats, hold)
            if stop:
                logger.info(
                    "留出 acc_q 连续 %s 次没有超过 %.4f（step %s），停在 step %s",
                    stale, float(best_acc or 0.0), best_step, step,
                )
                if best_blob is not None:
                    _restore_best(rm, best_blob)
                return history, {"best_step": best_step, "best_holdout_acc_q": best_acc, "stopped_early": True}
    if best_blob is not None:
        _restore_best(rm, best_blob)
        logger.info("训练结束，恢复留出 acc_q 最好的 step %s（%.4f）", best_step, float(best_acc or 0.0))
    return history, {"best_step": best_step, "best_holdout_acc_q": best_acc, "stopped_early": False}


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    p = argparse.ArgumentParser(description="训 ODIN 双头 RM（默认只训两个头）")
    od = grpo_odin_rm_config()
    p.add_argument("--pairs", type=Path, default=None, help="pairs.jsonl；与 --samples 二选一")
    p.add_argument("--samples", type=Path, default=None, help="若无 pairs 则现场造对")
    p.add_argument("--out", type=Path, required=True, help="checkpoint 目录")
    p.add_argument("--model", type=str, default="", help="backbone HF 路径；空则读 yaml odin-rm.model")
    p.add_argument("--dtype", choices=["bf16", "fp16", "fp32"], default="bf16")
    p.add_argument("--max-length", type=int, default=int(od.get("max-length") or 2048))
    p.add_argument("--batch", type=int, default=int(od.get("batch-pairs") or 4), help="头训练的 pair batch（缓存 hidden 后）")
    p.add_argument("--encode-batch", type=int, default=1)
    p.add_argument("--epochs", type=float, default=float(od.get("epochs") or 3.0))
    p.add_argument("--lr", type=float, default=float(od.get("lr") or 1e-3))
    p.add_argument("--lambda-l", type=float, default=float(od.get("lambda-l") if od.get("lambda-l") is not None else LAMBDA_L))
    p.add_argument("--lambda-o", type=float, default=float(od.get("lambda-o") if od.get("lambda-o") is not None else LAMBDA_O))
    p.add_argument("--lambda-gap", type=float, default=float(od.get("lambda-gap") if od.get("lambda-gap") is not None else LAMBDA_GAP))
    p.add_argument(
        "--min-margin",
        type=float,
        default=float(od.get("min-margin") if od.get("min-margin") is not None else MIN_SCORE_GAP),
        help="S_fp 分差不大于此值的对不进 RM 训练",
    )
    p.add_argument("--holdout-frac", type=float, default=0.1)
    p.add_argument("--log-every", type=int, default=20)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--system-prompt", type=str, default="")
    p.add_argument(
        "--unfreeze-layers",
        type=int,
        default=int(od.get("unfreeze-layers") if od.get("unfreeze-layers") is not None else DEFAULT_UNFREEZE_LAYERS),
        help="只训练基座最后几层和最终 norm。0 表示整座冻住、只训两个头",
    )
    p.add_argument(
        "--layer-lr",
        type=float,
        default=float(od.get("layer-lr") if od.get("layer-lr") is not None else DEFAULT_LAYER_LR),
        help="解开层的学习率。两个头仍用 --lr",
    )
    p.add_argument(
        "--patience-evals",
        type=int,
        default=int(od.get("patience-evals") if od.get("patience-evals") is not None else DEFAULT_PATIENCE_EVALS),
        help="留出 acc_q 连续这么多次评估没有提升就停。0 表示只在结束时恢复最好的一次",
    )
    p.add_argument(
        "--min-epochs",
        type=float,
        default=float(od.get("min-epochs") if od.get("min-epochs") is not None else DEFAULT_MIN_EPOCHS),
        help="这么多 epoch 之前不因耐心提前停",
    )
    p.add_argument(
        "--unfreeze-backbone",
        action="store_true",
        help="全参微调 backbone（显存大；本脚本不接这条路径）",
    )
    args = p.parse_args()

    if args.pairs is None and args.samples is None:
        raise SystemExit("需要 --pairs 或 --samples")
    if args.pairs is not None:
        from .data import read_jsonl

        pairs = list(read_jsonl(args.pairs))
    else:
        pairs, summary = build_preference_pairs(
            args.samples, min_margin=args.min_margin, holdout_frac=args.holdout_frac
        )
        logger.info("built pairs: %s", summary)
    n_raw = len(pairs)
    pairs = [x for x in pairs if pair_in_rm_training(x, args.min_margin)]
    logger.info("RM 对：%s / %s（S_fp 分差 > %s）", len(pairs), n_raw, args.min_margin)
    train_pairs = [x for x in pairs if x.get("split") != "holdout"]
    hold_pairs = [x for x in pairs if x.get("split") == "holdout"]
    if not train_pairs:
        train_pairs = list(pairs)
        hold_pairs = []
    if not train_pairs:
        raise SystemExit("没有偏好对可训")

    model_id = args.model.strip() or default_odin_rm_model()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    dtype = _dtype(args.dtype)
    logger.info(
        "backbone=%s device=%s unfreeze_layers=%s",
        model_id, device, args.unfreeze_layers,
    )

    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    backbone = AutoModelForCausalLM.from_pretrained(
        model_id,
        trust_remote_code=True,
        torch_dtype=dtype if args.dtype != "fp32" else None,
    )
    if hasattr(backbone.config, "use_cache"):
        backbone.config.use_cache = False
    rm = DualHeadRewardModel(backbone)
    rm.to(device)
    if args.unfreeze_backbone:
        raise SystemExit(
            "全参反传尚未接到本脚本主循环。用 --unfreeze-layers 2 只解开最后两层。"
        )
    n_unfreeze = max(0, int(args.unfreeze_layers))
    opened = unfreeze_last_layers(rm.backbone, n_unfreeze)
    tuned_names = [name for name, param in rm.backbone.named_parameters() if param.requires_grad]
    if opened:
        logger.info("可训基座参数 %s 个（最后 %s 层 + norm）", len(tuned_names), opened)

    _attach_token_counts(train_pairs + hold_pairs, tokenizer)
    sides = _collect_unique_sides(train_pairs + hold_pairs)
    metrics_jsonl = args.out / "metrics.jsonl"
    best_info: Dict[str, Any] = {}
    if opened:
        if not hold_pairs:
            logger.warning("没有留出对，无法按 acc_q 早停，将跑满 epoch 并保存最后一步")
        token_cache = _token_id_cache(
            tokenizer, sides, max_length=args.max_length, system_prompt=args.system_prompt,
        )
        history, best_info = train_unfrozen_suffix(
            rm, token_cache, train_pairs, hold_pairs,
            device=device, pad_id=int(tokenizer.pad_token_id or 0),
            n_unfreeze=opened, tuned_names=tuned_names,
            epochs=args.epochs, batch=args.batch, lr=args.lr, layer_lr=args.layer_lr,
            lambda_l=args.lambda_l, lambda_o=args.lambda_o, lambda_gap=args.lambda_gap,
            log_every=args.log_every,
            patience_evals=args.patience_evals if hold_pairs else 0,
            min_epochs=args.min_epochs, seed=args.seed,
            metrics_path=metrics_jsonl, checkpoint_dir=args.out, backbone_path=model_id,
        )
        hold_final = eval_pairs_tokens(
            rm, token_cache, hold_pairs or train_pairs[: min(64, len(train_pairs))],
            device=device, pad_id=int(tokenizer.pad_token_id or 0), n_unfreeze=opened,
            lambda_l=args.lambda_l, lambda_o=args.lambda_o, lambda_gap=args.lambda_gap,
            batch=args.batch,
        )
    else:
        rm.freeze_backbone()
        cache = encode_hidden_cache(
            rm, tokenizer, sides,
            max_length=args.max_length, device=device,
            system_prompt=args.system_prompt, encode_batch=args.encode_batch,
        )
        history = train_heads_cached(
            rm, cache, train_pairs, hold_pairs,
            device=device, epochs=args.epochs, batch=args.batch, lr=args.lr,
            lambda_l=args.lambda_l, lambda_o=args.lambda_o, lambda_gap=args.lambda_gap,
            log_every=args.log_every, seed=args.seed,
            metrics_path=metrics_jsonl,
        )
        hold_final = eval_pairs_cached(
            rm, cache, hold_pairs or train_pairs[: min(64, len(train_pairs))],
            device=device, lambda_l=args.lambda_l, lambda_o=args.lambda_o, lambda_gap=args.lambda_gap,
            batch=args.batch,
        )
    save_rm(
        rm, args.out,
        backbone_path=model_id,
        freeze_backbone=True,
        tuned_names=tuned_names,
        unfreeze_layers=opened,
        extra={
            "lambda_l": args.lambda_l,
            "lambda_o": args.lambda_o,
            "lambda_gap": args.lambda_gap,
            "min_margin": args.min_margin,
            "epochs": args.epochs,
            "lr": args.lr,
            "layer_lr": args.layer_lr,
            "unfreeze_layers": opened,
            "patience_evals": args.patience_evals,
            "min_epochs": args.min_epochs,
            "train_pairs": len(train_pairs),
            "holdout_pairs": len(hold_pairs),
            "best_step": best_info.get("best_step"),
            "best_holdout_acc_q": best_info.get("best_holdout_acc_q"),
            "stopped_early": best_info.get("stopped_early"),
            "adam_state_dtype": "bf16",
            "history": history[-20:],
        },
    )
    (args.out / "train_metrics.json").write_text(
        json.dumps({"holdout_or_train_probe": hold_final, "history": history}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    if len(history) >= 1:
        first_train = history[0].get("train") or {}
        last_train = history[-1].get("train") or {}
        first_hold = history[0].get("holdout") or {}
        last_hold = history[-1].get("holdout") or {}
        summary = progress_summary(
            stage="rm",
            global_step=int(history[-1].get("step") or 0),
            first={**{f"train_{k}": v for k, v in first_train.items()}, **{f"holdout_{k}": v for k, v in first_hold.items()}},
            last={**{f"train_{k}": v for k, v in last_train.items()}, **{f"holdout_{k}": v for k, v in last_hold.items()}},
            keys=(
                "train_loss",
                "train_L_R",
                "train_L_gap",
                "train_L_L",
                "train_L_O",
                "train_gap_mae",
                "train_acc_sum",
                "train_acc_q",
                "train_rho_q",
                "train_rho_l",
                "holdout_loss",
                "holdout_L_R",
                "holdout_L_gap",
                "holdout_L_L",
                "holdout_L_O",
                "holdout_gap_mae",
                "holdout_acc_sum",
                "holdout_acc_q",
                "holdout_rho_q",
                "holdout_rho_l",
            ),
        )
        append_metrics(metrics_jsonl, summary)
    logger.info("saved %s  holdout=%s", args.out, hold_final)


if __name__ == "__main__":
    main()
