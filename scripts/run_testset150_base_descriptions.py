#!/usr/bin/env python3
"""用基座 7B 跑测试集已对齐主题的生成流，停在 look 描述。

只取测试集 catalog 里已经写明 theme_dir 的季。品牌、主题、主题描述都读
season_themes index，不读配置里的 Chanel 示例。每个季按 index 的章节数和
look 数生成。品牌调性改写、质量改写和评分都不跑。

    python scripts/run_testset150_base_descriptions.py --dry-run
    python scripts/run_testset150_base_descriptions.py
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

CATALOG = REPO / "fashion_research_dir" / "test_set_300" / "inverse" / "catalog.jsonl"
INDEX = REPO / "fashion_research_dir" / "season_themes_2026-09" / "index.json"
DEFAULT_OUT = REPO / "fashion_research_dir" / "test_set_300" / "generated_base7b"
BASE_MODEL = "Qwen2.5-7B-Instruct"


def _load_season():
    path = REPO / "scripts" / "run_season_index.py"
    spec = importlib.util.spec_from_file_location("run_season_index", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载 {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _read_jsonl(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def aligned_rows(catalog: list[dict], index_rows: list[dict]) -> tuple[list[dict], list[dict]]:
    """catalog 里有 theme_dir 的季才进入生成。没有主题描述的 look 单独列出。"""
    by_dir = {str(row.get("dir") or ""): row for row in index_rows}
    chosen: dict[str, dict] = {}
    skipped = []
    for row in catalog:
        theme_dir = str(row.get("theme_dir") or "").strip()
        if not theme_dir or theme_dir not in by_dir:
            skipped.append(
                {
                    "house": row.get("house"),
                    "season_code": row.get("season_code"),
                    "look": row.get("look"),
                    "text_file": row.get("text_file"),
                    "reason": "catalog 没有可对齐的 theme_dir",
                }
            )
            continue
        chosen[theme_dir] = by_dir[theme_dir]
    ordered = [chosen[key] for key in sorted(chosen)]
    return ordered, skipped


def main() -> None:
    parser = argparse.ArgumentParser(description="基座 7B：只生成测试集已对齐主题的 look 描述")
    parser.add_argument("--catalog", type=Path, default=CATALOG)
    parser.add_argument("--index", type=Path, default=INDEX)
    parser.add_argument("--yaml", type=Path, default=REPO / "fashion_config.yaml")
    parser.add_argument("--out-root", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--workflow-index-start", type=int, default=8100)
    parser.add_argument("--dry-run", action="store_true")
    cli = parser.parse_args()

    catalog = _read_jsonl(cli.catalog)
    payload = json.loads(cli.index.read_text(encoding="utf-8"))
    rows, skipped = aligned_rows(catalog, payload.get("collections") or [])
    if not rows:
        raise SystemExit("测试集 catalog 里没有能对齐到 index 的主题")

    out_root = cli.out_root if cli.out_root.is_absolute() else REPO / cli.out_root
    out_root.mkdir(parents=True, exist_ok=True)
    manifest = {
        "base_model": BASE_MODEL,
        "catalog_rows": len(catalog),
        "aligned_collections": [
            {
                "dir": row.get("dir"),
                "house": row.get("house"),
                "season": row.get("season"),
                "theme": row.get("theme"),
            }
            for row in rows
        ],
        "skipped_looks_without_theme": skipped,
        "rewrite": "skipped",
        "scoring": "skipped",
    }
    (out_root / "alignment.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"测试集 {len(catalog)} 条；可对齐主题 {len(rows)} 个；没有主题描述的 look {len(skipped)} 条")
    for row in rows:
        print(f"  {row.get('dir')} | {row.get('house')} | {row.get('theme')}")
    if cli.dry_run:
        print(f"dry-run，对齐清单写在 {out_root / 'alignment.json'}")
        return

    season = _load_season()
    os.chdir(REPO)
    args = season.parse_yaml(str(cli.yaml))
    import yaml as _yaml
    import inference as _inference

    cfg = _yaml.safe_load(Path(cli.yaml).read_text(encoding="utf-8")) or {}
    local = cfg.get("local-llm") or {}
    backend = str(cfg.get("llm-backend") or "").strip()
    if not bool(local.get("enabled", True)) or not bool(local.get("use-for-workflow", True)):
        raise SystemExit("fashion_config.yaml 的 local-llm 没有打开 workflow 生成")
    if backend != BASE_MODEL or str(local.get("model") or "").strip() != BASE_MODEL:
        raise SystemExit(f"当前配置不是基座 {BASE_MODEL}，拒绝开跑")
    if "8001" in str(local.get("api-base") or ""):
        raise SystemExit("workflow 指到了 8001 改写器，不是基座")

    api_key = args.api_key or os.getenv("OHMYGPT_API_KEY") or os.getenv("OPENAI_API_KEY") or "local"
    args.api_key = api_key
    api_base = str(cfg.get("api-base") or "").strip() or "https://api.ohmygpt.com/v1"
    os.environ["OPENAI_API_KEY"] = api_key
    os.environ["OHMYGPT_API_KEY"] = api_key
    os.environ["OPENAI_BASE_URL"] = api_base
    _inference.OPENAI_COMPAT_BASE_URL = api_base
    os.environ.pop("FASHION_FORCE_REMOTE_LLM", None)
    print(f"[API] workflow model={backend} local={local.get('api-base')} weights={local.get('model-path')}")

    num_chapters = int(payload["num_chapters"])
    num_looks = int(payload["num_looks"])
    written = []
    for offset, row in enumerate(rows):
        written.append(
            season.run_one(
                row,
                args,
                cli.workflow_index_start + offset,
                out_root,
                cli.index.parent,
                num_chapters,
                num_looks,
                skip_description_rewrite=True,
            )
        )
    print("\n完成:")
    for path in written:
        print(path)


if __name__ == "__main__":
    main()
