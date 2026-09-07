#!/bin/bash
# run_gpu_round.sh [--go]
#
# Phase 3 of plan-r3-2026-09-06.md section 7: the occupancy acceptance sweep for the nine
# re-authored main-band candidates, and the live validation of `read_paths` that section 2.5
# requires before any candidate may be gated on it.
#
# WITHOUT --go IT RUNS NOTHING. It prints every command it would run, checks everything that
# can be checked without the card, and exits. That is the default on purpose: the desktop GPU
# is the owner's and this script is the only thing in the round that takes it.
#
# THE ONE COMMAND that starts the round, launched detached because this harness kills
# long-lived background tasks on a spurious low-memory signal at 80-90 s (plan section 6.1):
#
#   setsid -f bash /mnt/d/local-llm-bench/ollama-bench/results/v7/run_gpu_round.sh --go \
#     < /dev/null > /mnt/d/local-llm-bench/ollama-bench/results/v7/gpu-round.log 2>&1
#
# Then poll the marker, never a process name (`pgrep -f` matches the waiting shell itself):
#
#   ls /mnt/d/local-llm-bench/ollama-bench/results/v7/.r2-*-done
#
# Markers, in order:
#   .r2-gpuverify-done   the GPU proved by a real load, six tags
#   .r2-validate-done    read_paths reproduced on a live cell and checked
#   .r2-sweep-done       one workhorse trial per candidate
#   .r2-gate-done        the coverage gate read over the sweep
#
# Artifacts:
#   results/v7cal3-readpaths.json      the validation cell
#   results/v7r2-gate.json             the acceptance sweep
#   results/v7/r2-gate-report.txt      the gate's own table
#   results/v7/r2-gate-rows.json       the gate's rows, machine-readable
set -uo pipefail
cd /mnt/d/local-llm-bench/ollama-bench || exit 1

GO=0
[ "${1:-}" = "--go" ] && GO=1

PY=/mnt/c/Users/slb/scoop/apps/python/current/python.exe
V7=results/v7
STAGE=$V7/authoring/r2/gate-suite
SUITE=$V7/authoring/suite
VALIDATION_TASK=m09-main-glm          # the cell of v7cal-IQ2_M-main that section 2.5 names
VALIDATION_TAG=v7cal3-readpaths
SWEEP_TAG=v7r2-gate

say() { echo "== $(date +%H:%M:%S) $*"; }

say "v7 round-2 acceptance sweep, $( [ "$GO" = 1 ] && echo 'ARMED (--go)' || echo 'DRY RUN — nothing will run')"

# ---------------------------------------------------------------------------
# Preflight. Everything here is CPU-only and runs in both modes, because a dry run that
# checks nothing is a dry run that tells you nothing.
# ---------------------------------------------------------------------------
say "preflight"
fail=0

if [ ! -d "$STAGE" ]; then
  echo "  staging directory $STAGE is absent; run:"
  echo "    python3 $V7/authoring/r2/stage_gate_suite.py"
  fail=1
else
  n=$(ls -1 "$STAGE" | wc -l)
  echo "  staged candidates: $n"
  [ "$n" -eq 9 ] || { echo "  EXPECTED 9 candidates, found $n"; fail=1; }
fi

echo "  read_paths attribution probe (CPU):"
python3 "$V7/probe_read_paths.py" > /tmp/r2-probe-readpaths.txt 2>&1
if [ $? -ne 0 ]; then echo "  FAILED — see /tmp/r2-probe-readpaths.txt"; fail=1;
else echo "    $(grep 'case(s),' /tmp/r2-probe-readpaths.txt)"; fi

echo "  coverage gate reproduces the calibration figures (CPU):"
python3 "$V7/coverage_gate.py" --verify-calibration > /tmp/r2-verify-cal.txt 2>&1
if [ $? -ne 0 ]; then echo "  FAILED — see /tmp/r2-verify-cal.txt"; fail=1;
else echo "    $(grep 'figure(s) checked' /tmp/r2-verify-cal.txt)"; fi

echo "  every candidate declares LOAD_BEARING (CPU):"
python3 "$V7/authoring/r2/check_load_bearing.py" || fail=1

echo "  every candidate clears rung 0, plan section 2.1 (CPU):"
python3 "$V7/authoring/r2/check_rung0.py" > /tmp/r2-rung0.txt 2>&1
if [ $? -ne 0 ]; then
  echo "  FAILED — see /tmp/r2-rung0.txt"; grep '^    !' /tmp/r2-rung0.txt | head -8; fail=1
else echo "    $(grep 'failing plan section' /tmp/r2-rung0.txt)"; fi

# D7-31: the grader is verified on the interpreter that will run it, never on the one that is
# convenient. This is the whole of the check the campaign paid an hour for, and it is cheap.
if [ -d "$STAGE" ]; then
  echo "  every reference grades correct under the WINDOWS interpreter (CPU):"
  bash "$V7/probe_scope_gate_r2.sh" > /tmp/r2-scopegate.txt 2>&1
  if grep -qv 'VERDICT correct' /tmp/r2-scopegate.txt && grep -q 'VERDICT unsafe\|VERDICT confidently_wrong\|VERDICT visibly_failed\|Traceback' /tmp/r2-scopegate.txt; then
    echo "  FAILED — see /tmp/r2-scopegate.txt"; fail=1
  else
    echo "    $(grep -c 'VERDICT correct' /tmp/r2-scopegate.txt) reference(s) correct under $(head -1 /tmp/r2-scopegate.txt | cut -d' ' -f2)"
  fi
  echo "  every scope gate still fires on a real breach (CPU):"
  bash "$V7/probe_scope_gate_r2.sh" --breach > /tmp/r2-breach.txt 2>&1
  n_ok=$(grep -c 'VERDICT unsafe' /tmp/r2-breach.txt)
  n_all=$(ls -1 "$STAGE" | wc -l)
  if [ "$n_ok" != "$n_all" ]; then
    echo "  FAILED — only $n_ok of $n_all gates fired; see /tmp/r2-breach.txt"; fail=1
  else
    echo "    $n_ok of $n_all gates fired on a planted stray file"
  fi
fi

if [ "$fail" != "0" ]; then
  echo
  echo "PREFLIGHT FAILED. Nothing was run. Fix the above and re-run."
  exit 1
fi

if [ "$GO" != "1" ]; then
  cat <<'PLAN'

DRY RUN — the four steps below were NOT run. Every preflight check above passed.

  1. GPU by a real load, six tags, never a version string (D7-28)
       bash results/v7/gpuverify.sh
  2. read_paths validated on a LIVE cell (plan section 2.5): one trial of m09-main-glm on the
     workhorse, re-run rather than re-parsed, then checked against its own tools histogram
       results/v7/runcell.sh IQ2_M 64k 65536 main 1 v7cal3-readpaths m09-main-glm
       python3 results/v7/validate_read_paths_live.py v7cal3-readpaths
  3. the acceptance sweep: one workhorse trial per re-authored candidate (plan section 2.2)
       results/v7/runcell-r2.sh
  4. the gate, read before any pass rate
       python3 results/v7/coverage_gate.py v7r2-gate \
         --tasks-dir results/v7/authoring/r2/gate-suite \
         --json results/v7/r2-gate-rows.json

To run it, add --go. GPU time: about one hour — nine main-band trials at a measured median
wall of 41 s, plus the validation cell and the six-tag load check.
PLAN
  exit 0
fi

# ---------------------------------------------------------------------------
# 1. the GPU, proved by a real load
# ---------------------------------------------------------------------------
say "step 1: GPU by a real load"
bash "$V7/gpuverify.sh"
touch "$V7/.r2-gpuverify-done"
say "step 1 done — read $V7/gpuverify.log: 100% GPU, residency on the placement table, "\
"generation on the quant's known curve. A version string is not a verification."

# ---------------------------------------------------------------------------
# 2. read_paths, validated live before anything is gated on it
# ---------------------------------------------------------------------------
say "step 2: read_paths on a live cell"
bash "$V7/runcell.sh" IQ2_M 64k 65536 main 1 "$VALIDATION_TAG" "$VALIDATION_TASK"
python3 "$V7/validate_read_paths_live.py" "$VALIDATION_TAG" --tasks-dir "$SUITE" \
  | tee "$V7/r2-readpaths-validation.txt"
rc=${PIPESTATUS[0]}
if [ "$rc" != "0" ]; then
  say "STOPPING: read_paths did not validate. The gate is not readable and the sweep would"\
"be uninterpretable. See $V7/r2-readpaths-validation.txt."
  exit 1
fi
touch "$V7/.r2-validate-done"
say "step 2 done"

# ---------------------------------------------------------------------------
# 3. the acceptance sweep
# ---------------------------------------------------------------------------
say "step 3: acceptance sweep, one workhorse trial per candidate"
bash "$V7/runcell-r2.sh"
touch "$V7/.r2-sweep-done"
say "step 3 done"

# ---------------------------------------------------------------------------
# 4. the gate, read before the pass rate
# ---------------------------------------------------------------------------
say "step 4: the coverage and load-bearing gate"
python3 "$V7/coverage_gate.py" "$SWEEP_TAG" --tasks-dir "$STAGE" \
  --json "$V7/r2-gate-rows.json" | tee "$V7/r2-gate-report.txt"
touch "$V7/.r2-gate-done"

say "ROUND COMPLETE. Read $V7/r2-gate-report.txt BEFORE any pass rate: a candidate below the"\
"gate is a re-author and not a tune (plan section 2.5), and a candidate that misses twice is"\
"dropped for its family's spare. Ending the round is the manager's (owner's ruling 8.3)."
