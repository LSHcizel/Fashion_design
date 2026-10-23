"""从 K 路 samples.jsonl 造同组比较对（老师 = 该条自己的裁判 S_fp）。

改写之间可以成对，原文和改写也可以成对。原文在样本里标成 baseline_reference，
不进 SFT/GRPO，但 RM 仍用它和同组改写比 S_fp。
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .data import include_in_training, log_len_of, teacher_score
from .modeling import MIN_SCORE_GAP


def _side_payload(rec: Dict[str, Any]) -> Dict[str, Any]:
    ctx = rec.get("context") or {}
    return {
        "group_id": rec.get("group_id"),
        "candidate_index": rec.get("candidate_index"),
        "completion": rec.get("completion"),
        "teacher_score": teacher_score(rec),
        "log_len": log_len_of(rec),
        "char_len": rec.get("char_len"),
        "context": {
            "shared_source_text": ctx.get("shared_source_text"),
            "business_context": ctx.get("business_context"),
        },
    }


def teacher_margin(pair: Dict[str, Any]) -> float:
    raw = pair.get("teacher_margin")
    if raw is not None:
        return abs(float(raw))
    chosen = float((pair.get("chosen") or {}).get("teacher_score") or 0.0)
    rejected = float((pair.get("rejected") or {}).get("teacher_score") or 0.0)
    return abs(chosen - rejected)


def pair_in_rm_training(pair: Dict[str, Any], min_margin: float = MIN_SCORE_GAP) -> bool:
    """分差必须严格大于 min_margin。旧的同分长度对不再进入训练。"""
    if pair.get("pair_kind") == "same_score_length":
        return False
    return round(teacher_margin(pair), 6) > float(min_margin)


def pairs_from_group(
    records: Sequence[Dict[str, Any]],
    *,
    min_margin: float = MIN_SCORE_GAP,
) -> List[Dict[str, Any]]:
    """只在同一个 group_id 内两两比较。混进别的组时按组拆开，不造跨组对。"""
    buckets: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for rec in records:
        gid = str(rec.get("group_id") or "")
        if not gid:
            continue
        buckets[gid].append(rec)
    if len(buckets) != 1:
        out: List[Dict[str, Any]] = []
        for recs in buckets.values():
            out.extend(_pairs_within_one_group(recs, min_margin=min_margin))
        return out
    return _pairs_within_one_group(next(iter(buckets.values())), min_margin=min_margin)


def _is_baseline_original(rec: Dict[str, Any]) -> bool:
    try:
        if int(rec.get("candidate_index", 0)) < 0:
            return True
    except (TypeError, ValueError):
        pass
    meta = rec.get("parallel_sampling") or {}
    return bool(meta.get("injected_original") or meta.get("reference_only"))


def eligible_for_rm_pair(rec: Dict[str, Any]) -> bool:
    """改写看 include_in_training。原文只因对照基线被排除时，仍可与改写成对。"""
    if include_in_training(rec):
        return True
    if not _is_baseline_original(rec):
        return False
    tf = rec.get("training_filter") or {}
    reasons = set(tf.get("exclude_reasons") or [])
    if reasons - {"baseline_reference"}:
        return False
    if tf.get("rewrite_error") or (rec.get("parallel_sampling") or {}).get("rewrite_error"):
        return False
    if not str(rec.get("completion") or "").strip():
        return False
    return teacher_score(rec) is not None


def _pairs_within_one_group(
    records: Sequence[Dict[str, Any]],
    *,
    min_margin: float,
) -> List[Dict[str, Any]]:
    """同一 group 内两两比较，含原文与改写。S_fp 分差不大于 min_margin 的对丢弃。高分一侧是 chosen。"""
    group_ids = {str(rec.get("group_id") or "") for rec in records}
    if len(group_ids) != 1:
        raise ValueError("比较对不能跨 group_id")
    scored: List[Tuple[float, Dict[str, Any]]] = []
    for rec in records:
        if not eligible_for_rm_pair(rec):
            continue
        s = teacher_score(rec)
        if s is None:
            continue
        if not str(rec.get("completion") or "").strip():
            continue
        scored.append((s, rec))
    out: List[Dict[str, Any]] = []
    n = len(scored)
    for i in range(n):
        for j in range(i + 1, n):
            s_i, rec_i = scored[i]
            s_j, rec_j = scored[j]
            gap_s = round(abs(s_i - s_j), 6)
            if gap_s <= float(min_margin):
                continue
            if s_i > s_j:
                win, lose = rec_i, rec_j
            else:
                win, lose = rec_j, rec_i
            kind = "score"
            gid = str(win.get("group_id") or "")
            if gid != str(lose.get("group_id") or ""):
                raise ValueError("比较对不能跨 group_id")
            out.append(
                {
                    "schema_version": "odin_pref_pair_v1",
                    "group_id": gid,
                    "pair_kind": kind,
                    "chosen": _side_payload(win),
                    "rejected": _side_payload(lose),
                    "teacher_margin": round(gap_s, 6),
                }
            )
    return out


def assign_splits(
    pairs: List[Dict[str, Any]],
    *,
    holdout_frac: float = 0.1,
) -> List[Dict[str, Any]]:
    """按 group_id 切 holdout，同一组不拆到两边。"""
    gids: List[str] = []
    seen = set()
    for p in pairs:
        gid = str(p.get("group_id") or "")
        if gid not in seen:
            seen.add(gid)
            gids.append(gid)
    n_hold = int(round(len(gids) * float(holdout_frac)))
    if len(gids) >= 2:
        n_hold = max(1, n_hold) if holdout_frac > 0 else 0
        n_hold = min(n_hold, len(gids) - 1)
    hold = set(gids[-n_hold:]) if n_hold else set()
    for p in pairs:
        p["split"] = "holdout" if str(p.get("group_id") or "") in hold else "train"
    return pairs


def build_preference_pairs(
    samples_jsonl: Path,
    *,
    min_margin: float = MIN_SCORE_GAP,
    holdout_frac: float = 0.1,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    n_rows = 0
    for rec in _iter_samples(samples_jsonl):
        n_rows += 1
        gid = str(rec.get("group_id") or "")
        if not gid:
            continue
        groups[gid].append(rec)

    pairs: List[Dict[str, Any]] = []
    n_groups_used = 0
    for recs in groups.values():
        g_pairs = pairs_from_group(recs, min_margin=min_margin)
        if g_pairs:
            n_groups_used += 1
        pairs.extend(g_pairs)
    assign_splits(pairs, holdout_frac=holdout_frac)
    n_train = sum(1 for p in pairs if p.get("split") == "train")
    n_hold = sum(1 for p in pairs if p.get("split") == "holdout")
    summary = {
        "samples_jsonl": str(Path(samples_jsonl).resolve()),
        "sample_rows": n_rows,
        "groups": len(groups),
        "groups_with_pairs": n_groups_used,
        "pairs": len(pairs),
        "train_pairs": n_train,
        "holdout_pairs": n_hold,
        "min_margin": min_margin,
        "holdout_frac": holdout_frac,
        "teacher": "s_fp_base / S_fp（不用 R_content）",
        "pairing": "within_group_only",
        "cross_group_pairs": sum(
            1
            for p in pairs
            if str(p.get("group_id") or "") != str((p.get("chosen") or {}).get("group_id") or "")
            or str(p.get("group_id") or "") != str((p.get("rejected") or {}).get("group_id") or "")
        ),
    }
    return pairs, summary


def _iter_samples(path: Path):
    from .data import read_jsonl

    yield from read_jsonl(path)


def main() -> None:
    p = argparse.ArgumentParser(description="K 路样本 → ODIN RM 偏好对 JSONL")
    p.add_argument("--samples", type=Path, required=True, help="samples.jsonl")
    p.add_argument("--out", type=Path, required=True, help="pairs.jsonl")
    p.add_argument("--min-margin", type=float, default=MIN_SCORE_GAP)
    p.add_argument("--holdout-frac", type=float, default=0.1)
    args = p.parse_args()
    pairs, summary = build_preference_pairs(
        args.samples,
        min_margin=args.min_margin,
        holdout_frac=args.holdout_frac,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as f:
        for row in pairs:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    summary_path = args.out.with_suffix(".summary.json")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
