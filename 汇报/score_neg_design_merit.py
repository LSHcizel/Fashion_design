"""Score DesignMerit for the 16-group original vs rewrite pack, then persist into 得分.json."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(r"c:\Users\lsh\Desktop\grpo_chanel_inverse_v3") / "负样本对照"
ORIG = ROOT / "01_原文原图"
NEW = ROOT / "02_高分改写新图"
CACHE = ROOT / "design_merit_scores.json"

PROJECT = Path(__file__).resolve().parents[1]
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

from plugins.text_description_evaluator.design_text_evaluator_api import (  # noqa: E402
    DesignTextEvaluator,
    apply_design_merit_auxiliary_caps,
    strip_eval_boilerplate,
)


def load_groups() -> list[dict]:
    return json.loads((ROOT / "对照一览.json").read_text(encoding="utf-8"))["groups"]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n").strip() if path.is_file() else ""


def score_design_merit(evaluator: DesignTextEvaluator, text: str) -> dict:
    raw = (text or "").strip()
    eval_prose = strip_eval_boilerplate(raw)
    text_for_judge = eval_prose if len(eval_prose) >= evaluator.MIN_VALIDATED_TEXT_LENGTH else raw
    module = next(m for m in evaluator.spec["quality_modules"] if m["name"] == "DesignMerit")
    metric_specs = evaluator._build_metric_specs(module["metrics"])
    module_output = evaluator.judge.judge_module(
        text_for_judge,
        "DesignMerit",
        metric_specs,
        "quality_score",
    )
    module_output = apply_design_merit_auxiliary_caps(raw, module_output)
    applicable: list[float] = []
    metrics = []
    for item in module_output.get("results") or []:
        metrics.append(
            {
                "metric": item.get("metric"),
                "applicable": item.get("applicable"),
                "score": item.get("score"),
                "hit": item.get("hit"),
                "reason": item.get("reason"),
            }
        )
        if item.get("applicable") and isinstance(item.get("score"), (int, float)):
            applicable.append(float(item["score"]))
    score = round(sum(applicable) / len(applicable), 4) if applicable else 0.0
    aux = module_output.get("auxiliary_caps") or {}
    return {
        "score": score,
        "applicable_metrics": len(applicable),
        "metrics": metrics,
        "auxiliary_applied": bool(aux.get("applied")),
        "auxiliary_cap": aux.get("cap"),
        "auxiliary_reason": aux.get("reason"),
    }


def load_cache() -> dict:
    if CACHE.is_file():
        return json.loads(CACHE.read_text(encoding="utf-8"))
    return {}


def save_cache(cache: dict) -> None:
    CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def patch_score_json(path: Path, payload: dict) -> None:
    data = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    data["DesignMerit"] = payload["score"]
    data["DesignMerit_detail"] = payload
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def score_one(evaluator: DesignTextEvaluator, text: str, retries: int = 4) -> dict:
    last = None
    for i in range(retries):
        try:
            return score_design_merit(evaluator, text)
        except Exception as exc:  # noqa: BLE001
            last = exc
            wait = 4 * (i + 1)
            print(f"  retry {i + 1}/{retries} after {wait}s: {exc}")
            time.sleep(wait)
    raise RuntimeError(last)


def main() -> None:
    groups = load_groups()
    evaluator = DesignTextEvaluator()
    judge = evaluator.judge
    cache = load_cache()
    cache.setdefault("judge_model", judge.model)
    cache.setdefault("judge_api_base", judge.api_base)
    cache.setdefault("groups", {})
    print(f"judge={judge.model} @ {judge.api_base}")

    for i, g in enumerate(groups, 1):
        gid = g["group_id"]
        entry = cache["groups"].setdefault(gid, {})
        print(f"[{i:02d}/{len(groups)}] {gid}")
        if "original" not in entry:
            text = read_text(ORIG / gid / "原描述.txt")
            entry["original"] = score_one(evaluator, text)
            save_cache(cache)
            print(f"  original DesignMerit={entry['original']['score']}")
        else:
            print(f"  original cached DesignMerit={entry['original']['score']}")
        if "rewrite" not in entry:
            text = read_text(NEW / gid / "高分改写.txt")
            entry["rewrite"] = score_one(evaluator, text)
            save_cache(cache)
            print(f"  rewrite  DesignMerit={entry['rewrite']['score']}")
        else:
            print(f"  rewrite  cached DesignMerit={entry['rewrite']['score']}")

        patch_score_json(ORIG / gid / "得分.json", entry["original"])
        patch_score_json(NEW / gid / "得分.json", entry["rewrite"])
        g["original_DesignMerit"] = entry["original"]["score"]
        g["best_DesignMerit"] = entry["rewrite"]["score"]
        g["delta_DesignMerit"] = round(entry["rewrite"]["score"] - entry["original"]["score"], 4)

    overview = json.loads((ROOT / "对照一览.json").read_text(encoding="utf-8"))
    by_id = {item["group_id"]: item for item in overview["groups"]}
    for g in groups:
        by_id[g["group_id"]].update(
            {
                "original_DesignMerit": g["original_DesignMerit"],
                "best_DesignMerit": g["best_DesignMerit"],
                "delta_DesignMerit": g["delta_DesignMerit"],
            }
        )
    overview["DesignMerit_judge_model"] = cache.get("judge_model")
    (ROOT / "对照一览.json").write_text(
        json.dumps(overview, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"wrote {CACHE}")


if __name__ == "__main__":
    main()
