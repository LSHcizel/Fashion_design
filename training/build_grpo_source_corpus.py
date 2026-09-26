"""Build GRPO source corpus: inverse descriptions (positive) + workflow looks (negative)."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

REPO = Path(__file__).resolve().parents[1]
DEFAULT_POSITIVE_DIR = (
    REPO / "fashion_research_dir" / "wgsn_batch_image_inverse" / "20260524T044337Z"
)
DEFAULT_NEGATIVE_DIRS = [
    REPO / "fashion_research_dir" / "workflow_0" / "2026-06-06",
    REPO / "fashion_research_dir" / "workflow_0" / "2026-04-02",
]
DEFAULT_OUT = REPO / "training" / "runs" / "corpus" / "source_corpus.jsonl"
DEFAULT_CONSISTENCY_DIR = REPO / "fashion_research_dir" / "consistency_defect_cases"

_TEXT_DESC_RE = re.compile(
    r"^##\s*text_description\s*\n+(.*?)(?=\n##\s|\Z)",
    re.IGNORECASE | re.DOTALL,
)


def extract_inverse_text_description(md_text: str) -> str:
    body = md_text.replace("\r\n", "\n")
    m = _TEXT_DESC_RE.search(body)
    if m:
        return m.group(1).strip()
    # fallback: first non-heading paragraph
    paras = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip() and not p.strip().startswith("#")]
    return paras[0] if paras else body.strip()


def iter_positive_sources(root: Path) -> Iterable[Dict[str, Any]]:
    files = sorted(root.glob("*_text_description.md"))
    for i, path in enumerate(files, start=1):
        text = extract_inverse_text_description(path.read_text(encoding="utf-8"))
        if not text:
            continue
        yield {
            "source_id": f"pos_{i:03d}_{path.stem[:80]}",
            "role": "positive",
            "path": str(path.relative_to(REPO)).replace("\\", "/"),
            "text": text,
            "business_context": (
                "Chanel Cruise / Pre-Summer 2027 look. Preserve identifying design "
                "(surface field, edge-path trim, inner garment readable when outer is open). "
                "Do not collapse into a collection-shared interchangeable garment formula."
            ),
        }


def iter_negative_look_txt(root: Path) -> Iterable[Path]:
    # Prefer chapter look_*.txt; skip reflections / eliminated copies.
    for path in sorted(root.rglob("look_*.txt")):
        name = path.name.lower()
        if "reflection" in name or "eliminated" in name:
            continue
        # skip looks_original if a sibling chapter look exists with same stem? keep both:
        # original drafts are also series-formula negatives.
        rel = path.as_posix()
        if "/text_eval_scores/" in rel:
            continue
        yield path


def iter_negative_sources(roots: List[Path]) -> Iterable[Dict[str, Any]]:
    n = 0
    for root in roots:
        if not root.is_dir():
            continue
        for path in iter_negative_look_txt(root):
            n += 1
            text = path.read_text(encoding="utf-8").strip()
            if not text:
                continue
            yield {
                "source_id": f"neg_{n:03d}_{root.name}_{path.parent.name}_{path.stem}",
                "role": "negative",
                "path": str(path.relative_to(REPO)).replace("\\", "/"),
                "text": text,
                "business_context": (
                    "This draft uses a collection-shared wardrobe grammar "
                    "(interchangeable trunk formula, numbered sections, "
                    "theme dualities). Rewrite into one grounded T2I paragraph. "
                    "Do not invent unstated garments. Do not keep a shared series formula "
                    "as the identifying idea."
                ),
            }


def build_corpus(
    *,
    positive_dir: Path,
    negative_dirs: List[Path],
    out_path: Path,
) -> Dict[str, int]:
    rows: List[Dict[str, Any]] = []
    rows.extend(iter_positive_sources(positive_dir))
    n_pos = sum(1 for r in rows if r["role"] == "positive")
    rows.extend(iter_negative_sources(negative_dirs))
    n_neg = sum(1 for r in rows if r["role"] == "negative")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return {"n_positive": n_pos, "n_negative": n_neg, "n_total": len(rows), "out": str(out_path)}


def load_corpus(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def bootstrap_identity_sft(
    corpus_path: Path,
    out_path: Path,
    *,
    system_prompt_path: Optional[Path] = None,
) -> int:
    """SFT seeds: positive inverse texts as identity rewrites (keep good prompts)."""
    sys_text = ""
    if system_prompt_path and system_prompt_path.is_file():
        sys_text = system_prompt_path.read_text(encoding="utf-8").strip()
    n = 0
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for row in load_corpus(corpus_path):
            if row.get("role") != "positive":
                continue
            text = str(row.get("text") or "").strip()
            biz = str(row.get("business_context") or "").strip()
            if not text:
                continue
            user_parts = []
            if biz:
                user_parts.append(f"[Business context]\n{biz}")
            user_parts.append(f"[Source text to rewrite]\n{text}")
            messages = []
            if sys_text:
                messages.append({"role": "system", "content": sys_text})
            messages.append({"role": "user", "content": "\n\n".join(user_parts)})
            messages.append({"role": "assistant", "content": text})
            rec = {
                "schema_version": "sft_phase_a_v1",
                "phase": "A_SFT",
                "group_id": row["source_id"],
                "role": "positive_identity",
                "messages": messages,
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            n += 1
    return n


def iter_consistency_defect_sources(root: Path) -> Iterable[Dict[str, Any]]:
    """18 条一致性负例：角色为 negative，供 K 路采集直接读取。"""
    manifest_by_file: Dict[str, Dict[str, Any]] = {}
    man = root / "manifest.json"
    if man.is_file():
        data = json.loads(man.read_text(encoding="utf-8"))
        for case in data.get("cases") or []:
            if isinstance(case, dict) and case.get("file"):
                manifest_by_file[str(case["file"])] = case
    files = sorted(p for p in root.glob("[0-9][0-9]_*.txt") if p.is_file())
    for path in files:
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            continue
        meta = manifest_by_file.get(path.name, {})
        theme = str(meta.get("theme") or "").strip()
        concept = str(meta.get("concept") or "").strip()
        defect = str(meta.get("defect_zh") or meta.get("defect") or "").strip()
        yield {
            "source_id": f"consistency_{path.stem}",
            "role": "negative",
            "path": str(path.relative_to(REPO)).replace("\\", "/"),
            "text": text,
            "business_context": (
                "Consistency-defect look. "
                f"Stated theme: {theme}. Stated concept: {concept}. Defect: {defect}. "
                "Keep that stated theme and concept. "
                "Clear stacked left-right trunk splits, same-element contradictions, "
                "and any garment that belongs to a different theme or concept."
            ),
        }


def build_consistency_corpus(root: Path, out_path: Path) -> Dict[str, int]:
    rows = list(iter_consistency_defect_sources(root))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return {"n_total": len(rows), "out": str(out_path)}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--positive-dir", type=Path, default=DEFAULT_POSITIVE_DIR)
    p.add_argument("--negative-dir", type=Path, action="append", default=None)
    p.add_argument("--out", type=Path, default=DEFAULT_OUT)
    p.add_argument(
        "--consistency-dir",
        type=Path,
        default=None,
        help="只把该目录下的一致性负例写成 K 路语料，不混入逆解析正样本",
    )
    p.add_argument(
        "--sft-out",
        type=Path,
        default=REPO / "training" / "runs" / "corpus" / "phase_a_sft_identity.jsonl",
    )
    p.add_argument(
        "--system-prompt-file",
        type=Path,
        default=REPO / "plugins" / "text_description_evaluator" / "fashion_sys_prompt.txt",
    )
    args = p.parse_args()
    if args.consistency_dir is not None:
        root = args.consistency_dir
        out = args.out if args.out != DEFAULT_OUT else root / "source_corpus.jsonl"
        stats = build_consistency_corpus(root, out)
        print(json.dumps(stats, ensure_ascii=False, indent=2))
        return
    neg_dirs = args.negative_dir or DEFAULT_NEGATIVE_DIRS
    stats = build_corpus(positive_dir=args.positive_dir, negative_dirs=neg_dirs, out_path=args.out)
    n_sft = bootstrap_identity_sft(args.out, args.sft_out, system_prompt_path=args.system_prompt_file)
    stats["n_identity_sft"] = n_sft
    stats["sft_out"] = str(args.sft_out)
    print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
