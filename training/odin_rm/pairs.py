"""从 K 路 samples.jsonl 造 Bradley–Terry 偏好对（老师 = 裁判 s_fp_base）。"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .data import include_in_training, log_len_of, teacher_score


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


def pairs_from_group(
    records: Sequence[Dict[str, Any]],
    *,
    min_margin: float = 1e-6,
) -> List[Dict[str, Any]]:
    """同一 group 内两两比裁判分；平分 / 差距过小丢掉。"""
    scored: List[Tuple[float, Dict[str, Any]]] = []
    for rec in records:
        if not include_in_training(rec):
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
            if abs(s_i - s_j) < min_margin:
                continue
            if s_i > s_j:
                win, lose = rec_i, rec_j
            else:
                win, lose = rec_j, rec_i
            out.append(
                {
                    "schema_version": "odin_pref_pair_v1",
                    "group_id": rec_i.get("group_id"),
                    "chosen": _side_payload(win),
                    "rejected": _side_payload(lose),
                    "teacher_margin": round(abs(s_i - s_j), 6),
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
    min_margin: float = 1e-6,
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
    }
    return pairs, summary


def _iter_samples(path: Path):
    from .data import read_jsonl

    yield from read_jsonl(path)


def main() -> None:
    p = argparse.ArgumentParser(description="K 路样本 → ODIN RM 偏好对 JSONL")
    p.add_argument("--samples", type=Path, required=True, help="samples.jsonl")
    p.add_argument("--out", type=Path, required=True, help="pairs.jsonl")
    p.add_argument("--min-margin", type=float, default=1e-6)
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
