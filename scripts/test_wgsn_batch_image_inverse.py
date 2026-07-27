#!/usr/bin/env python3
"""
烟测：从 ``downloads/wgsn_latest_batch`` 递归选取前 N 张图片（默认 5），
调用 ``ImageInverseParser`` 做「图 → 忠实文字稿」，结果写入 ``fashion_research_dir``。

依赖：仓库根目录 ``fashion_config.yaml`` 中可用的多模态 API（与 ``image-inverse-parser`` 共用配置）。

在仓库根目录执行::

    python scripts/test_wgsn_batch_image_inverse.py
    python scripts/test_wgsn_batch_image_inverse.py --limit 5 --batch-root downloads/wgsn_latest_batch
    python scripts/test_wgsn_batch_image_inverse.py --subfolder \"01_...\" --min-filename-serial 6 --out-dir fashion_research_dir/wgsn_batch_image_inverse/<run> --append-manifest
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from plugins.image_inverse_parser import ImageInverseParser  # noqa: E402

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"}
DEFAULT_BATCH_REL = Path("downloads") / "wgsn_latest_batch"
DEFAULT_RESEARCH_REL = Path("fashion_research_dir") / "wgsn_batch_image_inverse"


def iter_images_recursive(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES:
            yield path


def filename_leading_serial(name: str) -> Optional[int]:
    """文件名形如 ``001_media_....jpg`` 时返回 1。"""
    if len(name) < 4:
        return None
    prefix = name[:3]
    if prefix.isdigit() and name[3] == "_":
        return int(prefix)
    return None


def safe_slug(idx: int, image_path: Path, batch_root: Path) -> str:
    """避免不同子目录下同 stem 冲突：02d + 相对路径 slug。"""
    rel = image_path.resolve().relative_to(batch_root.resolve())
    parts_slug = "__".join(p.replace(" ", "_") for p in rel.with_suffix("").parts)
    return f"{idx:02d}_{parts_slug}"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="WGSN 批量目录前 N 张图 → image_inverse_parser 文字稿测试",
    )
    p.add_argument(
        "--batch-root",
        type=Path,
        default=None,
        help=f"图片根目录（默认仓库内 {DEFAULT_BATCH_REL.as_posix()}）；用于 manifest 相对路径与 slug",
    )
    p.add_argument(
        "--subfolder",
        type=str,
        default="",
        help="仅在 batch-root 下该相对子目录内取图（不递归下层目录）；文件名排序",
    )
    p.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help=f"输出目录（默认 {DEFAULT_RESEARCH_REL.as_posix()}/<UTC 时间戳>）",
    )
    p.add_argument(
        "--limit",
        type=int,
        default=5,
        help="处理的图片数量（按相对路径字典序取前 N 张；-1 表示不限制）。与 --subfolder/--min-filename-serial 联用时仍可截断数量",
    )
    p.add_argument(
        "--min-filename-serial",
        type=int,
        default=None,
        metavar="N",
        help="仅处理文件名为三位数字前缀的图（如 006_*.jpg），且序号 >= N",
    )
    p.add_argument(
        "--append-manifest",
        action="store_true",
        help="若输出目录已有 manifest.json，则从已有最大 index 续编号并合并 outputs（不删除已有产物）",
    )
    p.add_argument(
        "--skip-if-output-exists",
        action="store_true",
        help="若目标 .md/.json 已存在则跳过 API，仅补齐 manifest（用于断网/SSL 失败后续跑）",
    )
    p.add_argument(
        "--business-context",
        default="",
        help="传给逆解析模型的可选业务/系列上下文",
    )
    p.add_argument(
        "--extra-instruction",
        default="",
        help="传给逆解析模型的可选追加指令",
    )
    return p.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    logger = logging.getLogger(__name__)
    args = parse_args()

    batch_root = (args.batch_root or (REPO_ROOT / DEFAULT_BATCH_REL)).resolve()
    if not batch_root.is_dir():
        raise SystemExit(f"找不到批量图片目录：{batch_root}")

    scan_root = batch_root
    if args.subfolder.strip():
        scan_root = (batch_root / args.subfolder.strip()).resolve()
        if not scan_root.is_dir():
            raise SystemExit(f"找不到子目录：{scan_root}")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = args.out_dir
    if out_dir is None:
        out_dir = REPO_ROOT / DEFAULT_RESEARCH_REL / stamp
    else:
        out_dir = Path(out_dir)
        if not out_dir.is_absolute():
            out_dir = REPO_ROOT / out_dir
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.subfolder.strip():
        candidates = sorted(
            (
                p
                for p in scan_root.iterdir()
                if p.is_file() and p.suffix.lower() in IMAGE_SUFFIXES
            ),
            key=lambda p: p.name,
        )
    else:
        candidates = sorted(
            iter_images_recursive(scan_root),
            key=lambda p: str(p.resolve().relative_to(batch_root)).replace("\\", "/"),
        )

    if args.min_filename_serial is not None:
        lo = int(args.min_filename_serial)
        candidates = [
            p
            for p in candidates
            if (s := filename_leading_serial(p.name)) is not None and s >= lo
        ]

    if not candidates:
        raise SystemExit(f"目录内没有符合条件的图片：{scan_root}")

    limit_val = args.limit
    if limit_val is None:
        limit_val = 5
    if limit_val < 0:
        selected = candidates
    else:
        selected = candidates[: max(1, limit_val)]

    logger.info(
        "符合条件 %s 张图，本轮处理 %s 张；batch_root=%s；输出目录：%s",
        len(candidates),
        len(selected),
        batch_root,
        out_dir,
    )

    manifest_path = out_dir / "manifest.json"
    manifest_rows: list[dict] = []
    start_index = 1
    prior_batch_root_str: Optional[str] = None
    if args.append_manifest and manifest_path.is_file():
        prev = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest_rows.extend(prev.get("outputs") or [])
        if manifest_rows:
            start_index = max(int(r.get("index", 0)) for r in manifest_rows) + 1
        prior_batch_root_str = prev.get("batch_root")

    parser = ImageInverseParser(output_dir=out_dir)

    for idx, image_path in enumerate(selected, start=start_index):
        slug = safe_slug(idx, image_path, batch_root)
        md_out = out_dir / f"{slug}_text_description.md"
        json_out = md_out.with_suffix(".json")
        logger.info(
            "处理 [本轮 %s/%s, manifest_index=%s] %s",
            idx - start_index + 1,
            len(selected),
            idx,
            image_path,
        )
        if args.skip_if_output_exists and md_out.is_file() and json_out.is_file():
            try:
                prev_rec = json.loads(json_out.read_text(encoding="utf-8"))
                model_name = str(prev_rec.get("model", "gpt-5.5"))
            except (OSError, json.JSONDecodeError):
                model_name = "gpt-5.5"
            logger.info("已存在产出，跳过 API：%s", md_out.name)
            result_model = model_name
        else:
            try:
                result = parser.parse_image(
                    image_path,
                    business_context=args.business_context,
                    extra_instruction=args.extra_instruction,
                )
                parser.write_text_description_document(result, output_path=md_out)
                result_model = result.model
            except Exception:
                logger.exception("失败：%s", image_path)
                raise
        rel_from_batch = str(image_path.resolve().relative_to(batch_root)).replace("\\", "/")
        manifest_rows.append(
            {
                "index": idx,
                "source_image_relative": rel_from_batch,
                "markdown": str(md_out.relative_to(REPO_ROOT)),
                "json": str(md_out.with_suffix(".json").relative_to(REPO_ROOT)),
                "model": result_model,
            },
        )

    batch_root_note = str(batch_root.relative_to(REPO_ROOT))
    body: dict = {
        "batch_root": prior_batch_root_str or batch_root_note,
        "image_count": len(manifest_rows),
        "outputs": manifest_rows,
    }
    if args.subfolder.strip():
        body["subfolder"] = args.subfolder.strip()
    if args.min_filename_serial is not None:
        body["min_filename_serial"] = int(args.min_filename_serial)

    manifest_path.write_text(
        json.dumps(body, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info("已写入 manifest：%s", manifest_path)


if __name__ == "__main__":
    main()
