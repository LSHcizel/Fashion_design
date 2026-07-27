"""
第 5 步 — 阶段 A / B 数据集导出（SFT + GRPO 结构化 JSONL）。

从 ``samples.jsonl``（第 4 步）读取样本，按 ``group_id`` 分组后：

- **阶段 A（SFT）**：每组取奖励最高的一条作为 assistant 标签，写出 chat 格式 JSONL。
- **阶段 B（GRPO）**：每组内计算优势（可选 EMNLP 2025「Rewarding the Unlikely」：π_old 下 logprob 排名 → r_i → 标准化），写出供策略梯度使用的 JSONL。

本模块仅负责导出 JSONL。**本地真训练**（HuggingFace SFT + GRPO）见子包 ``training/hf_grpo/``。
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Literal, Optional, Tuple, cast

from .grpo_compute import (
    build_group_training_rows,
    pick_reward_scalar,
    skip_rank_correction_for_group,
)
from .record_builder import SCHEMA_VERSION as SAMPLES_SCHEMA

DEFAULT_SFT_SCHEMA = "sft_phase_a_v1"


def _training_data_yaml_snippet() -> Dict[str, Any]:
    try:
        from plugins.text_description_evaluator.design_text_evaluator_api import (
            grpo_training_data_config,
        )
    except Exception:
        return {}
    return cast(Dict[str, Any], grpo_training_data_config() or {})


def _resolve_rank_correction_params(
    *,
    beta_rank: Optional[float],
    pi_old_model_for_ranking: Optional[str],
    old_policy_ranks_by_group: Optional[Dict[str, List[int]]],
) -> Tuple[Optional[float], Optional[str], bool]:
    """
    返回 (effective_beta, effective_pi_old_id, use_auto_rank)。

    ``use_auto_rank``：在 ``old_policy_ranks_by_group is None`` 且配置了 π_old 与正 β 时为 True。
    若 YAML / 参数未给 β 但指定了 π_old，则 effective_beta 默认 **0.25**（与 EMNLP 2025 主实验一致）。
    """
    td = _training_data_yaml_snippet()
    eff_beta: Optional[float] = beta_rank
    if eff_beta is None and td.get("rank-correction-beta") is not None:
        try:
            eff_beta = float(td["rank-correction-beta"])
        except (TypeError, ValueError):
            eff_beta = None

    eff_pi = (pi_old_model_for_ranking or "").strip() or None
    if eff_pi is None:
        raw = td.get("pi-old-model-for-ranking")
        if isinstance(raw, str) and raw.strip():
            eff_pi = raw.strip()

    if eff_beta is None and eff_pi:
        eff_beta = 0.25

    use_auto = (
        old_policy_ranks_by_group is None
        and bool(eff_pi)
        and eff_beta is not None
        and eff_beta > 0.0
    )
    if eff_beta is not None and eff_beta <= 0.0:
        eff_beta = None
    return eff_beta, eff_pi, use_auto


def default_grpo_export_dir(run_id: str) -> Path:
    """
    ``grpo.training-data.runs-dir`` / ``run_id`` / ``export-subdir``。
    用于在写出 ``phase_a_sft.jsonl`` / ``phase_b_grpo.jsonl`` 时与 Logger 目录对齐。
    """
    try:
        from plugins.text_description_evaluator.design_text_evaluator_api import (
            grpo_training_data_config,
        )
    except Exception:
        grpo_training_data_config = lambda: {}  # type: ignore[assignment, misc]
    td = grpo_training_data_config()
    runs_rel = td.get("runs-dir") or "training/runs"
    sub = td.get("export-subdir") or "export"
    if not isinstance(runs_rel, str) or not str(runs_rel).strip():
        runs_rel = "training/runs"
    if not isinstance(sub, str) or not str(sub).strip():
        sub = "export"
    project = Path(__file__).resolve().parents[1]
    return (project / str(runs_rel).strip() / run_id / str(sub).strip()).resolve()


def _read_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def load_samples_by_group(
    samples_jsonl: Path,
    *,
    include_filter: Optional[Callable[[Dict[str, Any]], bool]] = None,
) -> Dict[str, List[Dict[str, Any]]]:
    """按 ``group_id`` 聚合；可选只保留满足 ``include_filter(rec)`` 的样本。"""
    groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for rec in _read_jsonl(samples_jsonl):
        if include_filter and not include_filter(rec):
            continue
        gid = str(rec.get("group_id") or "")
        if not gid:
            continue
        groups[gid].append(rec)
    for gid in groups:
        groups[gid].sort(key=lambda r: int(r.get("candidate_index", 0)))
    return dict(groups)


def default_include_for_training(rec: Dict[str, Any]) -> bool:
    return bool((rec.get("training_filter") or {}).get("include_in_training", True))


def build_sft_record_for_group(
    records: List[Dict[str, Any]],
    *,
    reward_key: Literal["R_content", "total_score"] = "R_content",
    system_prompt_text: str = "",
) -> Optional[Dict[str, Any]]:
    """
    阶段 A：组内 argmax 奖励 → 一条 SFT 样本。

    ``messages``：若提供 ``system_prompt_text`` 则插入 system；否则仅 user/assistant。
    user 文本由 ``context.shared_source_text`` 与 ``context.business_context`` 拼接。
    """
    if not records:
        return None
    scored: List[Tuple[float, Dict[str, Any]]] = []
    for rec in records:
        scored.append((pick_reward_scalar(rec, prefer=reward_key), rec))
    best_r, best = max(scored, key=lambda x: x[0])
    ctx = best.get("context") or {}
    src = str(ctx.get("shared_source_text", "")).strip()
    biz = str(ctx.get("business_context", "")).strip()
    user_parts = []
    if biz:
        user_parts.append(f"[Business context]\n{biz}")
    user_parts.append(f"[Source text to rewrite]\n{src}")
    user_content = "\n\n".join(user_parts).strip()
    assistant = str(best.get("completion") or "").strip()
    if not user_content or not assistant:
        return None

    messages: List[Dict[str, str]] = []
    if system_prompt_text.strip():
        messages.append({"role": "system", "content": system_prompt_text.strip()})
    messages.append({"role": "user", "content": user_content})
    messages.append({"role": "assistant", "content": assistant})

    win_idx = best.get("candidate_index")
    return {
        "schema_version": DEFAULT_SFT_SCHEMA,
        "phase": "A_SFT",
        "group_id": best.get("group_id"),
        "group_round": best.get("group_round"),
        "chosen_candidate_index": win_idx,
        "S_fp": best.get("S_fp"),
        "R_content": best.get("R_content"),
        "reward_best": round(best_r, 8),
        "reward_key": reward_key,
        "source_samples_schema": SAMPLES_SCHEMA,
        "messages": messages,
    }


def export_two_phase_from_samples(
    samples_jsonl: Path,
    out_dir: Path,
    *,
    system_prompt_text: str = "",
    reward_key: Literal["R_content", "total_score"] = "R_content",
    beta_rank: Optional[float] = None,
    pi_old_model_for_ranking: Optional[str] = None,
    pi_old_dtype: Literal["bf16", "fp16", "fp32"] = "bf16",
    pi_old_max_length: int = 2048,
    rank_correction_skip_valve: bool = True,
    old_policy_ranks_by_group: Optional[Dict[str, List[int]]] = None,
    min_group_size: int = 2,
    filter_fn: Callable[[Dict[str, Any]], bool] = default_include_for_training,
) -> Dict[str, Any]:
    """
    从 ``samples.jsonl`` 导出阶段 A / B 两个 JSONL + 简单指标。

    Parameters
    ----------
    old_policy_ranks_by_group :
        可选：``{ group_id: [rank_0, rank_1, ...] }``，与组内 ``candidate_index`` 排序一致；
        rank 取值 1…G（1 最易生成）。若提供则**不再**自动用 π_old 算排名。
    pi_old_model_for_ranking :
        可选：HF 因果 LM id 或路径，用作 **π_old** 对组内各 completion 算平均 logprob 并排序。
        留空时读 ``fashion_config.yaml`` → ``grpo.training-data.pi-old-model-for-ranking``。
    beta_rank :
        可选：**β_rank**（EMNLP 2025）；留空时读 ``grpo.training-data.rank-correction-beta``。
        若仍为空且已配置 π_old，则默认 **0.25**。
    rank_correction_skip_valve :
        为 True 时：全组 R 非正或几乎相同则跳过排名修正（计划文档「安全阀」）。
    min_group_size :
        GRPO 至少需要 2 条才有非零组内方差；``G<min_group_size`` 的组可写入但 advantage 可能全 0。
    """
    eff_beta, eff_pi, use_auto_rank = _resolve_rank_correction_params(
        beta_rank=beta_rank,
        pi_old_model_for_ranking=pi_old_model_for_ranking,
        old_policy_ranks_by_group=old_policy_ranks_by_group,
    )

    rank_model = None
    rank_tokenizer = None
    rank_device = None
    if use_auto_rank:
        try:
            import torch

            from .pi_old_ranking import (
                compute_old_policy_ranks_for_group,
                load_pi_old_model_and_tokenizer,
            )
        except ImportError as exc:
            raise ImportError(
                "自动 π_old 排名需要 PyTorch、transformers 与本地 HF 权重；"
                "请安装 training/hf_grpo/requirements.txt 中的依赖。"
            ) from exc
        rank_model, rank_tokenizer = load_pi_old_model_and_tokenizer(
            eff_pi or "",
            dtype=pi_old_dtype,
        )
        rank_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        rank_model.to(rank_device)

    out_dir.mkdir(parents=True, exist_ok=True)
    path_a = out_dir / "phase_a_sft.jsonl"
    path_b = out_dir / "phase_b_grpo.jsonl"

    groups = load_samples_by_group(samples_jsonl, include_filter=filter_fn)

    n_groups = 0
    n_sft = 0
    n_grpo_rows = 0
    n_rank_applied = 0
    n_rank_skipped_valve = 0
    n_rank_manual = 0

    with path_a.open("w", encoding="utf-8") as fa, path_b.open("w", encoding="utf-8") as fb:
        for gid, recs in groups.items():
            n_groups += 1
            sft = build_sft_record_for_group(
                recs,
                reward_key=reward_key,
                system_prompt_text=system_prompt_text,
            )
            if sft:
                fa.write(json.dumps(sft, ensure_ascii=False) + "\n")
                n_sft += 1

            ranks: Optional[List[int]] = None
            beta_eff: Optional[float] = None
            rank_meta: Optional[Dict[str, Any]] = None

            if old_policy_ranks_by_group is not None:
                ranks = old_policy_ranks_by_group.get(gid)
                if ranks is not None:
                    if len(ranks) != len(recs):
                        raise ValueError(
                            f"group {gid}: old_policy_ranks length {len(ranks)} != G {len(recs)}"
                        )
                    beta_eff = eff_beta
                    rank_meta = {"rank_correction_applied": beta_eff is not None, "mode": "manual_ranks"}
                    n_rank_manual += 1
                else:
                    rank_meta = {
                        "rank_correction_applied": False,
                        "mode": "manual_ranks",
                        "skip_reason": "missing_group_id_in_old_policy_ranks_by_group",
                    }
            elif use_auto_rank and rank_model is not None and rank_tokenizer is not None:
                rewards_pre = [pick_reward_scalar(r, prefer=reward_key) for r in recs]
                assert rank_device is not None
                if rank_correction_skip_valve and skip_rank_correction_for_group(rewards_pre):
                    rank_meta = {
                        "rank_correction_applied": False,
                        "mode": "rewarding_the_unlikely",
                        "skip_reason": "valve_all_nonpositive_or_uniform",
                        "pi_old_model": eff_pi,
                    }
                    n_rank_skipped_valve += 1
                else:
                    ranks, logps = compute_old_policy_ranks_for_group(
                        recs,
                        tokenizer=rank_tokenizer,
                        model=rank_model,
                        device=rank_device,
                        max_length=pi_old_max_length,
                        system_prompt=system_prompt_text,
                    )
                    beta_eff = eff_beta
                    rank_meta = {
                        "rank_correction_applied": True,
                        "mode": "rewarding_the_unlikely",
                        "pi_old_model": eff_pi,
                        "old_policy_mean_logprobs": logps,
                    }
                    n_rank_applied += 1
            else:
                rank_meta = {"rank_correction_applied": False, "mode": "disabled"}

            b_rows = build_group_training_rows(
                recs,
                reward_key=reward_key,
                beta_rank=beta_eff,
                old_policy_ranks=ranks,
                rank_correction_group_meta=rank_meta,
            )
            for row in b_rows:
                fb.write(json.dumps(row, ensure_ascii=False) + "\n")
                n_grpo_rows += 1

    manifest = {
        "samples_jsonl": str(samples_jsonl.resolve()),
        "phase_a_sft_jsonl": str(path_a.resolve()),
        "phase_b_grpo_jsonl": str(path_b.resolve()),
        "two_phase_summary_txt": str((out_dir / "two_phase_summary.txt").resolve()),
        "groups": n_groups,
        "sft_examples": n_sft,
        "grpo_rows": n_grpo_rows,
        "reward_key": reward_key,
        "beta_rank_param": beta_rank,
        "rank_correction_beta_effective": eff_beta,
        "pi_old_model_for_ranking_effective": eff_pi,
        "rank_correction_auto_enabled": use_auto_rank,
        "rank_correction_groups_applied": n_rank_applied,
        "rank_correction_groups_skipped_valve": n_rank_skipped_valve,
        "rank_correction_groups_manual": n_rank_manual,
        "min_group_size_note": min_group_size,
        "phase_A": "监督微调：每组最高奖励 completion 作为 assistant 标签",
        "phase_B": "GRPO：R_content →（可选 Rewarding the Unlikely）r_i → 组内标准化 advantage；训练时叠加 KL(π||π_ref)",
    }
    (out_dir / "two_phase_summary.txt").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return manifest


class TwoPhaseTrainingPipeline:
    """便捷封装：绑定输出目录与可选系统提示。"""

    def __init__(self, run_dir: Path, *, system_prompt_text: str = "") -> None:
        self.run_dir = Path(run_dir)
        self.system_prompt_text = system_prompt_text

    def export_from_logger_samples(
        self,
        samples_jsonl: Path,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        kwargs.setdefault("system_prompt_text", self.system_prompt_text)
        return export_two_phase_from_samples(samples_jsonl, self.run_dir, **kwargs)
