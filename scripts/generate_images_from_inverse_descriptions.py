#!/usr/bin/env python3
"""
从逆解析输出的 Markdown（``*_text_description.md``）中提取 ``## text_description`` 正文，
使用 ``fashion_config.yaml``（或 CLI）指定的 API Base，调用 ``gpt-image-2``（可改）的生图接口
``POST {api-base}/images/generations``，将结果写入与逆解析同级或指定子目录。

依赖：网关需兼容 OpenAI 风格 ``/v1/images/generations``（返回 ``data[].b64_json`` 或 ``data[].url``）。

在仓库根目录执行示例::

    # 逆解析 md 批量生图
    python scripts/generate_images_from_inverse_descriptions.py \\
      --inverse-dir fashion_research_dir/wgsn_batch_image_inverse/20260524T044337Z \\
      --index-from 8 --index-to 40 --model gpt-image-2

    # 工作流 chapter：每次只跑一张（默认 --look-to 等于 --look-from）
    python scripts/generate_images_from_inverse_descriptions.py \\
      --chapter-dir fashion_research_dir/workflow_0/2026-06-06/chapter_02 \\
      --look-from 4 \\
      --skip-existing --append-manifest \\
      --model gpt-image-2
"""

from __future__ import annotations

import argparse
import base64
import json
import logging
import os
import re
import ssl
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

DEFAULT_CONFIG_PATH = REPO_ROOT / "fashion_config.yaml"


def _load_root_config(config_path: Path) -> Dict[str, Any]:
    if not config_path.is_file():
        return {}
    with config_path.open("r", encoding="utf-8") as fp:
        return yaml.safe_load(fp) or {}


def _opt_str(val: Any) -> Optional[str]:
    return val.strip() if isinstance(val, str) and val.strip() else None


def load_generation_credentials(
    config_path: Path,
    *,
    api_key_arg: Optional[str],
    api_base_arg: Optional[str],
) -> tuple[str, str]:
    cfg = _load_root_config(config_path)
    api_key = (
        _opt_str(api_key_arg)
        or _opt_str(os.environ.get("IMAGE_GEN_API_KEY"))
        or _opt_str(cfg.get("openai-api-key"))
        or _opt_str(cfg.get("api-key"))
    )
    api_base_raw = (
        _opt_str(api_base_arg)
        or _opt_str(os.environ.get("IMAGE_GEN_API_BASE"))
        or _opt_str(cfg.get("openai-api-base"))
        or _opt_str(cfg.get("api-base"))
    )
    if not api_key:
        raise ValueError(
            "缺少 api-key：请在 fashion_config.yaml 配置 api-key/openai-api-key "
            "或设置环境变量 IMAGE_GEN_API_KEY，或使用 --api-key",
        )
    if not api_base_raw:
        raise ValueError(
            "缺少 api-base：请配置 api-base/openai-api-base 或 IMAGE_GEN_API_BASE 或 --api-base",
        )
    return api_key, api_base_raw.rstrip("/")


def extract_text_description_block(md_text: str) -> str:
    """取 ``## text_description`` 下第一个正文块，止于下一个 ``## `` 标题或 EOF。"""
    m = re.search(
        r"(?msi)^##\s*text_description\s*\n+(.*?)(?=^\#\#\s|\Z)",
        md_text,
    )
    if not m:
        raise ValueError("未找到 ## text_description 段落")
    return m.group(1).strip()


def load_look_prompt(look_txt: Path) -> str:
    """读取工作流 ``look_XX.txt`` 全文作为生图 prompt。"""
    text = look_txt.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError(f"空文件：{look_txt}")
    return text


def iter_chapter_look_paths(
    chapter_dir: Path,
    *,
    look_from: int,
    look_to: int,
) -> Iterable[tuple[int, Path]]:
    """文件名形如 ``look_01.txt``，按 look 序号筛选。"""
    if look_from > look_to:
        raise ValueError("--look-from 不能大于 --look-to")
    for n in range(look_from, look_to + 1):
        path = chapter_dir / f"look_{n:02d}.txt"
        if path.is_file():
            yield n, path


def iter_inverse_markdown_paths(
    inverse_dir: Path,
    *,
    index_from: int,
    index_to: int,
) -> Iterable[tuple[int, Path]]:
    """文件名形如 ``08_...@.._text_description.md``，按前缀序号筛选。"""
    if index_from > index_to:
        raise ValueError("--index-from 不能大于 --index-to")
    for path in sorted(inverse_dir.glob("*.md")):
        if not path.name.endswith("_text_description.md"):
            continue
        m = re.match(r"^(\d+)_", path.name)
        if not m:
            continue
        idx = int(m.group(1))
        if index_from <= idx <= index_to:
            yield idx, path


def generations_url(api_base: str) -> str:
    return f"{api_base}/images/generations"


def _resolve_read_timeout(timeout: Optional[int]) -> Optional[int]:
    """``0`` 或负数表示不设客户端读超时（一直等到服务端响应或连接断开）。"""
    if timeout is None or int(timeout) <= 0:
        return None
    return int(timeout)


def generate_one_image(
    *,
    api_key: str,
    api_base: str,
    prompt: str,
    model: str,
    size: str,
    quality: str,
    verify_ssl: bool,
    timeout: Optional[int] = None,
    n: int = 1,
) -> Dict[str, Any]:
    """
    单次 POST 调用 images/generations（不做自动重试，避免重复计费）。

    - 优先 URL 返回；仅当网关明确不支持时再试 b64_json（各一次 POST）。
    - 客户端不设读超时（除非显式传入正数 timeout）。
    - 仅当服务端返回 HTTP 错误体时视为失败；连接中断则抛错，由人工决定是否重跑。
    """
    base_payload: Dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "n": n,
    }
    if size:
        base_payload["size"] = size
    if quality:
        base_payload["quality"] = quality

    url = generations_url(api_base)
    ssl_context = ssl._create_unverified_context() if not verify_ssl else None
    read_timeout = _resolve_read_timeout(timeout)

    last_err = ""
    logging.info(
        "等待服务端响应（无客户端读超时=%s，单次 POST 不重试）…",
        read_timeout is None,
    )

    for use_b64_json in (False, True):
        payload = dict(base_payload)
        mode = "b64_json" if use_b64_json else "url"
        if use_b64_json:
            payload["response_format"] = "b64_json"
        body = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(
                request, timeout=read_timeout, context=ssl_context
            ) as resp:
                raw = resp.read().decode("utf-8")
            logging.info("生图响应已收到（mode=%s）", mode)
            return json.loads(raw)
        except urllib.error.HTTPError as exc:
            err_body = exc.read().decode("utf-8", errors="replace")
            last_err = f"HTTP {exc.code} ({mode}): {err_body}"
            lb = err_body.lower()
            if exc.code == 400 and use_b64_json and (
                "response_format" in lb or "unsupported" in lb or "unknown" in lb
            ):
                logging.info("网关不支持 response_format=b64_json，改试 URL 返回")
                continue
            raise RuntimeError(f"Images API 服务端拒绝 ({url}):\n{last_err}") from exc
        except (urllib.error.URLError, ConnectionError, TimeoutError, ssl.SSLError, OSError) as exc:
            last_err = f"{type(exc).__name__} ({mode}): {exc}"
            if not use_b64_json:
                logging.warning("%s — 将尝试 b64_json 返回格式", last_err[:220])
                continue
            raise RuntimeError(
                f"Images API 连接中断（未收到服务端错误响应）({url}):\n{last_err}\n"
                "提示：网关可能已扣费；请用 --skip-existing 手动重跑同一张，勿依赖自动重试。"
            ) from exc

    raise RuntimeError(f"Images API 无可用返回格式: {last_err}")


def save_response_item(
    parsed: Dict[str, Any],
    out_png: Path,
    *,
    download_timeout: Optional[int] = None,
) -> None:
    data = parsed.get("data") or []
    if not data:
        raise ValueError(f"响应无 data：{parsed!r}")
    item = data[0]
    if isinstance(item.get("b64_json"), str):
        raw = base64.standard_b64decode(item["b64_json"])
        out_png.write_bytes(raw)
        return
    if isinstance(item.get("url"), str):
        ssl_ctx = None
        req = urllib.request.Request(
            item["url"],
            headers={"User-Agent": "Mozilla/5.0"},
            method="GET",
        )
        with urllib.request.urlopen(
            req, timeout=_resolve_read_timeout(download_timeout), context=ssl_ctx
        ) as r:
            out_png.write_bytes(r.read())
        return
    raise ValueError(f"data[0] 无 b64_json/url：{item!r}")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="从逆解析 md 中提取 text_description 并调用 images/generations（gpt-image-2）",
    )
    p.add_argument(
        "--inverse-dir",
        type=Path,
        default=None,
        help="逆解析输出目录（含 *_text_description.md）；与 --chapter-dir 二选一",
    )
    p.add_argument(
        "--chapter-dir",
        type=Path,
        default=None,
        help="工作流章节目录（含 look_01.txt …）；与 --inverse-dir 二选一",
    )
    p.add_argument(
        "--look-from",
        type=int,
        default=1,
        help="chapter 模式：look 序号下界（含），对应 look_01.txt → 1",
    )
    p.add_argument(
        "--look-to",
        type=int,
        default=None,
        help="chapter 模式：look 序号上界（含）；默认与 --look-from 相同（每次只跑一张）",
    )
    p.add_argument(
        "--index-from",
        type=int,
        default=8,
        help="文件名前缀序号下界（含），如 08_*.md → 8",
    )
    p.add_argument(
        "--index-to",
        type=int,
        default=40,
        help="文件名前缀序号上界（含）",
    )
    p.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="生图保存目录（默认：inverse→generated_<model>；chapter→<chapter-dir>/image2_generation）",
    )
    p.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="fashion_config.yaml 路径",
    )
    p.add_argument("--api-key", default="", help="覆盖配置文件中的密钥")
    p.add_argument("--api-base", default="", help="覆盖配置文件中的网关 base（不含尾路径即可）")
    p.add_argument("--model", default="gpt-image-2", help="Images API model 字段")
    p.add_argument(
        "--size",
        default="1024x1024",
        help="分辨率（依网关支持的枚举；留空不传该字段）",
    )
    p.add_argument(
        "--quality",
        default="high",
        help="quality（依网关支持；留空不传）",
    )
    p.add_argument(
        "--timeout",
        type=int,
        default=0,
        help="客户端读超时秒；0=不限时，一直等到服务端响应或连接断开",
    )
    p.add_argument(
        "--no-verify-ssl",
        action="store_true",
        help="跳过 TLS 校验（不推荐，仅调试）",
    )
    p.add_argument(
        "--append-manifest",
        action="store_true",
        help="不清空既有 generation_manifest.jsonl，在原文件末尾追加",
    )
    p.add_argument(
        "--skip-existing",
        action="store_true",
        help="目标 PNG 已存在则跳过调用（幂等续跑）",
    )
    p.add_argument(
        "--continue-on-error",
        action="store_true",
        help="单次失败（含 moderation、网络）跳过并记入 generation_failures.jsonl，直至跑完区间内全部 md",
    )
    return p.parse_args()


def _resolve_path(path: Path) -> Path:
    p = Path(path)
    if not p.is_absolute():
        p = REPO_ROOT / p
    return p.resolve()


def _rel_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    logger = logging.getLogger(__name__)
    args = parse_args()
    if args.look_to is None:
        args.look_to = args.look_from

    use_chapter = args.chapter_dir is not None
    use_inverse = args.inverse_dir is not None
    if use_chapter and use_inverse:
        raise SystemExit("--chapter-dir 与 --inverse-dir 不能同时指定")
    if not use_chapter and not use_inverse:
        use_inverse = True

    api_key, api_base = load_generation_credentials(
        args.config,
        api_key_arg=args.api_key or None,
        api_base_arg=args.api_base or None,
    )

    safe_model = re.sub(r"[^\w\-]+", "_", args.model).strip("_") or "image_model"

    if use_chapter:
        chapter_dir = _resolve_path(args.chapter_dir)
        if not chapter_dir.is_dir():
            raise SystemExit(f"找不到章节目录：{chapter_dir}")
        out_dir = args.out_dir
        if out_dir is None:
            out_dir = chapter_dir / "image2_generation"
        else:
            out_dir = _resolve_path(out_dir)
        pairs = list(
            iter_chapter_look_paths(
                chapter_dir,
                look_from=args.look_from,
                look_to=args.look_to,
            )
        )
        if not pairs:
            raise SystemExit(
                f"{chapter_dir} 下没有 look 在 [{args.look_from}, {args.look_to}] 的 look_XX.txt",
            )
        source_kind = "chapter_look"
        logger.info("模式：chapter | 目录=%s", _rel_path(chapter_dir))
    else:
        default_inverse = REPO_ROOT / "fashion_research_dir/wgsn_batch_image_inverse/20260524T044337Z"
        inverse_dir = _resolve_path(args.inverse_dir or default_inverse)
        if not inverse_dir.is_dir():
            raise SystemExit(f"找不到目录：{inverse_dir}")
        out_dir = args.out_dir
        if out_dir is None:
            out_dir = inverse_dir / f"generated_{safe_model}"
        else:
            out_dir = _resolve_path(out_dir)
        pairs = list(
            iter_inverse_markdown_paths(
                inverse_dir,
                index_from=args.index_from,
                index_to=args.index_to,
            )
        )
        if not pairs:
            raise SystemExit(
                f"{inverse_dir} 下没有序号在 [{args.index_from}, {args.index_to}] 的 *_text_description.md",
            )
        source_kind = "inverse_md"
        logger.info("模式：inverse | 目录=%s", _rel_path(inverse_dir))

    out_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = out_dir / "generation_manifest.jsonl"
    if not args.append_manifest:
        manifest_path.unlink(missing_ok=True)

    failures_path = out_dir / "generation_failures.jsonl"

    size_arg = args.size.strip() if args.size else ""
    quality_arg = args.quality.strip() if args.quality else ""

    verify_ssl = not args.no_verify_ssl

    read_timeout = _resolve_read_timeout(args.timeout)
    logger.info(
        "将处理 %s 个条目；输出：%s；model=%s；base=%s；客户端读超时=%s",
        len(pairs),
        out_dir,
        args.model,
        api_base,
        "不限" if read_timeout is None else f"{read_timeout}s",
    )
    if use_chapter and args.look_from != args.look_to:
        logger.warning(
            "当前将连续处理 look %s~%s；若需控制额度，建议每次只跑一张（--look-from N，省略 --look-to）",
            args.look_from,
            args.look_to,
        )

    ok = 0
    skipped = 0
    failed = 0

    def append_fail(rec: Dict[str, Any]) -> None:
        nonlocal failed
        failed += 1
        with failures_path.open("a", encoding="utf-8") as lf:
            lf.write(json.dumps(rec, ensure_ascii=False) + "\n")

    for idx, source_path in pairs:
        try:
            if source_kind == "chapter_look":
                prompt = load_look_prompt(source_path)
            else:
                text = source_path.read_text(encoding="utf-8")
                prompt = extract_text_description_block(text)
        except ValueError as err:
            if args.continue_on_error:
                append_fail(
                    {
                        "kind": "parse_error",
                        "index": idx,
                        "source": str(source_path),
                        "error": str(err),
                    }
                )
                continue
            raise SystemExit(f"{source_path.name}: {err}") from err

        if source_kind == "chapter_look":
            stem = source_path.stem
            out_png = out_dir / f"{stem}_{args.model.replace('/', '_')}.png"
        else:
            stem = source_path.name[: -len("_text_description.md")]
            out_png = out_dir / f"{stem}_{args.model.replace('/', '_')}.png"

        if args.skip_existing and out_png.is_file():
            logger.info("[%s/%s] 已有 PNG，跳过", idx, stem)
            skipped += 1
            continue

        logger.info("[%s/%s] 生图 → %s", idx, stem, out_png.name)
        try:
            parsed = generate_one_image(
                api_key=api_key,
                api_base=api_base,
                prompt=prompt,
                model=args.model,
                size=size_arg,
                quality=quality_arg,
                verify_ssl=verify_ssl,
                timeout=args.timeout,
            )
            save_response_item(parsed, out_png, download_timeout=args.timeout)
        except (RuntimeError, ValueError, OSError, urllib.error.URLError) as exc:
            err_text = str(exc)
            kind = (
                "moderation_blocked"
                if "moderation_blocked" in err_text or "safety_system" in err_text
                else "generation_failed"
            )
            if args.continue_on_error:
                logger.warning("跳过（%s）: %s", kind, stem)
                append_fail(
                    {
                        "kind": kind,
                        "index": idx,
                        "source": _rel_path(source_path),
                        "error": err_text[:2000],
                    },
                )
                continue
            raise

        rec = {
            "source_kind": source_kind,
            "manifest_index": idx,
            "source": _rel_path(source_path),
            "output_png": _rel_path(out_png),
            "model": args.model,
            "prompt_chars": len(prompt),
        }
        if source_kind == "inverse_md":
            rec["manifest_md_index"] = idx
            rec["source_md"] = rec["source"]
        with manifest_path.open("a", encoding="utf-8") as lf:
            lf.write(json.dumps(rec, ensure_ascii=False) + "\n")
        ok += 1

    logger.info(
        "统计：成功 %s（清单 %s），跳过已有 %s，失败 %s（见 %s）",
        ok,
        _rel_path(manifest_path),
        skipped,
        failed,
        _rel_path(failures_path),
    )


if __name__ == "__main__":
    main()
