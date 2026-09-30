"""
冷启动之后的在线轮：不再 SFT。

每一轮外循环：

1. 把当前 policy 的 LoRA merge 后导入改写器，只重启 8001。
2. 用这份权重重新 K 路采样（条数读 yaml，现为 8）。
3. 冻结的冷启动双头 RM 打 ``r_Q``，导出新的 phase_b。
4. 只做 1 个 epoch 的短 GRPO，policy 接上一轮，KL 仍锚在初始改写器。
5. 再导入这一轮的新权重，供下一轮采样。验收里的 ``score_lift`` 记质量轴和总分提升。

用法（仓库根目录，训练卡用空闲 GPU，例如 2）::

    CUDA_VISIBLE_DEVICES=2 python -m training.run_next_grpo_round \\
      --run-id grpo_theme_2026-09-29

已有 samples、只打分再训时仍可用 ``--samples`` / ``--phase-b``。
"""

from __future__ import annotations

import argparse
import logging
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Sequence

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[1]
REC_MODULE = "training.hf_grpo.run_recommended_training"
DEFAULT_CORPUS = (
    REPO_ROOT
    / "fashion_research_dir"
    / "k_rewrite_instructions_2026-09-29"
    / "source_corpus.jsonl"
)


def _run(cmd: Sequence[str], *, dry_run: bool) -> None:
    logger.info("Run: %s", " ".join(cmd))
    if dry_run:
        return
    subprocess.run(list(cmd), cwd=str(REPO_ROOT), check=True)


def _latest_policy(train_work: Path) -> tuple[int, Path]:
    from training.hf_grpo.run_recommended_training import load_latest

    latest = load_latest(train_work / "grpo")
    if not latest or not latest.get("policy_dir"):
        raise SystemExit(
            f"找不到 {train_work / 'grpo' / 'latest.json'}。先完成冷启动（含一轮 GRPO），再跑在线轮。"
        )
    policy = Path(str(latest["policy_dir"])).resolve()
    if not policy.is_dir():
        raise SystemExit(f"latest.json 的 policy 不存在: {policy}")
    return int(latest.get("round") or 0), policy


def import_latest_weights(
    *,
    run_id: str,
    train_work: Path,
    dtype: str,
    vllm_gpu: str,
    restart: bool,
    dry_run: bool,
    skip_if_same: bool = False,
    merged: Optional[Path] = None,
) -> Optional[Path]:
    """Merge 当前 latest policy，把 rewriter-llm 指过去。默认只重启 8001。"""
    from training.hf_grpo.manage_rewriter import (
        default_merged_dir,
        read_applied_adapter,
        write_applied_adapter,
    )

    try:
        round_idx, policy = _latest_policy(train_work)
    except SystemExit:
        if dry_run:
            logger.info("dry-run：尚无 latest.json，跳过权重导入")
            return None
        raise
    merged = Path(merged) if merged is not None else default_merged_dir(run_id)
    if skip_if_same and read_applied_adapter(merged) == str(policy):
        logger.info("改写器已是 round_%02d 的权重，采样前不再重启: %s", round_idx, policy)
        return merged

    py = sys.executable
    cmd: List[str] = [
        py,
        "-m",
        "training.hf_grpo.manage_rewriter",
        "apply",
        "--run-id",
        run_id,
        "--adapter",
        str(policy),
        "--merged",
        str(merged),
        "--force-remerge",
        "--dtype",
        dtype,
        "--vllm-gpu",
        str(vllm_gpu),
    ]
    if restart:
        cmd.append("--restart")
    logger.info("导入 round_%02d 权重 → %s", round_idx, merged)
    _run(cmd, dry_run=dry_run)
    if not dry_run:
        write_applied_adapter(merged, policy)
    return merged


def build_collect_cmd(
    *,
    py: str,
    corpus: Path,
    collect_run_id: str,
    system_prompt_file: Optional[Path],
) -> List[str]:
    cmd = [
        py,
        "-m",
        "training.collect_k_rewrite_samples",
        "--corpus",
        str(corpus),
        "--run-id",
        collect_run_id,
        "--no-resume",
    ]
    if system_prompt_file and system_prompt_file.is_file():
        cmd.extend(["--system-prompt-file", str(system_prompt_file.resolve())])
    return cmd


def build_score_cmd(
    *,
    py: str,
    samples: Path,
    iter_dir: Path,
    rm_dir: Path,
    score_batch: int,
    max_length: int,
    dtype: str,
    model: str,
) -> List[str]:
    cmd = [
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
        str(score_batch),
        "--max-length",
        str(max_length),
        "--dtype",
        dtype,
    ]
    if model.strip():
        cmd.extend(["--model", model.strip()])
    return cmd


def build_grpo_cmd(
    *,
    py: str,
    phase_b: Path,
    train_work: Path,
    grpo_epochs: Optional[float],
    grpo_lr: float,
    beta_kl: float,
    dtype: str,
    max_length: int,
    batch: int,
    grad_accum: int,
    grpo_policy: str,
    system_prompt_file: Optional[Path],
    dry_run: bool,
) -> List[str]:
    cmd: List[str] = [
        py,
        "-m",
        REC_MODULE,
        "--phase-b",
        str(phase_b),
        "--work-dir",
        str(train_work),
        "--skip-sft",
        "--grpo-rounds",
        "1",
        "--grpo-lr",
        str(grpo_lr),
        "--beta-kl",
        str(beta_kl),
        "--dtype",
        dtype,
        "--max-length",
        str(max_length),
        "--batch",
        str(batch),
        "--grad-accum",
        str(grad_accum),
    ]
    if grpo_epochs is not None:
        cmd.extend(["--grpo-epochs", str(grpo_epochs)])
    if grpo_policy.strip():
        cmd.extend(["--grpo-policy", grpo_policy.strip()])
    if system_prompt_file and system_prompt_file.is_file():
        cmd.extend(["--system-prompt-file", str(system_prompt_file.resolve())])
    if dry_run:
        cmd.append("--dry-run")
    return cmd


def _paths_for_run(run_id: str, train_work: Optional[Path], rm_dir: Optional[Path]) -> tuple[Path, Path]:
    run_root = REPO_ROOT / "training" / "runs" / run_id
    work = (train_work or (run_root / "hf_checkpoints")).resolve()
    rm = (rm_dir or (run_root / "odin_rm" / "rm")).resolve()
    return work, rm


def run_online_rounds(args: argparse.Namespace) -> None:
    """采样 → 冻结 RM 打分 → 一轮 GRPO → 导入新权重。不做 SFT。"""
    train_work, rm_dir = _paths_for_run(args.run_id, args.train_work_dir, args.rm_dir)
    if not args.dry_run and not (rm_dir / "odin_heads.pt").is_file():
        raise SystemExit(f"找不到冷启动 RM: {rm_dir / 'odin_heads.pt'}")
    corpus = (args.corpus or DEFAULT_CORPUS).resolve()
    if not args.dry_run and not corpus.is_file():
        raise SystemExit(f"找不到语料: {corpus}")

    py = sys.executable
    outer = max(1, int(args.outer_rounds))
    for _ in range(outer):
        if not args.no_apply_weights:
            import_latest_weights(
                run_id=args.run_id,
                train_work=train_work,
                dtype=args.dtype,
                vllm_gpu=args.vllm_gpu,
                restart=not args.no_restart,
                dry_run=args.dry_run,
                skip_if_same=True,
            )
        done_round, _policy = _latest_policy(train_work)
        next_round = done_round + 1
        collect_run_id = f"{args.run_id}/online/round_{next_round:02d}"
        samples = REPO_ROOT / "training" / "runs" / collect_run_id / "samples.jsonl"
        iter_dir = train_work.parent / "grpo_iter" / f"round_{next_round:02d}"
        logger.info("在线轮 round_%02d：用当前改写器重新采样 → %s", next_round, samples)
        _run(
            build_collect_cmd(
                py=py,
                corpus=corpus,
                collect_run_id=collect_run_id,
                system_prompt_file=args.system_prompt_file,
            ),
            dry_run=args.dry_run,
        )
        if not args.dry_run and not samples.is_file():
            raise SystemExit(f"采样未写出: {samples}")
        logger.info("冻结 RM 打 r_Q → %s", iter_dir)
        _run(
            build_score_cmd(
                py=py,
                samples=samples,
                iter_dir=iter_dir,
                rm_dir=rm_dir,
                score_batch=args.score_batch,
                max_length=args.max_length,
                dtype=args.dtype,
                model=args.model,
            ),
            dry_run=args.dry_run,
        )
        phase_b = iter_dir / "export" / "phase_b_grpo.jsonl"
        if not args.dry_run and not phase_b.is_file():
            raise SystemExit(f"导出失败，找不到 {phase_b}")
        logger.info("一轮 GRPO（跳过 SFT） phase_b=%s", phase_b)
        _run(
            build_grpo_cmd(
                py=py,
                phase_b=phase_b,
                train_work=train_work,
                grpo_epochs=args.grpo_epochs,
                grpo_lr=args.grpo_lr,
                beta_kl=args.beta_kl,
                dtype=args.dtype,
                max_length=args.max_length,
                batch=args.batch,
                grad_accum=args.grad_accum,
                grpo_policy=args.grpo_policy,
                system_prompt_file=args.system_prompt_file,
                dry_run=args.dry_run,
            ),
            dry_run=False,
        )
        if not args.no_apply_weights:
            logger.info("本轮 GRPO 完成，导入新权重")
            import_latest_weights(
                run_id=args.run_id,
                train_work=train_work,
                dtype=args.dtype,
                vllm_gpu=args.vllm_gpu,
                restart=not args.no_restart,
                dry_run=args.dry_run,
                skip_if_same=False,
            )
        logger.info(
            "round_%02d 结束。质量轴和总分提升见 %s",
            next_round,
            train_work / "grpo" / f"round_{next_round:02d}" / "accept.json",
        )


def run_prepared_round(args: argparse.Namespace) -> None:
    """已有 phase_b 或 samples 时：打分（如需要）→ 一轮 GRPO → 导入权重。不做 SFT。"""
    if args.train_work_dir is None:
        if not args.run_id:
            raise SystemExit("需要 --train-work-dir，或 --run-id")
        train_work, default_rm = _paths_for_run(args.run_id, None, args.rm_dir)
    else:
        train_work = args.train_work_dir.resolve()
        default_rm = args.rm_dir.resolve() if args.rm_dir else None

    py = sys.executable
    phase_b = args.phase_b.resolve() if args.phase_b else None
    if phase_b is None:
        if args.samples is None or (args.rm_dir is None and default_rm is None):
            raise SystemExit("未给 --phase-b 时必须同时提供 --samples 与 --rm-dir（或 --run-id）")
        samples = args.samples.resolve()
        rm_dir = (args.rm_dir or default_rm).resolve()
        if not args.dry_run and not samples.is_file():
            raise SystemExit(f"找不到 samples: {samples}")
        if not args.dry_run and not (rm_dir / "odin_heads.pt").is_file():
            raise SystemExit(f"找不到冷启动 RM: {rm_dir / 'odin_heads.pt'}")
        from training.hf_grpo.run_recommended_training import load_latest

        latest = load_latest(train_work / "grpo")
        n = int((latest or {}).get("round") or 0) + 1
        iter_dir = (
            args.iter_dir.resolve()
            if args.iter_dir
            else (train_work.parent / "grpo_iter" / f"round_{n:02d}")
        )
        _run(
            build_score_cmd(
                py=py,
                samples=samples,
                iter_dir=iter_dir,
                rm_dir=rm_dir,
                score_batch=args.score_batch,
                max_length=args.max_length,
                dtype=args.dtype,
                model=args.model,
            ),
            dry_run=args.dry_run,
        )
        phase_b = iter_dir / "export" / "phase_b_grpo.jsonl"
        if not args.dry_run and not phase_b.is_file():
            raise SystemExit(f"导出失败，找不到 {phase_b}")
    elif not args.dry_run and not phase_b.is_file():
        raise SystemExit(f"找不到 phase B: {phase_b}")

    _run(
        build_grpo_cmd(
            py=py,
            phase_b=phase_b,
            train_work=train_work,
            grpo_epochs=args.grpo_epochs,
            grpo_lr=args.grpo_lr,
            beta_kl=args.beta_kl,
            dtype=args.dtype,
            max_length=args.max_length,
            batch=args.batch,
            grad_accum=args.grad_accum,
            grpo_policy=args.grpo_policy,
            system_prompt_file=args.system_prompt_file,
            dry_run=args.dry_run,
        ),
        dry_run=False,
    )
    if args.run_id and not args.no_apply_weights:
        import_latest_weights(
            run_id=args.run_id,
            train_work=train_work,
            dtype=args.dtype,
            vllm_gpu=args.vllm_gpu,
            restart=not args.no_restart,
            dry_run=args.dry_run,
            skip_if_same=False,
        )
    logger.info("短 GRPO 完成；验收见 %s/grpo/round_XX/accept.json", train_work)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    p = argparse.ArgumentParser(
        description="在线轮：导入权重、重新采样、冻结 RM 打分、一轮 GRPO、再导入。不做 SFT。",
    )
    p.add_argument("--run-id", default="", help="冷启动 run-id，例如 grpo_theme_2026-09-29")
    p.add_argument("--outer-rounds", type=int, default=1, help="外循环次数，每轮重新采样后再 GRPO，默认 1")
    p.add_argument("--corpus", type=Path, default=None, help="原文 jsonl；空则用 2026-09-29 语料")
    p.add_argument("--phase-b", type=Path, default=None, help="已导出的 phase_b；给出则不再采样")
    p.add_argument("--samples", type=Path, default=None, help="已有 samples.jsonl；给出则不再采样，只打分再训")
    p.add_argument("--rm-dir", type=Path, default=None, help="冷启动双头 RM；空则 training/runs/<run-id>/odin_rm/rm")
    p.add_argument("--iter-dir", type=Path, default=None, help="已有 samples 时的打分目录")
    p.add_argument("--train-work-dir", type=Path, default=None, help="hf_checkpoints；空则 training/runs/<run-id>/hf_checkpoints")
    p.add_argument("--grpo-policy", default="", help="起始 policy；空则读 grpo/latest.json")
    p.add_argument("--grpo-epochs", type=float, default=None, help="本轮 epoch；空则 yaml，缺省 1")
    p.add_argument("--grpo-lr", type=float, default=1e-6)
    p.add_argument("--beta-kl", type=float, default=0.001)
    p.add_argument("--dtype", choices=["bf16", "fp16", "fp32"], default="bf16")
    p.add_argument("--max-length", type=int, default=2048)
    p.add_argument("--batch", type=int, default=1)
    p.add_argument("--grad-accum", type=int, default=8)
    p.add_argument("--score-batch", type=int, default=1)
    p.add_argument("--model", default="", help="RM backbone 覆盖")
    p.add_argument("--system-prompt-file", type=Path, default=None)
    p.add_argument("--no-apply-weights", action="store_true", help="不 merge、不改 rewriter-llm")
    p.add_argument("--no-restart", action="store_true", help="导入时只改 yaml，不重启 8001")
    p.add_argument("--vllm-gpu", default="1", help="改写器 GPU，默认 1")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    prepared = args.phase_b is not None or args.samples is not None
    if prepared:
        run_prepared_round(args)
        return
    if not args.run_id:
        raise SystemExit("在线轮需要 --run-id。已有样本时改用 --samples 或 --phase-b。")
    run_online_rounds(args)


if __name__ == "__main__":
    main()
