#!/usr/bin/env bash
# v5 KV-cache rerun at 64k, per results/v5/kv-probe-plan-2026-09-03.md.
#
# Four symmetric cells only -- asymmetric K/V was removed from the plan and kvquality.py
# rejects it in argument validation. Each cell is one server, one model, one output file.
#
#   1. q27-IQ3_M-64k   q8_0/q8_0   expected-hardest fit case, the calibration cell
#   2. q27-IQ3_M-64k   q4_0/q4_0
#   3. q27-Q3_K_S-64k  q8_0/q8_0
#   4. q27-Q3_K_S-64k  q4_0/q4_0
#
# Preconditions the operator owns before running this: Ollama's model service is not
# serving, nothing else is on the GPU, and results/gpu-tune/watch.sh is live.
#
# Usage:   ./run-sweep.sh
# Env:     PY      python that can launch llama-server.exe   (default: python)
#          OLLAMA  ollama CLI used to resolve blob paths     (default: autodetected)
set -euo pipefail
cd "$(dirname "$0")"

PY="${PY:-python}"
CTX=65536
RECORDS=1200
NEEDLES=32

# 2026-09-10: the plan's two named tags no longer exist on this host. `ollama list` holds
# 35 models and neither `q27-IQ3_M-64k` nor `q27-Q3_K_S-64k` is among them, and the
# 2026-09-03 Q3_K_S blob sha256-ba0c5dee3026 is not in the blob store either, so the plan's
# original pair cannot be resolved at run time and cannot be guessed. The substitutes are the
# two 64k models of the same two classes that ARE present: q27-mrIQ3M-64k for the IQ3_M cell
# and q27-UDQ3KXL-64k for the Q3-K cell. The plan's question -- is q8_0 KV measurably better
# than q4_0 at 64k on the same model -- is answered on the same model twice either way; what
# is lost is continuity with the 16k/24k rows, and that is said in the record.
IQ3M_MODEL='q27-mrIQ3M-64k'
Q3KS_MODEL='q27-UDQ3KXL-64k'

OUT_1=./kv-64k-mrIQ3M-q8_0.json
OUT_2=./kv-64k-mrIQ3M-q4_0.json
OUT_3=./kv-64k-UDQ3KXL-q8_0.json
OUT_4=./kv-64k-UDQ3KXL-q4_0.json

# --- environment: log it, change nothing, restore anything we did change -------------
# OLLAMA_KV_CACHE_TYPE is the desktop's own user setting. It is not touched here: cache
# types are per-server flags on the direct llama-server launch, so the sweep needs no
# environment change at all. The guard below exists so that a future edit that does make
# one is forced to log and restore it.
if [[ -v OLLAMA_KV_CACHE_TYPE ]]; then
    KV_ENV_BEFORE="$OLLAMA_KV_CACHE_TYPE"; KV_ENV_SET_BEFORE=yes
else
    KV_ENV_BEFORE=""; KV_ENV_SET_BEFORE=no
fi
echo "[env] OLLAMA_KV_CACHE_TYPE at start: set=$KV_ENV_SET_BEFORE value='${KV_ENV_BEFORE}'"
echo "[env] the desktop's user setting is left unchanged; K/V types are passed per server"

restore_env() {
    local rc=$?
    local now_set now_val
    if [[ -v OLLAMA_KV_CACHE_TYPE ]]; then now_set=yes; now_val="$OLLAMA_KV_CACHE_TYPE"
    else now_set=no; now_val=""; fi
    if [[ "$now_set" != "$KV_ENV_SET_BEFORE" || "$now_val" != "$KV_ENV_BEFORE" ]]; then
        echo "[env] RESTORING OLLAMA_KV_CACHE_TYPE: was set=$KV_ENV_SET_BEFORE value='${KV_ENV_BEFORE}', became set=$now_set value='${now_val}'"
        if [[ "$KV_ENV_SET_BEFORE" == yes ]]; then export OLLAMA_KV_CACHE_TYPE="$KV_ENV_BEFORE"
        else unset OLLAMA_KV_CACHE_TYPE; fi
    else
        echo "[env] OLLAMA_KV_CACHE_TYPE unchanged: set=$now_set value='${now_val}'"
    fi
    echo "[exit] run-sweep.sh exiting with $rc"
}
trap restore_env EXIT

# --- gate 1: the offline grader calibration, before anything touches the GPU ---------
echo "########## GATE: offline grader calibration (no GPU, no server) ##########"
"$PY" kvquality.py --selftest-grader --records "$RECORDS" --needles "$NEEDLES"
echo "########## GATE: corpus shape ##########"
"$PY" kvquality.py --corpus-info --records "$RECORDS" --needles "$NEEDLES"

# --- resolve the two 64k blob paths AT RUN TIME, never a guessed hash ----------------
if [[ -z "${OLLAMA:-}" ]]; then
    for cand in ollama.exe ollama \
                /mnt/c/Users/slb/AppData/Local/Programs/Ollama/ollama.exe \
                "${LOCALAPPDATA:-/nonexistent}/Programs/Ollama/ollama.exe"; do
        if command -v "$cand" >/dev/null 2>&1; then OLLAMA="$cand"; break; fi
        if [[ -x "$cand" ]]; then OLLAMA="$cand"; break; fi
    done
fi
if [[ -z "${OLLAMA:-}" ]]; then
    echo "FATAL: no ollama CLI found; set OLLAMA=<path to ollama binary>" >&2
    exit 1
fi
echo "[blob] using ollama at: $OLLAMA"

resolve_blob() {
    # Print the GGUF blob path Ollama itself reports for a model, right now.
    local model="$1" line path
    line="$("$OLLAMA" show --modelfile "$model" 2>/dev/null | tr -d '\r' \
            | grep -m1 -E '^FROM[[:space:]]+.*sha256-' || true)"
    if [[ -z "$line" ]]; then
        echo "FATAL: could not resolve a blob path for '$model' from 'ollama show --modelfile'" >&2
        return 1
    fi
    path="${line#FROM}"
    path="${path#"${path%%[![:space:]]*}"}"
    path="${path%"${path##*[![:space:]]}"}"
    case "$path" in
        *blobs*sha256-*) : ;;
        *) echo "FATAL: resolved path for '$model' does not look like a blob: $path" >&2; return 1 ;;
    esac
    printf '%s\n' "$path"
}

M_IQ3M="$(resolve_blob "$IQ3M_MODEL")"
M_Q3KS="$(resolve_blob "$Q3KS_MODEL")"
echo "[blob] $IQ3M_MODEL -> $M_IQ3M"
echo "[blob] $Q3KS_MODEL -> $M_Q3KS"
if [[ "$M_IQ3M" == "$M_Q3KS" ]]; then
    echo "FATAL: both models resolved to the same blob; refusing to run" >&2
    exit 1
fi

run_cell() {
    # run_cell <label> <blob> <k:v> <out.json>
    local label="$1" blob="$2" cfg="$3" out="$4"
    echo
    echo "########## CELL $label  ($cfg, ctx $CTX) ##########"
    "$PY" kvquality.py --model "$blob" --ctx "$CTX" \
        --records "$RECORDS" --needles "$NEEDLES" \
        --configs "$cfg" --out "$out" 2>&1 | tee "${out%.json}.stdout.log"
    # pipefail makes tee transparent: a nonzero harness result stops the sweep here.
}

# --- cell 1: expected-hardest, and the live calibration cell ------------------------
run_cell "1/4 $IQ3M_MODEL q8_0" "$M_IQ3M" q8_0:q8_0 "$OUT_1"

# --- the plan's saturation stop rule, applied to the first full cell -----------------
# The thresholds (>= 98% of fields AND >= 90% all-four-fields) live in kvquality.py as
# SATURATION_FIELD_PCT / SATURATION_ALL_FIELDS_PCT and were declared before the run.
echo
echo "########## SATURATION STOP RULE (first full cell) ##########"
SAT="$("$PY" kvquality.py --saturation-check "$OUT_1")"
echo "$SAT"
if grep -qx 'saturated=yes' <<<"$SAT"; then
    echo
    echo "STOP: the probe is saturated on the first full cell. Per the plan the sweep"
    echo "stops here and cells 2-4 are NOT run. This is the successful outcome of the"
    echo "rule: a saturated probe cannot separate q8_0 from q4_0, and the next iteration"
    echo "needs a harder task. Record what saturated and at which depths; do not adjust"
    echo "the threshold after seeing the score."
    exit 0
fi
echo "not saturated: continuing with the remaining three cells"

run_cell "2/4 $IQ3M_MODEL q4_0"  "$M_IQ3M" q4_0:q4_0 "$OUT_2"
run_cell "3/4 $Q3KS_MODEL q8_0"  "$M_Q3KS" q8_0:q8_0 "$OUT_3"
run_cell "4/4 $Q3KS_MODEL q4_0"  "$M_Q3KS" q4_0:q4_0 "$OUT_4"

echo
echo "########## done: $OUT_1 $OUT_2 $OUT_3 $OUT_4 ##########"
