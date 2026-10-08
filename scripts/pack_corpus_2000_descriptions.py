"""合并 description 语料为 2000 条；只区分两类：inverse（逆解析）/ 生成型。"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]

KIND_INVERSE = "inverse"
KIND_GENERATED = "生成型"

_TEXT_DESC_RE = re.compile(
    r"^##\s*text_description\s*\n+(.*?)(?=\n##\s|\Z)",
    re.IGNORECASE | re.DOTALL,
)

DEFAULT_INVERSE_DIR = (
    REPO / "fashion_research_dir" / "image_inverse" / "vogue_cn_fw26_batch2"
)
DEFAULT_K_REWRITE = (
    REPO / "fashion_research_dir" / "k_rewrite_instructions_2026-09-29" / "source_corpus.jsonl"
)
DEFAULT_SEASON = (
    REPO / "fashion_research_dir" / "season_themes_2026-09" / "source_corpus_gpt54mini_keep.jsonl"
)
DEFAULT_MILD = (
    REPO
    / "fashion_research_dir"
    / "season_themes_2026-09"
    / "mild_defect_from_keep"
    / "source_corpus_mild_defect_192.jsonl"
)
DEFAULT_OUT = REPO / "training" / "runs" / "corpus" / "source_corpus_2000.jsonl"

# 写入语料行时保留的字段；分类只靠 sample_kind
_KEEP_KEYS = (
    "source_id",
    "role",
    "sample_kind",
    "path",
    "text",
    "business_context",
    "house",
    "season",
    "theme",
    "brand_dir",
    "chapter",
    "look",
)


def _extract_inverse(md_text: str) -> str:
    body = md_text.replace("\r\n", "\n")
    m = _TEXT_DESC_RE.search(body)
    if m:
        return m.group(1).strip()
    paras = [
        p.strip()
        for p in re.split(r"\n\s*\n", body)
        if p.strip() and not p.strip().startswith("#")
    ]
    return paras[0] if paras else body.strip()


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _as_kind(kind: str) -> str:
    raw = (kind or "").strip()
    if raw in (KIND_INVERSE, "逆解析"):
        return KIND_INVERSE
    return KIND_GENERATED


def _normalize_row(row: dict[str, Any], *, kind: str) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key in _KEEP_KEYS:
        if key in row and row[key] is not None:
            out[key] = row[key]
    out["role"] = "source"
    out["sample_kind"] = _as_kind(kind)
    if "source_id" not in out or "text" not in out:
        raise ValueError(f"row missing source_id/text: {row.get('source_id')}")
    return out


def iter_inverse_batch2(root: Path, limit: int = 800) -> list[dict[str, Any]]:
    files = sorted(root.rglob("*_text_description.md"))
    rows: list[dict[str, Any]] = []
    for i, path in enumerate(files, start=1):
        if len(rows) >= limit:
            break
        text = _extract_inverse(path.read_text(encoding="utf-8"))
        if not text:
            continue
        rel = str(path.relative_to(REPO)).replace("\\", "/")
        rows.append(
            _normalize_row(
                {
                    "source_id": f"inv_batch2_{i:04d}_{path.stem[:64]}",
                    "path": rel,
                    "text": text,
                    "business_context": (
                        "Runway inverse parse. Preserve identifying design "
                        "(surface field, edge-path trim, inner garment when outer is open). "
                        "Rewrite into one grounded T2I paragraph if needed."
                    ),
                },
                kind=KIND_INVERSE,
            )
        )
    return rows


def pack(
    *,
    inverse_dir: Path,
    k_rewrite: Path,
    season: Path,
    mild: Path,
    out_path: Path,
) -> dict[str, Any]:
    inv = iter_inverse_batch2(inverse_dir, limit=800)
    kr = [_normalize_row(r, kind=str(r.get("sample_kind") or KIND_INVERSE)) for r in _load_jsonl(k_rewrite)]
    sea = [_normalize_row(r, kind=KIND_GENERATED) for r in _load_jsonl(season)]
    mild_rows = [_normalize_row(r, kind=KIND_GENERATED) for r in _load_jsonl(mild)]

    if len(inv) != 800:
        raise SystemExit(f"inverse batch2 expected 800, got {len(inv)}")
    if len(kr) != 400:
        raise SystemExit(f"k_rewrite expected 400, got {len(kr)}")
    if len(sea) != 608:
        raise SystemExit(f"season expected 608, got {len(sea)}")
    if len(mild_rows) != 192:
        raise SystemExit(f"mild defect expected 192, got {len(mild_rows)}")

    packed = inv + kr + sea + mild_rows
    if len(packed) != 2000:
        raise SystemExit(f"expected 2000, got {len(packed)}")

    kinds = {KIND_INVERSE: 0, KIND_GENERATED: 0}
    for row in packed:
        kinds[row["sample_kind"]] += 1
        if row["sample_kind"] not in (KIND_INVERSE, KIND_GENERATED):
            raise SystemExit(f"illegal sample_kind: {row['sample_kind']}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for row in packed:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    mirror = (
        REPO
        / "fashion_research_dir"
        / "season_themes_2026-09"
        / "source_corpus_combined_2000.jsonl"
    )
    mirror.write_text(out_path.read_text(encoding="utf-8"), encoding="utf-8")

    manifest = {
        "n_total": len(packed),
        "n_inverse": kinds[KIND_INVERSE],
        "n_generated": kinds[KIND_GENERATED],
        "sample_kind_values": [KIND_INVERSE, KIND_GENERATED],
        "out": str(out_path.relative_to(REPO)).replace("\\", "/"),
        "mirror": str(mirror.relative_to(REPO)).replace("\\", "/"),
        "note": (
            "语料库只区分两类 sample_kind：inverse（逆解析）与 生成型。"
            "组成：batch2 逆解析 800 + k_rewrite 400 + season keep 608 + 同子主题轻缺陷 192。"
        ),
    }
    out_path.with_suffix(".manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return manifest


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--inverse-dir", type=Path, default=DEFAULT_INVERSE_DIR)
    ap.add_argument("--k-rewrite", type=Path, default=DEFAULT_K_REWRITE)
    ap.add_argument("--season", type=Path, default=DEFAULT_SEASON)
    ap.add_argument("--mild", type=Path, default=DEFAULT_MILD)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    print(
        json.dumps(
            pack(
                inverse_dir=args.inverse_dir,
                k_rewrite=args.k_rewrite,
                season=args.season,
                mild=args.mild,
                out_path=args.out,
            ),
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
