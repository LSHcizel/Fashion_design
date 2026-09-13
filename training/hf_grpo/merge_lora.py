"""把 LoRA adapter merge 成一份完整权重，默认写到新目录，不覆盖原改写器。"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from .model_load import adapter_base_model_path, is_peft_adapter_dir, require_peft

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BASE = "models/Qwen2.5-7B-Rewriter"


def merge_lora(
    *,
    adapter: Path,
    out: Path,
    base: str = "",
    dtype: str = "bf16",
    allow_overwrite_base: bool = False,
) -> Path:
    adapter = Path(adapter).resolve()
    if not is_peft_adapter_dir(adapter):
        raise SystemExit(f"不是 LoRA 目录（缺 adapter_config.json）: {adapter}")

    base_id = (base or "").strip() or adapter_base_model_path(adapter)
    out = Path(out)
    if not out.is_absolute():
        out = (REPO_ROOT / out).resolve()
    else:
        out = out.resolve()
    base_resolved = Path(base_id)
    if not base_resolved.is_absolute():
        base_resolved = (REPO_ROOT / base_id).resolve()

    if out.exists() and any(out.iterdir()) and not allow_overwrite_base:
        raise SystemExit(f"输出目录已存在且非空，拒绝覆盖: {out}")
    if out == base_resolved and not allow_overwrite_base:
        raise SystemExit(
            f"拒绝写回基座 {base_resolved}。换一个 --out，例如 "
            "models/Qwen2.5-7B-Rewriter-grpo-v2"
        )

    require_peft()
    from peft import PeftModel

    torch_dtype = {"bf16": torch.bfloat16, "fp16": torch.float16, "fp32": None}[dtype]
    logger.info("base=%s adapter=%s → %s", base_id, adapter, out)
    tok_src = adapter if (adapter / "tokenizer_config.json").is_file() else str(base_id)
    tokenizer = AutoTokenizer.from_pretrained(tok_src, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        base_id,
        trust_remote_code=True,
        torch_dtype=torch_dtype,
    )
    model = PeftModel.from_pretrained(model, str(adapter))
    merged = model.merge_and_unload()
    out.mkdir(parents=True, exist_ok=True)
    merged.save_pretrained(str(out))
    tokenizer.save_pretrained(str(out))
    logger.info("已写出完整权重（原基座未改）: %s", out)
    return out


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    p = argparse.ArgumentParser(
        description="LoRA → 完整 HF 目录。不要默认写回 models/Qwen2.5-7B-Rewriter。",
    )
    p.add_argument(
        "--adapter",
        type=Path,
        required=True,
        help="LoRA 目录，例如 hf_checkpoints/grpo/round_04",
    )
    p.add_argument(
        "--base",
        type=str,
        default="",
        help="基座；空则读 adapter_config.json 的 base_model_name_or_path",
    )
    p.add_argument(
        "--out",
        type=Path,
        required=True,
        help="新的完整权重目录（不要填原来的 Rewriter 路径）",
    )
    p.add_argument("--dtype", choices=["bf16", "fp16", "fp32"], default="bf16")
    p.add_argument(
        "--allow-overwrite-base",
        action="store_true",
        help="允许 --out 与基座同一路径。会毁掉训练前快照，一般不要开。",
    )
    args = p.parse_args()
    merge_lora(
        adapter=args.adapter,
        out=args.out,
        base=args.base,
        dtype=args.dtype,
        allow_overwrite_base=args.allow_overwrite_base,
    )


if __name__ == "__main__":
    main()
