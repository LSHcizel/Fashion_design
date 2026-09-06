"""
冷启动第 2、3 步：训双头 RM 并导出 phase_a/b，再 SFT 一次 + 多轮短 GRPO。

采数（第 1 步）需已写出 samples.jsonl。默认路径与
``collect_k_rewrite_samples.py --run-id`` 对齐。

用法（仓库根目录）::

    python -m training.run_coldstart_train --run-id grpo_chanel_inverse_v1
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
REC_SCRIPT = REPO_ROOT / "training" / "hf_grpo" / "run_recommended_training.py"


def _run(cmd: Sequence[str], *, dry_run: bool) -> None:
    logger.info("Run: %s", " ".join(cmd))
    if dry_run:
        return
    subprocess.run(list(cmd), cwd=str(REPO_ROOT), check=True)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    p = argparse.ArgumentParser(
        description="冷启动：双头 RM（一次）→ SFT（一次）→ 多轮短 GRPO",
    )
    p.add_argument(
        "--run-id",
        type=str,
        default="grpo_chanel_inverse_v1",
        help="与采数 --run-id 相同；默认在 training/runs/<run-id>/ 下找 samples、写 odin_rm 与 hf_checkpoints",
    )
    p.add_argument(
        "--samples",
        type=Path,
        default=None,
        help="K 路 samples.jsonl；空则 training/runs/<run-id>/samples.jsonl",
    )
    p.add_argument(
        "--odin-work-dir",
        type=Path,
        default=None,
        help="双头 RM 工作目录；空则 training/runs/<run-id>/odin_rm",
    )
    p.add_argument(
        "--train-work-dir",
        type=Path,
        default=None,
        help="SFT/GRPO 目录；空则 training/runs/<run-id>/hf_checkpoints",
    )
    p.add_argument("--dtype", choices=["bf16", "fp16", "fp32"], default="bf16")
    p.add_argument("--max-length", type=int, default=2048)
    p.add_argument("--score-batch", type=int, default=1)
    p.add_argument("--rm-epochs", type=float, default=3.0)
    p.add_argument("--rm-batch", type=int, default=8)
    p.add_argument("--batch", type=int, default=1)
    p.add_argument("--grad-accum", type=int, default=8)
    p.add_argument("--grpo-rounds", type=int, default=None)
    p.add_argument("--grpo-epochs", type=float, default=None)
    p.add_argument("--grpo-lr", type=float, default=1e-6)
    p.add_argument("--beta-kl", type=float, default=0.04)
    p.add_argument("--sft-epochs", type=float, default=1.0)
    p.add_argument("--sft-no-early-stop", action="store_true")
    p.add_argument("--system-prompt-file", type=Path, default=None)
    p.add_argument("--skip-rm", action="store_true", help="已有 odin export 时跳过第 2 步")
    p.add_argument("--skip-sft", action="store_true", help="只跑第 2 步，或第 3 步跳过 SFT")
    p.add_argument("--skip-grpo", action="store_true", help="第 3 步只 SFT")
    p.add_argument("--stop-after-rm", action="store_true", help="只做第 2 步")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    run_root = REPO_ROOT / "training" / "runs" / args.run_id
    samples = (args.samples or (run_root / "samples.jsonl")).resolve()
    odin_work = (args.odin_work_dir or (run_root / "odin_rm")).resolve()
    train_work = (args.train_work_dir or (run_root / "hf_checkpoints")).resolve()
    export_dir = odin_work / "export"
    phase_a = export_dir / "phase_a_sft.jsonl"
    phase_b = export_dir / "phase_b_grpo.jsonl"
    py = sys.executable

    if not args.skip_rm:
        if not args.dry_run and not samples.is_file():
            raise SystemExit(f"找不到 samples（请先完成第 1 步采数）: {samples}")
        odin_cmd: List[str] = [
            py,
            "-m",
            "training.odin_rm.run_pipeline",
            "--samples",
            str(samples),
            "--work-dir",
            str(odin_work),
            "--dtype",
            args.dtype,
            "--max-length",
            str(args.max_length),
            "--score-batch",
            str(args.score_batch),
            "--rm-epochs",
            str(args.rm_epochs),
            "--rm-batch",
            str(args.rm_batch),
        ]
        logger.info("第 2 步：双头 RM → %s", odin_work)
        _run(odin_cmd, dry_run=args.dry_run)
        if not args.dry_run and not (phase_a.is_file() and phase_b.is_file()):
            raise SystemExit(f"第 2 步未写出 phase_a/b: {export_dir}")

    if args.stop_after_rm:
        logger.info("已按 --stop-after-rm 结束；export=%s", export_dir)
        return

    if not args.dry_run and not phase_b.is_file():
        raise SystemExit(f"找不到 phase_b（需先完成第 2 步）: {phase_b}")
    if not args.skip_sft and not args.dry_run and not phase_a.is_file():
        raise SystemExit(f"找不到 phase_a（做 SFT 需要）: {phase_a}")

    rec_cmd: List[str] = [
        py,
        str(REC_SCRIPT),
        "--phase-b",
        str(phase_b),
        "--work-dir",
        str(train_work),
        "--dtype",
        args.dtype,
        "--max-length",
        str(args.max_length),
        "--batch",
        str(args.batch),
        "--grad-accum",
        str(args.grad_accum),
        "--sft-epochs",
        str(args.sft_epochs),
        "--grpo-lr",
        str(args.grpo_lr),
        "--beta-kl",
        str(args.beta_kl),
    ]
    if not args.skip_sft:
        rec_cmd.extend(["--phase-a", str(phase_a)])
    else:
        rec_cmd.append("--skip-sft")
    if args.skip_grpo:
        rec_cmd.append("--skip-grpo")
    if args.sft_no_early_stop:
        rec_cmd.append("--sft-no-early-stop")
    if args.grpo_rounds is not None:
        rec_cmd.extend(["--grpo-rounds", str(args.grpo_rounds)])
    if args.grpo_epochs is not None:
        rec_cmd.extend(["--grpo-epochs", str(args.grpo_epochs)])
    if args.system_prompt_file and args.system_prompt_file.is_file():
        rec_cmd.extend(["--system-prompt-file", str(args.system_prompt_file.resolve())])
    if args.dry_run:
        rec_cmd.append("--dry-run")

    logger.info("第 3 步：SFT + 短 GRPO → %s", train_work)
    _run(rec_cmd, dry_run=False)
    logger.info(
        "冷启动完成。RM=%s  改写器=%s  后续外循环: python -m training.run_next_grpo_round",
        odin_work / "rm",
        train_work / "grpo",
    )


if __name__ == "__main__":
    main()
