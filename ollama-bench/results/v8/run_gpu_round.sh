#!/bin/bash
# run_gpu_round.sh [--go] [--owner-ok] [--cells FILE]
#
# The v8 campaign's only GPU-taking script. Plan of record: results/v8/plan-2026-09-11.md.
#
# WITHOUT --go IT RUNS NOTHING. It runs every check that can be made without the card,
# prints the cells it would run with their budget estimates, and exits. That is the default
# on purpose: the desktop GPU is the owner's.
#
# --owner-ok is also required to run. The workhorse plan's automatic availability signal is a
# later phase and is NOT built, so there is nothing to read; the owner's word is the signal.
# A run without it refuses rather than guessing the desktop is idle.
#
# Launch detached, because this harness kills long-lived background tasks on a spurious
# low-memory signal at 80-90 s (v7 plan section 6.1):
#
#   setsid -f bash /mnt/d/local-llm-bench/ollama-bench/results/v8/run_gpu_round.sh --go --owner-ok \
#     < /dev/null > /mnt/d/local-llm-bench/ollama-bench/results/v8/gpu-round.log 2>&1
#
# Then poll the MARKER, never a process name: `pgrep -f` matches the waiting shell itself.
#   ls /mnt/d/local-llm-bench/ollama-bench/results/v8/.cell-*-done
set -uo pipefail
cd /mnt/d/local-llm-bench/ollama-bench 2>/dev/null || cd "$(dirname "$0")/../.." || exit 1

V8=results/v8
PY=/mnt/c/Users/slb/scoop/apps/python/current/python.exe
BUDGET=$V8/GPU_BUDGET.log
HARD_STOP=64800          # 18 h; the last 2 h of the 20 h grant are never planned work
# The managed route, not localhost: from WSL, localhost:11434 is a different and empty
# ollama, and a preflight that asks it anything gets a meaningless answer.
OLLAMA=${OLLAMA_HOST_URL:-http://fractal.wyvern-temperature.ts.net:11434}
GO=0; OWNER=0; CELLS=$V8/cells.tsv

for a in "$@"; do
  case "$a" in
    --go) GO=1 ;;
    --owner-ok) OWNER=1 ;;
    --cells=*) CELLS="${a#--cells=}" ;;
  esac
done

say() { echo "== $(date -u +%H:%M:%SZ) $*"; }

# accounted() sums gpu_seconds already booked in the budget log.
accounted() { grep -oE 'gpu_seconds=[0-9]+' "$BUDGET" 2>/dev/null | cut -d= -f2 | paste -sd+ | bc 2>/dev/null || echo 0; }

say "v8 GPU round — $( [ "$GO" = 1 ] && echo 'ARMED' || echo 'DRY RUN, nothing will run')"

# ---------------------------------------------------------------------------
# Preflight. CPU only, runs in both modes: a dry run that checks nothing tells nothing.
# ---------------------------------------------------------------------------
fail=0
say "preflight"

# Phase-1 gates are AUTHORING-TIME instruments: they regenerate corpora from the fleet's own
# pages, which exist on the WSL side only. Running them here wiped a slot and 89 report files
# once already. D7-31 asks only that the GRADER be verified on the interpreter that runs it,
# which is what refprobe.py does. So: read each item's machine-readable verdict, then probe the
# graders. GATES.md is prose and is never parsed — a grep for FAIL matched the word inside a
# documented command string and scored a passing item as failing.
echo "  phase-1 gate verdicts, from GATES.json:"
for item in item1 item2 item3; do
  # item 1 records its verdict beside its gate entrypoint; items 2 and 3 at the item root.
  j=$V8/$item/GATES.json
  [ -f "$j" ] || j=$V8/$item/gates/GATES.json
  if [ ! -f "$j" ]; then echo "    MISSING GATES.json for $item — phase 1 recorded no machine-readable verdict"; fail=1; continue; fi
  read -r ok passed failed when plat <<EOJ
$(python3 -c "
import json
d=json.load(open('$j'))
print(int(d.get('failed',1)==0), d.get('passed','?'), d.get('failed','?'), d.get('when','?'), d.get('platform','?'))
" 2>/dev/null)
EOJ
  if [ "${ok:-0}" = "1" ]; then
    echo "    $item ok — $passed passed, $failed failed, $when on $plat"
  else
    echo "    $item GATES RECORD $failed FAILURE(S) — rerun its gates on the WSL side"; fail=1
  fi
done

echo "  graders probed on THIS interpreter, rebuilding nothing (D7-31):"
for item in item1 item2 item3; do
  r=$V8/$item/refprobe.py
  if [ ! -f "$r" ]; then echo "    MISSING $r"; fail=1; continue; fi
  if ( cd "$V8/$item" && "$PY" refprobe.py > /tmp/v8-refprobe-$item.txt 2>&1 ); then
    echo "    $item ok — $(grep -oiE '([0-9]+ of [0-9]+|[0-9]+/[0-9]+) referenc[e s]* ?(answers? )?graded correct' /tmp/v8-refprobe-$item.txt | tail -1)"
  else
    echo "    $item REFPROBE FAILED under $PY — see /tmp/v8-refprobe-$item.txt"
    tail -3 /tmp/v8-refprobe-$item.txt | sed 's/^/      /'
    fail=1
  fi
done

echo "  cell inventory:"
if [ ! -f "$CELLS" ]; then
  echo "    MISSING $CELLS (tab-separated: cell_id, item, runner, tasks_dir, task, num_ctx, trials, est_gpu_s)"
  fail=1
else
  est=$(awk -F'\t' '!/^#/ && NF>=8 {s+=$8} END{print s+0}' "$CELLS")
  n=$(awk -F'\t' '!/^#/ && NF>=8' "$CELLS" | wc -l)
  echo "    $n cells, estimate ${est}s ($(echo "scale=2;$est/3600"|bc) h)"
  acc=$(accounted)
  echo "    already accounted ${acc}s; hard stop ${HARD_STOP}s"
  if [ "$((acc+est))" -gt "$HARD_STOP" ]; then
    echo "    ESTIMATE CROSSES THE HARD STOP — trim the inventory or spend reserve deliberately"; fail=1; fi
fi

echo "  windows interpreter present (the grader is verified on the interpreter that runs it, D7-31):"
if [ -x "$PY" ]; then echo "    $PY ok"; else echo "    MISSING $PY"; fail=1; fi

echo "  endpoint catalog (metadata only, loads no model, costs no GPU):"
if curl -sf -m 10 $OLLAMA/api/tags -o /tmp/v8-tags.json; then
  echo "    $(python3 -c "import json;print(', '.join(m['name'] for m in json.load(open('/tmp/v8-tags.json'))['models'])[:200])" 2>/dev/null)"
else
  echo "    endpoint $OLLAMA not reachable from here"
  [ "$GO" = 1 ] && fail=1
fi

echo "  card idle before the round (/api/ps must be empty):"
if curl -sf -m 10 $OLLAMA/api/ps -o /tmp/v8-ps.json; then
  if grep -q '"models":\[\]' /tmp/v8-ps.json; then echo "    empty, ok"; else
    echo "    A MODEL IS RESIDENT: $(cat /tmp/v8-ps.json | head -c 200)"
    echo "    unload with keep_alive:0 before starting; a leftover makes the first cell's placement another tag's"
    [ "$GO" = 1 ] && fail=1; fi
fi

if [ "$fail" != "0" ]; then
  echo; echo "PREFLIGHT FAILED. Nothing was run."; exit 1
fi

if [ "$GO" != 1 ] || [ "$OWNER" != 1 ]; then
  cat <<PLAN

DRY RUN — nothing was run; every preflight check above passed.

Steps --go would take, in ascending cost so a harness bug is found before a heavy cell pays:
  1. the GPU proved by a REAL LOAD on q27-IQ2_M-96k, never a version string
       $PY results/v5/gpu_verify.py q27-IQ2_M-96k
     then unload with keep_alive:0 and confirm /api/ps empty.
  2. each cell of $CELLS in ascending est_gpu_s, each bracketed by a STEP/END pair in
     $BUDGET carrying its measured gpu_seconds.
  3. stop before any cell that would cross ${HARD_STOP}s accounted, and report.

PLAN
  [ "$OWNER" != 1 ] && echo "--owner-ok was not given. The availability signal is not built;" \
    "the owner's word is the signal, so this run refuses rather than assume the desktop is idle."
  echo "To run: add --go --owner-ok."
  exit 0
fi

# ---------------------------------------------------------------------------
# 1. the GPU, proved by a real load
# ---------------------------------------------------------------------------
say "step 1: GPU by a real load on q27-IQ2_M-96k"
t0=$(date -u +%s)
echo "STEP gpuverify-IQ2_M-96k | process=v5/gpu_verify.py | start=$(date -u +%Y-%m-%dT%H:%M:%SZ) | end=PENDING" >> "$BUDGET"
"$PY" results/v5/gpu_verify.py q27-IQ2_M-96k 2>&1 | tee "$V8/gpuverify.log"
"$PY" -c "import json,urllib.request;urllib.request.urlopen(urllib.request.Request('http://localhost:11434/api/generate',data=json.dumps({'model':'q27-IQ2_M-96k','keep_alive':0}).encode(),headers={'Content-Type':'application/json'}),timeout=60).read()" >> "$V8/gpuverify.log" 2>&1
t1=$(date -u +%s)
echo "END gpuverify-IQ2_M-96k | end=$(date -u +%Y-%m-%dT%H:%M:%SZ) | gpu_seconds=$((t1-t0))" >> "$BUDGET"
touch "$V8/.cell-gpuverify-done"
say "step 1 done in $((t1-t0))s — read $V8/gpuverify.log for the processor split and the"\
"generation rate on this quant's known curve. A version string is not a verification."


# ---------------------------------------------------------------------------
# 1b. the tool-call smoke gate — the cheapest question that can void item 1
#
# Nothing offline could prove q27-IQ2_M-96k emits tool_calls on this endpoint at all, and
# item 1's 10,800 s all rest on it. One short trial answers it. If the model never emits a
# valid tool call, item 1 is void as designed and the round skips it rather than spending
# three hours discovering the same thing.
# ---------------------------------------------------------------------------
say "step 1b: tool-call smoke gate on t1 (about 60 s)"
s0=$(date -u +%s)
echo "STEP smoke-toolcalls | process=item1/leafloop.py:t1 | start=$(date -u +%Y-%m-%dT%H:%M:%SZ) | end=PENDING" >> "$BUDGET"
"$PY" "$V8/item1/leafloop.py" --api native --model q27-IQ2_M-96k --num-ctx 98304 \
  --tasks-dir "$V8/item1/tasks" --task t1 --max-wall 120 \
  --transcript "$V8/smoke-toolcalls.jsonl" > "$V8/smoke-toolcalls.log" 2>&1
s1=$(date -u +%s)
echo "END smoke-toolcalls | end=$(date -u +%Y-%m-%dT%H:%M:%SZ) | gpu_seconds=$((s1-s0))" >> "$BUDGET"

ncalls=$(grep -c '"tool_calls"' "$V8/smoke-toolcalls.jsonl" 2>/dev/null || echo 0)
say "step 1b done in $((s1-s0))s — $ncalls response(s) carried tool_calls"
if [ "${ncalls:-0}" -lt 1 ]; then
  echo "NOTE smoke-toolcalls: model emitted NO tool_calls; item 1 cells skipped as void by design." >> "$BUDGET"
  say "ITEM 1 IS VOID: the model emitted no tool call. Skipping every item1 cell; the rest of"\
"the round continues. Read $V8/smoke-toolcalls.log before re-planning item 1."
  SKIP_ITEM1=1
else
  SKIP_ITEM1=0
fi
touch "$V8/.cell-smoke-done"

# ---------------------------------------------------------------------------
# 2. the cells, cheapest first
# ---------------------------------------------------------------------------
sort -t$'\t' -k8 -n "$CELLS" | grep -v '^#' | while IFS=$'\t' read -r cid item runner tdir task nctx trials estimate; do
  [ -z "${cid:-}" ] && continue
  if [ "$item" = "item1" ] && [ "${SKIP_ITEM1:-0}" = "1" ]; then
    say "skipping $cid — item 1 voided by the smoke gate"; continue
  fi
  if [ "$item" = "item2" ] && [ "${SKIP_ITEM2:-0}" = "1" ]; then
    say "skipping $cid — item 2 halted by the occupancy calibration checkpoint"; continue
  fi
  acc=$(accounted)
  if [ "$((acc+estimate))" -gt "$HARD_STOP" ]; then
    say "STOPPING before $cid: ${acc}s accounted + ${estimate}s estimate crosses ${HARD_STOP}s."
    echo "NOTE stopped before $cid at ${acc}s accounted; hard stop ${HARD_STOP}s." >> "$BUDGET"
    break
  fi
  say "cell $cid ($item, $task, num_ctx=$nctx, trials=$trials, est ${estimate}s)"
  c0=$(date -u +%s)
  echo "STEP $cid | process=pibench.py:$cid | start=$(date -u +%Y-%m-%dT%H:%M:%SZ) | end=PENDING" >> "$BUDGET"
  case "$runner" in
    leafloop)
      "$PY" "$V8/item1/leafloop.py" --api native --model q27-IQ2_M-96k --num-ctx "$nctx" \
        --tasks-dir "$tdir" --task "$task" --trials "$trials" --max-wall 900 \
        --transcript "$V8/$cid.jsonl" >> "$V8/$cid.log" 2>&1 ;;
    batch)
      "$PY" "$V8/item3/batch_cell.py" --model q27-IQ2_M-96k --num-ctx "$nctx" \
        >> "$V8/$cid.log" 2>&1 ;;
    escalate)
      # Only the local-draft arm holds the GPU; the hosted arm is API-billed tokens.
      # A plan-bound harness reports no usage field and so cannot produce a ledger.
      "$PY" "$V8/item3/escalate.py" --family "$task" --slots-dir "$tdir" \
        --local-model q27-IQ2_M-96k --num-ctx "$nctx" --trials "$trials" \
        --ledger "$V8/$cid-ledger.json" >> "$V8/$cid.log" 2>&1 ;;
    *)
      # --api native: /v1/chat/completions IGNORES options.num_ctx and reports
      # usage.prompt_tokens rather than prompt_eval_count, so the occupancy rung and the
      # context window would both be unverifiable on that path.
      "$PY" pibench.py --models q27-IQ2_M-96k --tasks "$task" --tasks-dir "$tdir" \
        --trials "$trials" --num-ctx "$nctx" --tag "$cid" --timeout 900 --no-tps \
        >> "$V8/$cid.log" 2>&1 ;;
  esac
  rc=$?
  c1=$(date -u +%s)
  echo "END $cid | end=$(date -u +%Y-%m-%dT%H:%M:%SZ) | gpu_seconds=$((c1-c0)) | rc=$rc" >> "$BUDGET"
  touch "$V8/.cell-$cid-done"
  say "cell $cid done in $((c1-c0))s rc=$rc"

  # -------------------------------------------------------------------------
  # Item 2's occupancy calibration checkpoint.
  #
  # The rungs were sized with pibench's FILL_CHARS_PER_TOKEN = 4.664, which was measured on
  # v5's FILLER, not on prose carrying identifiers. If the real ratio is nearer 4.0 the 80k
  # rung arrives at about 93k tokens: still inside the 98,304 window, but +17% on its rung
  # and therefore VOID under plan section 4. Cells run cheapest-first, so the first item2
  # cell is a 20k rung and costs the least to learn this from. Read it, and if the ratio
  # disagrees, stop item 2 rather than paying for five more cells of void data.
  # -------------------------------------------------------------------------
  if [ "$item" = "item2" ] && [ "${ITEM2_CALIBRATED:-0}" = "0" ]; then
    ITEM2_CALIBRATED=1
    target=$(echo "$cid" | grep -oE '[0-9]+k' | head -1 | tr -d k)
    achieved=$("$PY" -c "
import json,sys,glob
rows=[]
for f in glob.glob('results/$cid.json'):
    d=json.load(open(f))
    for tag,v in d.items():
        if isinstance(v,dict):
            for k2,v2 in v.items():
                if isinstance(v2,list):
                    for r in v2:
                        t=r.get('achieved_fill_prompt_tokens') or r.get('peak_prompt') or r.get('prompt_tokens')
                        if t: rows.append(t)
print(max(rows) if rows else 0)
" 2>/dev/null)
    if [ "${achieved:-0}" -gt 0 ] && [ "${target:-0}" -gt 0 ]; then
      err=$(( (achieved - target*1000) * 100 / (target*1000) ))
      say "item2 calibration: rung ${target}k target=$((target*1000)) achieved=$achieved error=${err}%"
      echo "NOTE item2-calibration $cid: target=$((target*1000)) achieved=$achieved error=${err}%" >> "$BUDGET"
      if [ "${err#-}" -gt 15 ]; then
        say "ITEM 2 OCCUPANCY IS OUT OF BAND (${err}%). Remaining item2 cells would be VOID."
        say "Re-converge, then re-run:  cd $V8/item2 && python3 gen_aggregate.py --chars-per-token <measured>"\
"&& python3 gen_contradiction.py --chars-per-token <measured> && python3 gates.py"
        echo "NOTE item2 halted after $cid: occupancy ${err}% outside the +/-15% void rule." >> "$BUDGET"
        SKIP_ITEM2=1
      fi
    else
      say "item2 calibration: could not read achieved prompt tokens from results/$cid.json"
    fi
  fi
done

# ---------------------------------------------------------------------------
# 3. leave the card as it was found
# ---------------------------------------------------------------------------
"$PY" -c "import json,urllib.request;urllib.request.urlopen(urllib.request.Request('http://localhost:11434/api/generate',data=json.dumps({'model':'q27-IQ2_M-96k','keep_alive':0}).encode(),headers={'Content-Type':'application/json'}),timeout=60).read()" >/dev/null 2>&1
curl -sf -m 10 $OLLAMA/api/ps | tee -a "$V8/gpu-round.log"
touch "$V8/.round-done"
say "ROUND COMPLETE. Accounted total now $(accounted)s of ${HARD_STOP}s planned."
