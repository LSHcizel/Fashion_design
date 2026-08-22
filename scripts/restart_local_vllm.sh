#!/usr/bin/env bash
# 停止并重启本地 vLLM（读取 fashion_config.yaml）
# 基座（生成+评判）: VLLM_GPU=0 bash scripts/restart_local_vllm.sh
# 改写器（K 路改写）: VLLM_GPU=1 VLLM_PROFILE=rewriter bash scripts/restart_local_vllm.sh
# 双实例: bash scripts/restart_local_vllm.sh && VLLM_PROFILE=rewriter VLLM_GPU=1 bash scripts/restart_local_vllm.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PROFILE="${VLLM_PROFILE:-base}"

read -r MODEL MODEL_PATH PORT MAX_LEN_CFG <<< "$(python - <<PY
import yaml
from pathlib import Path
from urllib.parse import urlparse

profile = "${PROFILE}"
cfg = yaml.safe_load(Path("fashion_config.yaml").read_text(encoding="utf-8")) or {}
if profile == "rewriter":
    llm = (cfg.get("grpo") or {}).get("rewriter-llm") or {}
    default_model = "Qwen2.5-7B-Rewriter"
    default_path = "models/Qwen2.5-7B-Rewriter"
    default_port = 8001
else:
    llm = cfg.get("local-llm") or {}
    default_model = "Qwen2.5-7B-Instruct"
    default_path = "models/Qwen2.5-7B-Instruct"
    default_port = 8000
api_base = (llm.get("api-base") or f"http://127.0.0.1:{default_port}/v1").rstrip("/")
parsed = urlparse(api_base)
port = parsed.port or (443 if parsed.scheme == "https" else default_port)
max_len = llm.get("max-model-len", 8192)
print(llm.get("model", default_model), llm.get("model-path", default_path), port, max_len)
PY
)"

pick_freest_gpu() {
  nvidia-smi --query-gpu=index,memory.free --format=csv,noheader,nounits 2>/dev/null \
    | awk -F', ' '{gsub(/ /, "", $1); gsub(/ /, "", $2); print $2, $1}' \
    | sort -rn | awk 'NR==1 {print $2}'
}

if [ -n "${VLLM_GPU:-}" ]; then
  GPU="$VLLM_GPU"
elif [ -n "${CUDA_VISIBLE_DEVICES:-}" ]; then
  GPU="$CUDA_VISIBLE_DEVICES"
elif command -v nvidia-smi >/dev/null 2>&1; then
  GPU="$(pick_freest_gpu || true)"
  GPU="${GPU:-0}"
else
  GPU="0"
fi
if [ -z "${PYTHON:-}" ]; then
  if [ -x "${ROOT}/venv/bin/python" ]; then
    PYTHON="${ROOT}/venv/bin/python"
  else
    PYTHON="python"
  fi
fi
HOST="${VLLM_HOST:-127.0.0.1}"
PORT="${VLLM_PORT:-$PORT}"
LOG_DIR="${ROOT}/logs"
LOG_FILE="${LOG_DIR}/vllm_${PROFILE}.log"
PID_FILE="${LOG_DIR}/vllm_${PROFILE}.pid"
DTYPE="${VLLM_DTYPE:-bfloat16}"
MAX_LEN="${VLLM_MAX_MODEL_LEN:-$MAX_LEN_CFG}"
GPU_MEM_UTIL="${VLLM_GPU_MEMORY_UTILIZATION:-0.85}"
MIN_FREE_MB="${VLLM_MIN_FREE_MB:-16384}"
ENFORCE_EAGER="${VLLM_ENFORCE_EAGER:-1}"

gpu_free_mb() {
  nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i "$GPU" 2>/dev/null | tr -d ' ' || echo 0
}

show_gpu_pids() {
  echo "  GPU ${GPU} 计算进程:"
  nvidia-smi --query-compute-apps=pid,process_name,used_gpu_memory --format=csv,noheader -i "$GPU" 2>/dev/null | sed 's/^/    /' || echo "    (无)"
}

if ! "$PYTHON" -c "import vllm" 2>/dev/null; then
  echo "错误: 当前 Python 未安装 vllm: $("$PYTHON" -c 'import sys; print(sys.executable)')"
  echo "本项目 vllm 通常在: ${ROOT}/venv/bin/python"
  echo "请执行:"
  echo "  source venv/bin/activate && pip install -r scripts/requirements-vllm.txt"
  echo "或指定解释器:"
  echo "  PYTHON=${ROOT}/venv/bin/python bash scripts/restart_local_vllm.sh"
  exit 1
fi

mkdir -p "$LOG_DIR"

if command -v nvidia-smi >/dev/null 2>&1; then
  echo "[0/6] GPU 状态 (选用 GPU ${GPU}，可通过 VLLM_GPU=1 或 CUDA_VISIBLE_DEVICES=1 指定):"
  nvidia-smi --query-gpu=index,memory.used,memory.free,memory.total --format=csv,noheader | sed 's/^/  /' || true
  show_gpu_pids
fi

echo "[1/6] 停止旧 vLLM 进程 (profile=${PROFILE}, port=${PORT})..."
if command -v fuser >/dev/null 2>&1; then
  fuser -k "${PORT}/tcp" 2>/dev/null || true
fi
if [ "$PROFILE" = "base" ]; then
  pkill -9 -f "vllm.entrypoints.openai.api_server" 2>/dev/null || true
  pkill -9 -f "vllm.v1.engine" 2>/dev/null || true
  pkill -9 -f "EngineCore" 2>/dev/null || true
fi
sleep 3

if command -v nvidia-smi >/dev/null 2>&1; then
  FREE_MB="$(gpu_free_mb)"
  if [ "${FREE_MB:-0}" -lt "$MIN_FREE_MB" ] 2>/dev/null; then
    echo "[2/6] 警告: GPU ${GPU} 空闲显存仅约 ${FREE_MB} MiB (< ${MIN_FREE_MB} MiB)"
    show_gpu_pids
    if [ "${VLLM_FORCE_GPU_CLEAN:-0}" = "1" ]; then
      echo "  VLLM_FORCE_GPU_CLEAN=1：尝试结束 GPU ${GPU} 上所有计算进程..."
      while IFS= read -r pid; do
        pid="$(echo "$pid" | tr -d ' ')"
        [ -n "$pid" ] || continue
        kill -9 "$pid" 2>/dev/null || true
      done < <(nvidia-smi --query-compute-apps=pid --format=csv,noheader -i "$GPU" 2>/dev/null || true)
      sleep 3
    else
      echo "  请先手动释放显存，例如:"
      echo "    nvidia-smi"
      echo "    kill -9 <PID>   # 如日志中的 3884608 / 3892890"
      echo "  或强制清理: VLLM_FORCE_GPU_CLEAN=1 bash scripts/restart_local_vllm.sh"
      exit 1
    fi
  fi

  for _ in $(seq 1 15); do
    FREE_MB="$(gpu_free_mb)"
    if [ "${FREE_MB:-0}" -ge "$MIN_FREE_MB" ] 2>/dev/null; then
      break
    fi
    sleep 2
  done
  FREE_MB="$(gpu_free_mb)"
  if [ "${FREE_MB:-0}" -lt "$MIN_FREE_MB" ] 2>/dev/null; then
    echo "错误: GPU ${GPU} 空闲显存仍不足 (${FREE_MB} MiB)。"
    show_gpu_pids
    exit 1
  fi
  echo "[2/6] GPU ${GPU} 空闲显存约 ${FREE_MB} MiB，可启动"
fi

EXTRA_ARGS=()
if [ "$ENFORCE_EAGER" = "1" ]; then
  EXTRA_ARGS+=(--enforce-eager)
fi

echo "[3/6] 启动 vLLM (profile=${PROFILE})"
echo "  python=${PYTHON}"
echo "  model=${MODEL} path=${MODEL_PATH} port=${PORT} gpu=${GPU}"
echo "  max_len=${MAX_LEN} gpu_mem=${GPU_MEM_UTIL} enforce_eager=${ENFORCE_EAGER}"
export PYTORCH_CUDA_ALLOC_CONF="${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True}"
CUDA_VISIBLE_DEVICES="$GPU" nohup "$PYTHON" -m vllm.entrypoints.openai.api_server \
  --model "$MODEL_PATH" \
  --served-model-name "$MODEL" \
  --host "$HOST" \
  --port "$PORT" \
  --dtype "$DTYPE" \
  --max-model-len "$MAX_LEN" \
  --gpu-memory-utilization "$GPU_MEM_UTIL" \
  "${EXTRA_ARGS[@]}" \
  >> "$LOG_FILE" 2>&1 &
echo $! > "$PID_FILE"

echo "[4/6] 等待服务就绪 (最多 180s)..."
for i in $(seq 1 90); do
  if curl -sf "http://${HOST}:${PORT}/v1/models" >/dev/null 2>&1; then
    echo "[5/6] OK — vLLM 已就绪: http://${HOST}:${PORT}/v1"
    curl -s "http://${HOST}:${PORT}/v1/models" | python -m json.tool 2>/dev/null || true
    if command -v nvidia-smi >/dev/null 2>&1; then
      USED_MB="$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i "$GPU" 2>/dev/null | tr -d ' ' || echo '?')"
      echo "  GPU ${GPU} 当前已用显存约 ${USED_MB} MiB（vLLM 会预分配 KV cache，接近 gpu-memory-utilization 上限属正常）"
    fi
    echo "[6/6] 日志: tail -f ${LOG_FILE}"
    exit 0
  fi
  sleep 2
done

echo "启动超时，请查看日志: tail -100 ${LOG_FILE}"
exit 1
