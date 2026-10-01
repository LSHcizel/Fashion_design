"""每条原文只对比组内总分最高的改写。

已有 samples.jsonl 里如果没有原文分，会用评分器补打原文，不重写、不重训。

用法::

    python -m training.compare_best_rewrite \\
      --samples training/runs/grpo_theme_2026-10-01/samples.jsonl
"""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List, Optional

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


def _score_originals(missing: Dict[str, str], *, workers: int) -> List[Dict[str, Any]]:
    from plugins.text_description_evaluator.design_text_evaluator_api import (
        JudgeConnectionError,
        is_connection_failure,
        load_default_evaluator,
    )

    evaluator = load_default_evaluator()
    out: List[Dict[str, Any]] = []
    errors: List[BaseException] = []

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
                out.append(fut.result())
            except BaseException as exc:  # noqa: BLE001
                errors.append(exc)
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
    missing = _groups_missing_original(rows)
    print(f"groups_in_file={len({r.get('group_id') for r in rows})} missing_original={len(missing)}", flush=True)
    if missing and not args.no_score:
        print(f"scoring {len(missing)} originals with {args.workers} workers", flush=True)
        rows.extend(_score_originals(missing, workers=args.workers))
    elif missing:
        print(f"skip scoring; {len(missing)} groups have no original score", flush=True)
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
