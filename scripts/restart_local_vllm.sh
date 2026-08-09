#!/usr/bin/env bash
# 停止并重启本地 vLLM（读取 fashion_config.yaml → local-llm）
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

read -r MODEL MODEL_PATH API_BASE <<< "$(python - <<'PY'
import yaml
from pathlib import Path
from urllib.parse import urlparse

cfg = yaml.safe_load(Path("fashion_config.yaml").read_text(encoding="utf-8")) or {}
llm = cfg.get("local-llm") or {}
api_base = (llm.get("api-base") or "http://127.0.0.1:8000/v1").rstrip("/")
parsed = urlparse(api_base)
port = parsed.port or (443 if parsed.scheme == "https" else 80)
print(llm.get("model", "Qwen2.5-3B-Instruct"), llm.get("model-path", "models/Qwen2.5-3B-Instruct"), port)
PY
)"

HOST="${VLLM_HOST:-127.0.0.1}"
PORT="${VLLM_PORT:-$API_BASE}"
GPU="${CUDA_VISIBLE_DEVICES:-0}"
LOG_DIR="${ROOT}/logs"
LOG_FILE="${LOG_DIR}/vllm.log"
DTYPE="${VLLM_DTYPE:-bfloat16}"
MAX_LEN="${VLLM_MAX_MODEL_LEN:-4096}"

mkdir -p "$LOG_DIR"

echo "[1/4] 停止旧进程 (port=${PORT})..."
if command -v fuser >/dev/null 2>&1; then
  fuser -k "${PORT}/tcp" 2>/dev/null || true
fi
pkill -f "vllm.entrypoints.openai.api_server" 2>/dev/null || true
sleep 2

echo "[2/4] 启动 vLLM: model=${MODEL}, path=${MODEL_PATH}, port=${PORT}, GPU=${GPU}"
CUDA_VISIBLE_DEVICES="$GPU" nohup python -m vllm.entrypoints.openai.api_server \
  --model "$MODEL_PATH" \
  --served-model-name "$MODEL" \
  --host "$HOST" \
  --port "$PORT" \
  --dtype "$DTYPE" \
  --max-model-len "$MAX_LEN" \
  >> "$LOG_FILE" 2>&1 &
echo $! > "${LOG_DIR}/vllm.pid"

echo "[3/4] 等待服务就绪 (最多 120s)..."
for i in $(seq 1 60); do
  if curl -sf "http://${HOST}:${PORT}/v1/models" >/dev/null 2>&1; then
    echo "[4/4] OK — vLLM 已就绪: http://${HOST}:${PORT}/v1"
    curl -s "http://${HOST}:${PORT}/v1/models" | python -m json.tool 2>/dev/null || true
    echo "日志: tail -f ${LOG_FILE}"
    exit 0
  fi
  sleep 2
done

echo "启动超时，请查看日志: tail -100 ${LOG_FILE}"
exit 1
