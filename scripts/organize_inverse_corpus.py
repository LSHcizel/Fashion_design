#!/usr/bin/env python3
"""Classify / index inverse-parse text_description corpus by brand.

Writes:
  - brand_index.json / brand_index.md  (counts + sample paths per brand)
  - by_brand/<brand>/*.md soft-links or copied stubs (copy of md pointers)
  - corpus_catalog.jsonl              (one row per description)
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

DEFAULT_SOURCES = [
    REPO_ROOT / "fashion_research_dir/image_inverse/20260524T044337Z",
    REPO_ROOT / "fashion_research_dir/image_inverse/vogue_cn_fw26",
    REPO_ROOT / "fashion_research_dir/image_inverse/vogue_cn_fw26_batch2",
    REPO_ROOT / "fashion_research_dir/image_inverse/web_brand_ss26",
]


def infer_brand(path: Path, text: str = "") -> str:
    name = path.name.lower()
    # vogue style: brand_fw26_00001_text_description.md
    m = re.match(r"^([a-z0-9.\-]+)_(?:fw|ss|aw|cruise|ps|pre)\d{2}_", name)
    if m:
        return normalize_brand(m.group(1))
    m = re.match(r"^([a-z0-9.\-]+)_ss\d{2}_", name)
    if m:
        return normalize_brand(m.group(1))
    # Chanel WGSN dump
    if "chanel" in name:
        return "chanel"
    # web_brand: brand_ss26_motif_text_description.md
    m = re.match(r"^([a-z0-9.\-]+)_", name)
    if m and "text_description" in name:
        return normalize_brand(m.group(1))
    # fallback from body Source brand line
    m = re.search(r"(?im)^brand:\s*(.+)$", text)
    if m:
        return normalize_brand(m.group(1).strip())
    return "unknown"


def normalize_brand(raw: str) -> str:
    s = raw.strip().lower().replace(" ", "-").replace("&", "and").replace("'", "")
    aliases = {
        "alaia": "azzedine-alaia",
        "azzedine-alaia": "azzedine-alaia",
        "therow": "the-row",
        "the-row": "the-row",
        "row": "the-row",
        "dior": "christian-dior",
        "christian-dior": "christian-dior",
        "ysl": "saint-laurent",
        "saint-laurent": "saint-laurent",
        "cdg": "comme-des-garcons",
        "comme-des-garcons": "comme-des-garcons",
        "3.1-phillip-lim": "3-1-phillip-lim",
        "schiaparelli": "schiaparelli",
        "hermès": "hermes",
        "chloé": "chloe",
        "céline": "celine",
    }
    return aliases.get(s, s)


def collect_mds(sources: list[Path]) -> list[Path]:
    files: list[Path] = []
    for src in sources:
        if not src.exists():
            continue
        # prefer nested text/ folder if present, else top-level
        text_dir = src / "text"
        roots = [text_dir] if text_dir.is_dir() else [src]
        for root in roots:
            for p in sorted(root.rglob("*_text_description.md")):
                # skip score reports
                if "text_description_scores" in str(p) or p.name.endswith("_report.md"):
                    continue
                files.append(p)
        # also top-level for Chanel dump
        if text_dir.is_dir():
            for p in sorted(src.glob("*_text_description.md")):
                files.append(p)
    # dedupe by resolved path
    uniq = []
    seen = set()
    for p in files:
        key = str(p.resolve())
        if key in seen:
            continue
        seen.add(key)
        uniq.append(p)
    return uniq


def read_preview(path: Path, n: int = 240) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    # grab main paragraph after title if possible
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    body = " ".join(lines[1:4]) if len(lines) > 1 else " ".join(lines)
    return body[:n]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Organize inverse corpus by brand")
    p.add_argument(
        "--out-dir",
        type=Path,
        default=REPO_ROOT / "fashion_research_dir/image_inverse/_corpus_by_brand",
    )
    p.add_argument("--source", action="append", default=[], help="source dirs (repeatable)")
    p.add_argument("--copy-samples", type=int, default=3, help="每品牌复制样例 md 数")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    sources = [Path(s) for s in args.source] if args.source else DEFAULT_SOURCES
    sources = [s if s.is_absolute() else REPO_ROOT / s for s in sources]
    out_dir: Path = args.out_dir if args.out_dir.is_absolute() else REPO_ROOT / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    by_brand_dir = out_dir / "by_brand"
    if by_brand_dir.exists():
        shutil.rmtree(by_brand_dir)
    by_brand_dir.mkdir(parents=True, exist_ok=True)

    files = collect_mds(sources)
    groups: dict[str, list[Path]] = defaultdict(list)
    catalog = []
    for p in files:
        text = p.read_text(encoding="utf-8", errors="replace")
        brand = infer_brand(p, text)
        groups[brand].append(p)
        # source batch
        batch = "unknown"
        for src in sources:
            try:
                p.relative_to(src)
                batch = src.name
                break
            except ValueError:
                continue
        catalog.append(
            {
                "brand": brand,
                "path": str(p.relative_to(REPO_ROOT)).replace("\\", "/"),
                "batch": batch,
                "preview": read_preview(p),
            }
        )

    # copy samples
    for brand, paths in groups.items():
        bdir = by_brand_dir / brand
        bdir.mkdir(parents=True, exist_ok=True)
        for p in paths[: max(1, args.copy_samples)]:
            dest = bdir / p.name
            shutil.copy2(p, dest)

    brand_index = {
        "total_descriptions": len(files),
        "n_brands": len(groups),
        "brands": {
            b: {
                "count": len(ps),
                "samples": [
                    str(x.relative_to(REPO_ROOT)).replace("\\", "/")
                    for x in ps[: max(1, args.copy_samples)]
                ],
            }
            for b, ps in sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0]))
        },
        "sources": [str(s.relative_to(REPO_ROOT)).replace("\\", "/") for s in sources if s.exists()],
    }
    (out_dir / "brand_index.json").write_text(
        json.dumps(brand_index, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    with (out_dir / "corpus_catalog.jsonl").open("w", encoding="utf-8") as f:
        for row in catalog:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    # markdown summary
    lines = [
        "# 逆解析语料 · 品牌分类索引",
        "",
        f"- 描述总数：**{len(files)}**",
        f"- 品牌数：**{len(groups)}**",
        f"- 样例目录：`{by_brand_dir.relative_to(REPO_ROOT).as_posix()}/<brand>/`",
        "",
        "| 品牌 | n | 样例 |",
        "|---|---:|---|",
    ]
    for b, ps in sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        sample = ps[0].name if ps else ""
        lines.append(f"| {b} | {len(ps)} | `{sample}` |")
    zero_note = []
    expected = [
        "chanel",
        "christian-dior",
        "gucci",
        "balenciaga",
        "loewe",
        "azzedine-alaia",
        "the-row",
        "schiaparelli",
        "prada",
        "louis-vuitton",
        "saint-laurent",
        "hermes",
        "fendi",
        "bottega-veneta",
    ]
    missing = [b for b in expected if b not in groups]
    if missing:
        lines += ["", "## 热门品牌缺口", "", ", ".join(missing)]
    (out_dir / "brand_index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out_dir / 'brand_index.md'} brands={len(groups)} total={len(files)}")
    if missing:
        print("missing hot brands:", ", ".join(missing))


if __name__ == "__main__":
    main()
