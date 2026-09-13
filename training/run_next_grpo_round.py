"""
冷启动之后的后续轮：复用双头 RM，不再 SFT，只短 GRPO 并写验收摘要。

两种用法：

1. 已有新 phase_b（RM 已打过 r_Q）::

    python -m training.run_next_grpo_round \\
      --phase-b <export>/phase_b_grpo.jsonl \\
      --train-work-dir training/runs/<id>/hf_checkpoints

2. 新 K 路 samples.jsonl：用冷启动 RM 打分导出后再短 GRPO::

    python -m training.run_next_grpo_round \\
      --samples <new_samples.jsonl> \\
      --rm-dir training/runs/<id>/odin_rm/rm \\
      --train-work-dir training/runs/<id>/hf_checkpoints
"""

from __future__ import annotations

import argparse
import logging
import subprocess
import sys
from pathlib import Path
from typing import List, Sequence

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[1]
REC_MODULE = "training.hf_grpo.run_recommended_training"


def _run(cmd: Sequence[str], *, dry_run: bool) -> None:
    logger.info("Run: %s", " ".join(cmd))
    if dry_run:
        return
    subprocess.run(list(cmd), cwd=str(REPO_ROOT), check=True)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    p = argparse.ArgumentParser(
        description="后续轮：复用双头 RM、跳过 SFT、多轮短 GRPO + 验收",
    )
    p.add_argument("--phase-b", type=Path, default=None, help="已导出的 phase_b_grpo.jsonl")
    p.add_argument("--samples", type=Path, default=None, help="新 K 路 samples.jsonl；需同时给 --rm-dir")
    p.add_argument("--rm-dir", type=Path, default=None, help="冷启动双头 RM 目录")
    p.add_argument(
        "--iter-dir",
        type=Path,
        default=None,
        help="本轮 ODIN 打分/导出目录；空则 train-work-dir 的同级 grpo_iter/<n>",
    )
    p.add_argument(
        "--train-work-dir",
        type=Path,
        required=True,
        help="含 sft/ 与 grpo/ 的 hf_checkpoints 目录",
    )
    p.add_argument("--grpo-policy", type=str, default="", help="起始 policy；空则读 grpo/latest.json")
    p.add_argument("--grpo-rounds", type=int, default=1, help="本轮外循环要跑的短 GRPO 次数，默认 1")
    p.add_argument("--grpo-epochs", type=float, default=None, help="每一短轮的 epoch；空则 yaml")
    p.add_argument("--grpo-lr", type=float, default=1e-6)
    p.add_argument("--beta-kl", type=float, default=0.04)
    p.add_argument("--dtype", choices=["bf16", "fp16", "fp32"], default="bf16")
    p.add_argument("--max-length", type=int, default=2048)
    p.add_argument("--batch", type=int, default=1)
    p.add_argument("--grad-accum", type=int, default=8)
    p.add_argument("--score-batch", type=int, default=1)
    p.add_argument("--model", type=str, default="", help="RM backbone 覆盖")
    p.add_argument("--system-prompt-file", type=Path, default=None)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    train_work = args.train_work_dir.resolve()
    py = sys.executable

    phase_b = args.phase_b.resolve() if args.phase_b else None
    if phase_b is None:
        if args.samples is None or args.rm_dir is None:
            raise SystemExit("未给 --phase-b 时必须同时提供 --samples 与 --rm-dir")
        samples = args.samples.resolve()
        rm_dir = args.rm_dir.resolve()
        if not samples.is_file():
            raise SystemExit(f"找不到 samples: {samples}")
        if not (rm_dir / "odin_heads.pt").is_file():
            raise SystemExit(f"找不到冷启动 RM: {rm_dir / 'odin_heads.pt'}")

        from training.hf_grpo.run_recommended_training import load_latest

        latest = load_latest(train_work / "grpo")
        n = int((latest or {}).get("round") or 0) + 1
        iter_dir = (
            args.iter_dir.resolve()
            if args.iter_dir
            else (train_work.parent / "grpo_iter" / f"round_{n:02d}")
        )
        odin_cmd: List[str] = [
            py,
            "-m",
            "training.odin_rm.run_pipeline",
            "--samples",
            str(samples),
            "--work-dir",
            str(iter_dir),
            "--rm-dir",
            str(rm_dir),
            "--skip-train",
            "--skip-pairs",
            "--score-batch",
            str(args.score_batch),
            "--max-length",
            str(args.max_length),
            "--dtype",
            args.dtype,
        ]
        if args.model.strip():
            odin_cmd.extend(["--model", args.model.strip()])
        _run(odin_cmd, dry_run=args.dry_run)
        phase_b = iter_dir / "export" / "phase_b_grpo.jsonl"
        if not args.dry_run and not phase_b.is_file():
            raise SystemExit(f"导出失败，找不到 {phase_b}")
    elif not args.dry_run and not phase_b.is_file():
        raise SystemExit(f"找不到 phase B: {phase_b}")

    rec_cmd: List[str] = [
        py,
        "-m",
        REC_MODULE,
        "--phase-b",
        str(phase_b),
        "--work-dir",
        str(train_work),
        "--skip-sft",
        "--grpo-rounds",
        str(max(1, int(args.grpo_rounds))),
        "--grpo-lr",
        str(args.grpo_lr),
        "--beta-kl",
        str(args.beta_kl),
        "--dtype",
        args.dtype,
        "--max-length",
        str(args.max_length),
        "--batch",
        str(args.batch),
        "--grad-accum",
        str(args.grad_accum),
    ]
    if args.grpo_epochs is not None:
        rec_cmd.extend(["--grpo-epochs", str(args.grpo_epochs)])
    if args.grpo_policy.strip():
        rec_cmd.extend(["--grpo-policy", args.grpo_policy.strip()])
    if args.system_prompt_file and args.system_prompt_file.is_file():
        rec_cmd.extend(["--system-prompt-file", str(args.system_prompt_file.resolve())])
    if args.dry_run:
        rec_cmd.append("--dry-run")
    _run(rec_cmd, dry_run=False)
    logger.info("后续短 GRPO 完成；验收见 %s/grpo/round_XX/accept.json", train_work)


if __name__ == "__main__":
    main()
