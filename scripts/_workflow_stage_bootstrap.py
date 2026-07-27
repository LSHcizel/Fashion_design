"""临时分阶段脚本共用：从 fashion_config 构建 FashionWorkflow。"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from fashion_workflow import (  # noqa: E402
    RESEARCH_DIR_PATH,
    FashionWorkflow,
    TextEvaluatorConfig,
    create_dated_run_dir,
    resolve_chapter_sub_themes,
    parse_yaml,
)


def resolve_config_path(config_arg: str | None) -> Path:
    p = Path(config_arg or "fashion_config.yaml")
    if not p.is_absolute():
        p = REPO_ROOT / p
    if not p.is_file():
        raise SystemExit(f"找不到配置文件：{p}")
    return p


def resolve_api_key(args: Any) -> str:
    key = args.api_key or os.getenv("OHMYGPT_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not key:
        raise SystemExit("缺少 API key：请在 fashion_config.yaml 或环境变量中配置")
    return key


def build_task_notes(args: Any) -> list[dict]:
    notes: list[dict] = []
    for task, items in (getattr(args, "task_notes", None) or {}).items():
        for note in items:
            notes.append({"phases": [task.replace("-", " ")], "note": note})
    language = getattr(args, "language", "Chinese")
    if language != "Chinese":
        notes.append(
            {
                "phases": [
                    "theme analysis",
                    "concept brainstorming",
                    "design elements proposal",
                    "look description generation",
                ],
                "note": f"You should always write in the following language: {language}",
            }
        )
    return notes


def build_evaluator_config(args: Any) -> TextEvaluatorConfig:
    return TextEvaluatorConfig(
        enabled=bool(getattr(args, "text_evaluator_enabled", False)),
        adaptive_min_total_score=float(getattr(args, "evaluator_adaptive_min_total_score", 0.82)),
        adaptive_min_quality_score=float(getattr(args, "evaluator_adaptive_min_quality_score", 0.80)),
        adaptive_penalty_threshold=float(getattr(args, "evaluator_adaptive_penalty_threshold", 0.05)),
        score_gate_min=float(getattr(args, "evaluator_score_gate_min", 0.7)),
        penalty_gate_max=float(getattr(args, "evaluator_penalty_gate_max", 0.5)),
        evaluator_api_key=getattr(args, "evaluator_api_key", None),
        evaluator_api_base=getattr(args, "evaluator_api_base", None),
        evaluator_model=getattr(args, "evaluator_model", None),
        evaluator_temperature=float(getattr(args, "evaluator_temperature", 0.0)),
        rewriter_temperature=float(getattr(args, "evaluator_rewriter_temperature", 0.1)),
    )


def copilot_enabled(args: Any) -> bool:
    v = getattr(args, "copilot_mode", False)
    return v.lower() == "true" if isinstance(v, str) else bool(v)


def build_workflow(
    args: Any,
    *,
    workflow_dir: str | Path,
    api_key: str,
    human_mode: bool | None = None,
) -> FashionWorkflow:
    if human_mode is None:
        human_mode = copilot_enabled(args)

    agent_models = {
        "theme analysis": args.llm_backend,
        "concept brainstorming": args.llm_backend,
        "design elements proposal": args.llm_backend,
        "look description generation": args.llm_backend,
    }
    human_in_loop = {
        "theme analysis": human_mode,
        "concept brainstorming": human_mode,
        "design elements proposal": human_mode,
        "look description generation": human_mode,
    }

    return FashionWorkflow(
        design_target_prompt=args.design_target_prompt,
        theme=args.theme,
        brand=getattr(args, "brand", None),
        description=getattr(args, "description", "") or "",
        openai_api_key=api_key,
        max_steps=args.max_steps,
        agent_model_backbone=agent_models,
        notes=build_task_notes(args),
        human_in_loop_flag=human_in_loop,
        workflow_dir=str(workflow_dir),
        workflow_index=args.workflow_index,
        except_if_fail=args.except_if_fail,
        num_chapters=args.num_chapters,
        num_looks=args.num_looks,
        text_evaluator_config=build_evaluator_config(args),
    )


def default_new_workflow_dir(workflow_index: int) -> Path:
    root = REPO_ROOT / RESEARCH_DIR_PATH / f"workflow_{workflow_index}"
    root.mkdir(parents=True, exist_ok=True)
    return Path(create_dated_run_dir(str(root)))


def resolve_workflow_dir(path_arg: str | None, *, workflow_index: int, create_if_missing: bool) -> Path:
    if path_arg:
        p = Path(path_arg)
        if not p.is_absolute():
            p = REPO_ROOT / p
        p = p.resolve()
        if not p.is_dir():
            if create_if_missing:
                p.mkdir(parents=True, exist_ok=True)
            else:
                raise SystemExit(f"workflow 目录不存在：{p}")
        return p
    if create_if_missing:
        return default_new_workflow_dir(workflow_index)
    raise SystemExit("请通过 --workflow-dir 指定已有运行目录")


def hydrate_theme_analysis(workflow: FashionWorkflow, workflow_dir: Path) -> None:
    theme_path = workflow_dir / "theme_analysis.txt"
    if not theme_path.is_file():
        raise SystemExit(
            f"阶段2 需要阶段1 产物 theme_analysis.txt，未找到：{theme_path}\n"
            "请先运行 scripts/run_stage1_theme_analysis.py"
        )
    text = theme_path.read_text(encoding="utf-8").strip()
    workflow.theme_analyzer.theme_analysis = text
    workflow.theme_analyzer.sub_themes = resolve_chapter_sub_themes(text, workflow.num_chapters)

    key_path = workflow_dir / "description_key_elements.txt"
    if key_path.is_file():
        workflow.theme_analyzer.description_key_elements = key_path.read_text(encoding="utf-8").strip()

    workflow.phase_status["theme analysis"] = True


def load_config(config_path: Path) -> Any:
    return parse_yaml(str(config_path))
