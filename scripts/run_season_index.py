"""按 season_themes index 逐品牌跑文本生成：4 个子主题，每个 4 套 look。

用法（仓库根目录）:
  python scripts/run_season_index.py
  python scripts/run_season_index.py --only gucci_ss27 prada_ss27

模型、评分和 task-notes 仍用 fashion_config.yaml。
品牌、主题、description、章节数、每章 look 数只读 index，不读配置里的
brand / theme / description / design-target-prompt / num-chapters / num-looks。
设计目标读 index 同目录下各品牌的 design_target.txt。
文本模式，不询问图片导入。结果写到 index 旁的 generated/<dir>/<日期>/。
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fashion_workflow import (  # noqa: E402
    FashionWorkflow,
    TextEvaluatorConfig,
    create_dated_run_dir,
    parse_yaml,
)
from plugins.local_llm import workflow_vision_model_name  # noqa: E402

DEFAULT_INDEX = ROOT / "fashion_research_dir" / "season_themes_2026-09" / "index.json"
DEFAULT_YAML = ROOT / "fashion_config.yaml"


def _as_bool(value, default=False) -> bool:
    if value is None:
        return default
    if isinstance(value, str):
        return value.strip().lower() == "true"
    return bool(value)


def _task_notes(args) -> list:
    notes = []
    for task, items in (args.task_notes or {}).items():
        phase = task.replace("-", " ")
        for note in items or []:
            notes.append({"phases": [phase], "note": note})
    if getattr(args, "language", "English") != "Chinese":
        notes.append(
            {
                "phases": [
                    "theme analysis",
                    "concept brainstorming",
                    "design elements proposal",
                    "look description generation",
                ],
                "note": f"You should always write in the following language: {args.language}",
            }
        )
    return notes


def _evaluator(args) -> TextEvaluatorConfig:
    return TextEvaluatorConfig(
        enabled=args.text_evaluator_enabled,
        adaptive_min_total_score=args.evaluator_adaptive_min_total_score,
        adaptive_min_quality_score=args.evaluator_adaptive_min_quality_score,
        adaptive_penalty_threshold=args.evaluator_adaptive_penalty_threshold,
        score_gate_min=args.evaluator_score_gate_min,
        penalty_gate_max=args.evaluator_penalty_gate_max,
        evaluator_api_key=args.evaluator_api_key,
        evaluator_api_base=args.evaluator_api_base,
        evaluator_model=args.evaluator_model,
        evaluator_temperature=args.evaluator_temperature,
        rewriter_temperature=args.evaluator_rewriter_temperature,
        rewrite_on_gate_fail=getattr(args, "evaluator_rewrite_on_gate_fail", True),
    )


def _agent_models(args) -> dict:
    models = {
        "theme analysis": args.llm_backend,
        "concept brainstorming": args.llm_backend,
        "design elements proposal": args.llm_backend,
        "look description generation": args.llm_backend,
    }
    vision_model = workflow_vision_model_name()
    if vision_model:
        models["single look reflection"] = vision_model
        models["chapter image reduction"] = vision_model
        models["collection reflection"] = vision_model
    return models


def _load_index(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("collections") or []
    if not rows:
        raise SystemExit(f"index 里没有 collections: {path}")
    for key in ("num_chapters", "num_looks"):
        if int(payload.get(key) or 0) < 1:
            raise SystemExit(f"index 缺少有效的 {key}: {path}")
    return payload


def _select(rows: list[dict], only: list[str]) -> list[dict]:
    if not only:
        return rows
    wanted = {item.strip().lower() for item in only if item.strip()}
    picked = []
    for row in rows:
        keys = {
            str(row.get("dir") or "").lower(),
            str(row.get("house") or "").lower(),
        }
        if keys & wanted:
            picked.append(row)
    if not picked:
        known = ", ".join(str(row.get("dir")) for row in rows)
        raise SystemExit(f"没有匹配的品牌。可选: {known}")
    return picked


def _read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8").strip()


def run_one(
    row: dict,
    args,
    workflow_index: int,
    out_root: Path,
    index_root: Path,
    num_chapters: int,
    num_looks: int,
) -> Path:
    # 内容只来自 index 及其品牌目录，不使用 config 的 brand / theme / description。
    brand_dir = index_root / str(row["dir"])
    design_target = _read_text(brand_dir / "design_target.txt")
    theme = str(row.get("theme") or "").strip() or _read_text(brand_dir / "theme.txt")
    description = str(row.get("description") or "").strip() or _read_text(brand_dir / "description.txt")
    house = str(row.get("house") or "").strip()
    if not house or not theme or not description:
        raise SystemExit(f"index 记录缺少 house、theme 或 description: {row.get('dir')}")
    season = str(row.get("season") or "")

    run_root = out_root / str(row["dir"])
    run_root.mkdir(parents=True, exist_ok=True)
    workflow_dir = create_dated_run_dir(str(run_root))

    print(
        f"\n=== {house} | {season} | chapters={num_chapters} looks={num_looks} ===\n"
        f"输出: {workflow_dir}"
    )
    workflow = FashionWorkflow(
        design_target_prompt=design_target,
        theme=theme,
        brand=house,
        description=description,
        openai_api_key=args.api_key,
        max_steps=args.max_steps,
        agent_model_backbone=_agent_models(args),
        notes=_task_notes(args),
        human_in_loop_flag={
            "theme analysis": False,
            "concept brainstorming": False,
            "design elements proposal": False,
            "look description generation": False,
            "chapter image reduction": False,
            "collection reflection": False,
        },
        workflow_dir=workflow_dir,
        workflow_index=workflow_index,
        except_if_fail=_as_bool(args.except_if_fail, False),
        num_chapters=num_chapters,
        num_looks=num_looks,
        text_only_mode=True,
        text_evaluator_config=_evaluator(args),
    )
    workflow.perform_research()
    return Path(workflow_dir)


def main() -> None:
    parser = argparse.ArgumentParser(description="按 index 逐品牌生成 4x4 设计文本")
    parser.add_argument("--index", type=Path, default=DEFAULT_INDEX)
    parser.add_argument("--yaml", type=Path, default=DEFAULT_YAML)
    parser.add_argument(
        "--only",
        nargs="*",
        default=[],
        help="只跑这些 dir 或品牌名，例如 gucci_ss27 Chanel",
    )
    parser.add_argument(
        "--workflow-index-start",
        type=int,
        default=4100,
        help="状态文件编号起点，避免覆盖 workflow_0",
    )
    cli = parser.parse_args()

    os.chdir(ROOT)
    args = parse_yaml(str(cli.yaml))
    api_key = args.api_key or os.getenv("OHMYGPT_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("需要 fashion_config.yaml 的 api-key，或环境变量 OHMYGPT_API_KEY / OPENAI_API_KEY")
    args.api_key = api_key

    payload = _load_index(cli.index)
    rows = _select(payload["collections"], cli.only)
    num_chapters = int(payload["num_chapters"])
    num_looks = int(payload["num_looks"])
    out_root = cli.index.parent / "generated"
    written = []
    for offset, row in enumerate(rows):
        written.append(
            run_one(
                row,
                args,
                cli.workflow_index_start + offset,
                out_root,
                cli.index.parent,
                num_chapters,
                num_looks,
            )
        )
    print("\n完成:")
    for path in written:
        print(path)


if __name__ == "__main__":
    main()
