#!/usr/bin/env python3
"""用当前裁判把已有 samples.jsonl 的 S_fp 重打一遍。

不改原文文件。输出是新的 jsonl，按输入行序写出，中断后按已写行数续跑。
同时在飞的条数由 --workers 控制，完成一条就从后面补一条。
裁判地址和模型名要和正在服务的 vLLM 一致。

    python -m training.rescore_sfp \
      --samples training/runs/grpo_corpus2000_20261011/samples.jsonl \
      --out training/runs/grpo_corpus2000_20261023_sfp3b/samples.jsonl \
      --api-base http://127.0.0.1:8002/v1 \
      --model Qwen2.5-3B-Instruct \
      --workers 32
"""

from __future__ import annotations

import argparse
import json
import sys
import threading
import traceback
from collections import deque
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from pathlib import Path

from plugins.text_description_evaluator.design_text_evaluator_api import DesignTextEvaluator
from training.record_builder import build_training_record

_tls = threading.local()


def _load_done(path: Path) -> int:
    """已写好的完整 JSON 行数。末尾半行丢掉，避免中断后续跑错位。"""
    if not path.is_file():
        return 0
    kept: list[str] = []
    dropped_partial = False
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            try:
                json.loads(line)
            except json.JSONDecodeError:
                dropped_partial = True
                break
            kept.append(line if line.endswith("\n") else line + "\n")
    if dropped_partial:
        path.write_text("".join(kept), encoding="utf-8")
    return len(kept)


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


def _evaluator(api_key: str, api_base: str, model: str) -> DesignTextEvaluator:
    ev = getattr(_tls, "evaluator", None)
    if ev is None:
        ev = DesignTextEvaluator(
            api_key=api_key,
            api_base=api_base,
            model=model,
            verify_ssl=False,
        )
        _tls.evaluator = ev
    return ev


def _score_one(index: int, rec: dict, api_key: str, api_base: str, model: str) -> tuple[int, dict]:
    text = str(rec.get("completion") or "").strip()
    if not text:
        return index, rec
    evaluation = _evaluator(api_key, api_base, model).evaluate_text(text, source_name=f"row-{index}")
    return index, _rewrite(rec, evaluation)


def _iter_pending(path: Path, done: int):
    with path.open(encoding="utf-8") as handle:
        for index, line in enumerate(handle):
            if not line.strip() or index < done:
                continue
            yield index, json.loads(line)


def main() -> None:
    parser = argparse.ArgumentParser(description="用指定裁判重打 samples 的 S_fp")
    parser.add_argument("--samples", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--api-base", type=str, default="http://127.0.0.1:8000/v1")
    parser.add_argument("--model", type=str, required=True, help="vLLM --served-model-name")
    parser.add_argument("--api-key", type=str, default="local")
    parser.add_argument("--workers", type=int, default=32, help="同时在飞的条数，完成一条就补一条")
    args = parser.parse_args()
    if args.workers < 1:
        raise SystemExit("--workers 至少为 1")

    src = args.samples
    if not src.is_file():
        raise SystemExit(f"找不到 samples: {src}")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    done = _load_done(args.out)
    api_base = args.api_base.rstrip("/")
    print(
        f"start skip={done} workers={args.workers} api={api_base} model={args.model}",
        flush=True,
    )

    pending = _iter_pending(src, done)
    inflight = {}
    ready: dict[int, dict] = {}
    expected: deque[int] = deque()
    written = 0
    stop_hb = threading.Event()

    def heartbeat() -> None:
        while not stop_hb.wait(30):
            try:
                flying = len(inflight)
            except RuntimeError:
                flying = -1
            print(f"inflight {flying} written {done + written}", flush=True)

    hb = threading.Thread(target=heartbeat, name="rescore-heartbeat", daemon=True)
    hb.start()

    def submit_one(pool: ThreadPoolExecutor) -> bool:
        try:
            index, rec = next(pending)
        except StopIteration:
            return False
        fut = pool.submit(_score_one, index, rec, args.api_key, api_base, args.model)
        inflight[fut] = index
        expected.append(index)
        return True

    try:
        with ThreadPoolExecutor(max_workers=args.workers, thread_name_prefix="rescore") as pool:
            with args.out.open("a", encoding="utf-8") as outgoing:
                for _ in range(args.workers):
                    if not submit_one(pool):
                        break
                def drain() -> None:
                    nonlocal written
                    while expected and expected[0] in ready:
                        index = expected.popleft()
                        updated = ready.pop(index)
                        outgoing.write(json.dumps(updated, ensure_ascii=False) + "\n")
                        outgoing.flush()
                        written += 1
                        print(
                            f"rescored {done + written} row={index} S_fp={updated.get('S_fp')}",
                            flush=True,
                        )

                while inflight:
                    finished, _ = wait(set(inflight), return_when=FIRST_COMPLETED)
                    for fut in finished:
                        inflight.pop(fut, None)
                        try:
                            index, updated = fut.result()
                        except Exception:
                            drain()
                            raise
                        ready[index] = updated
                        submit_one(pool)
                    drain()
    except Exception:
        traceback.print_exc()
        raise
    finally:
        stop_hb.set()

    print(f"done out={args.out} new_rows={written} skipped_existing={done}", flush=True)


if __name__ == "__main__":
    sys.exit(main())
