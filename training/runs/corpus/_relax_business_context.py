"""把语料 business_context 里收紧改写的句子换成适度新增。"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
FILES = [
    ROOT / "training/runs/corpus/source_corpus_2000.jsonl",
    ROOT / "training/runs/corpus/season_themes_gpt54mini_keep.jsonl",
    ROOT / "training/runs/corpus/season_mild_defect_192.jsonl",
    ROOT / "training/runs/corpus/source_corpus.jsonl",
]
REPLACEMENTS = [
    (
        "Preserve identifying design (surface field, edge-path trim, inner garment when outer is open). "
        "Rewrite into one grounded T2I paragraph if needed.",
        "Keep the theme and the identifying features. "
        "A moderate new element that fits this brand and this theme is allowed. "
        "Rewrite into one T2I paragraph if needed.",
    ),
    (
        "Preserve identifying design (surface field, edge-path trim, inner garment readable when outer is open). ",
        "Keep the theme and the identifying features. "
        "A moderate new element that fits this brand and this theme is allowed. ",
    ),
    (
        "Preserve identifying design inside this house theme; "
        "rewrite into one grounded T2I paragraph if used for K-rewrite training.",
        "Keep the theme and the identifying features. "
        "A moderate new element that fits this brand and this theme is allowed. "
        "Rewrite into one T2I paragraph if used for K-rewrite training.",
    ),
    (
        "Rewrite into one grounded T2I paragraph. Do not invent unstated garments. ",
        "Rewrite into one T2I paragraph. "
        "A moderate new element that fits this brand and this theme is allowed. ",
    ),
    (
        "Delete the conflict in SOURCE: a left-right split on one zone, a second binding on the same "
        "garment, an or-choice between two garments, or a second sleeve state. "
        "Do not keep the deleted binding as an inner layer. ",
        "Resolve that slight conflict into the one outfit. "
        "A moderate new element that fits this brand and this theme is allowed. ",
    ),
    (
        "Delete the conflict in SOURCE: a left-right garment split, a same-element contradiction, "
        "or a garment from a different theme or concept. "
        "Do not keep the deleted garment as an inner layer. ",
        "Resolve a conflict in SOURCE when one is present: a left-right garment split, "
        "a same-element contradiction, or a garment from a different theme or concept. "
        "A moderate new element that fits this brand and this theme is allowed. ",
    ),
]


def main() -> None:
    for path in FILES:
        if not path.is_file():
            print("missing", path)
            continue
        text = path.read_text(encoding="utf-8")
        counts = []
        for old, new in REPLACEMENTS:
            n = text.count(old)
            if n:
                text = text.replace(old, new)
            counts.append(n)
        path.write_text(text, encoding="utf-8")
        left = sum(text.count(s) for s in (
            "Preserve identifying design",
            "Do not invent unstated garments",
            "Delete the conflict in SOURCE",
            "grounded T2I",
        ))
        print(path.name, "replaced", counts, "left", left)


if __name__ == "__main__":
    main()
