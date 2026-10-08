"""把 season_themes 生成结果整理进语料库 jsonl（带 house / theme / season）。"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INDEX = ROOT / "fashion_research_dir" / "season_themes_2026-09" / "index.json"
DEFAULT_OUT = (
    ROOT
    / "fashion_research_dir"
    / "season_themes_2026-09"
    / "source_corpus_gpt54mini_keep.jsonl"
)


def _iter_looks(run_dir: Path) -> list[Path]:
    out: list[Path] = []
    for path in sorted(run_dir.rglob("look_*.txt")):
        name = path.name.lower()
        if any(x in name for x in ("reflection", "eliminated", "original")):
            continue
        if "/text_eval_scores/" in path.as_posix():
            continue
        out.append(path)
    return out


def _latest_complete_run(brand_root: Path, num_chapters: int, num_looks: int) -> Path | None:
    if not brand_root.is_dir():
        return None
    want = num_chapters * num_looks
    best: Path | None = None
    for run_dir in sorted(p for p in brand_root.iterdir() if p.is_dir()):
        looks = _iter_looks(run_dir)
        if len(looks) >= want:
            best = run_dir
    return best


def pack(
    *,
    index_path: Path,
    generated_root: Path,
    out_path: Path,
) -> dict[str, Any]:
    index_path = Path(index_path)
    if not index_path.is_absolute():
        index_path = (ROOT / index_path).resolve()
    generated_root = Path(generated_root)
    if not generated_root.is_absolute():
        generated_root = (ROOT / generated_root).resolve()
    out_path = Path(out_path)
    if not out_path.is_absolute():
        out_path = (ROOT / out_path).resolve()

    payload = json.loads(index_path.read_text(encoding="utf-8"))
    num_chapters = int(payload.get("num_chapters") or 4)
    num_looks = int(payload.get("num_looks") or 4)
    rows: list[dict[str, Any]] = []
    missing: list[str] = []

    for rec in payload.get("collections") or []:
        brand_dir = str(rec.get("dir") or "")
        house = str(rec.get("house") or "")
        theme = str(rec.get("theme") or "")
        season = str(rec.get("season") or "")
        run = _latest_complete_run(generated_root / brand_dir, num_chapters, num_looks)
        if run is None:
            missing.append(brand_dir)
            continue
        for path in _iter_looks(run):
            text = path.read_text(encoding="utf-8").strip()
            if not text:
                continue
            path = path.resolve()
            try:
                rel = str(path.relative_to(ROOT)).replace("\\", "/")
            except ValueError:
                rel = str(path).replace("\\", "/")
            m = re.search(r"chapter_(\d+)", path.as_posix())
            chapter = int(m.group(1)) if m else None
            look_m = re.search(r"look_(\d+)", path.name, re.I)
            look_n = int(look_m.group(1)) if look_m else None
            sid = f"gen_{brand_dir}_c{chapter or 0:02d}_l{look_n or 0:02d}"
            rows.append(
                {
                    "source_id": sid,
                    "role": "negative",
                    "sample_kind": "workflow_generated_gpt54mini_keep_gate_fail",
                    "path": rel,
                    "text": text,
                    "house": house,
                    "season": season,
                    "theme": theme,
                    "brand_dir": brand_dir,
                    "chapter": chapter,
                    "look": look_n,
                    "business_context": (
                        f"{house} {season}. Theme: {theme}. "
                        "Preserve identifying design inside this house theme; "
                        "rewrite into one grounded T2I paragraph if used for K-rewrite training."
                    ),
                }
            )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    # 同步一份到 training/runs，便于对照
    mirror = ROOT / "training" / "runs" / "corpus" / "season_themes_gpt54mini_keep.jsonl"
    mirror.parent.mkdir(parents=True, exist_ok=True)
    mirror.write_text(out_path.read_text(encoding="utf-8"), encoding="utf-8")

    return {
        "n_total": len(rows),
        "n_brands_packed": len({r["brand_dir"] for r in rows}),
        "missing_brands": missing,
        "out": str(out_path.relative_to(ROOT)).replace("\\", "/"),
        "mirror": str(mirror.relative_to(ROOT)).replace("\\", "/"),
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Pack season generated looks into corpus jsonl")
    p.add_argument("--index", type=Path, default=DEFAULT_INDEX)
    p.add_argument(
        "--generated-root",
        type=Path,
        default=DEFAULT_INDEX.parent / "generated_gpt54mini_keep",
    )
    p.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = p.parse_args()
    stats = pack(index_path=args.index, generated_root=args.generated_root, out_path=args.out)
    print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
