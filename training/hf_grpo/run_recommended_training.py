"""
推荐训练顺序（编排执行）：

1. **SFT**（``train_sft.py``）：基座模型 + ``phase_a_sft.jsonl`` → 写入 ``<work-dir>/sft/``。
2. **GRPO**（``train_grpo.py``）：**policy** = 上一步 SFT 目录，**ref** = 与 SFT 相同的**基座**（KL 锚点），数据 ``phase_b_grpo.jsonl`` → 写入 ``<work-dir>/grpo/``。

SFT 默认启用 **训练 loss（EMA）平台早停**（见 ``train_sft.py``），满足「连续若干次 log 未显著下降」则结束 SFT 并开始 GRPO；可用 ``--sft-no-early-stop`` 关闭。

用法（在仓库根目录执行）::

    python training/hf_grpo/run_recommended_training.py \\
      --phase-a training/runs/<run_id>/export/phase_a_sft.jsonl \\
      --phase-b training/runs/<run_id>/export/phase_b_grpo.jsonl \\
      --work-dir training/runs/<run_id>/hf_checkpoints
"""

from __future__ import annotations

import argparse
import logging
import subprocess
import sys
from pathlib import Path
from typing import List, Sequence

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[2]
SFT_SCRIPT = REPO_ROOT / "training" / "hf_grpo" / "train_sft.py"
GRPO_SCRIPT = REPO_ROOT / "training" / "hf_grpo" / "train_grpo.py"


def _run(cmd: Sequence[str], *, dry_run: bool) -> None:
    logger.info("Run: %s", " ".join(cmd))
    if dry_run:
        return
    subprocess.run(list(cmd), cwd=str(REPO_ROOT), check=True)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    p = argparse.ArgumentParser(
        description="按推荐顺序执行 SFT → GRPO（policy=SFT 输出，ref=基座）",
    )
    p.add_argument("--phase-a", type=Path, required=True, help="phase_a_sft.jsonl")
    p.add_argument("--phase-b", type=Path, required=True, help="phase_b_grpo.jsonl")
    p.add_argument(
        "--work-dir",
        type=Path,
        required=True,
        help="工作目录；将创建子目录 sft/ 与 grpo/",
    )
    p.add_argument(
        "--base-model",
        type=str,
        default="",
        help="基座 HF id 或路径（SFT 起点 + GRPO 的 ref）；空则读 fashion_config → grpo.hf-local-training.model",
    )
    p.add_argument("--dtype", choices=["bf16", "fp16", "fp32"], default="bf16")
    p.add_argument("--max-length", type=int, default=2048)
    p.add_argument("--batch", type=int, default=1)
    p.add_argument("--grad-accum", type=int, default=8)

    p.add_argument("--sft-epochs", type=float, default=1.0)
    p.add_argument("--sft-lr", type=float, default=2e-5)
    p.add_argument("--sft-logging-steps", type=int, default=10)
    p.add_argument(
        "--sft-no-early-stop",
        action="store_true",
        help="SFT 不启用训练 loss 平台早停（跑满 sft-epochs）",
    )
    p.add_argument("--sft-early-stop-patience", type=int, default=6)
    p.add_argument("--sft-early-stop-rel-delta", type=float, default=0.005)
    p.add_argument("--sft-early-stop-abs-delta", type=float, default=1e-4)
    p.add_argument("--sft-early-stop-min-steps", type=int, default=100)
    p.add_argument("--sft-early-stop-ema-decay", type=float, default=0.92)

    p.add_argument("--grpo-epochs", type=float, default=1.0)
    p.add_argument("--grpo-lr", type=float, default=1e-6)
    p.add_argument("--beta-kl", type=float, default=0.04)
    p.add_argument(
        "--system-prompt-file",
        type=Path,
        default=None,
        help="仅 GRPO：可选 system 文本文件路径",
    )

    p.add_argument("--skip-sft", action="store_true", help="跳过 SFT（要求已有 SFT 目录）")
    p.add_argument("--skip-grpo", action="store_true", help="只跑到 SFT 结束")
    p.add_argument("--dry-run", action="store_true", help="只打印命令不执行")

    args = p.parse_args()

    if not SFT_SCRIPT.is_file() or not GRPO_SCRIPT.is_file():
        raise SystemExit(f"脚本缺失: {SFT_SCRIPT} 或 {GRPO_SCRIPT}")

    try:
        from plugins.text_description_evaluator.design_text_evaluator_api import (
            default_hf_local_grpo_model,
        )
    except Exception as exc:  # noqa: BLE001
        raise SystemExit(
            "无法导入 default_hf_local_grpo_model，请在仓库根目录执行本脚本"
        ) from exc

    base = (args.base_model or "").strip() or default_hf_local_grpo_model()
    work = args.work_dir.resolve()
    sft_out = work / "sft"
    grpo_out = work / "grpo"

    phase_a = args.phase_a.resolve()
    phase_b = args.phase_b.resolve()
    if not phase_a.is_file():
        raise SystemExit(f"找不到 phase A: {phase_a}")
    if not args.skip_grpo and not phase_b.is_file():
        raise SystemExit(f"找不到 phase B: {phase_b}")

    py = sys.executable

    if not args.skip_sft:
        sft_cmd: List[str] = [
            py,
            str(SFT_SCRIPT),
            "--jsonl",
            str(phase_a),
            "--model",
            base,
            "--out",
            str(sft_out),
            "--max-length",
            str(args.max_length),
            "--epochs",
            str(args.sft_epochs),
            "--lr",
            str(args.sft_lr),
            "--batch",
            str(args.batch),
            "--grad-accum",
            str(args.grad_accum),
            "--dtype",
            args.dtype,
            "--logging-steps",
            str(args.sft_logging_steps),
        ]
        if args.sft_no_early_stop:
            sft_cmd.append("--no-early-stop")
        else:
            sft_cmd.extend(
                [
                    "--early-stop-patience",
                    str(args.sft_early_stop_patience),
                    "--early-stop-rel-delta",
                    str(args.sft_early_stop_rel_delta),
                    "--early-stop-abs-delta",
                    str(args.sft_early_stop_abs_delta),
                    "--early-stop-min-steps",
                    str(args.sft_early_stop_min_steps),
                    "--early-stop-ema-decay",
                    str(args.sft_early_stop_ema_decay),
                ]
            )
        _run(sft_cmd, dry_run=args.dry_run)
    elif not args.dry_run and not sft_out.is_dir():
        raise SystemExit(f"--skip-sft 但不存在 SFT 目录: {sft_out}")

    if args.skip_grpo:
        logger.info("已跳过 GRPO（--skip-grpo）")
        return

    grpo_cmd: List[str] = [
        py,
        str(GRPO_SCRIPT),
        "--jsonl",
        str(phase_b),
        "--model",
        str(sft_out.resolve()),
        "--ref-model",
        base,
        "--out",
        str(grpo_out),
        "--max-length",
        str(args.max_length),
        "--epochs",
        str(args.grpo_epochs),
        "--lr",
        str(args.grpo_lr),
        "--batch",
        str(args.batch),
        "--grad-accum",
        str(args.grad_accum),
        "--beta-kl",
        str(args.beta_kl),
        "--dtype",
        args.dtype,
    ]
    if args.system_prompt_file and args.system_prompt_file.is_file():
        grpo_cmd.extend(["--system-prompt-file", str(args.system_prompt_file.resolve())])

    _run(grpo_cmd, dry_run=args.dry_run)
    logger.info("完成：SFT → %s ，GRPO policy → %s", sft_out, grpo_out)


if __name__ == "__main__":
    main()
