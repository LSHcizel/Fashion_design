#!/usr/bin/env python3
"""把负样本原文/原图/原分 与 高分改写/新图/新分 收进同一对照目录。"""

from __future__ import annotations

import json
import shutil
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO = Path(__file__).resolve().parents[1]
SAMPLES = Path(r"c:\Users\lsh\Desktop\grpo_chanel_inverse_v3\samples.jsonl")
NEW_IMG_DIR = Path(r"c:\Users\lsh\Desktop\grpo_chanel_inverse_v3\neg_best_rewrite_images")
OUT = Path(r"c:\Users\lsh\Desktop\grpo_chanel_inverse_v3\负样本对比")
ORIG_DIR = OUT / "01_原文原图原分"
NEW_DIR = OUT / "02_高分改写与新图"


def compact_score(rec: Dict[str, Any], *, kind: str) -> Dict[str, Any]:
    ctx = rec.get("context") or {}
    sc = rec.get("scores_compact") or {}
    gates = rec.get("gates_compact") or {}
    pens = rec.get("penalties") or {}
    return {
        "kind": kind,
        "group_id": rec.get("group_id"),
        "candidate_index": rec.get("candidate_index"),
        "R_content": rec.get("R_content"),
        "S_fp": rec.get("S_fp"),
        "coverage_axis_score": sc.get("coverage_axis_score"),
        "quality_penalized_score": sc.get("quality_penalized_score"),
        "total_penalty": sc.get("total_penalty") if sc.get("total_penalty") is not None else pens.get("total_penalty"),
        "score_gate_passed": gates.get("score_gate_passed"),
        "penalty_gate_passed": gates.get("penalty_gate_passed"),
        "both_passed": gates.get("both_passed"),
        "char_len": rec.get("char_len"),
        "source_path": ctx.get("source_path"),
        "source_role": ctx.get("source_role"),
    }


def write_score_files(folder: Path, score: Dict[str, Any]) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "得分.json").write_text(
        json.dumps(score, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    lines = [
        f"group_id: {score.get('group_id')}",
        f"类型: {score.get('kind')}",
        f"R_content: {score.get('R_content')}",
        f"S_fp: {score.get('S_fp')}",
        f"coverage: {score.get('coverage_axis_score')}",
        f"quality: {score.get('quality_penalized_score')}",
        f"total_penalty: {score.get('total_penalty')}",
        f"score_gate_passed: {score.get('score_gate_passed')}",
        f"penalty_gate_passed: {score.get('penalty_gate_passed')}",
        f"both_passed: {score.get('both_passed')}",
        f"char_len: {score.get('char_len')}",
        f"candidate_index: {score.get('candidate_index')}",
        f"source_path: {score.get('source_path')}",
        "",
    ]
    (folder / "得分.txt").write_text("\n".join(lines), encoding="utf-8")


def find_original_image(source_path: str) -> Optional[Path]:
    src = REPO / source_path
    look_name = src.stem  # look_01
    chapter = src.parent
    candidates = [
        chapter / "image2_generation" / f"{look_name}_gpt-image-2.png",
        chapter.parent / "image2_generation" / f"{look_name}_gpt-image-2.png",
    ]
    for p in candidates:
        if p.is_file() and p.stat().st_size > 0:
            return p
    return None


def load_neg_records() -> Dict[str, List[Dict[str, Any]]]:
    groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    with SAMPLES.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            if (rec.get("context") or {}).get("source_role") != "negative":
                continue
            groups[str(rec.get("group_id"))].append(rec)
    return groups


def best_rewrite(recs: List[Dict[str, Any]]) -> Dict[str, Any]:
    cands = [r for r in recs if r.get("candidate_index") != -1 and str(r.get("completion") or "").strip()]
    return max(cands, key=lambda r: float(r.get("R_content") or -1))


def original_row(recs: List[Dict[str, Any]]) -> Dict[str, Any]:
    for r in recs:
        if r.get("candidate_index") == -1:
            return r
    raise KeyError("no injected original")


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    ORIG_DIR.mkdir(parents=True)
    NEW_DIR.mkdir(parents=True)

    groups = load_neg_records()
    missing_orig_img: List[str] = []
    table_rows: List[Dict[str, Any]] = []

    for gid in sorted(groups):
        recs = groups[gid]
        orig = original_row(recs)
        best = best_rewrite(recs)
        src_rel = str((orig.get("context") or {}).get("source_path") or "")
        src = REPO / src_rel

        o_folder = ORIG_DIR / gid
        n_folder = NEW_DIR / gid
        o_folder.mkdir(parents=True)
        n_folder.mkdir(parents=True)

        if src.is_file():
            (o_folder / "原描述.txt").write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        else:
            (o_folder / "原描述.txt").write_text(str(orig.get("completion") or ""), encoding="utf-8")

        write_score_files(o_folder, compact_score(orig, kind="原文"))

        img = find_original_image(src_rel)
        if img:
            shutil.copy2(img, o_folder / "原图.png")
        else:
            missing_orig_img.append(gid)
            (o_folder / "原图缺失.txt").write_text(
                "仓库里没有该负样本原文对应的 image2 原图，待按原文补生成。\n"
                f"source: {src_rel}\n",
                encoding="utf-8",
            )

        (n_folder / "高分描述.txt").write_text(str(best.get("completion") or ""), encoding="utf-8")
        write_score_files(n_folder, compact_score(best, kind="高分改写"))
        new_png = NEW_IMG_DIR / f"{gid}_gpt-image-2.png"
        if new_png.is_file():
            shutil.copy2(new_png, n_folder / "新图.png")
        else:
            (n_folder / "新图缺失.txt").write_text(f"找不到 {new_png}\n", encoding="utf-8")

        table_rows.append(
            {
                "group_id": gid,
                "source_path": src_rel,
                "原文_R_content": orig.get("R_content"),
                "高分改写_R_content": best.get("R_content"),
                "delta_R": round(float(best.get("R_content") or 0) - float(orig.get("R_content") or 0), 4),
                "高分改写_candidate_index": best.get("candidate_index"),
                "原文_原图": "有" if img else "缺",
                "改写_新图": "有" if new_png.is_file() else "缺",
            }
        )

    (OUT / "对照表.json").write_text(
        json.dumps(table_rows, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    lines = [
        "负样本对照：原文/原图/原分  vs  高分改写/新图/新分",
        "得分均为 grpo_chanel_inverse_v3 同一套评判（原文取注入的 candidate_index=-1）。",
        "",
        f"{'group_id':<48} {'原文R':>8} {'改写R':>8} {'ΔR':>8} {'原图':>4} {'新图':>4}",
    ]
    for row in table_rows:
        lines.append(
            f"{row['group_id']:<48} {row['原文_R_content']:>8} {row['高分改写_R_content']:>8} "
            f"{row['delta_R']:>8} {row['原文_原图']:>4} {row['改写_新图']:>4}"
        )
    (OUT / "对照表.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (OUT / "缺原图清单.json").write_text(
        json.dumps(missing_orig_img, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"packed {len(table_rows)} groups -> {OUT}")
    print("missing original images:", len(missing_orig_img))
    for g in missing_orig_img:
        print(" ", g)


if __name__ == "__main__":
    main()
