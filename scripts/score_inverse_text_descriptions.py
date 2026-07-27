#!/usr/bin/env python3
"""
对逆解析输出的 ``*_text_description.md`` 提取 ``## text_description`` 正文，
调用 ``plugins/text_description_evaluator``（``DesignTextEvaluator``）进行与主流程一致的 LLM-as-judge 打分，
写入 JSONL / 汇总 JSON。

鉴权：继承 ``fashion_config.yaml`` → ``grpo.design-text-evaluator``（api-key/api-base/model 等）。

在仓库根目录执行::

    python scripts/score_inverse_text_descriptions.py \\
      --inverse-dir fashion_research_dir/wgsn_batch_image_inverse/20260524T044337Z

    python scripts/score_inverse_text_descriptions.py --inverse-dir PATH --limit 3
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from plugins.text_description_evaluator import load_default_evaluator  # noqa: E402
from plugins.text_description_evaluator.evaluation_export import summarize_evaluation_row  # noqa: E402


def extract_text_description_block(md_text: str) -> str:
    """取 ``## text_description`` 下第一个正文块，止于下一个 ``## `` 标题或 EOF。"""
    m = re.search(
        r"(?msi)^##\s*text_description\s*\n+(.*?)(?=^\#\#\s|\Z)",
        md_text,
    )
    if not m:
        raise ValueError("未找到 ## text_description 段落")
    return m.group(1).strip()


def _md_manifest_index(filename: str) -> Optional[int]:
    m = re.match(r"^(\d+)_", filename)
    return int(m.group(1)) if m else None


def iter_md_paths(
    inverse_dir: Path,
    *,
    index_from: Optional[int],
    index_to: Optional[int],
) -> Iterable[Path]:
    for path in sorted(inverse_dir.glob("*_text_description.md")):
        idx = _md_manifest_index(path.name)
        if index_from is not None and idx is not None and idx < index_from:
            continue
        if index_to is not None and idx is not None and idx > index_to:
            continue
        yield path


def load_gate_config_from_fashion(config_path: Path) -> Dict[str, float]:
    """与 ``text-evaluator`` / spec 对齐：缺省沿用 fashion_config 双门限。"""
    cfg: Dict[str, Any] = {}
    if config_path.is_file():
        with config_path.open("r", encoding="utf-8") as fp:
            cfg = yaml.safe_load(fp) or {}
    te = dict(cfg.get("text-evaluator") or {})
    return {
        "score_gate_min": float(te.get("score-gate-min", 0.7)),
        "penalty_gate_max": float(te.get("penalty-gate-max", 0.5)),
    }


def summarize_row(full: Dict[str, Any], *, rel_repo: str, md_index: Optional[int]) -> Dict[str, Any]:
    return summarize_evaluation_row(
        full,
        extra={
            "source_md": rel_repo,
            "md_index": md_index,
        },
    )


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="对 *_text_description.md 使用 DesignTextEvaluator 批量打分",
    )
    default_dir = Path("fashion_research_dir/wgsn_batch_image_inverse/20260524T044337Z")
    p.add_argument("--inverse-dir", type=Path, default=default_dir, help="逆解析目录（内含 md）")
    p.add_argument("--out-dir", type=Path, default=None, help="评分输出目录；默认 <inverse-dir>/text_description_scores/<UTC>")
    p.add_argument("--config", type=Path, default=REPO_ROOT / "fashion_config.yaml", help="fashion_config.yaml")
    p.add_argument("--index-from", type=int, default=None, help="仅处理文件名前缀序号 >=该值（含）")
    p.add_argument("--index-to", type=int, default=None, help="仅处理文件名前缀序号 <=该值（含）")
    p.add_argument("--limit", type=int, default=0, help="最多处理多少个 md（调试用）；0 表示不限制")
    p.add_argument(
        "--no-gates-from-config",
        action="store_true",
        help="不把 text-evaluator 双门限传入 evaluate_text（仅用 spec 默认）",
    )
    p.add_argument(
        "--stop-on-error",
        action="store_true",
        help="任一条解析或评测失败立即退出（默认失败跳过并记入 errors.jsonl）",
    )
    p.add_argument(
        "--write-full-json",
        action="store_true",
        help="为每条写入完整评测 JSON 到 details/（体积大）",
    )
    return p.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    logger = logging.getLogger(__name__)
    args = parse_args()

    inverse_dir = (args.inverse_dir if args.inverse_dir.is_absolute() else REPO_ROOT / args.inverse_dir).resolve()
    if not inverse_dir.is_dir():
        raise SystemExit(f"找不到目录：{inverse_dir}")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = args.out_dir
    if out_dir is None:
        out_dir = inverse_dir / "text_description_scores" / stamp
    else:
        out_dir = Path(out_dir)
        if not out_dir.is_absolute():
            out_dir = REPO_ROOT / out_dir
    out_dir = out_dir.resolve()
    details_dir = out_dir / "details"
    out_dir.mkdir(parents=True, exist_ok=True)
    if args.write_full_json:
        details_dir.mkdir(parents=True, exist_ok=True)

    gate_config: Optional[Dict[str, float]] = None
    if not args.no_gates_from_config:
        gate_config = load_gate_config_from_fashion(args.config.resolve())
        logger.info("门限：score_gate_min=%s penalty_gate_max=%s", gate_config["score_gate_min"], gate_config["penalty_gate_max"])

    evaluator = load_default_evaluator()

    rows = sorted(iter_md_paths(inverse_dir, index_from=args.index_from, index_to=args.index_to))
    if args.limit and args.limit > 0:
        rows = rows[: args.limit]

    if not rows:
        raise SystemExit(f"未找到匹配的 *_text_description.md：{inverse_dir}")

    jsonl_path = out_dir / "scores.jsonl"
    err_path = out_dir / "errors.jsonl"
    jsonl_path.unlink(missing_ok=True)
    err_path.unlink(missing_ok=True)

    summaries: list[Dict[str, Any]] = []
    errors: list[Dict[str, Any]] = []

    for i, md_path in enumerate(rows, start=1):
        rel = str(md_path.relative_to(REPO_ROOT))
        idx = _md_manifest_index(md_path.name)
        logger.info("[%s/%s] 评测 %s", i, len(rows), md_path.name)
        text = md_path.read_text(encoding="utf-8")
        try:
            desc = extract_text_description_block(text)
        except ValueError as e:
            rec = {"source_md": rel, "error": str(e)}
            if args.stop_on_error:
                raise SystemExit(f"{rel}: {e}") from e
            errors.append(rec)
            with err_path.open("a", encoding="utf-8") as ef:
                ef.write(json.dumps(rec, ensure_ascii=False) + "\n")
            logger.warning("解析跳过：%s", md_path.name)
            continue

        try:
            full = evaluator.evaluate_text(
                desc,
                source_name=md_path.name,
                gate_config=gate_config,
            )
        except Exception:
            logger.exception("评测失败：%s", md_path.name)
            if args.stop_on_error:
                raise
            rec = {"source_md": rel, "md_index": idx, "error": "evaluation_exception"}
            errors.append(rec)
            with err_path.open("a", encoding="utf-8") as ef:
                ef.write(json.dumps(rec, ensure_ascii=False) + "\n")
            continue

        slim = summarize_row(full, rel_repo=rel, md_index=idx)
        summaries.append(slim)
        with jsonl_path.open("a", encoding="utf-8") as jf:
            jf.write(json.dumps(slim, ensure_ascii=False) + "\n")

        if args.write_full_json:
            stem = md_path.stem.replace(" ", "_")
            dj = details_dir / f"{stem}_evaluation.json"
            dj.write_text(json.dumps(full, ensure_ascii=False, indent=2), encoding="utf-8")

    # 汇总统计
    agg: Dict[str, Any] = {
        "run_utc": stamp,
        "inverse_dir": str(inverse_dir.relative_to(REPO_ROOT)),
        "processed": len(summaries),
        "failed_parse_or_eval": len(errors),
        "judge_model": summaries[0].get("judge_model") if summaries else None,
    }
    if summaries:
        ts = [float(s["total_score_S_fp"] or 0) for s in summaries]
        agg["mean_total_score"] = round(sum(ts) / len(ts), 6)
        agg["min_total_score"] = round(min(ts), 6)
        agg["max_total_score"] = round(max(ts), 6)
        passed = sum(1 for s in summaries if s.get("gates_both_passed"))
        agg["gates_both_passed_count"] = passed
        agg["gates_both_passed_rate"] = round(passed / len(summaries), 6)
        rs = [s["R_content_scalar"] for s in summaries if s.get("R_content_scalar") is not None]
        if rs:
            agg["mean_R_content"] = round(sum(rs) / len(rs), 6)

    agg_path = out_dir / "summary.json"
    agg_path.write_text(json.dumps(agg, ensure_ascii=False, indent=2), encoding="utf-8")

    logger.info(
        "完成：成功 %s 条 → %s；失败 %s 条",
        len(summaries),
        jsonl_path.relative_to(REPO_ROOT),
        len(errors),
    )


if __name__ == "__main__":
    main()
