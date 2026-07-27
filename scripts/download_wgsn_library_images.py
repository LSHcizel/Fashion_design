#!/usr/bin/env python3
"""
下载 WGSN China 检索页中的图片。

首次运行建议使用 --login 手动登录并保存浏览器会话，后续运行可复用该会话：

    python scripts/download_wgsn_library_images.py --login
    python scripts/download_wgsn_library_images.py --url "https://www.wgsnchina.cn/library/results/ce7d4e8c22d01a063ecefe196c432ffd" --expected 79
    python scripts/download_wgsn_library_images.py --url "URL1" --url "URL2" --workers 2
    python scripts/download_wgsn_library_images.py --url-file wgsn_urls.txt --workers 4

依赖：

    pip install playwright
    python -m playwright install chromium

说明：脚本只复用你已授权登录的账号会话，不绕过登录或权限控制。
"""

from __future__ import annotations

import argparse
import os
import hashlib
import json
import mimetypes
import re
import sys
import time
from dataclasses import dataclass
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urljoin, urlparse

try:
    from playwright.sync_api import BrowserContext, Page, Response, sync_playwright
except ImportError:  # pragma: no cover - 给未安装依赖时提供清晰提示
    BrowserContext = Any  # type: ignore
    Page = Any  # type: ignore
    Response = Any  # type: ignore
    sync_playwright = None  # type: ignore


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_URL = "https://www.wgsnchina.cn/library/results/ce7d4e8c22d01a063ecefe196c432ffd"
DEFAULT_AUTH_STATE = REPO_ROOT / ".cache" / "wgsn_storage_state.json"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "downloads" / "wgsn_library_images"
IMAGE_EXTENSIONS = {
    ".avif",
    ".bmp",
    ".gif",
    ".jpeg",
    ".jpg",
    ".png",
    ".svg",
    ".webp",
}


@dataclass
class ImageCandidate:
    url: str
    source: str
    width: int = 0
    height: int = 0
    alt: str = ""
    order: int = 0


@dataclass
class DownloadResult:
    url: str
    output_dir: str
    candidate_count: int
    downloaded_count: int
    ok: bool
    error: str = ""


def require_playwright() -> None:
    if sync_playwright is None:
        raise SystemExit(
            "缺少依赖 playwright。\n"
            "请先执行：pip install playwright\n"
            "然后执行：python -m playwright install chromium"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="下载 WGSN China 检索页图片")
    parser.add_argument(
        "--url",
        action="append",
        default=None,
        help="检索结果页 URL；可重复传入多个 --url",
    )
    parser.add_argument(
        "--url-file",
        type=Path,
        default=None,
        help="批量 URL 文件，每行一个链接，空行和 # 开头的行会被忽略",
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT_DIR, help="图片输出根目录")
    parser.add_argument(
        "--auth-state",
        type=Path,
        default=DEFAULT_AUTH_STATE,
        help="Playwright 登录态文件路径，包含 cookie，请勿提交到 git",
    )
    parser.add_argument(
        "--login",
        action="store_true",
        help="打开浏览器手动登录，关闭前会保存登录态",
    )
    parser.add_argument(
        "--login-wait-seconds",
        type=int,
        default=0,
        help="登录模式下等待多少秒后自动保存登录态；0 表示等待终端 Enter",
    )
    parser.add_argument("--expected", type=int, default=0, help="期望下载的图片数量，例如 79")
    parser.add_argument("--max-images", type=int, default=0, help="最多下载多少张，0 表示不限制")
    parser.add_argument("--min-width", type=int, default=120, help="过滤小图标的最小宽度")
    parser.add_argument("--min-height", type=int, default=120, help="过滤小图标的最小高度")
    parser.add_argument("--scrolls", type=int, default=40, help="最多滚动次数")
    parser.add_argument("--wait-ms", type=int, default=900, help="每次滚动后的等待毫秒数")
    parser.add_argument(
        "--headless",
        action="store_true",
        help="无头模式运行；首次登录或排查问题时建议不加",
    )
    parser.add_argument(
        "--keep-query",
        action="store_true",
        help="去重时保留 URL query；默认忽略 query，避免同图不同签名重复下载",
    )
    parser.add_argument(
        "--include-url-regex",
        default="",
        help="只下载 URL 匹配该正则的图片，例如 media_cha_biarritz_ps27",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=0,
        help="并行进程数；0 表示根据 URL 数量自动决定",
    )
    parser.add_argument(
        "--folder-name",
        default="",
        help="单 URL 下载时强制指定子文件夹名；多 URL 时会自动追加序号避免冲突",
    )
    return parser.parse_args()


def resolve_urls(args: argparse.Namespace) -> list[str]:
    urls: list[str] = []
    if args.url:
        urls.extend(args.url)
    if args.url_file:
        if not args.url_file.is_file():
            raise SystemExit(f"找不到 URL 文件：{args.url_file}")
        for line in args.url_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                urls.append(line)

    if not urls:
        urls.append(DEFAULT_URL)

    deduped: list[str] = []
    seen: set[str] = set()
    for url in urls:
        if url not in seen:
            deduped.append(url)
            seen.add(url)
    return deduped


def first_url(args: argparse.Namespace) -> str:
    return resolve_urls(args)[0]


def normalize_url(url: str, keep_query: bool) -> str:
    parsed = urlparse(url)
    query = parsed.query if keep_query else ""
    return parsed._replace(query=query, fragment="").geturl()


def looks_like_image_url(url: str) -> bool:
    path = urlparse(url).path.lower()
    return Path(path).suffix in IMAGE_EXTENSIONS


def is_useful_dom_image(candidate: ImageCandidate, min_width: int, min_height: int) -> bool:
    if candidate.width <= 0 or candidate.height <= 0:
        return looks_like_image_url(candidate.url)
    return candidate.width >= min_width and candidate.height >= min_height


def safe_filename(text: str, fallback: str) -> str:
    text = unquote(text).strip() or fallback
    text = re.sub(r"[\\/:*?\"<>|\r\n\t]+", "_", text)
    text = re.sub(r"\s+", "_", text).strip("._ ")
    return (text or fallback)[:120]


def safe_folder_name(text: str, fallback: str) -> str:
    text = safe_filename(text, fallback)
    text = re.sub(r"_+", "_", text).strip("._ ")
    return (text or fallback)[:160]


def fallback_folder_name(url: str, index: int) -> str:
    digest = hashlib.sha1(url.encode("utf-8")).hexdigest()[:10]
    path_name = safe_filename(Path(urlparse(url).path).name, "wgsn")
    return f"{index:02d}_{path_name}_{digest}"


def extract_folder_name(page: Page, url: str, index: int) -> str:
    data: dict[str, Any] = page.evaluate(
        """
        () => {
          const skip = new Set([
            'WGSN', 'Insight', 'City by City', 'Fashion Design',
            'Fashion Buying', 'Beauty', 'Food & Drink', 'Interiors',
            'Consumer Tech', 'Sports & Outdoor', 'Barometer', 'Advisory',
            'Coloro', 'Pulse', '保存此搜索', '筛选', '下载', '搜索'
          ]);
          const parts = [];
          const add = (text) => {
            text = (text || '').replace(/\\s+/g, ' ').trim();
            if (!text || text.length > 48 || skip.has(text)) return;
            if (/^\\d+\\s*发现结果$/.test(text)) return;
            if (/^[×xX]$/.test(text)) return;
            if (!parts.includes(text)) parts.push(text);
          };

          for (const el of document.querySelectorAll('h1, h2')) {
            add(el.textContent);
          }

          const selectedSelector = [
            '[aria-pressed="true"]',
            '[aria-selected="true"]',
            '[class*="selected" i]',
            '[class*="active" i]',
            '[class*="tag" i]',
            '[class*="chip" i]'
          ].join(',');
          for (const el of document.querySelectorAll(selectedSelector)) {
            add(el.textContent);
          }

          // WGSN 的筛选 chip 常在页面顶部，即使没有 selected class，也能从位置识别。
          for (const el of document.querySelectorAll('button, [role="button"], a, span')) {
            const rect = el.getBoundingClientRect();
            if (rect.top < 150 && rect.width >= 16 && rect.width <= 260 && rect.height <= 44) {
              add(el.textContent);
            }
          }
          return { title: document.title || '', parts };
        }
        """
    )
    parts = [str(part).strip() for part in data.get("parts", []) if str(part).strip()]
    if not parts:
        title = str(data.get("title", "")).replace("WGSN", "").strip(" -|")
        if title:
            parts.append(title)

    if parts:
        return safe_folder_name("_".join(parts[:8]), fallback_folder_name(url, index))
    return fallback_folder_name(url, index)


def extract_result_count(page: Page) -> int:
    text = page.evaluate(
        """
        () => document.body ? document.body.innerText : ''
        """
    )
    match = re.search(r"(\d+)\s*发现结果", str(text))
    return int(match.group(1)) if match else 0


def output_dir_for_job(args: argparse.Namespace, folder_name: str, index: int, total: int) -> Path:
    if args.folder_name:
        folder_name = args.folder_name if total == 1 else f"{index:02d}_{args.folder_name}"
    elif total > 1:
        folder_name = f"{index:02d}_{folder_name}"
    return args.out / safe_folder_name(folder_name, fallback_folder_name("", index))


def extension_from_content_type(content_type: str) -> str:
    media_type = content_type.split(";", 1)[0].strip().lower()
    if media_type == "image/jpeg":
        return ".jpg"
    if media_type == "image/svg+xml":
        return ".svg"
    return mimetypes.guess_extension(media_type) or ""


def extension_for(url: str, content_type: str) -> str:
    suffix = Path(urlparse(url).path).suffix.lower()
    if suffix in IMAGE_EXTENSIONS:
        return suffix
    return extension_from_content_type(content_type) or ".jpg"


def candidate_filename(index: int, candidate: ImageCandidate, content_type: str) -> str:
    parsed = urlparse(candidate.url)
    stem = Path(parsed.path).stem
    if candidate.alt:
        stem = f"{safe_filename(candidate.alt, 'image')}_{safe_filename(stem, 'asset')}"
    stem = safe_filename(stem, hashlib.sha1(candidate.url.encode("utf-8")).hexdigest()[:10])
    return f"{index:03d}_{stem}{extension_for(candidate.url, content_type)}"


def extract_dom_images(page: Page, min_width: int, min_height: int) -> list[ImageCandidate]:
    raw_items: list[dict[str, Any]] = page.evaluate(
        """
        () => {
          const items = [];
          const push = (url, source, el) => {
            if (!url || url.startsWith('data:') || url.startsWith('blob:')) return;
            items.push({
              url,
              source,
              width: el?.naturalWidth || el?.clientWidth || 0,
              height: el?.naturalHeight || el?.clientHeight || 0,
              alt: el?.alt || el?.title || '',
              top: el?.getBoundingClientRect ? el.getBoundingClientRect().top : 0,
              left: el?.getBoundingClientRect ? el.getBoundingClientRect().left : 0
            });
          };
          const pushSrcset = (srcset, source, el) => {
            if (!srcset) return;
            for (const part of srcset.split(',')) {
              const url = part.trim().split(/\\s+/)[0];
              push(url, source, el);
            }
          };

          for (const img of document.querySelectorAll('img')) {
            push(img.currentSrc || img.src, 'img', img);
            pushSrcset(img.srcset, 'img-srcset', img);
          }
          for (const source of document.querySelectorAll('source[srcset]')) {
            pushSrcset(source.getAttribute('srcset'), 'source-srcset', source);
          }
          for (const el of document.querySelectorAll('*')) {
            const bg = getComputedStyle(el).backgroundImage;
            if (!bg || bg === 'none') continue;
            for (const match of bg.matchAll(/url\\(["']?([^"')]+)["']?\\)/g)) {
              push(match[1], 'background-image', el);
            }
          }
          return items.sort((a, b) => (a.top - b.top) || (a.left - b.left));
        }
        """
    )

    result: list[ImageCandidate] = []
    for order, item in enumerate(raw_items):
        absolute_url = urljoin(page.url, str(item.get("url", "")))
        candidate = ImageCandidate(
            url=absolute_url,
            source=str(item.get("source", "dom")),
            width=int(item.get("width") or 0),
            height=int(item.get("height") or 0),
            alt=str(item.get("alt") or ""),
            order=order,
        )
        if is_useful_dom_image(candidate, min_width, min_height):
            result.append(candidate)
    return result


def collect_images(page: Page, args: argparse.Namespace) -> list[ImageCandidate]:
    by_key: dict[str, ImageCandidate] = {}
    last_count = -1
    stable_rounds = 0
    target_count = args.expected or extract_result_count(page)
    discovery_order = 0

    def add(candidate: ImageCandidate) -> None:
        nonlocal discovery_order
        key = normalize_url(candidate.url, args.keep_query)
        if key not in by_key:
            discovery_order += 1
            candidate.order = discovery_order
            by_key[key] = candidate

    def scroll_lazy_containers() -> None:
        page.evaluate(
            """
            () => {
              window.scrollBy(0, 2600);
              document.documentElement.scrollTop += 2600;
              document.body.scrollTop += 2600;

              for (const el of document.querySelectorAll('*')) {
                const style = getComputedStyle(el);
                const canScroll = /(auto|scroll)/.test(style.overflowY)
                  && el.scrollHeight > el.clientHeight + 50;
                if (canScroll) {
                  el.scrollTop += 2600;
                }
              }
            }
            """
        )

    for _ in range(max(args.scrolls, 1)):
        for candidate in extract_dom_images(page, args.min_width, args.min_height):
            add(candidate)

        count = len(by_key)
        print(f"已发现 {count} 个图片候选")
        if target_count and count >= target_count:
            break

        stable_rounds = stable_rounds + 1 if count == last_count else 0
        if not target_count and stable_rounds >= 8:
            break

        last_count = count
        page.mouse.wheel(0, 2400)
        scroll_lazy_containers()
        page.wait_for_timeout(args.wait_ms)

    return sorted(by_key.values(), key=lambda candidate: candidate.order)


def download_images(
    context: BrowserContext,
    candidates: list[ImageCandidate],
    output_dir: Path,
    max_images: int,
) -> list[dict[str, Any]]:
    output_dir.mkdir(parents=True, exist_ok=True)
    limit = max_images if max_images > 0 else len(candidates)
    manifest: list[dict[str, Any]] = []

    for index, candidate in enumerate(candidates[:limit], start=1):
        try:
            response = context.request.get(candidate.url, timeout=30_000)
            if not response.ok:
                print(f"跳过 {candidate.url}，HTTP {response.status}")
                continue

            content_type = response.headers.get("content-type", "")
            if content_type and not content_type.lower().startswith("image/"):
                print(f"跳过非图片响应 {candidate.url}，content-type={content_type}")
                continue

            filename = candidate_filename(index, candidate, content_type)
            target = output_dir / filename
            target.write_bytes(response.body())
            manifest.append(
                {
                    "file": str(target.relative_to(output_dir)),
                    "url": candidate.url,
                    "source": candidate.source,
                    "width": candidate.width,
                    "height": candidate.height,
                    "alt": candidate.alt,
                    "order": candidate.order,
                    "content_type": content_type,
                }
            )
            print(f"下载 {len(manifest):03d}: {filename}")
            time.sleep(0.15)
        except Exception as exc:  # noqa: BLE001 - 单张失败不应中断整批下载
            print(f"下载失败 {candidate.url}: {exc}")

    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return manifest


def save_login_state(args: argparse.Namespace) -> None:
    require_playwright()
    args.auth_state.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto(first_url(args), wait_until="domcontentloaded")
        print("请在打开的浏览器中完成登录，并确认能看到目标检索页。")
        if args.login_wait_seconds > 0:
            print(f"将在 {args.login_wait_seconds} 秒后自动保存登录态...")
            page.wait_for_timeout(args.login_wait_seconds * 1000)
        else:
            input("登录完成后回到终端按 Enter 保存登录态...")
        context.storage_state(path=str(args.auth_state))
        browser.close()

    print(f"已保存登录态：{args.auth_state}")


def run_download_for_url(args: argparse.Namespace, url: str, index: int, total: int) -> DownloadResult:
    require_playwright()
    if not args.auth_state.exists():
        raise SystemExit(
            f"找不到登录态文件：{args.auth_state}\n"
            "请先运行：python scripts/download_wgsn_library_images.py --login"
        )

    network_images: dict[str, ImageCandidate] = {}
    prefix = f"[{index}/{total}] "

    def on_response(response: Response) -> None:
        content_type = response.headers.get("content-type", "").lower()
        if content_type.startswith("image/") or looks_like_image_url(response.url):
            key = normalize_url(response.url, args.keep_query)
            network_images.setdefault(key, ImageCandidate(url=response.url, source="network", order=1_000_000))

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=args.headless)
        context = browser.new_context(storage_state=str(args.auth_state))
        page = context.new_page()
        page.on("response", on_response)
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(2000)
        folder_name = extract_folder_name(page, url, index)

        candidates = collect_images(page, args)
        seen = {normalize_url(candidate.url, args.keep_query) for candidate in candidates}
        for key, candidate in network_images.items():
            if key not in seen:
                candidates.append(candidate)
                seen.add(key)
        candidates.sort(key=lambda candidate: candidate.order)
        if args.include_url_regex:
            include_pattern = re.compile(args.include_url_regex)
            candidates = [candidate for candidate in candidates if include_pattern.search(candidate.url)]

        output_dir = output_dir_for_job(args, folder_name, index, total)
        print(f"{prefix}输出目录：{output_dir}")
        print(f"{prefix}最终候选图片数：{len(candidates)}")
        manifest = download_images(context, candidates, output_dir, args.max_images)
        browser.close()

    print(f"{prefix}完成：下载 {len(manifest)} 张图片，输出目录：{output_dir}")
    return DownloadResult(
        url=url,
        output_dir=str(output_dir),
        candidate_count=len(candidates),
        downloaded_count=len(manifest),
        ok=True,
    )


def run_download_worker(args: argparse.Namespace, url: str, index: int, total: int) -> DownloadResult:
    try:
        return run_download_for_url(args, url, index, total)
    except Exception as exc:  # noqa: BLE001 - 单个页面失败不应中断整批任务
        return DownloadResult(
            url=url,
            output_dir="",
            candidate_count=0,
            downloaded_count=0,
            ok=False,
            error=str(exc),
        )


def run_downloads(args: argparse.Namespace) -> None:
    urls = resolve_urls(args)
    total = len(urls)
    if total == 1:
        result = run_download_worker(args, urls[0], 1, 1)
        if not result.ok:
            raise SystemExit(result.error)
        return

    workers = args.workers or min(total, max(os.cpu_count() or 1, 1))
    workers = max(1, min(workers, total))
    print(f"共 {total} 个链接，开启 {workers} 个进程并行下载。")

    results: list[DownloadResult] = []
    with ProcessPoolExecutor(max_workers=workers) as executor:
        future_map = {
            executor.submit(run_download_worker, args, url, index, total): url
            for index, url in enumerate(urls, start=1)
        }
        for future in as_completed(future_map):
            result = future.result()
            results.append(result)
            status = "完成" if result.ok else "失败"
            print(f"{status}: {result.url} -> {result.output_dir or result.error}")

    summary_path = args.out / "batch_manifest.json"
    args.out.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(
        json.dumps([result.__dict__ for result in results], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    failed = [result for result in results if not result.ok]
    if failed:
        raise SystemExit(f"批量下载完成，但有 {len(failed)} 个页面失败；详情见 {summary_path}")
    print(f"批量下载完成，汇总文件：{summary_path}")


def main() -> None:
    args = parse_args()
    if args.login:
        save_login_state(args)
        return
    run_downloads(args)


if __name__ == "__main__":
    main()
