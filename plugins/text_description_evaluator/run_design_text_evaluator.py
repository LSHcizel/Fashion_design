"""
CLI for DesignTextEvaluator.

Examples:
    python -m plugins.text_description_evaluator.run_design_text_evaluator --input sample.txt
    python -m plugins.text_description_evaluator.run_design_text_evaluator --input some_dir --output results.json
    python -m plugins.text_description_evaluator.run_design_text_evaluator --mode adaptive --input sample.txt
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Tuple

from .design_text_evaluator_api import DesignTextEvaluator


def _get_quality_penalized_score(result: Dict) -> float:
    return float(result["scores"]["quality_score"].get("penalized_score", 0.0) or 0.0)


def _get_active_penalties(result: Dict, penalty_threshold: float) -> list[Dict]:
    penalties = result["scores"]["quality_score"].get("penalties", {})
    penalty_items = penalties.get("items", {})
    active_penalties = []
    for penalty_key in penalty_items.keys():
        penalty_score = float(penalties.get(penalty_key, 0.0) or 0.0)
        if penalty_score < penalty_threshold:
            continue
        active_penalties.append(
            {
                "penalty_key": penalty_key,
                "score": penalty_score,
                "reason": penalty_items.get(penalty_key, {}).get("reason", ""),
            }
        )
    return active_penalties


def _should_optimize_adaptively(
    evaluation_result: Dict,
    min_total_score: float,
    min_quality_score: float,
    penalty_threshold: float,
) -> Tuple[bool, Dict]:
    total_score = float(evaluation_result.get("total_score", 0.0) or 0.0)
    quality_score = _get_quality_penalized_score(evaluation_result)
    active_penalties = _get_active_penalties(evaluation_result, penalty_threshold)

    reasons = []
    if total_score < min_total_score:
        reasons.append(
            {
                "type": "total_score_below_threshold",
                "actual": total_score,
                "threshold": min_total_score,
            }
        )
    if quality_score < min_quality_score:
        reasons.append(
            {
                "type": "quality_score_below_threshold",
                "actual": quality_score,
                "threshold": min_quality_score,
            }
        )
    if active_penalties:
        reasons.append(
            {
                "type": "active_penalties_detected",
                "threshold": penalty_threshold,
                "items": active_penalties,
            }
        )

    return bool(reasons), {
        "triggered": bool(reasons),
        "total_score": total_score,
        "quality_score": quality_score,
        "thresholds": {
            "min_total_score": min_total_score,
            "min_quality_score": min_quality_score,
            "penalty_threshold": penalty_threshold,
        },
        "reasons": reasons,
    }


def _run_adaptive_file(
    evaluator: DesignTextEvaluator,
    input_path: Path,
    report_dir: str | None,
    max_rounds: int,
    min_score_improvement: float,
    min_quality_improvement: float,
    adaptive_min_total_score: float,
    adaptive_min_quality_score: float,
    adaptive_penalty_threshold: float,
    score_gate_min: float | None = None,
    penalty_gate_max: float | None = None,
) -> Dict:
    evaluation_result = evaluator.evaluate_txt_file(input_path)
    should_optimize, decision = _should_optimize_adaptively(
        evaluation_result=evaluation_result,
        min_total_score=adaptive_min_total_score,
        min_quality_score=adaptive_min_quality_score,
        penalty_threshold=adaptive_penalty_threshold,
    )

    optimization_result = None
    final_result = evaluation_result
    if should_optimize:
        optimization_result = evaluator.optimize_txt_file(
            input_path,
            report_dir=report_dir,
            max_rounds=max_rounds,
            min_score_improvement=min_score_improvement,
            min_quality_improvement=min_quality_improvement,
            score_gate_min=score_gate_min,
            penalty_gate_max=penalty_gate_max,
        )
        final_result = optimization_result["optimized_result"]

    return {
        "mode": "adaptive",
        "source_name": input_path.name,
        "adaptive_decision": decision,
        "evaluation_result": evaluation_result,
        "optimization_result": optimization_result,
        "final_result": final_result,
    }


def _run_adaptive_directory(
    evaluator: DesignTextEvaluator,
    input_path: Path,
    report_dir: str | None,
    max_rounds: int,
    min_score_improvement: float,
    min_quality_improvement: float,
    adaptive_min_total_score: float,
    adaptive_min_quality_score: float,
    adaptive_penalty_threshold: float,
    score_gate_min: float | None = None,
    penalty_gate_max: float | None = None,
) -> Dict[str, Dict]:
    results = {}
    for txt_file in sorted(input_path.glob("*.txt")):
        results[txt_file.name] = _run_adaptive_file(
            evaluator=evaluator,
            input_path=txt_file,
            report_dir=report_dir,
            max_rounds=max_rounds,
            min_score_improvement=min_score_improvement,
            min_quality_improvement=min_quality_improvement,
            adaptive_min_total_score=adaptive_min_total_score,
            adaptive_min_quality_score=adaptive_min_quality_score,
            adaptive_penalty_threshold=adaptive_penalty_threshold,
            score_gate_min=score_gate_min,
            penalty_gate_max=penalty_gate_max,
        )
    return results


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate fashion text descriptions from txt files.")
    parser.add_argument(
        "--mode",
        choices=["evaluate", "optimize", "adaptive"],
        default="adaptive",
        help="Run evaluation only, targeted optimization, or adaptive evaluate-then-optimize flow.",
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to a txt file or a directory containing txt files.",
    )
    parser.add_argument(
        "--spec",
        default=None,
        help="Optional path to fashion_prompt_optimizer_spec.json.",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="API key for the OpenAI-compatible judge API. Defaults to AI_API_KEY.",
    )
    parser.add_argument(
        "--api-base",
        default=None,
        help="API base URL for the OpenAI-compatible judge API. Defaults to AI_API_BASE.",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Judge model name for the API. Defaults to AI_API_MODEL or AI_MODEL.",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="Sampling temperature for the LLM judge. Use 0 for deterministic judging.",
    )
    parser.add_argument(
        "--rewriter-temperature",
        type=float,
        default=None,
        help="Temperature for optimize rewrite calls only; default from spec rewriter.temperature (fallback 0.1). Judge still uses --temperature.",
    )
    parser.add_argument(
        "--top-p",
        type=float,
        default=1.0,
        help="Top-p sampling for the LLM judge when temperature > 0.",
    )
    parser.add_argument(
        "--max-new-tokens",
        type=int,
        default=1600,
        help="Maximum tokens returned by the LLM judge per module call.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=120,
        help="HTTP timeout in seconds for each judge API request.",
    )
    parser.add_argument(
        "--insecure",
        action="store_true",
        help="Disable SSL certificate verification for environments with gateway certificate mismatch.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional path to save the JSON result.",
    )
    parser.add_argument(
        "--report-dir",
        default=None,
        help="Optional output directory for optimization reports.",
    )
    parser.add_argument(
        "--max-rounds",
        type=int,
        default=5,
        help="Maximum optimization rounds (mode=optimize or adaptive). Stops early when both optimization gates pass.",
    )
    parser.add_argument(
        "--min-score-improvement",
        type=float,
        default=0.02,
        help="Early-stop threshold for total score improvement between optimization rounds.",
    )
    parser.add_argument(
        "--min-quality-improvement",
        type=float,
        default=0.05,
        help="Early-stop threshold for quality score improvement between optimization rounds.",
    )
    parser.add_argument(
        "--adaptive-min-total-score",
        type=float,
        default=0.82,
        help="When mode=adaptive, trigger optimization if total score is below this threshold.",
    )
    parser.add_argument(
        "--adaptive-min-quality-score",
        type=float,
        default=0.80,
        help="When mode=adaptive, trigger optimization if penalized quality score is below this threshold.",
    )
    parser.add_argument(
        "--adaptive-penalty-threshold",
        type=float,
        default=0.05,
        help="When mode=adaptive, trigger optimization if any penalty reaches this threshold.",
    )
    parser.add_argument(
        "--score-gate-min",
        type=float,
        default=None,
        help="Override spec optimization_gates.score_gate_min for optimize/adaptive optimization (weighted coverage+quality_base).",
    )
    parser.add_argument(
        "--penalty-gate-max",
        type=float,
        default=None,
        help="Override spec optimization_gates.penalty_gate_max for optimize/adaptive (max allowed penalties.total_penalty).",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    evaluator = DesignTextEvaluator(
        spec_path=args.spec,
        api_key=args.api_key,
        api_base=args.api_base,
        model=args.model,
        temperature=args.temperature,
        top_p=args.top_p,
        max_new_tokens=args.max_new_tokens,
        timeout=args.timeout,
        verify_ssl=not args.insecure,
        rewriter_temperature=args.rewriter_temperature,
    )
    input_path = Path(args.input)

    if input_path.is_dir():
        if args.mode == "adaptive":
            result = _run_adaptive_directory(
                evaluator=evaluator,
                input_path=input_path,
                report_dir=args.report_dir,
                max_rounds=args.max_rounds,
                min_score_improvement=args.min_score_improvement,
                min_quality_improvement=args.min_quality_improvement,
                adaptive_min_total_score=args.adaptive_min_total_score,
                adaptive_min_quality_score=args.adaptive_min_quality_score,
                adaptive_penalty_threshold=args.adaptive_penalty_threshold,
                score_gate_min=args.score_gate_min,
                penalty_gate_max=args.penalty_gate_max,
            )
        elif args.mode == "optimize":
            result = evaluator.optimize_txt_directory(
                input_path,
                report_dir=args.report_dir,
                max_rounds=args.max_rounds,
                min_score_improvement=args.min_score_improvement,
                min_quality_improvement=args.min_quality_improvement,
                score_gate_min=args.score_gate_min,
                penalty_gate_max=args.penalty_gate_max,
            )
        else:
            result = evaluator.evaluate_txt_directory(input_path)
    else:
        if args.mode == "adaptive":
            result = _run_adaptive_file(
                evaluator=evaluator,
                input_path=input_path,
                report_dir=args.report_dir,
                max_rounds=args.max_rounds,
                min_score_improvement=args.min_score_improvement,
                min_quality_improvement=args.min_quality_improvement,
                adaptive_min_total_score=args.adaptive_min_total_score,
                adaptive_min_quality_score=args.adaptive_min_quality_score,
                adaptive_penalty_threshold=args.adaptive_penalty_threshold,
                score_gate_min=args.score_gate_min,
                penalty_gate_max=args.penalty_gate_max,
            )
        elif args.mode == "optimize":
            result = evaluator.optimize_txt_file(
                input_path,
                report_dir=args.report_dir,
                max_rounds=args.max_rounds,
                min_score_improvement=args.min_score_improvement,
                min_quality_improvement=args.min_quality_improvement,
                score_gate_min=args.score_gate_min,
                penalty_gate_max=args.penalty_gate_max,
            )
        else:
            result = evaluator.evaluate_txt_file(input_path)

    json_text = json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None)

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(json_text, encoding="utf-8")
    else:
        print(json_text)


if __name__ == "__main__":
    main()
