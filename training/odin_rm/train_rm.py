"""训 ODIN 双头 RM。默认冻住 backbone，只训两个头（可先缓存 last-token hidden）。"""

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

from .data import messages_from_record
from .modeling import DualHeadRewardModel, odin_rm_loss
from .pairs import build_preference_pairs

logger = logging.getLogger(__name__)

HEADS_NAME = "odin_heads.pt"
RM_CONFIG_NAME = "odin_rm_config.json"


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


def _log_lens(pairs: Sequence[Dict[str, Any]], which: str, device: torch.device) -> torch.Tensor:
    vals = [float(p[which].get("log_len") or 0.0) for p in pairs]
    return torch.tensor(vals, dtype=torch.float32, device=device)


def _mean_stats(rows: List[Dict[str, float]]) -> Dict[str, float]:
    if not rows:
        return {}
    keys = rows[0].keys()
    return {k: sum(r[k] for r in rows) / len(rows) for k in keys}


@torch.no_grad()
def eval_pairs_cached(
    rm: DualHeadRewardModel,
    cache: Dict[str, torch.Tensor],
    pairs: Sequence[Dict[str, Any]],
    *,
    device: torch.device,
    lambda_corr: float,
    lambda_orth: float,
    batch: int,
) -> Dict[str, float]:
    if not pairs:
        return {}
    rm.eval()
    stats_rows: List[Dict[str, float]] = []
    for start in range(0, len(pairs), batch):
        chunk = pairs[start : start + batch]
        h_w = _stack_cached(cache, chunk, "chosen", device)
        h_l = _stack_cached(cache, chunk, "rejected", device)
        rqw, rlw = rm.scores_from_hidden(h_w)
        rql, rll = rm.scores_from_hidden(h_l)
        llw = _log_lens(chunk, "chosen", device)
        lll = _log_lens(chunk, "rejected", device)
        _, stats = odin_rm_loss(
            rqw, rlw, rql, rll, llw, lll,
            head_q=rm.head_q, head_l=rm.head_l,
            lambda_corr=lambda_corr, lambda_orth=lambda_orth,
        )
        stats_rows.append(stats)
    return _mean_stats(stats_rows)


def save_rm(
    rm: DualHeadRewardModel,
    out_dir: Path,
    *,
    backbone_path: str,
    freeze_backbone: bool,
    extra: Optional[Dict[str, Any]] = None,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    blob = rm.heads_state_dict()
    blob["backbone_path"] = backbone_path
    blob["freeze_backbone"] = freeze_backbone
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
    if freeze:
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
    lambda_corr: float,
    lambda_orth: float,
    log_every: int,
    seed: int,
) -> List[Dict[str, Any]]:
    rng = random.Random(seed)
    opt = torch.optim.AdamW(
        [p for p in list(rm.head_q.parameters()) + list(rm.head_l.parameters()) if p.requires_grad],
        lr=lr,
    )
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
            llw = _log_lens(chunk, "chosen", device)
            lll = _log_lens(chunk, "rejected", device)
            loss, stats = odin_rm_loss(
                rqw, rlw, rql, rll, llw, lll,
                head_q=rm.head_q, head_l=rm.head_l,
                lambda_corr=lambda_corr, lambda_orth=lambda_orth,
            )
            opt.zero_grad(set_to_none=True)
            loss.backward()
            opt.step()
            step += 1
            if step % max(1, log_every) == 0 or step == 1 or step == total_steps:
                hold = eval_pairs_cached(
                    rm, cache, hold_pairs, device=device,
                    lambda_corr=lambda_corr, lambda_orth=lambda_orth, batch=max(1, batch),
                )
                row = {"step": step, "train": stats, "holdout": hold}
                history.append(row)
                logger.info("step %s train=%s holdout=%s", step, stats, hold)
                rm.head_q.train()
                rm.head_l.train()
    return history


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
    p.add_argument("--batch", type=int, default=int(od.get("batch-pairs") or 8), help="头训练的 pair batch（缓存 hidden 后）")
    p.add_argument("--encode-batch", type=int, default=1)
    p.add_argument("--epochs", type=float, default=float(od.get("epochs") or 3.0))
    p.add_argument("--lr", type=float, default=float(od.get("lr") or 1e-3))
    p.add_argument("--lambda-corr", type=float, default=float(od.get("lambda-corr") or 1.0))
    p.add_argument("--lambda-orth", type=float, default=float(od.get("lambda-orth") or 1.0))
    p.add_argument("--min-margin", type=float, default=1e-6)
    p.add_argument("--holdout-frac", type=float, default=0.1)
    p.add_argument("--log-every", type=int, default=20)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--system-prompt", type=str, default="")
    p.add_argument(
        "--unfreeze-backbone",
        action="store_true",
        help="全参微调 backbone（显存大；默认冻住只训头）",
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
    logger.info("backbone=%s device=%s freeze=%s", model_id, device, not args.unfreeze_backbone)

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
    freeze = not args.unfreeze_backbone
    if freeze:
        rm.freeze_backbone()
    rm.to(device)

    if not freeze:
        raise SystemExit(
            "全参反传尚未接到本脚本主循环；请去掉 --unfreeze-backbone，"
            "用冻 backbone + 缓存 hidden 的默认路径。"
        )

    sides = _collect_unique_sides(train_pairs + hold_pairs)
    cache = encode_hidden_cache(
        rm, tokenizer, sides,
        max_length=args.max_length, device=device,
        system_prompt=args.system_prompt, encode_batch=args.encode_batch,
    )
    history = train_heads_cached(
        rm, cache, train_pairs, hold_pairs,
        device=device, epochs=args.epochs, batch=args.batch, lr=args.lr,
        lambda_corr=args.lambda_corr, lambda_orth=args.lambda_orth,
        log_every=args.log_every, seed=args.seed,
    )
    save_rm(
        rm, args.out,
        backbone_path=model_id,
        freeze_backbone=True,
        extra={
            "lambda_corr": args.lambda_corr,
            "lambda_orth": args.lambda_orth,
            "epochs": args.epochs,
            "lr": args.lr,
            "train_pairs": len(train_pairs),
            "holdout_pairs": len(hold_pairs),
            "history": history[-20:],
        },
    )
    metrics_path = args.out / "train_metrics.json"
    hold_final = eval_pairs_cached(
        rm, cache, hold_pairs or train_pairs[: min(64, len(train_pairs))],
        device=device, lambda_corr=args.lambda_corr, lambda_orth=args.lambda_orth,
        batch=args.batch,
    )
    metrics_path.write_text(
        json.dumps({"holdout_or_train_probe": hold_final, "history": history}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info("saved %s  holdout=%s", args.out, hold_final)


if __name__ == "__main__":
    main()
