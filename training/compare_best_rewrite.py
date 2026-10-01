"""每条原文只对比组内总分最高的改写。

samples 里没有原文分时，在同目录维护 ``original_scores.jsonl``。
已写入的原文不再打分；samples 里出现新组时再跑一次即可增量补上。

用法::

    python -m training.compare_best_rewrite \\
      --samples training/runs/grpo_theme_2026-10-01/samples.jsonl
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List, Set

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from training.accept_report import summarize_score_lift
from training.record_builder import build_training_record


def _load_rows(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _is_original_row(rec: Dict[str, Any]) -> bool:
    try:
        if int(rec.get("candidate_index", 0)) < 0:
            return True
    except (TypeError, ValueError):
        pass
    return bool((rec.get("parallel_sampling") or {}).get("injected_original"))


def _source_text(rec: Dict[str, Any]) -> str:
    ctx = rec.get("context") or {}
    return str(ctx.get("shared_source_text") or "").strip()


def _groups_missing_original(rows: List[Dict[str, Any]]) -> Dict[str, str]:
    seen: Dict[str, str] = {}
    have = set()
    for rec in rows:
        gid = str(rec.get("group_id") or "")
        if not gid or _is_original_row(rec):
            if gid and _is_original_row(rec) and rec.get("S_fp") is not None:
                have.add(gid)
            continue
        text = _source_text(rec)
        if gid not in seen and text:
            seen[gid] = text
    return {gid: text for gid, text in seen.items() if gid not in have}


def originals_already_scored(rows: List[Dict[str, Any]]) -> Set[str]:
    return {
        str(rec.get("group_id"))
        for rec in rows
        if rec.get("group_id") and _is_original_row(rec) and rec.get("S_fp") is not None
    }


def load_score_cache(path: Path) -> Dict[str, Dict[str, Any]]:
    cached: Dict[str, Dict[str, Any]] = {}
    if not path.is_file():
        return cached
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            gid = str(rec.get("group_id") or "")
            if gid and rec.get("S_fp") is not None:
                cached[gid] = rec
    return cached


def append_score_cache(path: Path, rec: Dict[str, Any], lock: threading.Lock) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(rec, ensure_ascii=False) + "\n"
    with lock:
        with path.open("a", encoding="utf-8") as f:
            f.write(line)
            f.flush()
            os.fsync(f.fileno())


def pending_originals(
    rows: List[Dict[str, Any]],
    cached_ids: Set[str],
) -> Dict[str, str]:
    missing = _groups_missing_original(rows)
    return {gid: text for gid, text in missing.items() if gid not in cached_ids}


def _score_originals(
    missing: Dict[str, str],
    *,
    workers: int,
    cache_path: Path,
) -> List[Dict[str, Any]]:
    from plugins.text_description_evaluator.design_text_evaluator_api import (
        JudgeConnectionError,
        is_connection_failure,
        load_default_evaluator,
    )

    evaluator = load_default_evaluator()
    out: List[Dict[str, Any]] = []
    errors: List[BaseException] = []
    lock = threading.Lock()
    done = 0
    total = len(missing)

    def one(item: tuple) -> Dict[str, Any]:
        gid, text = item
        try:
            ev = evaluator.evaluate_text(text, source_name=f"{gid}.baseline")
        except JudgeConnectionError:
            raise
        except Exception as exc:  # noqa: BLE001
            if is_connection_failure(exc):
                raise JudgeConnectionError(str(exc)) from exc
            raise
        return build_training_record(
            group_id=gid,
            group_round=0,
            candidate_index=-1,
            context={"shared_source_text": text},
            completion_text=text,
            evaluation=ev,
            r_content_block=ev.get("r_content") if isinstance(ev, dict) else None,
            parallel_meta={"injected_original": True, "reference_only": True, "dedupe_kept": True},
            run_id="best_vs_original",
        )

    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        futures = [pool.submit(one, item) for item in missing.items()]
        for fut in as_completed(futures):
            try:
                rec = fut.result()
            except BaseException as exc:  # noqa: BLE001
                errors.append(exc)
                continue
            append_score_cache(cache_path, rec, lock)
            out.append(rec)
            done += 1
            print(
                f"cached {done}/{total} {rec.get('group_id')} S_fp={rec.get('S_fp')}",
                flush=True,
            )
    if errors:
        raise errors[0]
    return out


def main() -> None:
    p = argparse.ArgumentParser(description="每条原文对比组内总分最高的改写")
    p.add_argument("--samples", type=Path, required=True)
    p.add_argument("--out", type=Path, default=None, help="默认写到 samples 同目录 best_vs_original.json")
    p.add_argument("--workers", type=int, default=4, help="补打原文时的并发")
    p.add_argument("--no-score", action="store_true", help="缺原文分时不调用评分器")
    args = p.parse_args()
    samples = args.samples.resolve()
    if not samples.is_file():
        raise SystemExit(f"找不到 samples: {samples}")
    rows = _load_rows(samples)
    cache_path = samples.parent / "original_scores.jsonl"
    in_samples = originals_already_scored(rows)
    cache = load_score_cache(cache_path)
    pending = pending_originals(rows, set(cache))
    n_groups = len({r.get("group_id") for r in rows if r.get("group_id")})
    print(
        f"groups={n_groups} originals_in_samples={len(in_samples)} "
        f"cached={len(cache)} pending={len(pending)} cache={cache_path}",
        flush=True,
    )
    if in_samples and not pending and not cache:
        print("samples 里已有原文分，不调用评分器", flush=True)
    if pending and not args.no_score:
        print(f"scoring {len(pending)} new originals with {args.workers} workers", flush=True)
        fresh = _score_originals(pending, workers=args.workers, cache_path=cache_path)
        for rec in fresh:
            gid = str(rec.get("group_id") or "")
            if gid:
                cache[gid] = rec
    elif pending:
        print(f"skip scoring; {len(pending)} groups still have no original score", flush=True)
    already = set(in_samples)
    rows.extend(rec for gid, rec in cache.items() if gid not in already)
    lift = summarize_score_lift(rows)
    best = lift.get("best_rewrite_lift_vs_original") or {}
    out = args.out or (samples.parent / "best_vs_original.json")
    out.write_text(json.dumps(lift, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        f"最好改写相对原文  组数 {best.get('groups')}  "
        f"总分 {best.get('S_fp')}  质量轴 {best.get('quality')}  "
        f"更高 {best.get('groups_best_higher')} 组 / 更低 {best.get('groups_best_lower')} 组 / "
        f"持平 {best.get('groups_best_tied')} 组",
        flush=True,
    )
    print(f"wrote {out}", flush=True)


if __name__ == "__main__":
    main()
