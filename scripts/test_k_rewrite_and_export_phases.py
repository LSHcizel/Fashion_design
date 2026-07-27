#!/usr/bin/env python3
"""
端到端烟测：对一段输入 description 做一轮并行 K 改写 + spec 评判，
写入 samples.jsonl，并导出 phase_a_sft.jsonl / phase_b_grpo.jsonl。

依赖：``fashion_config.yaml``（local-llm / grpo.*）；K 路改写与候选评判均走本地 vLLM（若已启用）。

在仓库根目录执行::

    python scripts/test_k_rewrite_and_export_phases.py --description \"Your text...\"
    python scripts/test_k_rewrite_and_export_phases.py --description-file path/to/look.txt
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from plugins.parallel_k_rewrite import generate_k_parallel_rewrites  # noqa: E402
from training.grpo_pipeline import (  # noqa: E402
    default_grpo_export_dir,
    default_include_for_training,
    export_two_phase_from_samples,
)
from training.jsonl_logger import TrainingRunLogger  # noqa: E402

logger = logging.getLogger(__name__)


def _load_description(args: argparse.Namespace) -> str:
    if args.description_file:
        p = Path(args.description_file).resolve()
        if not p.is_file():
            raise SystemExit(f"找不到文件: {p}")
        return p.read_text(encoding="utf-8").strip()
    if args.description:
        return args.description.strip()
    raise SystemExit("请提供 --description 或 --description-file")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    p = argparse.ArgumentParser(
        description="K 路并行改写 + 评判 + 导出阶段 A/B JSONL（烟测）",
    )
    p.add_argument("--description", "-d", default="", help="待改写的正文（英文/原文）")
    p.add_argument("--description-file", "-f", type=Path, default=None, help="从文件读取正文")
    p.add_argument(
        "--business-context",
        default="",
        help="可选：与各候选共享的业务/约束说明（写入 context.business_context）",
    )
    p.add_argument(
        "--k",
        type=int,
        default=None,
        help="并行候选数；默认读 fashion_config → grpo.parallel-k-rewrite.k（缺省 10）",
    )
    p.add_argument(
        "--run-id",
        default="",
        help="运行 id；默认 test_k_<UTC时间>_<短uuid>",
    )
    p.add_argument(
        "--export-dir",
        type=Path,
        default=None,
        help="阶段 A/B 输出目录；默认 training/runs/<run_id>/export",
    )
    p.add_argument(
        "--strict-training-filter",
        action="store_true",
        help="导出时仅保留 training_filter.include_in_training（与正式 GRPO 管线一致）",
    )
    p.add_argument(
        "--reward-key",
        choices=["R_content", "total_score"],
        default="R_content",
        help="阶段 A argmax / 阶段 B 奖励标量",
    )
    p.add_argument(
        "--pi-old-model-for-ranking",
        default=None,
        help="阶段 B：用作 π_old 的 HF 模型 id 或路径（平均 logprob 排名）；不传则读 fashion_config.training-data",
    )
    p.add_argument(
        "--rank-correction-beta",
        type=float,
        default=None,
        help="Rewarding the Unlikely 的 β_rank；不传则读 YAML，若已配置 π_old 且无 YAML 则默认 0.25",
    )
    p.add_argument(
        "--rank-correction-no-skip-valve",
        action="store_true",
        help="关闭排名修正安全阀（全组 R 非正或几乎相同仍强制算 π_old 排名）",
    )
    p.add_argument(
        "--no-evaluate",
        action="store_true",
        help="只生成改写不调用 evaluate_text（导出将大量缺少评测，不建议）",
    )
    args = p.parse_args()

    body = _load_description(args)
    if not body:
        raise SystemExit("description 为空")

    run_id = (args.run_id or "").strip()
    if not run_id:
        suffix = uuid.uuid4().hex[:8]
        run_id = f"test_k_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{suffix}"

    export_dir = args.export_dir
    if export_dir is None:
        export_dir = default_grpo_export_dir(run_id)

    filter_fn: Callable[[Dict[str, Any]], bool]
    if args.strict_training_filter:
        filter_fn = default_include_for_training
    else:
        filter_fn = lambda _rec: True  # noqa: E731

    logger.info("run_id=%s", run_id)
    logger.info("K=%s evaluate=%s", args.k if args.k is not None else "YAML 默认", not args.no_evaluate)

    try:
        parallel = generate_k_parallel_rewrites(
            body,
            args.k,
            extra_context=args.business_context or "",
            evaluate_candidates=not args.no_evaluate,
        )
    except Exception as exc:  # noqa: BLE001
        raise SystemExit(f"generate_k_parallel_rewrites 失败: {exc}") from exc

    logger.info(
        "改写完成 group_id=%s k_requested=%s candidates=%s evaluated=%s dup_removed=%s",
        parallel.get("group_id"),
        parallel.get("k_requested"),
        len(parallel.get("candidates") or []),
        parallel.get("candidates_evaluated"),
        parallel.get("duplicates_removed"),
    )

    tlog = TrainingRunLogger(run_id)
    context: Dict[str, Any] = {
        "shared_source_text": body,
        "business_context": args.business_context or "",
        "instruction_summary": "test_k_rewrite_and_export_phases",
    }
    written = tlog.append_parallel_result(
        parallel,
        context=context,
        group_round=0,
    )
    logger.info("已写入 %s 行 → %s", len(written), tlog.path())

    export_kw: Dict[str, Any] = {
        "reward_key": args.reward_key,
        "filter_fn": filter_fn,
    }
    if args.pi_old_model_for_ranking is not None:
        export_kw["pi_old_model_for_ranking"] = args.pi_old_model_for_ranking.strip()
    if args.rank_correction_beta is not None:
        export_kw["beta_rank"] = args.rank_correction_beta
    if args.rank_correction_no_skip_valve:
        export_kw["rank_correction_skip_valve"] = False

    manifest = export_two_phase_from_samples(
        tlog.path(),
        export_dir,
        **export_kw,
    )
    logger.info("阶段 A: %s", manifest.get("phase_a_sft_jsonl"))
    logger.info("阶段 B: %s", manifest.get("phase_b_grpo_jsonl"))
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
