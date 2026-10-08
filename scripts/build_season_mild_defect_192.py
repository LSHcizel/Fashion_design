"""从 season gpt54mini_keep look 抽样，同子主题注入绑定矛盾/重复绑定等轻缺陷，产出 192 条。"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from plugins.text_description_evaluator.design_text_evaluator_api import (  # noqa: E402
    detect_consistency_conflicts,
)

DEFAULT_SEASON_CORPUS = (
    REPO / "fashion_research_dir" / "season_themes_2026-09" / "source_corpus_gpt54mini_keep.jsonl"
)
DEFAULT_OUT_DIR = (
    REPO / "fashion_research_dir" / "season_themes_2026-09" / "mild_defect_from_keep"
)
DEFAULT_N = 192

PREAMBLE_MARKER = "No collage, no flat lay"

# 每条只注入一处轻缺陷（detector: active 且非 severe）
DEFECT_TEMPLATES: list[dict[str, str]] = [
    {
        "defect": "binding_shell",
        "defect_zh": "同一件外壳面料重复绑定：正文已有面料，又写成黑缎",
        "suffix": " The same shell is liquid black satin.",
    },
    {
        "defect": "binding_neckline",
        "defect_zh": "同一领口重复绑定：已有领型，又写成深V",
        "suffix": " The same neckline drops in a deep V to the waist.",
    },
    {
        "defect": "binding_jacket",
        "defect_zh": "同一件外套重复绑定：已有表面，又写成素羊毛无绣",
        "suffix": " The same jacket is plain black wool with no embroidery.",
    },
    {
        "defect": "binding_double",
        "defect_zh": "同一件外套重复绑定：已有门襟，又写成双排扣",
        "suffix": " The same jacket is double-breasted with two columns of buttons.",
    },
    {
        "defect": "or_shoe",
        "defect_zh": "鞋品类 or 并列：高跟与平底不能同时穿",
        "suffix": " The feet are a black satin pump or an ivory leather flat.",
    },
    {
        "defect": "or_bottom",
        "defect_zh": "下装品类 or 并列：裙与裤不能同时穿",
        "suffix": " The lower half is a black nylon skirt or a grey wool trouser.",
    },
    {
        "defect": "lr_sleeve",
        "defect_zh": "左右袖面料不一致",
        "suffix": (
            " The left sleeve is a long wool sleeve in the cloth. "
            "The right sleeve is a long silk sleeve in plain ivory."
        ),
    },
    {
        "defect": "sleeve_state",
        "defect_zh": "袖型两套：一侧长袖一侧无袖",
        "suffix": (
            " A long set-in sleeve covers one arm to the wrist. The other side is sleeveless."
        ),
    },
    {
        "defect": "length_conflict",
        "defect_zh": "同一件外套两个长度：及臀又及腰",
        "suffix": " The jacket is hip-length and cropped to the waist.",
    },
]


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _body_len(text: str) -> int:
    i = text.find(PREAMBLE_MARKER)
    if i < 0:
        return len(text.strip())
    return len(text[i + len(PREAMBLE_MARKER) :].strip())


def _chapter_theme_line(src_path: str) -> str:
    """同子主题：读取同 chapter 的 design_chapter 首行作 Theme。"""
    path = REPO / src_path
    chapter_dir = path.parent
    design = chapter_dir / "design_chapter.txt"
    if not design.is_file():
        return ""
    for line in design.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s:
            return s[:160]
    return ""


def _eligible(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows:
        text = str(row.get("text") or "").strip()
        if _body_len(text) < 200:
            continue
        found = detect_consistency_conflicts(text)
        if found["active"]:
            continue
        out.append(row)
    return out


def _pick_192(eligible: list[dict[str, Any]], n: int) -> list[dict[str, Any]]:
    """优先每品牌每 chapter（同子主题）取 1 条，再补齐到 n。"""
    by_bucket: dict[tuple[str, int], list[dict[str, Any]]] = {}
    for row in eligible:
        key = (str(row.get("brand_dir") or ""), int(row.get("chapter") or 0))
        by_bucket.setdefault(key, []).append(row)

    picked: list[dict[str, Any]] = []
    used_ids: set[str] = set()
    for key in sorted(by_bucket.keys()):
        if len(picked) >= n:
            break
        row = by_bucket[key][0]
        sid = str(row["source_id"])
        if sid in used_ids:
            continue
        picked.append(row)
        used_ids.add(sid)

    # 补齐：按 brand/chapter/look 轮转取剩余
    rest = [r for r in eligible if str(r["source_id"]) not in used_ids]
    rest.sort(
        key=lambda r: (
            str(r.get("brand_dir") or ""),
            int(r.get("chapter") or 0),
            int(r.get("look") or 0),
        )
    )
    for row in rest:
        if len(picked) >= n:
            break
        picked.append(row)
        used_ids.add(str(row["source_id"]))

    if len(picked) < n:
        raise SystemExit(f"only {len(picked)} eligible looks, need {n}")
    return picked[:n]


def _inject(text: str, template: dict[str, str]) -> str | None:
    candidate = text.rstrip() + template["suffix"]
    found = detect_consistency_conflicts(candidate)
    if found["active"] and not found["severe"]:
        return candidate
    return None


def _business_context(row: dict[str, Any], defect_zh: str) -> str:
    house = str(row.get("house") or "")
    season = str(row.get("season") or "")
    theme = str(row.get("theme") or "")
    return (
        f"{house} {season}. Theme: {theme}. "
        f"Same subtheme/chapter as the source look. "
        f"The source has one slight consistency or binding conflict: {defect_zh}. "
        "Keep the theme and concept named in SOURCE. "
        "Delete the conflict in SOURCE: a left-right split on one zone, a second binding on the same "
        "garment, an or-choice between two garments, or a second sleeve state. "
        "Do not keep the deleted binding as an inner layer. "
        "Write the rewrite in English. Do not invent another house's logo."
    )


def build(*, season_corpus: Path, out_dir: Path, n: int) -> dict[str, Any]:
    rows = _load_jsonl(season_corpus)
    eligible = _eligible(rows)
    picked = _pick_192(eligible, n)

    out_dir.mkdir(parents=True, exist_ok=True)
    text_dir = out_dir / "texts"
    text_dir.mkdir(parents=True, exist_ok=True)

    out_rows: list[dict[str, Any]] = []
    failed: list[str] = []

    for i, src in enumerate(picked):
        tmpl = DEFECT_TEMPLATES[i % len(DEFECT_TEMPLATES)]
        text = str(src["text"]).strip()
        injected = _inject(text, tmpl)
        if injected is None:
            # 轮转模板直到命中轻缺陷
            for alt in DEFECT_TEMPLATES:
                injected = _inject(text, alt)
                if injected is not None:
                    tmpl = alt
                    break
        if injected is None:
            failed.append(str(src["source_id"]))
            continue

        idx = len(out_rows) + 1
        brand = re.sub(r"[^\w]+", "_", str(src.get("brand_dir") or "brand")).strip("_")
        chapter = int(src.get("chapter") or 0)
        look = int(src.get("look") or 0)
        fname = f"{idx:03d}_{brand}_c{chapter:02d}_l{look:02d}_{tmpl['defect']}.txt"
        rel = f"fashion_research_dir/season_themes_2026-09/mild_defect_from_keep/texts/{fname}"
        (text_dir / fname).write_text(injected + "\n", encoding="utf-8")

        chapter_theme = _chapter_theme_line(str(src.get("path") or ""))
        out_rows.append(
            {
                "source_id": f"mild_season_{idx:03d}_{brand}_c{chapter:02d}_l{look:02d}",
                "role": "source",
                "sample_kind": "生成型",
                "path": rel,
                "text": injected,
                "house": src.get("house"),
                "season": src.get("season"),
                "theme": src.get("theme"),
                "brand_dir": src.get("brand_dir"),
                "chapter": chapter,
                "look": look,
                "chapter_theme": chapter_theme,
                "parent_source_id": src.get("source_id"),
                "defect": tmpl["defect"],
                "defect_zh": tmpl["defect_zh"],
                "business_context": _business_context(src, tmpl["defect_zh"]),
            }
        )

    if failed:
        raise SystemExit(f"inject failed for {len(failed)} rows: {failed[:8]}")
    if len(out_rows) != n:
        raise SystemExit(f"expected {n} rows, got {len(out_rows)}")

    # detector 复核
    bad = []
    for row in out_rows:
        found = detect_consistency_conflicts(row["text"])
        if not found["active"] or found["severe"]:
            bad.append((row["source_id"], found))
    if bad:
        raise SystemExit(f"{len(bad)} cases inactive or severe: {bad[:3]}")

    corpus_path = out_dir / "source_corpus_mild_defect_192.jsonl"
    with corpus_path.open("w", encoding="utf-8") as f:
        for row in out_rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    mirror = REPO / "training" / "runs" / "corpus" / "season_mild_defect_192.jsonl"
    mirror.parent.mkdir(parents=True, exist_ok=True)
    mirror.write_text(corpus_path.read_text(encoding="utf-8"), encoding="utf-8")

    defect_counts: dict[str, int] = {}
    for row in out_rows:
        defect_counts[str(row["defect"])] = defect_counts.get(str(row["defect"]), 0) + 1

    manifest = {
        "n_total": len(out_rows),
        "n_eligible_pool": len(eligible),
        "parent_corpus": str(season_corpus.relative_to(REPO)).replace("\\", "/"),
        "corpus_jsonl": str(corpus_path.relative_to(REPO)).replace("\\", "/"),
        "mirror_jsonl": str(mirror.relative_to(REPO)).replace("\\", "/"),
        "note": (
            "192 条同子主题（同 brand×chapter）轻缺陷描述，由 gpt54mini_keep look 注入："
            "绑定矛盾、重复绑定、or 并列品类、左右袖分裂、双袖态等；每条仅一处，detector 非 severe。"
        ),
        "defect_counts": defect_counts,
        "cases": [
            {
                "source_id": r["source_id"],
                "parent_source_id": r["parent_source_id"],
                "brand_dir": r["brand_dir"],
                "chapter": r["chapter"],
                "look": r["look"],
                "defect": r["defect"],
                "path": r["path"],
            }
            for r in out_rows
        ],
    }
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return manifest


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--season-corpus", type=Path, default=DEFAULT_SEASON_CORPUS)
    ap.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    ap.add_argument("--n", type=int, default=DEFAULT_N)
    args = ap.parse_args()
    manifest = build(season_corpus=args.season_corpus, out_dir=args.out_dir, n=args.n)
    print(json.dumps({k: manifest[k] for k in ("n_total", "n_eligible_pool", "defect_counts", "corpus_jsonl")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
