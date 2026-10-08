"""
为论文 Stage 1 插图跑通真实案例：Theme → Concept → Elements → Look（仅文本）。
强制走远程 ohmygpt API（本地 vLLM 未启动时也能跑），并关闭 Text Evaluator。
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)


def _bootstrap_remote_api() -> tuple[dict, str, str]:
    """先读配置并注入环境变量，再 import inference / fashion_workflow。"""
    import yaml

    cfg_path = ROOT / "fashion_config.yaml"
    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    api_key = (cfg.get("api-key") or "").strip()
    api_base = (cfg.get("api-base") or "https://api.ohmygpt.com/v1").strip()
    if not api_key:
        raise SystemExit("fashion_config.yaml 缺少 api-key")

    os.environ["OPENAI_API_KEY"] = api_key
    os.environ["OPENAI_BASE_URL"] = api_base
    os.environ["OHMYGPT_API_KEY"] = api_key
    return cfg, api_key, api_base


def main() -> None:
    cfg, api_key, api_base = _bootstrap_remote_api()

    # 必须在设置 OPENAI_BASE_URL 之后再 import
    import inference as inference_mod
    from fashion_workflow import (
        FashionWorkflow,
        TextEvaluatorConfig,
        create_dated_run_dir,
        RESEARCH_DIR_PATH,
    )

    inference_mod.OPENAI_COMPAT_BASE_URL = api_base

    # 插图案例：2 个子主题（图中展示分歧），只展开第 1 章、1 条 look
    model = "gpt-4o-mini"
    num_chapters = 2
    num_looks = 1

    design_target = cfg["design-target-prompt"]
    theme = cfg["theme"]
    brand = cfg.get("brand") or "Chanel"
    description = (cfg.get("description") or "").strip()

    out_root = Path(RESEARCH_DIR_PATH) / "workflow_0" / "stage1_figure_case"
    out_root.mkdir(parents=True, exist_ok=True)
    workflow_dir = create_dated_run_dir(str(out_root))

    snap = Path(workflow_dir) / "_case_inputs.md"
    snap.write_text(
        f"# Stage1 figure case inputs\n\n"
        f"- brand: {brand}\n"
        f"- theme: {theme}\n"
        f"- model: {model} @ {api_base}\n"
        f"- num_chapters: {num_chapters}\n"
        f"- num_looks: {num_looks}\n\n"
        f"## design-target-prompt\n\n{design_target}\n\n"
        f"## description (truncated for figure)\n\n"
        + "\n\n".join(description.split("\n\n")[:2])
        + "\n",
        encoding="utf-8",
    )

    agent_models = {
        "theme analysis": model,
        "concept brainstorming": model,
        "design elements proposal": model,
        "look description generation": model,
    }
    notes = [
        {
            "phases": [
                "theme analysis",
                "concept brainstorming",
                "design elements proposal",
                "look description generation",
            ],
            "note": "You should always write in the following language: English",
        }
    ]

    workflow = FashionWorkflow(
        design_target_prompt=design_target,
        theme=theme,
        brand=brand,
        description=description,
        openai_api_key=api_key,
        max_steps=12,
        agent_model_backbone=agent_models,
        notes=notes,
        human_in_loop_flag={
            "theme analysis": False,
            "concept brainstorming": False,
            "design elements proposal": False,
            "look description generation": False,
        },
        workflow_dir=workflow_dir,
        workflow_index=0,
        except_if_fail=True,
        num_chapters=num_chapters,
        num_looks=num_looks,
        text_only_mode=True,
        text_evaluator_config=TextEvaluatorConfig(enabled=False),
    )

    print(f"[stage1-case] workflow_dir = {workflow_dir}")
    print("[stage1-case] Theme Analysis ...")
    repeat = True
    while repeat:
        repeat = workflow.theme_analysis()

    print("[stage1-case] Chapter 1 only (Concept → Elements → Look) ...")
    workflow.process_chapters_sequentially(
        chapter_from=1,
        chapter_to=1,
        skip_image_eval=True,
        skip_collection_reflection=True,
    )

    print("[stage1-case] DONE")
    print(f"  theme_analysis: {Path(workflow_dir) / 'theme_analysis.txt'}")
    print(f"  chapter_01:     {Path(workflow_dir) / 'chapter_01'}")


if __name__ == "__main__":
    main()
