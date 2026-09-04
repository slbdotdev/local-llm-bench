# FRACTAL has no working CUDA backend: Ollama is CPU-only, and the v5 grid cannot run

**Severity: blocking for the entire GPU half of the v5 benchmark.** Found 2026-09-04 by the
Opus manager session while proving the KV-probe lifecycle fix. Not previously known, not in
`org/pending.md`, and not visible from any of the state checks the handoff prescribed — the GPU
reads idle and healthy, `nvidia-smi` works, the driver is fine, `ollama list` is fine, and
`ollama ps` is empty. Nothing looks wrong until a model is actually loaded.

**This is a fleet-level fault and belongs in an `ansible-slb/org/` page.** It is written here
because this session was explicitly barred from touching `~/ansible-slb` (busy, with another
worker in flight). A later session should move it, and it must not be added to
`org/pending.md` as an item — the standing rule is that findings go to dated pages.

## The measurement

| | 2026-09-03, measured | 2026-09-04, measured now |
| --- | --- | --- |
| `q27-Q3_K_S` generation | **51.2-53.5 tok/s** | **3.2 tok/s** |
| `/api/ps` GPU share | 100%, 66/66 layers | **0%** |
| `/api/ps` VRAM | ~13.7 GB | **0.00 GB** |
| `nvidia-smi` during load | ~14 GB used | **1304 MiB, unchanged** |

A direct `llama-server` launch says it outright:

    load_backend: failed to load C:\Users\slb/AppData/Local/Programs/Ollama/lib/ollama\cuda_v13\ggml-cuda.dll:
    warning: no usable GPU found, --gpu-layers option will be ignored

That is a **16x** slowdown. Every trial in the fifteen-cell grid would hit the 900 s wall, and
the campaign would reproduce the v4 failure exactly: the wall censors everything and quant
quality is never measured.

## The cause

An Ollama install or upgrade was **interrupted on 2026-09-03 between 21:16 and 21:17** and left
the CUDA 13 backend half-written.

    lib/ollama/cuda_v12/   14 files, complete, all dated 2026-09-03 16:49
                           including ggml-cuda.dll (351 MB)
    lib/ollama/cuda_v13/   concrt140.dll, cublas64_13.dll   (16:49)
                           is-XMOXADJX6M.tmp  (477 MB, 21:17)   <-- Inno Setup temp
                           ggml-cuda.dll            ABSENT
                           cublasLt64_13.dll        ABSENT
                           cudart64_13.dll          ABSENT

A second orphaned temp file, `is-KSV0S4JSX9.tmp` (4.4 MB, 21:16), sits in the Ollama root.
`ollama.exe` itself is intact and dated 16:50, and reports version 0.33.3 — so the binary is the
working one and only its CUDA 13 backend was destroyed. The 21:16-21:17 timestamps are the whole
story: something started replacing the backend and died partway.

## What was tried, and the result

The smallest reversible action available was to move the broken directory aside and let Ollama
fall back to the intact `cuda_v12`:

    lib/ollama/cuda_v13  ->  lib/ollama/cuda_v13.broken-20260904   (rename, never delete)
    restart Ollama, reload q27-Q3_K_S, re-probe

**It did not work.** Still `pct_gpu 0`, `vram 0.00 GB`, 3.1 tok/s. The almost certain reason is
that an **RTX 5080 is Blackwell, compute capability sm_120**, which needs CUDA 12.8 or newer;
Ollama ships a `cuda_v13` build precisely for such cards, and its `cuda_v12` build evidently
carries no sm_120 kernels. So the fallback is not merely unselected, it is unusable, and there is
no software-only workaround on this machine. The rename **has been reverted** and the host is
back in exactly the state it was found in.

The script that did both directions, with its reasoning, is kept at
`results/v5/repair-cuda.py`. It is idempotent, refuses to act if the destination exists, and
takes `--revert`.

## What will fix it

Reinstalling Ollama 0.33.3 on FRACTAL, so that `lib/ollama/cuda_v13` is written completely, and
deleting the two orphaned `is-*.tmp` files. Afterwards the check that matters is not `ollama
list` or a version string — it is a real load:

    # WINDOWS python, runnable from WSL; expect pct_gpu 100 and >40 tok/s
    /mnt/c/Users/slb/scoop/apps/python/current/python.exe \
        /mnt/d/local-llm-bench/ollama-bench/results/v5/repair-cuda.py --revert   # or just the probe

A version check would have passed throughout this fault. **Any converge that installs or
upgrades Ollama should assert residency on a real load, not a version string**, or this class of
half-finished install stays invisible until something needs the GPU. That is the durable lesson
and it is worth a role-level assertion.

This session did **not** attempt the reinstall. Reinstalling a managed Windows application is
fleet-layer work, `~/ansible-slb` was explicitly out of bounds for this session with another
worker in flight there, and an unattended installer run on a machine whose last installer run
died halfway is exactly the wrong thing to do without the owner.

## A second, unrelated thing found on the way

A **WSL-side `ollama serve` is running** (pid 190, `/usr/local/bin/ollama`) holding
`127.0.0.1:11434` **inside WSL** with **zero models**. It is not the Ollama the benchmark uses;
the real one is the Windows install, and a Windows process reaching `localhost:11434` correctly
gets the Windows one. But anything run with **WSL** Python against `localhost:11434` silently
talks to the empty Linux daemon and gets `404 model not found`, which reads as a missing model
rather than a wrong endpoint. It cost this session one confused diagnosis.

`pibench.py` is unaffected because it is a Windows-side harness by construction (`node.exe`,
`ollama app.exe` paths). The hazard is entirely for ad-hoc probing from WSL. Whether the WSL
daemon should exist at all is a fleet question, not a bench one.

## Consequence for the v5 plan

Blocked, until the reinstall:

- the fifteen-cell bend-finding grid, and everything downstream of it;
- the 64k KV-precision rerun in `kv-probe-plan-2026-09-03.md`;
- plan section 6 loop step 3, "calibrate on the GPU" — so the per-task properties that need the
  local model (does a trial finish under 300 s, does the prompt read unambiguously to a small
  model) cannot be settled and must be inherited by the session that gets the GPU back.

**Not blocked, and worth doing meanwhile** — this is most of the authoring night:

- authoring the eight-task suite (cloud only);
- the mechanical selfcheck, which needs no model at all;
- the Sonnet 3/3, GLM 2/3 and Haiku x3 gates (cloud and subscription);
- the `pibench.py` harness gaps in `findings-2026-09-04-grid-harness-gap.md`.

Section 4a is unaffected and if anything is easier to hold: with no local quant reachable, there
is no possibility of selecting tasks against what a quant passed.


## Closing note, added 2026-09-04 — this fault was repaired the same day

Everything above is a record of what was true when it was measured, and is deliberately left
unedited. **The fault is fixed.** The control session removed the two orphaned `is-*.tmp` files
and ran a forced repair install of the managed winget package (`Ollama.Ollama`, the id ansible
uses). `cuda_v13` now carries all thirteen files, including `ggml-cuda.dll` at 126.1 MB and
`cublasLt64_13.dll` at 455.8 MB — the latter exactly the size of the stranded temp file named
above, which confirms what the interrupted installer had been in the middle of writing.

Verified afterwards by a real load rather than a version string: `q27-Q3_K_S` at **100% GPU,
15357 MiB, 52.7 eval tok/s**, which sits on the Q3_K_S curve in `results/gpu-tune/summary.md`.

The repair is written up in **`ansible-slb/org/ollama-cuda-repair-2026-09-04.md`**. Read that page
alongside this one; this page is the diagnosis, that one is the fix, and read out of order this
one will look like a live blocker when it is not.
