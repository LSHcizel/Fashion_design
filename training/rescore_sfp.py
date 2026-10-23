#!/usr/bin/env python3
"""用当前裁判把已有 samples.jsonl 的 S_fp 重打一遍。

不改原文文件。输出是新的 jsonl，中断后按已写行数续跑。
裁判地址和模型名要和正在服务的 vLLM 一致。

    python -m training.rescore_sfp \
      --samples training/runs/grpo_corpus2000_20261011/samples.jsonl \
      --out training/runs/grpo_corpus2000_20261023_sfp3b/samples.jsonl \
      --api-base http://127.0.0.1:8000/v1 \
      --model Qwen2.5-3B-Instruct
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from plugins.text_description_evaluator.design_text_evaluator_api import DesignTextEvaluator
from training.record_builder import build_training_record


def _load_done(path: Path) -> int:
    if not path.is_file():
        return 0
    with path.open(encoding="utf-8") as handle:
        return sum(1 for line in handle if line.strip())


def _rewrite(rec: dict, evaluation: dict | None) -> dict:
    rc = evaluation.get("r_content") if isinstance(evaluation, dict) else None
    ctx = dict(rec.get("context") or {})
    return build_training_record(
        group_id=str(rec.get("group_id") or ""),
        group_round=int(rec.get("group_round") or 0),
        candidate_index=int(rec.get("candidate_index") or 0),
        context=ctx,
        completion_text=str(rec.get("completion") or ""),
        evaluation=evaluation,
        r_content_block=rc if isinstance(rc, dict) else None,
        parallel_meta=rec.get("parallel_sampling") or {},
        run_id=str(rec.get("run_id") or "rescore_sfp"),
        record_type=str(rec.get("record_type") or "rewrite_candidate"),
        system_prompt_sha256=ctx.get("system_prompt_sha256"),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="用指定裁判重打 samples 的 S_fp")
    parser.add_argument("--samples", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--api-base", type=str, default="http://127.0.0.1:8000/v1")
    parser.add_argument("--model", type=str, required=True, help="vLLM --served-model-name")
    parser.add_argument("--api-key", type=str, default="local")
    args = parser.parse_args()

    src = args.samples
    if not src.is_file():
        raise SystemExit(f"找不到 samples: {src}")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    done = _load_done(args.out)
    evaluator = DesignTextEvaluator(
        api_key=args.api_key,
        api_base=args.api_base.rstrip("/"),
        model=args.model,
        verify_ssl=False,
    )
    written = 0
    with src.open(encoding="utf-8") as incoming, args.out.open("a", encoding="utf-8") as outgoing:
        for index, line in enumerate(incoming):
            if not line.strip():
                continue
            if index < done:
                continue
            rec = json.loads(line)
            text = str(rec.get("completion") or "").strip()
            if not text:
                updated = rec
            else:
                evaluation = evaluator.evaluate_text(text, source_name=f"row-{index}")
                updated = _rewrite(rec, evaluation)
            outgoing.write(json.dumps(updated, ensure_ascii=False) + "\n")
            outgoing.flush()
            written += 1
            if written % 20 == 0:
                print(f"rescored {done + written}", flush=True)
    print(f"done out={args.out} new_rows={written} skipped_existing={done}")


if __name__ == "__main__":
    sys.exit(main())
