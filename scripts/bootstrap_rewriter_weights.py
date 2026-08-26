"""
Download Qwen2.5-7B-Instruct and materialize an independent Rewriter copy.

E: is too small for 7B weights (~15GB). Default physical root is D:\\models;
this script then creates directory junctions under ``models/`` so
``fashion_config.yaml`` paths keep working.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_PHYSICAL = Path(r"D:\models")
INSTRUCT_NAME = "Qwen2.5-7B-Instruct"
REWRITER_NAME = "Qwen2.5-7B-Rewriter"
HF_REPO = "Qwen/Qwen2.5-7B-Instruct"


def _make_junction(link: Path, target: Path) -> None:
    link.parent.mkdir(parents=True, exist_ok=True)
    if link.exists():
        try:
            if link.resolve() == target.resolve():
                print(f"junction ok: {link} -> {target}")
                return
        except OSError:
            pass
        try:
            link.unlink()
        except OSError:
            os.rmdir(link)
    completed = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(link), str(target)],
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise SystemExit(f"mklink /J failed:\n{completed.stdout}\n{completed.stderr}")
    print(completed.stdout.strip() or f"junction: {link} -> {target}")


def _download_instruct(dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    cfg = dest / "config.json"
    weights = list(dest.glob("*.safetensors")) + list(dest.glob("model*.safetensors"))
    if cfg.exists() and (weights or list(dest.glob("model-*.safetensors"))):
        print(f"Instruct already present: {dest}")
        return
    os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
    from huggingface_hub import snapshot_download

    print(f"Downloading {HF_REPO} -> {dest}")
    snapshot_download(
        repo_id=HF_REPO,
        local_dir=str(dest),
        local_dir_use_symlinks=False,
        resume_download=True,
    )
    print("Download finished.")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--physical-root", type=Path, default=DEFAULT_PHYSICAL)
    p.add_argument("--skip-download", action="store_true")
    p.add_argument("--skip-copy", action="store_true")
    args = p.parse_args()

    physical_instruct = (args.physical_root / INSTRUCT_NAME).resolve()
    physical_rewriter = (args.physical_root / REWRITER_NAME).resolve()
    link_instruct = REPO / "models" / INSTRUCT_NAME
    link_rewriter = REPO / "models" / REWRITER_NAME

    free_gb = shutil.disk_usage(str(args.physical_root.drive) + "\\").free / 1024**3
    if free_gb < 20 and not args.skip_download:
        raise SystemExit(
            f"{args.physical_root.drive} free space {free_gb:.1f} GB < 20 GB; "
            "need room for Instruct + Rewriter copies."
        )

    if not args.skip_download:
        _download_instruct(physical_instruct)

    if not args.skip_copy:
        if not (physical_instruct / "config.json").exists():
            raise SystemExit(f"missing Instruct config: {physical_instruct}")
        if physical_rewriter.exists() and (physical_rewriter / "config.json").exists():
            print(f"Rewriter already present: {physical_rewriter}")
        else:
            if physical_rewriter.exists():
                shutil.rmtree(physical_rewriter)
            print(f"Copying Instruct -> Rewriter ({physical_rewriter})")
            shutil.copytree(physical_instruct, physical_rewriter)
            print("Copy finished.")

    _make_junction(link_instruct, physical_instruct)
    _make_junction(link_rewriter, physical_rewriter)
    print("Done. Paths:")
    print(f"  {link_instruct} -> {physical_instruct}")
    print(f"  {link_rewriter} -> {physical_rewriter}")


if __name__ == "__main__":
    if sys.platform != "win32":
        raise SystemExit("this bootstrap currently uses Windows junctions")
    main()
