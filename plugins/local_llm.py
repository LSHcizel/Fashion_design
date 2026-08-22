"""
本地 OpenAI 兼容推理（vLLM 等）配置与路由。

``fashion_config.yaml`` 双模型约定：
- ``local-llm:`` — **基座 7B**：workflow 生成 + 评判（权重冻结）
- ``grpo.rewriter-llm:`` — **改写器 7B**：K 路改写 + SFT/GRPO 训练对象

多模态 vision（reflection / 图片逆解析）仍走远程 API。
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

_LOCAL_ALIASES = frozenset({"local", "local-llm"})


def _load_fashion_config() -> Dict[str, Any]:
    config_path = Path(__file__).resolve().parents[1] / "fashion_config.yaml"
    if not config_path.exists():
        return {}
    try:
        with config_path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def local_llm_config() -> Dict[str, Any]:
    return dict(_load_fashion_config().get("local-llm") or {})


def rewriter_llm_config() -> Dict[str, Any]:
    """``grpo.rewriter-llm`` — 改写专用 vLLM / HF 权重。"""
    grpo = _load_fashion_config().get("grpo") or {}
    return dict(grpo.get("rewriter-llm") or {})


def rewriter_llm_enabled() -> bool:
    return bool(rewriter_llm_config().get("enabled", True))


def resolve_local_rewriter_endpoint() -> Optional[Dict[str, Any]]:
    """解析改写器 vLLM 端点；未启用时返回 None。"""
    if not rewriter_llm_enabled():
        return None
    cfg = rewriter_llm_config()
    api_base = (
        _opt_str(os.environ.get("REWRITER_LLM_API_BASE"))
        or _opt_str(cfg.get("api-base"))
    )
    api_key = (
        _opt_str(os.environ.get("REWRITER_LLM_API_KEY"))
        or _opt_str(cfg.get("api-key"))
        or "local"
    )
    model = (
        _opt_str(os.environ.get("REWRITER_LLM_MODEL"))
        or _opt_str(cfg.get("model"))
    )
    if not api_base or not model:
        return None
    timeout = int(cfg.get("timeout", 300))
    max_tokens = int(cfg.get("max-tokens", 2048))
    verify_ssl = bool(cfg.get("verify-ssl", False))
    return {
        "api_base": api_base.rstrip("/"),
        "api_key": api_key,
        "model": model,
        "timeout": timeout,
        "max_tokens": max_tokens,
        "verify_ssl": verify_ssl,
    }


def local_llm_enabled() -> bool:
    return bool(local_llm_config().get("enabled"))


def _opt_str(value: Any) -> Optional[str]:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def resolve_local_llm_endpoint() -> Optional[Dict[str, Any]]:
    """解析本地 vLLM / OpenAI 兼容端点；未启用时返回 None。"""
    if not local_llm_enabled():
        return None
    cfg = local_llm_config()
    api_base = (
        _opt_str(os.environ.get("LOCAL_LLM_API_BASE"))
        or _opt_str(cfg.get("api-base"))
    )
    api_key = (
        _opt_str(os.environ.get("LOCAL_LLM_API_KEY"))
        or _opt_str(cfg.get("api-key"))
        or "local"
    )
    model = (
        _opt_str(os.environ.get("LOCAL_LLM_MODEL"))
        or _opt_str(cfg.get("model"))
    )
    if not api_base or not model:
        return None
    timeout = int(cfg.get("timeout", 300))
    max_tokens = int(cfg.get("max-tokens", 4096))
    judge_max_tokens = int(cfg.get("judge-max-tokens", 2048))
    verify_ssl = bool(cfg.get("verify-ssl", False))
    return {
        "api_base": api_base.rstrip("/"),
        "api_key": api_key,
        "model": model,
        "timeout": timeout,
        "max_tokens": max_tokens,
        "judge_max_tokens": judge_max_tokens,
        "verify_ssl": verify_ssl,
    }


def local_llm_model_name() -> Optional[str]:
    ep = resolve_local_llm_endpoint()
    return ep["model"] if ep else None


def use_local_for_workflow() -> bool:
    cfg = local_llm_config()
    return local_llm_enabled() and bool(cfg.get("use-for-workflow", True))


def use_local_for_parallel_k_rewrite() -> bool:
    cfg = local_llm_config()
    pk = (_load_fashion_config().get("grpo") or {}).get("parallel-k-rewrite") or {}
    if "use-local-rewrite" in pk:
        if not bool(pk["use-local-rewrite"]):
            return False
        return rewriter_llm_enabled() and resolve_local_rewriter_endpoint() is not None
    if rewriter_llm_enabled() and resolve_local_rewriter_endpoint():
        return True
    return local_llm_enabled() and bool(cfg.get("use-for-parallel-k-rewrite", False))


def use_local_for_candidate_evaluation() -> bool:
    cfg = local_llm_config()
    pk = (_load_fashion_config().get("grpo") or {}).get("parallel-k-rewrite") or {}
    if "use-local-evaluation" in pk:
        return bool(pk["use-local-evaluation"])
    return local_llm_enabled() and bool(cfg.get("use-for-candidate-evaluation", False))


def use_local_for_text_evaluator() -> bool:
    cfg = local_llm_config()
    te = _load_fashion_config().get("text-evaluator") or {}
    if "use-local" in te:
        return bool(te["use-local"])
    return local_llm_enabled() and bool(cfg.get("use-for-text-evaluator", False))


def model_should_use_local(model_str: Optional[str]) -> bool:
    """判断 ``query_model`` / workflow 是否应走本地端点。"""
    ep = resolve_local_llm_endpoint()
    if not ep or not use_local_for_workflow():
        return False
    ms = (model_str or "").strip()
    if ms in _LOCAL_ALIASES:
        return True
    if ms == ep["model"]:
        return True
    llm_backend = _opt_str(_load_fashion_config().get("llm-backend"))
    if llm_backend and ms == llm_backend and llm_backend == ep["model"]:
        return True
    return False


def resolve_workflow_llm_backend(configured: Optional[str]) -> str:
    """若启用本地 workflow，将 ``llm-backend`` 解析为本地 served model 名。"""
    ep = resolve_local_llm_endpoint()
    if ep and use_local_for_workflow():
        return ep["model"]
    if configured:
        return configured.strip()
    return "gpt-5.4-mini"


def workflow_vision_model_name() -> Optional[str]:
    """本地 workflow 启用时，多模态 reflection 阶段使用的 API vision 模型。"""
    if not local_llm_enabled() or not use_local_for_workflow():
        return None
    cfg = local_llm_config()
    explicit = _opt_str(cfg.get("workflow-vision-model"))
    if explicit:
        return explicit
    grpo_ev = (_load_fashion_config().get("grpo") or {}).get("design-text-evaluator") or {}
    return _opt_str(grpo_ev.get("vision-model"))


def local_chat_completion(
    *,
    system_prompt: str,
    user_prompt: str,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    model: Optional[str] = None,
) -> str:
    """调用本地 OpenAI 兼容 chat/completions。"""
    from openai import OpenAI

    ep = resolve_local_llm_endpoint()
    if not ep:
        raise RuntimeError("local-llm 未启用或未配置 api-base / model")

    client = OpenAI(
        base_url=ep["api_base"],
        api_key=ep["api_key"],
        timeout=float(ep["timeout"]),
        max_retries=2,
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    kwargs: Dict[str, Any] = {
        "model": model or ep["model"],
        "messages": messages,
    }
    if temperature is not None:
        kwargs["temperature"] = temperature
    if max_tokens is not None:
        kwargs["max_tokens"] = max_tokens
    else:
        kwargs["max_tokens"] = ep["max_tokens"]

    completion = client.chat.completions.create(**kwargs)
    answer = completion.choices[0].message.content
    if not answer:
        raise RuntimeError("local LLM returned empty content")
    return answer


def try_local_chat_completion(
    model_str: str,
    system_prompt: str,
    user_prompt: str,
    temperature: Optional[float] = None,
) -> Optional[str]:
    """若 ``model_str`` 应走本地，则返回生成文本；否则返回 None。"""
    if not model_should_use_local(model_str):
        return None
    return local_chat_completion(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=temperature,
    )


class HybridGenerationJudge:
    """``generate_*`` 与 ``judge_*`` 可分别绑定不同 ``ApiLLMJudge`` 后端。"""

    def __init__(self, rewrite_judge: Any, evaluate_judge: Any) -> None:
        self._rewrite = rewrite_judge
        self._evaluate = evaluate_judge

    def generate_text(self, *args: Any, **kwargs: Any) -> str:
        return self._rewrite.generate_text(*args, **kwargs)

    def generate_multimodal(self, *args: Any, **kwargs: Any) -> str:
        return self._rewrite.generate_multimodal(*args, **kwargs)

    def judge_module(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._evaluate.judge_module(*args, **kwargs)

    def judge_quality_penalties(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._evaluate.judge_quality_penalties(*args, **kwargs)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._evaluate, name)


def build_local_api_judge(**overrides: Any) -> Any:
    """构造指向**基座** local-llm vLLM 的 ``ApiLLMJudge``（生成 / 评判）。"""
    from .text_description_evaluator.design_text_evaluator_api import ApiLLMJudge

    ep = resolve_local_llm_endpoint()
    if not ep:
        raise RuntimeError("local-llm 未启用或未配置 api-base / model")

    grpo_ev = (_load_fashion_config().get("grpo") or {}).get("design-text-evaluator") or {}
    defaults: Dict[str, Any] = {
        "api_key": ep["api_key"],
        "api_base": ep["api_base"],
        "model": ep["model"],
        "temperature": float(grpo_ev.get("temperature", 0.0)),
        "max_tokens": int(grpo_ev.get("max-tokens", ep["judge_max_tokens"])),
        "timeout": int(grpo_ev.get("timeout", ep["timeout"])),
        "verify_ssl": ep["verify_ssl"],
    }
    defaults.update(overrides)
    return ApiLLMJudge(**defaults)


def build_local_rewriter_api_judge(**overrides: Any) -> Any:
    """构造指向**改写器** grpo.rewriter-llm vLLM 的 ``ApiLLMJudge``。"""
    from .text_description_evaluator.design_text_evaluator_api import ApiLLMJudge

    ep = resolve_local_rewriter_endpoint()
    if not ep:
        raise RuntimeError("grpo.rewriter-llm 未启用或未配置 api-base / model")

    pk = (_load_fashion_config().get("grpo") or {}).get("parallel-k-rewrite") or {}
    defaults: Dict[str, Any] = {
        "api_key": ep["api_key"],
        "api_base": ep["api_base"],
        "model": ep["model"],
        "temperature": float(pk.get("rewrite-temperature", 0.3)),
        "max_tokens": int(pk.get("rewrite-max-tokens", ep["max_tokens"])),
        "timeout": int(pk.get("rewrite-timeout", ep["timeout"])),
        "verify_ssl": ep["verify_ssl"],
    }
    defaults.update(overrides)
    return ApiLLMJudge(**defaults)


def _explicit_api_overrides(
    *,
    api_key: Optional[str],
    api_base: Optional[str],
    model: Optional[str],
) -> bool:
    return any(_opt_str(v) for v in (api_key, api_base, model))


def build_parallel_k_evaluator() -> Any:
    """K 路改写：改写 → rewriter-llm；评判 → local-llm 基座（冻结）。"""
    from .text_description_evaluator.design_text_evaluator_api import DesignTextEvaluator

    evaluator = DesignTextEvaluator()
    pk = (_load_fashion_config().get("grpo") or {}).get("parallel-k-rewrite") or {}

    use_rewrite = use_local_for_parallel_k_rewrite()
    use_eval = use_local_for_candidate_evaluation()

    if not use_rewrite and not use_eval:
        return evaluator

    api_judge = evaluator.judge

    rewrite_judge = (
        build_local_rewriter_api_judge()
        if use_rewrite
        else api_judge
    )
    eval_judge = (
        build_local_api_judge()
        if use_eval and local_llm_enabled() and resolve_local_llm_endpoint()
        else api_judge
    )

    if rewrite_judge is eval_judge:
        evaluator.judge = rewrite_judge
    else:
        evaluator.judge = HybridGenerationJudge(rewrite_judge, eval_judge)
    return evaluator


def build_workflow_text_evaluator(
    *,
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.0,
    rewriter_temperature: Optional[float] = None,
) -> Any:
    """workflow ``text-evaluator``：默认按 ``local-llm.use-for-text-evaluator`` 路由。"""
    from .text_description_evaluator.design_text_evaluator_api import DesignTextEvaluator

    del rewriter_temperature
    if (
        use_local_for_text_evaluator()
        and resolve_local_llm_endpoint()
        and not _explicit_api_overrides(api_key=api_key, api_base=api_base, model=model)
    ):
        te = _load_fashion_config().get("text-evaluator") or {}
        return DesignTextEvaluator(
            api_key=resolve_local_llm_endpoint()["api_key"],
            api_base=resolve_local_llm_endpoint()["api_base"],
            model=resolve_local_llm_endpoint()["model"],
            temperature=float(te.get("temperature", temperature)),
            max_new_tokens=int(
                te.get("max-tokens")
                or (_load_fashion_config().get("grpo") or {})
                .get("design-text-evaluator", {})
                .get("max-tokens", resolve_local_llm_endpoint()["judge_max_tokens"])
            ),
            timeout=int(
                te.get("timeout")
                or (_load_fashion_config().get("grpo") or {})
                .get("design-text-evaluator", {})
                .get("timeout", resolve_local_llm_endpoint()["timeout"])
            ),
            verify_ssl=resolve_local_llm_endpoint()["verify_ssl"],
        )
    return DesignTextEvaluator(
        api_key=api_key,
        api_base=api_base,
        model=model,
        temperature=temperature,
    )
