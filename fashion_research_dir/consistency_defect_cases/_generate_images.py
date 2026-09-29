"""用 scripts/generate_images_from_inverse_descriptions.py 的同一套生图接口，给本目录 txt 出图。"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = REPO_ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from generate_images_from_inverse_descriptions import (  # type: ignore
    DEFAULT_CONFIG_PATH,
    generate_one_image,
    load_generation_credentials,
    save_response_item,
)

HERE = Path(__file__).resolve().parent
MODEL = "gpt-image-2"
OUT = HERE / f"generated_{MODEL.replace('/', '_')}"


def _already_moderated(failures: Path, source_name: str) -> bool:
    if not failures.is_file():
        return False
    for line in failures.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        if rec.get("source") == source_name and "moderation_blocked" in str(rec.get("error") or ""):
            return True
    return False


def _save_with_download_retry(parsed: dict, out_png: Path, tries: int = 4) -> None:
    last: Exception | None = None
    for attempt in range(1, tries + 1):
        try:
            save_response_item(parsed, out_png, download_timeout=0)
            if out_png.is_file() and out_png.stat().st_size > 10_000:
                return
            raise OSError(f"下载结果过小：{out_png}")
        except Exception as exc:
            last = exc
            logging.getLogger("consistency_defect_images").warning(
                "下载第 %s/%s 次失败：%s", attempt, tries, str(exc)[:180]
            )
    assert last is not None
    raise last


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    log = logging.getLogger("consistency_defect_images")
    files = sorted(p for p in HERE.glob("[0-9][0-9]_*.txt") if p.is_file())
    if not files:
        raise SystemExit("没有可生图的描述")
    OUT.mkdir(parents=True, exist_ok=True)
    api_key, api_base = load_generation_credentials(
        DEFAULT_CONFIG_PATH, api_key_arg=None, api_base_arg=None
    )
    log.info("将处理 %s 条；输出 %s；base=%s", len(files), OUT, api_base)
    manifest = OUT / "generation_manifest.jsonl"
    failures = OUT / "generation_failures.jsonl"
    ok = skipped = failed = 0
    for i, path in enumerate(files, start=1):
        prompt = path.read_text(encoding="utf-8").strip()
        out_png = OUT / f"{path.stem}_{MODEL}.png"
        if out_png.is_file() and out_png.stat().st_size > 0:
            log.info("[%s/%s] 已有 PNG，跳过 %s", i, len(files), out_png.name)
            skipped += 1
            continue
        if _already_moderated(failures, path.name):
            log.warning("[%s/%s] 此前被安全策略拒绝，跳过 %s", i, len(files), path.name)
            failed += 1
            continue
        log.info("[%s/%s] 生图 → %s", i, len(files), out_png.name)
        try:
            parsed = None
            last_exc: Exception | None = None
            for attempt in range(1, 4):
                try:
                    parsed = generate_one_image(
                        api_key=api_key,
                        api_base=api_base,
                        prompt=prompt,
                        model=MODEL,
                        size="1024x1024",
                        quality="high",
                        verify_ssl=True,
                        timeout=0,
                    )
                    _save_with_download_retry(parsed, out_png)
                    last_exc = None
                    break
                except Exception as exc:
                    last_exc = exc
                    if "IncompleteRead" not in type(exc).__name__ and "IncompleteRead" not in str(exc):
                        raise
                    log.warning("连接中断，第 %s/3 次重试 %s", attempt, path.name)
            if last_exc is not None:
                raise last_exc
        except Exception as exc:
            failed += 1
            log.warning("失败 %s: %s", path.name, str(exc)[:400])
            with failures.open("a", encoding="utf-8") as lf:
                lf.write(
                    json.dumps(
                        {"source": path.name, "error": str(exc)[:2000]},
                        ensure_ascii=False,
                    )
                    + "\n"
                )
            continue
        ok += 1
        with manifest.open("a", encoding="utf-8") as lf:
            lf.write(
                json.dumps(
                    {
                        "source": path.name,
                        "output_png": out_png.name,
                        "model": MODEL,
                        "prompt_chars": len(prompt),
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
        log.info("[%s/%s] 已保存 %s (%s bytes)", i, len(files), out_png.name, out_png.stat().st_size)
    log.info("统计：成功 %s，跳过已有 %s，失败 %s", ok, skipped, failed)


if __name__ == "__main__":
    main()
