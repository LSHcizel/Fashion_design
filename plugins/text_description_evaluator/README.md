# Text Description Evaluator Plugin

该插件用于对 `fashion design` 场景中的 `text_description` 做独立评估。

## 功能

- 基于 OpenAI 兼容接口做 `LLM-as-a-judge`
- 对单条文本或目录内批量 `txt` 文件评分
- 输出覆盖度、质量、加分项、诊断信息与逐指标结果
- 作为独立插件存在，当前未接入 `fashion_workflow.py`

## 目录

- `design_text_evaluator_api.py`：核心 API
- `run_design_text_evaluator.py`：命令行入口
- `fashion_prompt_optimizer_spec.json`：指标定义、`llm.default_model` 与 `optimization_compact_summary`
- `fashion_sys_prompt.txt`：优化器系统提示词
- `CONTEXT.md`：模型与 optimize 上下文（token）说明

## 环境变量

- `AI_API_KEY`
- `AI_API_BASE`
- `AI_API_MODEL`（未设置时使用 spec 中 `llm.default_model`，当前默认 **gpt-5.4-mini**）

## 调用方式

作为 Python API 导入：

```python
from plugins.text_description_evaluator import DesignTextEvaluator

evaluator = DesignTextEvaluator()
result = evaluator.evaluate_text("your fashion description")
```

作为 CLI 运行：

```bash
python -m plugins.text_description_evaluator.run_design_text_evaluator --input "path/to/file.txt" --pretty
```
