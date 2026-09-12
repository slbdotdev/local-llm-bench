#!/usr/bin/env bash
set -uo pipefail

ROOT="$HOME/local-llm-bench/ollama-bench"
SCRATCH="$HOME/.local/state/control-scratch/cachy-1080ti"
OLLAMA_BIN="$SCRATCH/ollama-pkg/usr/bin/ollama"
MODELS="$SCRATCH/models"
PORT=11435
TAG="v7r6-accept-qwen3-8b-1080ti"
LOG="$ROOT/results/v7/GPU_BUDGET-1080ti.log"
SERVER_LOG="$SCRATCH/server-vulkan-qwen3-8b-accept.log"
RESULT="$ROOT/results/$TAG.json"
TRIALS="${TRIALS:-10}"
GLM_TASKS="${ONLY_TASKS:-m01-main-glm,m04-main-glm,m07-main-glm,m10-main-glm,q09-main-glm}"
LUNA_TASKS="${ONLY_LUNA_TASKS:-m03-main-luna,m09-main-luna}"
CLAUDE_TASKS="${ONLY_CLAUDE_TASKS:-m02-main-claude,m05-main-claude}"

mkdir -p "$ROOT/results/v7"
stamp() { date -u +%Y-%m-%dT%H:%M:%SZ; }
server_pid=""
cleanup() {
    if [ -n "$server_pid" ]; then
        curl -fsS -X POST "http://127.0.0.1:$PORT/api/generate" \
            -H 'Content-Type: application/json' \
            -d '{"model":"qwen3:8b","keep_alive":0}' >/dev/null 2>&1 || true
        kill "$server_pid" 2>/dev/null || true
        wait "$server_pid" 2>/dev/null || true
        server_pid=""
    fi
}
trap cleanup EXIT INT TERM

if [ -e "$RESULT" ]; then
    echo "NOTE $(stamp) resuming existing $RESULT" >> "$LOG"
fi

OLLAMA_HOST="http://127.0.0.1:$PORT" \
OLLAMA_MODELS="$MODELS" \
OLLAMA_VULKAN=true \
OLLAMA_LLM_LIBRARY=vulkan \
OLLAMA_KV_CACHE_TYPE=q8_0 \
OLLAMA_FLASH_ATTENTION=true \
OLLAMA_CONTEXT_LENGTH=32768 \
OLLAMA_NUM_PARALLEL=1 \
OLLAMA_MAX_LOADED_MODELS=1 \
OLLAMA_NO_CLOUD=1 \
    "$OLLAMA_BIN" serve >"$SERVER_LOG" 2>&1 &
server_pid=$!

ready=0
for _ in $(seq 1 120); do
    if curl -fsS "http://127.0.0.1:$PORT/api/tags" 2>/dev/null | grep -q 'qwen3:8b'; then
        ready=1
        break
    fi
    sleep 1
done
if [ "$ready" != 1 ]; then
    echo "NOTE $(stamp) server/model readiness failed; see $SERVER_LOG" >> "$LOG"
    exit 1
fi

export PIBENCH_OLLAMA="http://127.0.0.1:$PORT"
export PIBENCH_NODE_BIN=/usr/bin
export PIBENCH_NODE_EXE=/usr/bin/node
export PIBENCH_PI_CLI="$HOME/.local/lib/node_modules/@earendil-works/pi-coding-agent/dist/bundle/cli.js"
export PI_CODING_AGENT_DIR="$ROOT/pi-agent-cachy-1080ti"
export PIBENCH_PI_ARGS=""

run_group() {
    local label="$1" dir="$2" tasks="$3" start end rc
    start=$(stamp)
    echo "STEP $label | process=pibench.py:$TAG | start=$start | end=PENDING" >> "$LOG"
    echo "RUN $label start=$start tasks=$tasks" >&2
    python3 "$ROOT/pibench.py" \
        --models qwen3:8b --tasks "$tasks" --tasks-dir "$ROOT/$dir" \
        --agent-dir "$ROOT/pi-agent-cachy-1080ti" \
        --trials "$TRIALS" --think medium --num-ctx 32768 --no-tps --timeout 900 --tag "$TAG"
    rc=$?
    end=$(stamp)
    echo "END $label | end=$end | rc=$rc" >> "$LOG"
    echo "RUN $label end=$end rc=$rc" >&2
    return "$rc"
}

run_group "acceptance-glm-m01-m04-m07-m10-q09" \
    "results/v7/authoring/cand-glm" \
    "$GLM_TASKS" || exit $?
run_group "acceptance-luna-m03-m09" \
    "results/v7/authoring/cand-luna" \
    "$LUNA_TASKS" || exit $?
run_group "acceptance-claude-m02-m05" \
    "results/v7/authoring/cand-claude" \
    "$CLAUDE_TASKS" || exit $?

echo "NOTE $(stamp) configuration: qwen3:8b Q4_K_M; Vulkan scratch server 127.0.0.1:11435; q8_0 KV; flash attention; num_ctx=32768; node=/usr/bin/node; pi=$PIBENCH_PI_CLI" >> "$LOG"
echo "NOTE $(stamp) result=$RESULT" >> "$LOG"
