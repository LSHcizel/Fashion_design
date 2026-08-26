"""用训好的双头 RM 给 samples.jsonl 打 r_Q / r_L；GRPO 只写 r_Q。"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Any, Dict, List

import torch
from transformers import AutoTokenizer

from plugins.text_description_evaluator.r_content_reward import pearson_corr

from .data import (
    apply_r_q_to_record,
    include_in_training,
    log_len_of,
    messages_from_record,
    read_jsonl,
    teacher_score,
)
from .modeling import DualHeadRewardModel
from .train_rm import _dtype, _pad_ids, _tokenize_side, load_rm

logger = logging.getLogger(__name__)


def _score_batch(
    rm: DualHeadRewardModel,
    tokenizer,
    recs: List[Dict[str, Any]],
    *,
    max_length: int,
    device: torch.device,
    system_prompt: str,
    backbone: str,
) -> List[Dict[str, Any]]:
    pad_id = tokenizer.pad_token_id or 0
    id_rows: List[List[int]] = []
    keep_idx: List[int] = []
    skipped: List[int] = []
    for i, rec in enumerate(recs):
        if not str(rec.get("completion") or "").strip():
            skipped.append(i)
            continue
        ids, _ = _tokenize_side(
            tokenizer,
            {
                "context": rec.get("context") or {},
                "completion": rec.get("completion") or "",
                "group_id": rec.get("group_id"),
                "candidate_index": rec.get("candidate_index"),
            },
            max_length,
            system_prompt,
        )
        id_rows.append(ids)
        keep_idx.append(i)
    out = [dict(r) for r in recs]
    if not id_rows:
        return out
    input_ids, attn = _pad_ids(id_rows, pad_id)
    input_ids = input_ids.to(device)
    attn = attn.to(device)
    with torch.no_grad():
        hidden = rm.pool_hidden(input_ids, attn)
        r_q, r_l = rm.scores_from_hidden(hidden)
    r_q = r_q.float().cpu().tolist()
    r_l = r_l.float().cpu().tolist()
    for j, i in enumerate(keep_idx):
        apply_r_q_to_record(out[i], r_q=float(r_q[j]), r_l=float(r_l[j]), backbone=backbone)
    return out


def summarize_rm_scores(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    rqs: List[float] = []
    rls: List[float] = []
    ells: List[float] = []
    teachers: List[float] = []
    for rec in rows:
        block = rec.get("odin_rm") or {}
        if block.get("r_Q") is None:
            continue
        rqs.append(float(block["r_Q"]))
        rls.append(float(block["r_L"]))
        ells.append(log_len_of(rec))
        ts = teacher_score(rec)
        if ts is not None:
            teachers.append(ts)
    return {
        "n_scored": len(rqs),
        "mean_r_Q": None if not rqs else round(sum(rqs) / len(rqs), 6),
        "mean_r_L": None if not rls else round(sum(rls) / len(rls), 6),
        "pearson_r_Q_vs_log_len": pearson_corr(rqs, ells),
        "pearson_r_L_vs_log_len": pearson_corr(rls, ells),
        "note": "验收：ρ(r_Q, ℓ)≈0，ρ(r_L, ℓ)>0。S_fp 仍是裁判 0～1。",
    }


def score_samples(
    samples_jsonl: Path,
    ckpt_dir: Path,
    out_jsonl: Path,
    *,
    batch: int = 1,
    max_length: int = 2048,
    dtype: str = "bf16",
    system_prompt: str = "",
    backbone_override: str = "",
) -> Dict[str, Any]:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    rm = load_rm(
        ckpt_dir,
        device=device,
        dtype=_dtype(dtype),
        backbone_override=backbone_override,
    )
    cfg_path = Path(ckpt_dir) / "odin_rm_config.json"
    cfg = json.loads(cfg_path.read_text(encoding="utf-8")) if cfg_path.is_file() else {}
    backbone = backbone_override or str(cfg.get("backbone_path") or "")
    tokenizer = AutoTokenizer.from_pretrained(backbone or str(ckpt_dir), trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    recs = list(read_jsonl(samples_jsonl))
    written: List[Dict[str, Any]] = []
    bs = max(1, int(batch))
    for start in range(0, len(recs), bs):
        chunk = recs[start : start + bs]
        scored = _score_batch(
            rm, tokenizer, chunk,
            max_length=max_length, device=device,
            system_prompt=system_prompt, backbone=backbone,
        )
        written.extend(scored)
        if start == 0 or (start // bs) % 10 == 0:
            logger.info("scored %s / %s", min(start + bs, len(recs)), len(recs))

    out_jsonl.parent.mkdir(parents=True, exist_ok=True)
    with out_jsonl.open("w", encoding="utf-8") as f:
        for row in written:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    summary = summarize_rm_scores(written)
    summary["samples_in"] = str(samples_jsonl.resolve())
    summary["samples_out"] = str(out_jsonl.resolve())
    summary["ckpt"] = str(Path(ckpt_dir).resolve())
    summary["include_in_training"] = sum(1 for r in written if include_in_training(r))
    (out_jsonl.with_suffix(".metrics.json")).write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return summary


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    p = argparse.ArgumentParser(description="用 r_Q 重写 samples.jsonl 的 R_content")
    p.add_argument("--samples", type=Path, required=True)
    p.add_argument("--ckpt", type=Path, required=True, help="train_rm 输出目录")
    p.add_argument("--out", type=Path, required=True, help="samples_rq.jsonl")
    p.add_argument("--batch", type=int, default=1)
    p.add_argument("--max-length", type=int, default=2048)
    p.add_argument("--dtype", choices=["bf16", "fp16", "fp32"], default="bf16")
    p.add_argument("--system-prompt", type=str, default="")
    p.add_argument("--model", type=str, default="", help="覆盖 backbone 路径")
    args = p.parse_args()
    summary = score_samples(
        args.samples, args.ckpt, args.out,
        batch=args.batch, max_length=args.max_length, dtype=args.dtype,
        system_prompt=args.system_prompt, backbone_override=args.model,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
