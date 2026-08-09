"""Evaluate workflow chapter_01 look_01 and write report to 汇报/."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from 汇报._run_single_eval import evaluate_and_write

TEXT_PATH = ROOT / "fashion_research_dir/workflow_0/2026-06-06/chapter_01/look_01.txt"
OUT_MD = ROOT / "汇报/chapter01_look01_完整评分报告.md"
OUT_JSON = ROOT / "汇报/chapter01_look01_完整评分报告.json"


def main() -> None:
    full = evaluate_and_write(
        TEXT_PATH,
        out_md=OUT_MD,
        out_json=OUT_JSON,
        title="Look 01 · The Shoreline Opening Suit 完整评分报告",
    )
    print(f"Saved: {OUT_MD}")
    print(f"Saved: {OUT_JSON}")
    print(f"S_fp={full.get('total_score')} band={full.get('score_band')}")


if __name__ == "__main__":
    main()
