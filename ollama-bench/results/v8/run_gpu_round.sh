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

echo "  phase-1 instrument gates recorded and passing:"
for item in item1 item2 item3; do
  g=$V8/$item/GATES.md
  if [ ! -f "$g" ]; then echo "    MISSING $g — phase 1 is not done for $item"; fail=1; continue; fi
  if grep -qiE '\b(FAIL|FAILED)\b' "$g"; then echo "    $g records a FAIL"; fail=1; else
    echo "    $g ok ($(grep -ciE '\bpass(ed)?\b' "$g") pass lines)"; fi
done

echo "  two-directional instrument proof recorded (a perfect answer 1.0 AND a decoy answer 0):"
for item in item1 item2 item3; do
  g=$V8/$item/GATES.md
  [ -f "$g" ] || continue
  if grep -qi 'two-direction' "$g"; then echo "    $item ok"; else
    echo "    $item does not record it — plan section 4 forbids trusting the instrument"; fail=1; fi
done

echo "  cell inventory:"
if [ ! -f "$CELLS" ]; then
  echo "    MISSING $CELLS (tab-separated: cell_id, item, tasks_dir, task, num_ctx, trials, est_gpu_s)"
  fail=1
else
  est=$(awk -F'\t' '!/^#/ && NF>=7 {s+=$7} END{print s+0}' "$CELLS")
  n=$(awk -F'\t' '!/^#/ && NF>=7' "$CELLS" | wc -l)
  echo "    $n cells, estimate ${est}s ($(echo "scale=2;$est/3600"|bc) h)"
  acc=$(accounted)
  echo "    already accounted ${acc}s; hard stop ${HARD_STOP}s"
  if [ "$((acc+est))" -gt "$HARD_STOP" ]; then
    echo "    ESTIMATE CROSSES THE HARD STOP — trim the inventory or spend reserve deliberately"; fail=1; fi
fi

echo "  windows interpreter present (the grader is verified on the interpreter that runs it, D7-31):"
if [ -x "$PY" ]; then echo "    $PY ok"; else echo "    MISSING $PY"; fail=1; fi

echo "  endpoint catalog (metadata only, loads no model, costs no GPU):"
if curl -sf -m 10 http://localhost:11434/api/tags -o /tmp/v8-tags.json; then
  echo "    $(python3 -c "import json;print(', '.join(m['name'] for m in json.load(open('/tmp/v8-tags.json'))['models'])[:200])" 2>/dev/null)"
else
  echo "    endpoint not reachable from here; on the desktop it is localhost:11434"
  [ "$GO" = 1 ] && fail=1
fi

echo "  card idle before the round (/api/ps must be empty):"
if curl -sf -m 10 http://localhost:11434/api/ps -o /tmp/v8-ps.json; then
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
# 2. the cells, cheapest first
# ---------------------------------------------------------------------------
sort -t$'\t' -k7 -n "$CELLS" | grep -v '^#' | while IFS=$'\t' read -r cid item tdir task nctx trials estimate; do
  [ -z "${cid:-}" ] && continue
  acc=$(accounted)
  if [ "$((acc+estimate))" -gt "$HARD_STOP" ]; then
    say "STOPPING before $cid: ${acc}s accounted + ${estimate}s estimate crosses ${HARD_STOP}s."
    echo "NOTE stopped before $cid at ${acc}s accounted; hard stop ${HARD_STOP}s." >> "$BUDGET"
    break
  fi
  say "cell $cid ($item, $task, num_ctx=$nctx, trials=$trials, est ${estimate}s)"
  c0=$(date -u +%s)
  echo "STEP $cid | process=pibench.py:$cid | start=$(date -u +%Y-%m-%dT%H:%M:%SZ) | end=PENDING" >> "$BUDGET"
  "$PY" pibench.py --models q27-IQ2_M-96k --tasks "$task" --tasks-dir "$tdir" \
    --trials "$trials" --num-ctx "$nctx" --tag "$cid" --timeout 900 --no-tps \
    >> "$V8/$cid.log" 2>&1
  rc=$?
  c1=$(date -u +%s)
  echo "END $cid | end=$(date -u +%Y-%m-%dT%H:%M:%SZ) | gpu_seconds=$((c1-c0)) | rc=$rc" >> "$BUDGET"
  touch "$V8/.cell-$cid-done"
  say "cell $cid done in $((c1-c0))s rc=$rc"
done

# ---------------------------------------------------------------------------
# 3. leave the card as it was found
# ---------------------------------------------------------------------------
"$PY" -c "import json,urllib.request;urllib.request.urlopen(urllib.request.Request('http://localhost:11434/api/generate',data=json.dumps({'model':'q27-IQ2_M-96k','keep_alive':0}).encode(),headers={'Content-Type':'application/json'}),timeout=60).read()" >/dev/null 2>&1
curl -sf -m 10 http://localhost:11434/api/ps | tee -a "$V8/gpu-round.log"
touch "$V8/.round-done"
say "ROUND COMPLETE. Accounted total now $(accounted)s of ${HARD_STOP}s planned."
