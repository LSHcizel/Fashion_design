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
PYTHON="${PYTHON:-python}"
LOG_DIR="${ROOT}/logs"
LOG_FILE="${LOG_DIR}/vllm.log"
DTYPE="${VLLM_DTYPE:-bfloat16}"
MAX_LEN="${VLLM_MAX_MODEL_LEN:-2048}"
GPU_MEM_UTIL="${VLLM_GPU_MEMORY_UTILIZATION:-0.90}"

if ! "$PYTHON" -c "import vllm" 2>/dev/null; then
  echo "错误: 当前 Python 未安装 vllm: $("$PYTHON" -c 'import sys; print(sys.executable)')"
  echo "请先执行:"
  echo "  conda activate prompt_env"
  echo "  pip install -r scripts/requirements-vllm.txt"
  echo "或指定已安装 vllm 的解释器: PYTHON=/path/to/python bash scripts/restart_local_vllm.sh"
  exit 1
fi

mkdir -p "$LOG_DIR"

if command -v nvidia-smi >/dev/null 2>&1; then
  echo "[0/5] GPU 状态 (CUDA_VISIBLE_DEVICES=${GPU}):"
  nvidia-smi --query-gpu=index,memory.used,memory.free,memory.total --format=csv,noheader | sed 's/^/  /' || true
fi

echo "[1/5] 停止旧 vLLM 进程 (port=${PORT})..."
if command -v fuser >/dev/null 2>&1; then
  fuser -k "${PORT}/tcp" 2>/dev/null || true
fi
pkill -f "vllm.entrypoints.openai.api_server" 2>/dev/null || true
pkill -f "vllm.v1.engine" 2>/dev/null || true
pkill -f "EngineCore" 2>/dev/null || true
sleep 3

if command -v nvidia-smi >/dev/null 2>&1; then
  FREE_MB="$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i "$GPU" 2>/dev/null | tr -d ' ' || echo 0)"
  if [ "${FREE_MB:-0}" -lt 4096 ] 2>/dev/null; then
    echo "警告: GPU ${GPU} 空闲显存仅约 ${FREE_MB} MiB，可能仍有其它进程占用。"
    echo "  请执行 nvidia-smi 查看 PID，必要时: kill -9 <PID>"
    echo "  或换卡: CUDA_VISIBLE_DEVICES=1 bash scripts/restart_local_vllm.sh"
    echo "  或降显存: VLLM_MAX_MODEL_LEN=1024 VLLM_GPU_MEMORY_UTILIZATION=0.85 bash scripts/restart_local_vllm.sh"
  fi
fi

echo "[2/5] 启动 vLLM: model=${MODEL}, path=${MODEL_PATH}, port=${PORT}, GPU=${GPU}, max_len=${MAX_LEN}, gpu_mem=${GPU_MEM_UTIL}"
export PYTORCH_CUDA_ALLOC_CONF="${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True}"
CUDA_VISIBLE_DEVICES="$GPU" nohup "$PYTHON" -m vllm.entrypoints.openai.api_server \
  --model "$MODEL_PATH" \
  --served-model-name "$MODEL" \
  --host "$HOST" \
  --port "$PORT" \
  --dtype "$DTYPE" \
  --max-model-len "$MAX_LEN" \
  --gpu-memory-utilization "$GPU_MEM_UTIL" \
  >> "$LOG_FILE" 2>&1 &
echo $! > "${LOG_DIR}/vllm.pid"

echo "[3/5] 等待服务就绪 (最多 180s)..."
for i in $(seq 1 90); do
  if curl -sf "http://${HOST}:${PORT}/v1/models" >/dev/null 2>&1; then
    echo "[4/5] OK — vLLM 已就绪: http://${HOST}:${PORT}/v1"
    curl -s "http://${HOST}:${PORT}/v1/models" | python -m json.tool 2>/dev/null || true
    echo "[5/5] 日志: tail -f ${LOG_FILE}"
    exit 0
  fi
  sleep 2
done

echo "启动超时，请查看日志: tail -100 ${LOG_FILE}"
exit 1
