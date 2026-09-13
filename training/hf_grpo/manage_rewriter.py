"""
改写器服务权重：merge LoRA、切到新完整权重、恢复默认基座。

只改 ``fashion_config.yaml`` 的 ``grpo.rewriter-llm.model`` / ``model-path``。
``hf-local-training.ref-model`` 保持原改写器，作为 KL 锚点。

用法（仓库根目录）::

    # 当前这次冷启动：merge + 改配置（可选重启 8001）
    python -m training.hf_grpo.manage_rewriter apply \\
      --run-id grpo_chanel_inverse_v2 --restart

    # 只切到已 merge 的目录
    python -m training.hf_grpo.manage_rewriter use \\
      --merged models/Qwen2.5-7B-Rewriter-grpo-chanel-inverse-v2 --restart

    # 恢复默认改写器
    python -m training.hf_grpo.manage_rewriter restore --restart

    python -m training.hf_grpo.manage_rewriter status
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO_ROOT / "fashion_config.yaml"
DEFAULT_MODEL = "Qwen2.5-7B-Rewriter"
DEFAULT_PATH = "models/Qwen2.5-7B-Rewriter"
LATEST_NAME = "latest.json"


def _clear_merged_out(out: Path) -> None:
    out = Path(out)
    if not out.is_absolute():
        out = (REPO_ROOT / out).resolve()
    else:
        out = out.resolve()
    default = (REPO_ROOT / DEFAULT_PATH).resolve()
    if out == default:
        raise SystemExit(f"拒绝删除默认改写器: {out}")
    if out.exists():
        logger.info("清除旧 merge 目录: %s", out)
        shutil.rmtree(out)


def default_merged_dir(run_id: str) -> Path:
    return REPO_ROOT / "models" / f"Qwen2.5-7B-Rewriter-{run_id}"


def latest_adapter_dir(run_id: str) -> Path:
    latest = REPO_ROOT / "training" / "runs" / run_id / "hf_checkpoints" / "grpo" / LATEST_NAME
    if not latest.is_file():
        raise SystemExit(f"找不到 {latest}，请先完成短 GRPO")
    data = json.loads(latest.read_text(encoding="utf-8"))
    policy = Path(str(data.get("policy_dir") or ""))
    if not policy.is_dir():
        raise SystemExit(f"latest.json 的 policy_dir 不存在: {policy}")
    return policy


def patch_rewriter_llm_fields(text: str, *, model: str, model_path: str) -> str:
    """只改 ``rewriter-llm`` 块里的 model / model-path，保留注释与其它键。"""
    updates = {"model": model, "model-path": model_path}
    lines = text.splitlines(keepends=True)
    out = []
    in_block = False
    block_indent: Optional[int] = None
    child_indent: Optional[int] = None
    replaced = set()
    for line in lines:
        body = line.splitlines()[0]
        stripped = body.lstrip(" ")
        indent = len(body) - len(stripped)
        if not in_block:
            if stripped.rstrip() == "rewriter-llm:":
                in_block = True
                block_indent = indent
            out.append(line)
            continue
        if not stripped or stripped.startswith("#"):
            out.append(line)
            continue
        if block_indent is not None and indent <= block_indent:
            in_block = False
            out.append(line)
            continue
        if child_indent is None:
            child_indent = indent
        key = stripped.split(":", 1)[0].strip()
        if key in updates and indent == child_indent:
            ending = line[len(body) :]
            out.append(f'{indent * " "}{key}: "{updates[key]}"{ending}')
            replaced.add(key)
            continue
        out.append(line)
    missing = [k for k in updates if k not in replaced]
    if missing:
        raise SystemExit(f"fashion_config.yaml 的 rewriter-llm 缺少键: {missing}")
    return "".join(out)


def read_rewriter_llm(config_path: Path = CONFIG_PATH) -> Tuple[str, str]:
    text = config_path.read_text(encoding="utf-8")
    try:
        import yaml
    except ImportError:
        return DEFAULT_MODEL, DEFAULT_PATH
    cfg = yaml.safe_load(text) or {}
    llm = (cfg.get("grpo") or {}).get("rewriter-llm") or {}
    return str(llm.get("model") or DEFAULT_MODEL), str(llm.get("model-path") or DEFAULT_PATH)


def write_rewriter_llm(*, model: str, model_path: str, config_path: Path = CONFIG_PATH) -> None:
    original = config_path.read_text(encoding="utf-8")
    updated = patch_rewriter_llm_fields(original, model=model, model_path=model_path)
    config_path.write_text(updated, encoding="utf-8")
    logger.info("已更新 %s → model=%s path=%s", config_path, model, model_path)


def restart_rewriter_vllm(*, gpu: str = "1") -> None:
    script = REPO_ROOT / "scripts" / "restart_local_vllm.sh"
    if not script.is_file():
        raise SystemExit(f"找不到 {script}")
    if os.name == "nt":
        raise SystemExit("请在 Linux 训练机上重启: VLLM_GPU=1 VLLM_PROFILE=rewriter bash scripts/restart_local_vllm.sh")
    env = os.environ.copy()
    env["VLLM_PROFILE"] = "rewriter"
    env["VLLM_GPU"] = str(gpu)
    logger.info("重启改写器 vLLM GPU=%s", gpu)
    subprocess.run(["bash", str(script)], cwd=str(REPO_ROOT), env=env, check=True)


def _maybe_restart(args: argparse.Namespace) -> None:
    if args.restart:
        restart_rewriter_vllm(gpu=str(args.vllm_gpu))
    else:
        logger.info("配置已改，8001 仍是旧权重。生效请加 --restart，或手动:")
        logger.info("  VLLM_GPU=%s VLLM_PROFILE=rewriter bash scripts/restart_local_vllm.sh", args.vllm_gpu)


def cmd_status(_: argparse.Namespace) -> None:
    model, path = read_rewriter_llm()
    resolved = Path(path)
    if not resolved.is_absolute():
        resolved = (REPO_ROOT / path).resolve()
    using_default = Path(path).as_posix().rstrip("/") == DEFAULT_PATH
    print(f"rewriter-llm.model      = {model}")
    print(f"rewriter-llm.model-path = {path}")
    print(f"resolved                = {resolved}")
    print(f"mode                    = {'default' if using_default else 'custom'}")
    print(f"KL / 训练锚点保持        = {DEFAULT_PATH}（未改 hf-local-training.ref-model）")


def cmd_use(args: argparse.Namespace) -> None:
    merged = Path(args.merged)
    if not merged.is_absolute():
        merged = (REPO_ROOT / merged).resolve()
    if not (merged / "config.json").is_file():
        raise SystemExit(f"不是完整 HF 权重目录（缺 config.json）: {merged}")
    rel = merged
    try:
        rel = Path(os.path.relpath(merged, REPO_ROOT))
    except ValueError:
        pass
    model_path = rel.as_posix()
    model = args.served_name or merged.name
    write_rewriter_llm(model=model, model_path=model_path)
    _maybe_restart(args)


def cmd_restore(args: argparse.Namespace) -> None:
    write_rewriter_llm(model=DEFAULT_MODEL, model_path=DEFAULT_PATH)
    _maybe_restart(args)


def cmd_merge(args: argparse.Namespace) -> None:
    from .merge_lora import merge_lora

    if not args.adapter and not args.run_id:
        raise SystemExit("merge 需要 --run-id 或 --adapter")
    adapter = Path(args.adapter) if args.adapter else latest_adapter_dir(args.run_id)
    out = Path(args.out) if args.out else default_merged_dir(args.run_id or "merged")
    if args.run_id and not args.out:
        out = default_merged_dir(args.run_id)
    if (out / "config.json").is_file() and not args.force_remerge:
        logger.info("已有 merge 目录，跳过: %s", out)
        print(out)
        return
    _clear_merged_out(out)
    merge_lora(
        adapter=adapter,
        out=out,
        base=args.base,
        dtype=args.dtype,
        allow_overwrite_base=False,
    )
    print(out)


def cmd_apply(args: argparse.Namespace) -> None:
    if not args.run_id and not (args.adapter and args.merged):
        raise SystemExit("apply 需要 --run-id，或同时给 --adapter 与 --merged")
    run_id = args.run_id or ""
    adapter = Path(args.adapter) if args.adapter else latest_adapter_dir(run_id)
    merged = Path(args.merged) if args.merged else default_merged_dir(run_id)
    if not (merged / "config.json").is_file() or args.force_remerge:
        from .merge_lora import merge_lora

        if args.force_remerge:
            _clear_merged_out(merged)
        merge_lora(
            adapter=adapter,
            out=merged,
            base=args.base,
            dtype=args.dtype,
            allow_overwrite_base=False,
        )
    else:
        logger.info("复用已有 merge: %s", merged)
    args.merged = str(merged)
    args.served_name = args.served_name or Path(merged).name
    cmd_use(args)


def main(argv: Optional[list[str]] = None) -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    p = argparse.ArgumentParser(description="改写器：merge / 切新权重 / 恢复默认")
    sub = p.add_subparsers(dest="cmd", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--restart", action="store_true", help="改配置后重启 8001 改写器 vLLM")
    common.add_argument("--vllm-gpu", default="1", help="改写器 GPU，默认 1")

    sp = sub.add_parser("status", help="看当前 rewriter-llm 指向哪里")
    sp.set_defaults(func=cmd_status)

    su = sub.add_parser("use", parents=[common], help="把 rewriter-llm 指到已 merge 的完整权重")
    su.add_argument("--merged", type=Path, required=True, help="完整 HF 目录")
    su.add_argument("--served-name", default="", help="vLLM --served-model-name；默认用目录名")
    su.set_defaults(func=cmd_use)

    sr = sub.add_parser("restore", parents=[common], help="rewriter-llm 改回默认 Qwen2.5-7B-Rewriter")
    sr.set_defaults(func=cmd_restore)

    sm = sub.add_parser("merge", help="LoRA merge 到新目录，不覆盖默认改写器")
    sm.add_argument("--run-id", default="", help="读 training/runs/<id>/hf_checkpoints/grpo/latest.json")
    sm.add_argument("--adapter", type=Path, default=None, help="LoRA 目录；与 --run-id 二选一")
    sm.add_argument("--out", type=Path, default=None, help="输出目录；默认 models/Qwen2.5-7B-Rewriter-<run-id>")
    sm.add_argument("--base", default="", help="基座；空则读 adapter_config")
    sm.add_argument("--dtype", choices=["bf16", "fp16", "fp32"], default="bf16")
    sm.add_argument("--force-remerge", action="store_true")
    sm.set_defaults(func=cmd_merge)

    sa = sub.add_parser("apply", parents=[common], help="merge（如需要）+ 切 rewriter-llm")
    sa.add_argument("--run-id", default="", help="例如 grpo_chanel_inverse_v2")
    sa.add_argument("--adapter", type=Path, default=None)
    sa.add_argument("--merged", type=Path, default=None, help="merge 输出；默认 models/Qwen2.5-7B-Rewriter-<run-id>")
    sa.add_argument("--base", default="")
    sa.add_argument("--dtype", choices=["bf16", "fp16", "fp32"], default="bf16")
    sa.add_argument("--force-remerge", action="store_true")
    sa.add_argument("--served-name", default="")
    sa.set_defaults(func=cmd_apply)

    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
