# pi-run sanity - GLM 5.3 Flash through pi, v5 suite, 2026-09-05

## tiny band (`pirun-sanity-tiny`)

| task | pass | wall s | usage_in | usage_in_peak | usage_out | turns | tools | stop reason | auto_retry | compaction | error |
|---|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| g01 | PASS | 86.1 | 29012 | 6135 | 3612 | 7 | 6 | stop | 0 | 0 |  |
| g02 | PASS | 31.8 | 15726 | 4194 | 911 | 5 | 5 | stop | 0 | 0 |  |
| g03 | FAIL | 49.5 | 36652 | 5737 | 3340 | 10 | 15 | stop | 0 | 0 |  |
| g04 | FAIL | 72.6 | 9764 | 3153 | 1173 | 4 | 4 | stop | 0 | 0 |  |
| t01 | PASS | 12.4 | 14486 | 3729 | 804 | 5 | 4 | stop | 0 | 0 |  |
| t02 | FAIL | 22.9 | 7654 | 2320 | 423 | 4 | 3 | stop | 0 | 0 |  |
| t03 | PASS | 5.2 | 18214 | 7550 | 487 | 4 | 3 | stop | 0 | 0 |  |
| t04 | PASS | 6.8 | 9140 | 2092 | 339 | 5 | 4 | stop | 0 | 0 |  |
| **total (8 tasks)** | **5/8** | **287.3** | **140648** | | **11089** | **44** | **44** | | | | |

## large band (`pirun-sanity-large`)

| task | pass | wall s | usage_in | usage_in_peak | usage_out | turns | tools | stop reason | auto_retry | compaction | error |
|---|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| g01 | PASS | 50.0 | 118336 | 17014 | 1769 | 13 | 12 | stop | 0 | 0 |  |
| g02 | PASS | 283.1 | 1401549 | 63670 | 18376 | 48 | 52 | stop | 0 | 0 |  |
| g03 | PASS | 229.7 | 573927 | 29155 | 11233 | 29 | 36 | stop | 0 | 0 |  |
| g04 | PASS | 36.7 | 105521 | 13410 | 1937 | 13 | 16 | stop | 0 | 0 |  |
| t01 | FAIL | 211.2 | 545471 | 29556 | 12542 | 32 | 32 | stop | 0 | 0 |  |
| t02 | PASS | 22.1 | 138496 | 16363 | 1323 | 13 | 12 | stop | 0 | 0 |  |
| t03 | PASS | 11.0 | 65268 | 16376 | 779 | 7 | 6 | stop | 0 | 0 |  |
| t04 | PASS | 29.9 | 78622 | 10288 | 1659 | 13 | 12 | stop | 0 | 0 |  |
| **total (8 tasks)** | **7/8** | **873.7** | **3027190** | | **49618** | **168** | **178** | | | | |

## large-ext band (`pirun-sanity-large-ext`)

| task | pass | wall s | usage_in | usage_in_peak | usage_out | turns | tools | stop reason | auto_retry | compaction | error |
|---|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| g01 | PASS | 51.5 | 72176 | 15619 | 2239 | 9 | 12 | stop | 0 | 0 |  |
| g02 | PASS | 294.2 | 956882 | 40189 | 22148 | 45 | 46 | stop | 0 | 0 |  |
| g03 | FAIL | 399.1 | 1291605 | 41971 | 17575 | 45 | 49 | stop | 0 | 0 | Provider finish_reason: error |
| g04 | PASS | 64.0 | 86596 | 13333 | 2869 | 12 | 16 | stop | 0 | 0 |  |
| t01 | PASS | 43.1 | 53421 | 13151 | 3191 | 7 | 6 | stop | 0 | 0 |  |
| t02 | PASS | 50.5 | 44433 | 7318 | 1307 | 9 | 9 | stop | 0 | 0 |  |
| t03 | PASS | 35.1 | 62396 | 12244 | 906 | 8 | 7 | stop | 0 | 0 |  |
| t04 | FAIL | 9.9 | 23716 | 5264 | 618 | 7 | 7 | stop | 0 | 0 |  |
| **total (8 tasks)** | **6/8** | **947.4** | **2591225** | | **50853** | **142** | **152** | | | | |

## Both bands

| | value |
|---|---|
| tasks | 24 |
| passed | 18/24 |
| summed task wall | 2108.4 s |
| usage_in (summed) | 5759063 |
| usage_out (summed) | 111560 |

The `large-ext` process is the large band run a second time with the resilience
extension loaded, not a third set of tasks; the 24-task line above therefore counts
the large band's eight families twice.

## Run

| | value |
|---|---|
| date | 2026-09-05 (host `date` reports 2026-09-04) |
| started | 2026-09-04T19:45:50-06:00 |
| finished | 2026-09-04T20:01:39-06:00 |
| wall clock, whole run (three processes in parallel) | 949 s (15 m 49 s) |
| tiny process | 19:45:50 -> 19:50:38, exit 0 |
| large process | 19:45:50 -> 20:00:25, exit 0 |
| large-ext process | 19:45:50 -> 20:01:38, exit 0 |
| OpenRouter key usage before | USD 37.091598 |
| OpenRouter key usage after | USD 37.421274 |
| key spend delta | **USD 0.329676** |
| pi version | 0.85.0 |
| node | v24.20.0 |
| model | `z-ai/glm-5.3-flash` via `--provider openrouter` |
| agent dir | managed `C:\Users\slb\.pi\agent` (no `--agent-dir`) |
| extension | `C:\Users\slb\.claude\skills\pi-run\scripts\pi-resilience.ts`, `large-ext` process only |
| bench code commit (scratch clone) | `07de475` plus the local `PIBENCH_PI_ARGS` hook below |
| GPU before / after | 721 MiB, 1% / 1026 MiB, 0%; `nvidia-smi --query-compute-apps` empty both times |

## Exact commands

Run from WSL as `bash run-sanity.sh` in the scratch clone's `ollama-bench/`.
`PY=/mnt/c/Users/slb/scoop/apps/python/current/python.exe`,
`EXT='C:\Users\slb\.claude\skills\pi-run\scripts\pi-resilience.ts'`.

```
PYTHONUTF8=1 "$PY" pibench.py --provider openrouter --models z-ai/glm-5.3-flash \
    --think medium --trials 1 --no-tps --timeout 900 \
    --tasks-dir results/v5/authoring/round2/suite-0 --num-ctx 24576 \
    --tag pirun-sanity-tiny > results/pirun-sanity-tiny.log 2>&1

PYTHONUTF8=1 "$PY" pibench.py --provider openrouter --models z-ai/glm-5.3-flash \
    --think medium --trials 1 --no-tps --timeout 900 \
    --tasks-dir results/v5/authoring/round3/suite --num-ctx 65536 \
    --tag pirun-sanity-large > results/pirun-sanity-large.log 2>&1

PYTHONUTF8=1 WSLENV="PIBENCH_PI_ARGS${WSLENV:+:$WSLENV}" PIBENCH_PI_ARGS="-e $EXT" \
    "$PY" pibench.py --provider openrouter --models z-ai/glm-5.3-flash \
    --think medium --trials 1 --no-tps --timeout 900 \
    --tasks-dir results/v5/authoring/round3/suite --num-ctx 65536 \
    --tag pirun-sanity-large-ext > results/pirun-sanity-large-ext.log 2>&1
```

All three were launched together and `wait`ed on.

## The `PIBENCH_PI_ARGS` hook

Scratch clone only. The whole diff against `07de475`:

```diff
diff --git a/ollama-bench/pibench.py b/ollama-bench/pibench.py
index 80c3bc4..94d5a42 100644
--- a/ollama-bench/pibench.py
+++ b/ollama-bench/pibench.py
@@ -574,7 +574,12 @@ def run_pi(model, task, think, timeout, provider="ollama", agent_dir=AGENT_DIR,
     env["PYTHONIOENCODING"] = "utf-8"
     cmd = [NODE_EXE, PI_CLI, "-p", "--no-session", "--no-context-files", "--no-extensions", "--no-skills",
            "--no-prompt-templates", "--mode", "json", "--model", f"{provider}/{model}",
-           "--thinking", think, "--", prompt_arg]
+           "--thinking", think]
+    # Opt-in only: PIBENCH_PI_ARGS is whitespace-split and inserted just before the prompt
+    # separator, so a single process can carry extra pi flags without changing any other row.
+    # `--no-extensions` disables discovery but still honours an explicit `-e <path>`.
+    cmd += os.environ.get("PIBENCH_PI_ARGS", "").split()
+    cmd += ["--", prompt_arg]
     smi_sampler = _NvidiaSmiSampler() if provider == "ollama" else None
     if smi_sampler:
         smi_sampler.start()
```

**`WSLENV` is required and is not optional.** A plain WSL environment variable does not
reach a Windows process launched over interop: without
`WSLENV="PIBENCH_PI_ARGS${WSLENV:+:$WSLENV}"` the variable arrives as `None` in the
Windows interpreter, `.split()` yields `[]`, and the row runs silently *without* the
extension while looking entirely normal. Verified both ways before the run.

## Did the extension load, and did it act

Proven, not assumed, in three steps.

1. **Negative control on the path.** `pi -e <nonexistent>.ts` exits 1 with
   `Failed to load extension ... Extension path does not exist`. So a loaded extension is
   distinguishable from an ignored one.
2. **Negative control through the hook.** One `pibench.py` task run with
   `PIBENCH_PI_ARGS='-e ...\NOPE.ts'` produced `rc 1` and that same loader error in the
   trial's own `stderr` field. So the hook's arguments demonstrably reach pi, and pi's
   stderr demonstrably reaches the result JSON.
3. **The extension logged in the real run.** Two `pi-run-resilience:` lines survive in the
   `large-ext` rows, and zero appear in any of the four non-extension bands
   (`pirun-sanity-tiny`, `pirun-sanity-large`, and both baseline bands), whose `stderr`
   fields are empty throughout:

   | task | line |
   |---|---|
   | g02 | `pi-run-resilience: tool output 36588 chars exceeded 24000; truncated 20588 chars (~56%) from the middle` |
   | g03 | `pi-run-resilience: provider error (Provider finish_reason: error); retry 1/5 in 3000ms` |

   Both of the extension's headline behaviours — middle-truncation of an oversized tool
   result, and a retry of a provider-error turn — therefore fired under load.

**Caveat on that evidence.** `pibench.py` keeps only the last 400 characters of each
trial's stderr (`"stderr": err[-400:]`), so these two lines are a floor, not a count: any
earlier `pi-run-resilience:` line in the same trial was discarded before the JSON was
written. Absence in a row is correspondingly weak evidence; presence is not.

## Sanity against baseline

| band | baseline pass | sanity pass | baseline wall | sanity wall | baseline usage_in | sanity usage_in | baseline usage_out | sanity usage_out |
|---|---|---|---:|---:|---:|---:|---:|---:|
| tiny | 5/8 | 5/8 | 149.2 s | 287.3 s | 153,219 | 140,648 | 11,956 | 11,089 |
| large | 7/8 | 7/8 | 952.4 s | 873.7 s | 3,170,622 | 3,027,190 | 83,003 | 49,618 |
| large-ext | - | 6/8 | - | 947.4 s | - | 2,591,225 | - | 50,853 |

Whole-run wall clock: 954 s baseline (two processes), 949 s sanity (three). Key spend
USD 0.197232 baseline, USD 0.329676 sanity.

**Pass counts match per band, but not task for task.** Tiny holds at 5/8 with two rows
swapping sides (`t02` PASS -> FAIL, `t04` FAIL -> PASS). Large holds at 7/8, likewise with
two swaps (`g03` FAIL -> PASS, `t01` PASS -> FAIL). That is single-trial noise on a
non-deterministic model, not a change in the harness: the same four families
(`g03`, `g04`, `t01`, `t02`/`t04`) do all the discriminating in both runs.

## Notes

No timeouts, no memory-guard kills and no non-zero `rc` in any of the 24 sanity trials;
every last stop reason is `stop`; `auto_retry_end` and `compaction_end` are zero
throughout, in the sanity run exactly as in the baseline, so pi's own in-band retry and
compaction machinery was never engaged in either. The one recorded error text in the whole
pass is `large-ext` `g03`'s `Provider finish_reason: error` — which is the very turn the
extension retried, and the run went on to finish with `stop_reason` `stop` rather than
dying. It still failed the grader, `visibly_failed`; a retried provider error is a
recovered turn, not a correct answer.

Wall time is the noisy axis. Tiny nearly doubled, 149.2 s to 287.3 s, on identical work
and slightly *fewer* tokens, and the individual moves are large in both directions
(`g01` 32.1 -> 86.1 s, `g04` 46.1 -> 72.6 s against `t01` 21.6 -> 12.4 s). The sanity pass
also ran three processes against OpenRouter where the baseline ran two. Treat per-task wall
seconds here as provider-side latency, not as a property of the suite or of the fix.
