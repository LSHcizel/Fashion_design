#!/usr/bin/env bash
# 改写器服务权重：切到 merge 后的新模型，或恢复默认。
#
#   bash scripts/rewriter_weights.sh apply --run-id grpo_chanel_inverse_v2
#   bash scripts/rewriter_weights.sh restore
#   bash scripts/rewriter_weights.sh status
#
# apply / restore 默认会重启 8001（VLLM_GPU=1）。加 --no-restart 只改 yaml。
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [ -x "${ROOT}/venv/bin/python" ]; then
  PYTHON="${PYTHON:-${ROOT}/venv/bin/python}"
else
  PYTHON="${PYTHON:-python}"
fi

GPU="${VLLM_GPU:-1}"
CMD="${1:-}"
shift || true

if [ -z "$CMD" ] || [ "$CMD" = "-h" ] || [ "$CMD" = "--help" ]; then
  echo "用法:"
  echo "  bash scripts/rewriter_weights.sh apply --run-id <id> [--no-restart]"
  echo "  bash scripts/rewriter_weights.sh use --merged <dir> [--no-restart]"
  echo "  bash scripts/rewriter_weights.sh restore [--no-restart]"
  echo "  bash scripts/rewriter_weights.sh merge --run-id <id>"
  echo "  bash scripts/rewriter_weights.sh status"
  exit 0
fi

NO_RESTART=0
PY_ARGS=()
for arg in "$@"; do
  if [ "$arg" = "--no-restart" ]; then
    NO_RESTART=1
  else
    PY_ARGS+=("$arg")
  fi
done

case "$CMD" in
  status|merge)
    exec "$PYTHON" -m training.hf_grpo.manage_rewriter "$CMD" "${PY_ARGS[@]}"
    ;;
  apply|use|restore)
    EXTRA=()
    if [ "$NO_RESTART" -eq 0 ]; then
      EXTRA+=(--restart --vllm-gpu "$GPU")
    fi
    exec "$PYTHON" -m training.hf_grpo.manage_rewriter "$CMD" "${PY_ARGS[@]}" "${EXTRA[@]}"
    ;;
  *)
    echo "未知命令: $CMD" >&2
    exit 1
    ;;
esac
