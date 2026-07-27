#!/usr/bin/env python3
"""CLI for image inverse parsing."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from plugins.image_inverse_parser import ImageInverseParser  # noqa: E402


IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="将时装图片逆解析为 text_description 文档")
    parser.add_argument("--image", action="append", default=[], help="图片路径；可重复传入")
    parser.add_argument("--image-dir", type=Path, default=None, help="批量图片目录")
    parser.add_argument("--out-dir", type=Path, default=None, help="输出目录；默认读取 fashion_config.yaml")
    parser.add_argument("--business-context", default="", help="可选业务/系列上下文")
    parser.add_argument("--extra-instruction", default="", help="可选额外指令")
    parser.add_argument("--model", default="", help="覆盖 image-inverse-parser.model")
    parser.add_argument("--temperature", type=float, default=None, help="覆盖 temperature")
    parser.add_argument("--max-tokens", type=int, default=None, help="覆盖 max-tokens")
    return parser.parse_args()


def collect_images(args: argparse.Namespace) -> list[Path]:
    images = [Path(item) for item in args.image]
    if args.image_dir:
        if not args.image_dir.is_dir():
            raise SystemExit(f"找不到图片目录：{args.image_dir}")
        images.extend(
            path
            for path in sorted(args.image_dir.iterdir())
            if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
        )
    if not images:
        raise SystemExit("请提供 --image 或 --image-dir")
    return images


def main() -> None:
    args = parse_args()
    overrides = {}
    if args.out_dir:
        overrides["output_dir"] = args.out_dir
    if args.model.strip():
        overrides["model"] = args.model.strip()
    if args.temperature is not None:
        overrides["temperature"] = args.temperature
    if args.max_tokens is not None:
        overrides["max_tokens"] = args.max_tokens

    parser = ImageInverseParser(**overrides)
    for image_path in collect_images(args):
        result = parser.parse_image(
            image_path,
            business_context=args.business_context,
            extra_instruction=args.extra_instruction,
        )
        output_path = parser.write_text_description_document(result)
        print(f"完成：{image_path} -> {output_path}")


if __name__ == "__main__":
    main()
