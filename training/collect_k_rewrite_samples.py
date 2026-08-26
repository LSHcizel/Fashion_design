"""K-rewrite sampling for GRPO: rewrite via rewriter-llm, score via frozen base 7B."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from plugins.parallel_k_rewrite import generate_k_parallel_rewrites
from plugins.text_description_evaluator.design_text_evaluator_api import (
    DesignTextEvaluator,
    load_default_evaluator,
)
from training.build_grpo_source_corpus import DEFAULT_OUT as DEFAULT_CORPUS
from training.jsonl_logger import TrainingRunLogger
from training.record_builder import sha256_text


def _load_corpus(path: Path, *, roles: Optional[List[str]], limit: int) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if roles and rec.get("role") not in roles:
                continue
            rows.append(rec)
            if limit > 0 and len(rows) >= limit:
                break
    return rows


def _inject_original_as_candidate(
    evaluator: DesignTextEvaluator,
    parallel_result: Dict[str, Any],
    source_text: str,
    *,
    source_name: str,
) -> None:
    """Keep the unrevised draft in the group as a low-reward contrast (negatives)."""
    ev = evaluator.evaluate_text(source_text, source_name=source_name)
    cands = list(parallel_result.get("candidates") or [])
    cands.append(
        {
            "candidate_index": -1,
            "text": source_text,
            "temperature": 0.0,
            "dedupe_kept": True,
            "evaluation": ev,
            "error": None,
            "injected_original": True,
        }
    )
    parallel_result["candidates"] = cands


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    p.add_argument("--run-id", type=str, default="grpo_chanel_inverse_v1")
    p.add_argument("--k", type=int, default=None)
    p.add_argument("--limit", type=int, default=0, help="0 = all sources")
    p.add_argument("--roles", type=str, default="positive,negative")
    p.add_argument("--start", type=int, default=0)
    p.add_argument(
        "--no-inject-original-negatives",
        action="store_true",
        help="Do not add the original negative draft as an extra group member",
    )
    p.add_argument(
        "--system-prompt-file",
        type=Path,
        default=REPO / "plugins" / "text_description_evaluator" / "fashion_sys_prompt.txt",
    )
    args = p.parse_args()
    inject_neg = not args.no_inject_original_negatives
    roles = [x.strip() for x in args.roles.split(",") if x.strip()]
    corpus = _load_corpus(args.corpus, roles=roles, limit=0)
    corpus = corpus[args.start :]
    if args.limit > 0:
        corpus = corpus[: args.limit]
    if not corpus:
        raise SystemExit(f"no sources in {args.corpus}")

    sys_hash = None
    if args.system_prompt_file.is_file():
        sys_hash = sha256_text(args.system_prompt_file.read_text(encoding="utf-8"))

    evaluator = load_default_evaluator()
    logger = TrainingRunLogger(args.run_id)
    print(f"run_dir={logger.run_dir} n_sources={len(corpus)} jsonl={logger.path()}")

    for i, src in enumerate(corpus, start=1):
        sid = str(src.get("source_id") or f"src_{i}")
        text = str(src.get("text") or "").strip()
        biz = str(src.get("business_context") or "")
        role = str(src.get("role") or "")
        print(f"[{i}/{len(corpus)}] {role} {sid}")
        result = generate_k_parallel_rewrites(
            text,
            k=args.k,
            evaluator=evaluator,
            group_id=sid,
            extra_context=biz,
        )
        if inject_neg and role == "negative":
            _inject_original_as_candidate(
                evaluator,
                result,
                text,
                source_name=f"{sid}.original",
            )
        logger.append_parallel_result(
            result,
            context={
                "shared_source_text": text,
                "business_context": biz,
                "source_role": role,
                "source_path": src.get("path"),
                "instruction_summary": "Rewrite the look into a grounded T2I fashion prompt.",
                "system_prompt_label": "fashion_sys_prompt.txt",
            },
            system_prompt_sha256=sys_hash,
        )
    print("done", logger.path())


if __name__ == "__main__":
    main()
