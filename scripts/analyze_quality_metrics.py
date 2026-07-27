#!/usr/bin/env python3
"""Analyze quality metric discrimination from eval JSON outputs."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

WF = Path("fashion_research_dir/workflow_0/2026-06-06/text_eval_scores/20260712T104516Z")
WGSN = Path(
    "fashion_research_dir/wgsn_batch_image_inverse/20260524T044337Z/text_description_scores/七月完整测试"
)
MODS = [
    "BindingAccuracy",
    "LanguageClarity",
    "StructuralClarity",
    "GenerationReadiness",
    "ConcisenessAndDensity",
    "DesignMerit",
]


def metric_stats(d: Path) -> dict[str, list[float]]:
    acc: dict[str, list[float]] = defaultdict(list)
    for p in d.glob("*_evaluation.json"):
        data = json.loads(p.read_text(encoding="utf-8"))
        for k, v in data["metric_results"].items():
            if v.get("axis") == "quality_score" and v.get("applicable"):
                acc[k].append(float(v.get("score_value", 0)))
    return acc


def summarize(acc: dict[str, list[float]], label: str) -> None:
    print(f"\n=== {label} ===")
    rows = []
    for k, vals in acc.items():
        avg = sum(vals) / len(vals)
        std = (sum((x - avg) ** 2 for x in vals) / len(vals)) ** 0.5
        rows.append((k, avg, std, min(vals), max(vals), len(vals)))
    rows.sort(key=lambda x: x[1], reverse=True)
    for k, avg, std, mn, mx, n in rows:
        print(f"{k:40s} avg={avg:.3f} std={std:.3f} range=[{mn:.2f},{mx:.2f}] n={n}")


def main() -> None:
    wf = metric_stats(WF)
    wgsn = metric_stats(WGSN)
    summarize(wf, "workflow")
    summarize(wgsn, "wgsn")

    print("\n=== DISCRIMINATION (wgsn_avg - wf_avg) ===")
    diffs = []
    for k in sorted(set(wf) | set(wgsn)):
        wa = sum(wf[k]) / len(wf[k]) if wf.get(k) else None
        ga = sum(wgsn[k]) / len(wgsn[k]) if wgsn.get(k) else None
        if wa is not None and ga is not None:
            diffs.append((ga - wa, k, wa, ga))
    diffs.sort(reverse=True)
    for d, k, wa, ga in diffs:
        print(f"{d:+.3f}  {k:40s}  wf={wa:.3f}  wgsn={ga:.3f}")

    print("\n=== MODULE scores ===")
    for d, label in [(WF, "wf"), (WGSN, "wgsn")]:
        ms: dict[str, list[float]] = defaultdict(list)
        for p in d.glob("*_evaluation.json"):
            data = json.loads(p.read_text(encoding="utf-8"))
            for k, v in data["scores"]["module_scores"].items():
                if k in MODS:
                    ms[k].append(v["score"])
        print(label, {k: round(sum(v) / len(v), 3) for k, v in ms.items()})

    # applicability skip rate
    print("\n=== APPLICABILITY skip rate (quality only) ===")
    skip: dict[str, int] = defaultdict(int)
    total: dict[str, int] = defaultdict(int)
    for d in (WF, WGSN):
        for p in d.glob("*_evaluation.json"):
            data = json.loads(p.read_text(encoding="utf-8"))
            for k, v in data["metric_results"].items():
                if v.get("axis") != "quality_score":
                    continue
                total[k] += 1
                if not v.get("applicable"):
                    skip[k] += 1
    for k in sorted(total):
        print(f"{k:40s} skipped {skip[k]}/{total[k]} ({100*skip[k]/total[k]:.0f}%)")


if __name__ == "__main__":
    main()
