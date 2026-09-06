"""
短 GRPO 每轮后的验收摘要。

本摘要统计的是当前 ``phase_b`` / samples 上的标签与门限，
**不会**随刚写入的 policy 权重自动变化。要判断本轮改写器是否更好，
需用该 policy 重新 K 路抽检后再跑本模块。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Union

JsonPath = Union[str, Path]


def read_jsonl(path: JsonPath) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def _mean(xs: List[float]) -> Optional[float]:
    if not xs:
        return None
    return round(sum(xs) / len(xs), 6)


def _rate(ok: int, n: int) -> Optional[float]:
    if n <= 0:
        return None
    return round(ok / n, 6)


def summarize_rows(rows: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    """从 phase_b 或 samples 行汇总门限、奖励、长度。"""
    r_content: List[float] = []
    s_fp: List[float] = []
    penalties: List[float] = []
    char_lens: List[float] = []
    advs: List[float] = []
    n = 0
    n_train = 0
    both_ok = 0
    score_ok = 0
    penalty_ok = 0
    gate_n = 0
    groups = set()

    for rec in rows:
        n += 1
        gid = rec.get("group_id")
        if gid:
            groups.add(str(gid))
        if (rec.get("training_filter") or {}).get("include_in_training", True):
            n_train += 1

        r = (rec.get("grpo") or {}).get("reward_scalar")
        if r is None:
            r = rec.get("R_content")
        if r is None:
            rc = rec.get("r_content") or {}
            r = rc.get("R_content") or rc.get("r_Q")
        if r is not None:
            r_content.append(float(r))

        sf = rec.get("S_fp")
        if sf is None:
            sf = (rec.get("scores_compact") or {}).get("S_fp")
        if sf is not None:
            s_fp.append(float(sf))

        cl = rec.get("char_len")
        if cl is not None:
            char_lens.append(float(cl))

        adv = rec.get("advantage")
        if adv is not None:
            advs.append(float(adv))

        pen = rec.get("penalties") or {}
        tp = pen.get("total_penalty") if isinstance(pen, dict) else None
        if tp is None:
            tp = (rec.get("scores_compact") or {}).get("total_penalty")
        if tp is not None:
            penalties.append(float(tp))

        g = rec.get("gates_compact") or {}
        if g:
            gate_n += 1
            if g.get("both_passed") is True:
                both_ok += 1
            if g.get("score_gate_passed") is True:
                score_ok += 1
            if g.get("penalty_gate_passed") is True:
                penalty_ok += 1

    pos_adv = sum(1 for a in advs if a > 0)
    return {
        "rows": n,
        "groups": len(groups),
        "included_for_training": n_train,
        "mean_R_content": _mean(r_content),
        "mean_S_fp": _mean(s_fp),
        "mean_total_penalty": _mean(penalties),
        "mean_char_len": _mean(char_lens),
        "score_gate_pass_rate": _rate(score_ok, gate_n),
        "penalty_gate_pass_rate": _rate(penalty_ok, gate_n),
        "both_gates_pass_rate": _rate(both_ok, gate_n),
        "gate_rows": gate_n,
        "advantage_positive_rate": _rate(pos_adv, len(advs)) if advs else None,
        "mean_advantage": _mean(advs),
    }


def summarize_jsonl(path: JsonPath) -> Dict[str, Any]:
    p = Path(path)
    summary = summarize_rows(read_jsonl(p))
    summary["path"] = str(p.resolve())
    return summary


HUMAN_CHECKLIST = (
    "抽看改写是否编造原文没有的事实",
    "主干单品是否对称稳定、能否直接当出图 prompt",
    "是否明显靠写长涨分",
    "得分门与惩罚门通过率是否好于上一轮抽检",
)


def build_round_accept(
    *,
    round_idx: int,
    policy_dir: Path,
    ref_dir: str,
    epochs: float,
    data_summary: Dict[str, Any],
    sft_dir: Optional[Path] = None,
    note: str = "",
) -> Dict[str, Any]:
    return {
        "round": int(round_idx),
        "policy_dir": str(Path(policy_dir).resolve()),
        "ref_dir": ref_dir,
        "sft_dir": str(Path(sft_dir).resolve()) if sft_dir else None,
        "epochs_this_round": float(epochs),
        "cold_start": {
            "dual_head_rm": "once",
            "sft": "once",
            "grpo": "short_rounds",
            "kl_ref": "frozen_at_cold_start",
        },
        "data": data_summary,
        "human_checklist": list(HUMAN_CHECKLIST),
        "note": note
        or (
            "data 统计的是当前 phase_b 标签，不是本轮权重的在线表现。"
            "验收本轮改写器请用 policy_dir 重新 K 路抽检；不满意则复用双头 RM、跳过 SFT，再开下一轮短 GRPO。"
        ),
    }


def write_json(path: JsonPath, obj: Dict[str, Any]) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    return out
