"""
档 3 编排：samples.jsonl → 偏好对 → 训双头 RM（仅冷启动）→ r_Q 重打分 → 导出 phase_a / phase_b。

冷启动之后不要再训双头。后续新 K 路样本用 ``--skip-train --rm-dir <冷启动 rm>`` 只打分导出，
再 ``python -m training.run_next_grpo_round`` 做短 GRPO（不 SFT）。
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from .pairs import build_preference_pairs
from .score import score_samples
from .train_rm import main as train_rm_main

logger = logging.getLogger(__name__)


def _export(samples_rq: Path, export_dir: Path) -> dict:
    from ..grpo_pipeline import default_include_for_training, export_two_phase_from_samples

    export_dir.mkdir(parents=True, exist_ok=True)
    return export_two_phase_from_samples(
        samples_rq,
        export_dir,
        include_filter=default_include_for_training,
        reward_key="R_content",
    )


def _next_steps(export_dir: Path, rm_dir: Path, *, skip_train: bool) -> str:
    phase_a = export_dir / "phase_a_sft.jsonl"
    phase_b = export_dir / "phase_b_grpo.jsonl"
    if skip_train:
        return (
            "\n下一步（复用双头 RM，不再 SFT，只短 GRPO）:\n"
            f"  python -m training.run_next_grpo_round \\\n"
            f"    --phase-b {phase_b} \\\n"
            f"    --train-work-dir <hf_checkpoints>\n"
        )
    return (
        "\n下一步（冷启动：SFT 一次 + 多轮短 GRPO）:\n"
        f"  python training/hf_grpo/run_recommended_training.py \\\n"
        f"    --phase-a {phase_a} \\\n"
        f"    --phase-b {phase_b} \\\n"
        f"    --work-dir <hf_checkpoints>\n"
        "\n之后新 K 路样本（勿再训双头 / 勿再 SFT）:\n"
        f"  python -m training.run_next_grpo_round \\\n"
        f"    --samples <new_samples.jsonl> \\\n"
        f"    --rm-dir {rm_dir} \\\n"
        f"    --train-work-dir <hf_checkpoints>\n"
    )


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    p = argparse.ArgumentParser(
        description="ODIN 档 3：造对 → 训双头 RM（冷启动一次）→ r_Q 打分 → 导出 JSONL",
    )
    p.add_argument("--samples", type=Path, required=True, help="K 路采数 samples.jsonl（裁判已打分）")
    p.add_argument("--work-dir", type=Path, required=True, help="写出 pairs / rm / samples_rq / export")
    p.add_argument(
        "--rm-dir",
        type=Path,
        default=None,
        help="双头 RM 目录；空则 work-dir/rm。后续轮 --skip-train 时指向冷启动 rm",
    )
    p.add_argument("--model", type=str, default="", help="RM backbone；空则 yaml odin-rm.model")
    p.add_argument("--dtype", choices=["bf16", "fp16", "fp32"], default="bf16")
    p.add_argument("--max-length", type=int, default=2048)
    p.add_argument("--rm-epochs", type=float, default=3.0)
    p.add_argument("--rm-lr", type=float, default=1e-3)
    p.add_argument("--rm-batch", type=int, default=8)
    p.add_argument("--encode-batch", type=int, default=1)
    p.add_argument("--score-batch", type=int, default=1)
    p.add_argument("--lambda-corr", type=float, default=1.0)
    p.add_argument("--lambda-orth", type=float, default=1.0)
    p.add_argument("--holdout-frac", type=float, default=0.1)
    p.add_argument("--skip-train", action="store_true", help="复用已有双头 RM，不再训练")
    p.add_argument("--skip-pairs", action="store_true", help="跳过造偏好对（后续轮只打分时可用）")
    p.add_argument("--skip-score", action="store_true")
    p.add_argument("--skip-export", action="store_true")
    args = p.parse_args()

    work = args.work_dir.resolve()
    work.mkdir(parents=True, exist_ok=True)
    pairs_path = work / "pairs.jsonl"
    rm_dir = (args.rm_dir or (work / "rm")).resolve()
    samples_rq = work / "samples_rq.jsonl"
    export_dir = work / "export"

    if not args.skip_pairs:
        pairs, summary = build_preference_pairs(
            args.samples, holdout_frac=args.holdout_frac
        )
        from .data import write_jsonl

        write_jsonl(pairs_path, pairs)
        (work / "pairs.summary.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        logger.info("pairs: %s", summary)
        if not args.skip_train and summary["pairs"] < 1:
            raise SystemExit("没有偏好对：检查 samples 是否含同组多条且 s_fp_base 有差距")
    elif not args.skip_train:
        raise SystemExit("--skip-pairs 仅能与 --skip-train 一起使用")

    if not args.skip_train:
        argv = [
            "train_rm",
            "--pairs",
            str(pairs_path),
            "--out",
            str(rm_dir),
            "--dtype",
            args.dtype,
            "--max-length",
            str(args.max_length),
            "--epochs",
            str(args.rm_epochs),
            "--lr",
            str(args.rm_lr),
            "--batch",
            str(args.rm_batch),
            "--encode-batch",
            str(args.encode_batch),
            "--lambda-corr",
            str(args.lambda_corr),
            "--lambda-orth",
            str(args.lambda_orth),
            "--holdout-frac",
            str(args.holdout_frac),
        ]
        if args.model.strip():
            argv.extend(["--model", args.model.strip()])
        old = sys.argv
        try:
            sys.argv = argv
            train_rm_main()
        finally:
            sys.argv = old
    elif not (rm_dir / "odin_heads.pt").is_file():
        raise SystemExit(f"--skip-train 但找不到 {rm_dir / 'odin_heads.pt'}")

    if not args.skip_score:
        score_summary = score_samples(
            args.samples, rm_dir, samples_rq,
            batch=args.score_batch, max_length=args.max_length, dtype=args.dtype,
            backbone_override=args.model.strip(),
        )
        logger.info("score: %s", score_summary)
    elif not samples_rq.is_file():
        raise SystemExit(f"--skip-score 但找不到 {samples_rq}")

    if not args.skip_export:
        manifest = _export(samples_rq, export_dir)
        logger.info("export: %s", manifest)
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        print(_next_steps(export_dir, rm_dir, skip_train=bool(args.skip_train)))


if __name__ == "__main__":
    main()
