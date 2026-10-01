"""唯一 K 路语料的路径。采集、在线轮和原文补分都从这里读。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

REPO = Path(__file__).resolve().parents[1]
FALLBACK_CORPUS = (
    REPO
    / "fashion_research_dir"
    / "k_rewrite_instructions_2026-09-29"
    / "source_corpus.jsonl"
)


def default_corpus_path() -> Path:
    """``fashion_config.yaml`` → ``grpo.corpus``，缺省为上面的 jsonl。"""
    rel = ""
    try:
        import yaml

        cfg = yaml.safe_load((REPO / "fashion_config.yaml").read_text(encoding="utf-8")) or {}
        raw = (cfg.get("grpo") or {}).get("corpus") or ""
        rel = str(raw).strip()
    except Exception:
        rel = ""
    if not rel:
        return FALLBACK_CORPUS
    path = Path(rel)
    if not path.is_absolute():
        path = REPO / path
    return path


def load_corpus_rows(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with Path(path).open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def corpus_texts(rows: List[Dict[str, Any]]) -> Dict[str, str]:
    """source_id → 原文。后出现的同号覆盖先出现的。"""
    out: Dict[str, str] = {}
    for rec in rows:
        sid = str(rec.get("source_id") or "").strip()
        text = str(rec.get("text") or "").strip()
        if sid and text:
            out[sid] = text
    return out
