"""
推荐训练顺序（冷启动一次 + 多轮短 GRPO）：

1. **SFT 一次**（``train_sft.py``）：改写器基座 + ``phase_a_sft.jsonl`` → ``<work-dir>/sft/``。
2. **短 GRPO 多轮**（``train_grpo.py``）：每轮 epoch 默认 0.25；
   第 1 轮 policy = SFT，之后 policy = 上一轮 GRPO；
   **ref 始终冻在** ``grpo.hf-local-training.ref-model``（冷启动快照）。
   每轮写入 ``<work-dir>/grpo/round_XX/``，并写验收摘要。

双头 RM 不在本脚本内训练。后续若用新 K 路样本继续，走
``python -m training.run_next_grpo_round``（复用 RM、跳过 SFT）。

用法::

    python training/hf_grpo/run_recommended_training.py \\
      --phase-a training/runs/<run_id>/export/phase_a_sft.jsonl \\
      --phase-b training/runs/<run_id>/export/phase_b_grpo.jsonl \\
      --work-dir training/runs/<run_id>/hf_checkpoints
"""

from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from .model_load import DEFAULT_LORA_ALPHA, DEFAULT_LORA_R, lora_cli_args

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
SFT_MODULE = "training.hf_grpo.train_sft"
GRPO_MODULE = "training.hf_grpo.train_grpo"
LATEST_NAME = "latest.json"
ACCEPT_LOG_NAME = "accept_rounds.jsonl"


def _run(cmd: Sequence[str], *, dry_run: bool) -> None:
    logger.info("Run: %s", " ".join(cmd))
    if dry_run:
        return
    subprocess.run(list(cmd), cwd=str(REPO_ROOT), check=True)


def grpo_round_dir(grpo_root: Path, round_idx: int) -> Path:
    return Path(grpo_root) / f"round_{int(round_idx):02d}"


def load_latest(grpo_root: Path) -> Optional[Dict[str, Any]]:
    path = Path(grpo_root) / LATEST_NAME
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def write_latest(grpo_root: Path, *, round_idx: int, policy_dir: Path, ref_dir: str) -> Path:
    blob = {
        "round": int(round_idx),
        "policy_dir": str(Path(policy_dir).resolve()),
        "ref_dir": ref_dir,
    }
    out = Path(grpo_root) / LATEST_NAME
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(blob, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def resolve_grpo_start(
    *,
    skip_sft: bool,
    sft_out: Path,
    grpo_root: Path,
    grpo_policy: str,
    round_start: int,
) -> tuple[Path, int]:
    """
    返回 (本轮起始 policy 路径, 第一轮编号)。

    冷启动（做 SFT）：从 sft 目录、编号 1。
    续跑（跳过 SFT）：优先 ``--grpo-policy``，否则 ``grpo/latest.json``，否则已有 sft。
    """
    if not skip_sft:
        start = 1 if round_start < 1 else int(round_start)
        return sft_out, start

    if (grpo_policy or "").strip():
        policy = Path(grpo_policy.strip()).resolve()
        start = int(round_start) if round_start >= 1 else 1
        latest = load_latest(grpo_root)
        if round_start < 1 and latest and latest.get("round") is not None:
            start = int(latest["round"]) + 1
        return policy, start

    latest = load_latest(grpo_root)
    if latest and latest.get("policy_dir"):
        policy = Path(str(latest["policy_dir"]))
        start = int(latest.get("round") or 0) + 1
        if round_start >= 1:
            start = int(round_start)
        return policy, start

    if sft_out.is_dir():
        start = 1 if round_start < 1 else int(round_start)
        return sft_out.resolve(), start

    raise SystemExit(
        "跳过 SFT 时需要 --grpo-policy、已有 grpo/latest.json，或已有 sft/ 目录"
    )


def build_sft_cmd(
    *,
    py: str,
    phase_a: Path,
    model: str,
    sft_out: Path,
    args: argparse.Namespace,
) -> List[str]:
    sft_cmd: List[str] = [
        py,
        "-m",
        SFT_MODULE,
        "--jsonl",
        str(phase_a),
        "--model",
        model,
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
    sft_cmd.extend(
        lora_cli_args(
            lora_r=args.lora_r,
            lora_alpha=args.lora_alpha,
            full_finetune=args.full_finetune,
        )
    )
    return sft_cmd


def build_grpo_cmd(
    *,
    py: str,
    phase_b: Path,
    policy: Path,
    ref: str,
    out: Path,
    args: argparse.Namespace,
) -> List[str]:
    grpo_cmd: List[str] = [
        py,
        "-m",
        GRPO_MODULE,
        "--jsonl",
        str(phase_b),
        "--model",
        str(Path(policy).resolve()),
        "--ref-model",
        ref,
        "--out",
        str(out),
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
    grpo_cmd.extend(
        lora_cli_args(
            lora_r=args.lora_r,
            lora_alpha=args.lora_alpha,
            full_finetune=args.full_finetune,
        )
    )
    return grpo_cmd


def _write_round_accept(
    *,
    round_idx: int,
    out_dir: Path,
    ref: str,
    sft_out: Path,
    phase_b: Path,
    epochs: float,
) -> None:
    from training.accept_report import (
        build_round_accept,
        summarize_jsonl,
        write_json,
    )

    blob = build_round_accept(
        round_idx=round_idx,
        policy_dir=out_dir,
        ref_dir=ref,
        epochs=epochs,
        data_summary=summarize_jsonl(phase_b),
        sft_dir=sft_out if sft_out.is_dir() else None,
    )
    write_json(out_dir / "accept.json", blob)
    log_path = out_dir.parent / ACCEPT_LOG_NAME
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(blob, ensure_ascii=False) + "\n")
    logger.info("验收摘要 round=%s → %s", round_idx, out_dir / "accept.json")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    p = argparse.ArgumentParser(
        description="冷启动只 SFT 一次，随后多轮短 GRPO（ref 冻结）；每轮写验收摘要。双头 RM 不在此重训。",
    )
    p.add_argument("--phase-a", type=Path, default=None, help="phase_a_sft.jsonl（做 SFT 时必填）")
    p.add_argument("--phase-b", type=Path, required=True, help="phase_b_grpo.jsonl")
    p.add_argument(
        "--work-dir",
        type=Path,
        required=True,
        help="工作目录；sft/ 只写一次，grpo/round_XX/ 每轮一份",
    )
    p.add_argument(
        "--base-model",
        type=str,
        default="",
        help="SFT 起点；空则读 grpo.hf-local-training.model（改写器）",
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

    p.add_argument(
        "--grpo-rounds",
        type=int,
        default=None,
        help="短 GRPO 轮数；空则读 yaml grpo-rounds（缺省 4）",
    )
    p.add_argument(
        "--grpo-epochs",
        type=float,
        default=None,
        help="每一轮的 epoch；空则读 yaml grpo-epochs-per-round（缺省 0.25）",
    )
    p.add_argument("--grpo-lr", type=float, default=1e-6)
    p.add_argument("--beta-kl", type=float, default=0.04)
    p.add_argument(
        "--grpo-policy",
        type=str,
        default="",
        help="跳过 SFT 时的起始 policy（续跑上一轮 GRPO 目录）",
    )
    p.add_argument(
        "--grpo-round-start",
        type=int,
        default=0,
        help="第一轮编号；0 表示冷启动从 1，续跑则 latest.round+1",
    )
    p.add_argument(
        "--system-prompt-file",
        type=Path,
        default=None,
        help="仅 GRPO：可选 system 文本文件路径",
    )

    p.add_argument("--lora-r", type=int, default=DEFAULT_LORA_R)
    p.add_argument("--lora-alpha", type=int, default=DEFAULT_LORA_ALPHA)
    p.add_argument(
        "--full-finetune",
        action="store_true",
        help="7B 全参。24G 会 OOM，仅大显存使用。",
    )
    p.add_argument("--skip-sft", action="store_true", help="跳过 SFT（冷启动已完成时）")
    p.add_argument("--skip-grpo", action="store_true", help="只跑到 SFT 结束")
    p.add_argument("--dry-run", action="store_true", help="只打印命令不执行")

    args = p.parse_args()

    try:
        from plugins.text_description_evaluator.design_text_evaluator_api import (
            default_hf_grpo_epochs_per_round,
            default_hf_grpo_rounds,
            default_hf_local_grpo_model,
            default_hf_local_grpo_ref_model,
        )
    except Exception as exc:  # noqa: BLE001
        raise SystemExit(
            "无法导入 default_hf_local_grpo_model，请在仓库根目录执行本脚本"
        ) from exc

    if args.grpo_rounds is None:
        args.grpo_rounds = default_hf_grpo_rounds()
    if args.grpo_epochs is None:
        args.grpo_epochs = default_hf_grpo_epochs_per_round()
    if args.grpo_rounds < 1:
        raise SystemExit("grpo-rounds 必须 >= 1")

    base = (args.base_model or "").strip() or default_hf_local_grpo_model()
    ref = default_hf_local_grpo_ref_model()
    work = args.work_dir.resolve()
    sft_out = work / "sft"
    grpo_root = work / "grpo"

    phase_b = args.phase_b.resolve()
    if not args.skip_grpo and not phase_b.is_file():
        raise SystemExit(f"找不到 phase B: {phase_b}")

    py = sys.executable

    if not args.skip_sft:
        if args.phase_a is None:
            raise SystemExit("做 SFT 时需要 --phase-a")
        phase_a = args.phase_a.resolve()
        if not phase_a.is_file():
            raise SystemExit(f"找不到 phase A: {phase_a}")
        sft_cmd = build_sft_cmd(
            py=py, phase_a=phase_a, model=base, sft_out=sft_out, args=args
        )
        _run(sft_cmd, dry_run=args.dry_run)

    if args.skip_grpo:
        logger.info("已跳过 GRPO（--skip-grpo）；SFT → %s", sft_out)
        return

    policy, round_idx = resolve_grpo_start(
        skip_sft=args.skip_sft,
        sft_out=sft_out,
        grpo_root=grpo_root,
        grpo_policy=args.grpo_policy,
        round_start=args.grpo_round_start,
    )
    if args.skip_sft and not args.dry_run and not policy.exists():
        raise SystemExit(f"起始 policy 不存在: {policy}")

    last_out = policy
    for i in range(int(args.grpo_rounds)):
        this_round = round_idx + i
        out_dir = grpo_round_dir(grpo_root, this_round)
        cmd = build_grpo_cmd(
            py=py,
            phase_b=phase_b,
            policy=last_out,
            ref=ref,
            out=out_dir,
            args=args,
        )
        logger.info(
            "短 GRPO round=%s policy=%s → %s epochs=%s ref=%s",
            this_round,
            last_out,
            out_dir,
            args.grpo_epochs,
            ref,
        )
        _run(cmd, dry_run=args.dry_run)
        if not args.dry_run:
            write_latest(grpo_root, round_idx=this_round, policy_dir=out_dir, ref_dir=ref)
            _write_round_accept(
                round_idx=this_round,
                out_dir=out_dir,
                ref=ref,
                sft_out=sft_out,
                phase_b=phase_b,
                epochs=float(args.grpo_epochs),
            )
        last_out = out_dir

    logger.info(
        "完成：SFT 一次 → %s ；短 GRPO %s 轮，最新 policy → %s",
        sft_out,
        args.grpo_rounds,
        last_out,
    )


if __name__ == "__main__":
    main()
