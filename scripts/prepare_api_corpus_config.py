"""从 fashion_config.yaml 生成 API 语料跑配置：gpt-5.4-mini + keep-on-gate-fail。"""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "fashion_config.yaml"
OUT = ROOT / "fashion_research_dir" / "season_themes_2026-09" / "generate_gpt54mini_keep.yaml"


def main() -> None:
    cfg = yaml.safe_load(SRC.read_text(encoding="utf-8")) or {}
    cfg["llm-backend"] = "gpt-5.4-mini"
    cfg["num-chapters"] = 4
    cfg["num-looks"] = 4
    cfg["text-only-mode"] = True
    cfg["copilot-mode"] = False
    cfg["load-previous"] = False

    local = dict(cfg.get("local-llm") or {})
    local["enabled"] = False
    local["use-for-workflow"] = False
    local["use-for-text-evaluator"] = False
    local["use-for-candidate-evaluation"] = False
    local["use-for-parallel-k-rewrite"] = False
    cfg["local-llm"] = local

    ev = dict(cfg.get("text-evaluator") or {})
    ev["enabled"] = True
    ev["use-local"] = False
    ev["keep-on-gate-fail"] = True
    ev["rewrite-on-gate-fail"] = False
    ev["model"] = "gpt-5.4-mini"
    cfg["text-evaluator"] = ev

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        yaml.safe_dump(cfg, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    print(OUT)


if __name__ == "__main__":
    main()
