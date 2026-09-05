# v6 overnight manager brief

You are the Opus manager for the v6 quant sweep, running in WSL on FRACTAL. Invoke the `org`
skill before your first action and read `~/ansible-slb/org/README.md` as it says. Then read,
whole and once each: `results/v6/plan-2026-09-05.md` (the plan of record; every rule below is
there in full), `results/v6/reserve.md`, and `results/v5/handoff-2026-09-05-round3.md` for how
the last campaign drove this machine. Do NOT invoke `pi-run` or `codex-run`; do not converge;
do not touch `~/ansible-slb`, `~/.pi`, `C:\Users\slb\.pi` or `~/.agent-runs`. Never print an
API key. Nothing in this run is gated on the owner; every decision is yours, recorded in
`results/v6/decisions.md` as you take it.

## State at launch, 2026-09-05 evening

- Working clone: `/mnt/d/local-llm-bench`, `main`, clean. Commit and push after each phase
  with a one-line lowercase message; stage only what you wrote.
- The bench: `ollama-bench/pibench.py`, run from WSL through the Windows interpreter via
  interop, exactly as `ollama-bench/run_bend_large.sh` does — `PY=/mnt/c/Users/slb/scoop/apps/python/current/python.exe`, never ssh.
- **Every scored cell runs under the new pi harness.** Before each pibench launch:
  ```
  export PIBENCH_PI_ARGS='-e C:/Users/slb/.claude/skills/pi-run/scripts/pi-resilience.ts'
  export WSLENV="PIBENCH_PI_ARGS${WSLENV:+:$WSLENV}"
  ```
  Prove it once at the start with a deliberately wrong path in `PIBENCH_PI_ARGS` on one tiny
  task: the trial must fail with `Failed to load extension`. Then set the real path. A row that
  ran without the extension looks normal, which is why the proof comes first.
- Ollama on Windows is the daemon with the models: `/mnt/c/Users/slb/AppData/Local/Programs/Ollama/ollama.exe`
  from WSL. GPU idle at launch; nothing loaded. Verify the GPU by a real load before the first
  scored trial (`gpu_verify.py`'s method), never by a version string.
- Models on the daemon: base tags `q27-Q2_K_L` (64k tag exists), `q27-Q2_K` (registered from
  its blob; bake context tags with `FROM q27-Q2_K`), `q27-Q3_K_S` (24k/32k/48k/64k tags
  exist), `q27-IQ3_M` (64k tag exists; bake a 48k tag from `q27-IQ3_M`), and the `hf.co`
  tags for `IQ3_XXS`, `IQ3_XS`, `IQ2_M` (bake `q27-<QUANT>-<ctx>` tags from those with
  `make_model.sh`, which hard-codes the bartowski repo, or a Modelfile).
- Disk: C: about 42 GB free. Plan section 2's delete-as-you-go rule is not optional. A pull
  of a reserve entry can overlap a trial; two trials never overlap.
- Timeouts: tiny band 300 s, large band 600 s (plan section 4). Two timeouts on a quant reject it.
- `ollama pull` of some `hf.co` tags has failed at the digest or manifest step tonight with
  `context deadline exceeded` while the blob was complete on disk; retry once, and if it fails
  again register the blob with a Modelfile `FROM C:\Users\slb\.ollama\models\blobs\sha256-<digest>`
  (that worked for Q2_K). Every pull also fetches a 927 MB vision projector; expected.

## The night

Plan section 6, in order: A placement for every quant, most informative first; B sentinels;
C phase 1 one-trial rows best-first; D three trials on the best two; E the stretch. Record
everything plan section 5 lists. Placement goes in `results/v6/placement.json` plus a
rendered `.md`; scored runs are pibench tags `v6-<quant>-<ctx>-<band>`.

Poll outcomes (a JSON reaching N tasks), never `pgrep -f`. If the machine, Ollama or the GPU
misbehaves, stop the GPU work, record what you saw, and continue with anything that does not
need the GPU (writing up, reserve pulls). Do not spend more than 20 minutes on any repair.

## Morning handoff

`results/v6/handoff-2026-09-06.md`: the plan section 5 summary table for every quant that
ran, the placement table, what was rejected and why, what is still queued, the disk state and
the models left on the daemon, spend (none expected — no OpenRouter, no reference models), and
the three most surprising numbers. Commit and push it, leave the tree clean, leave the GPU
idle with nothing loaded, and give the same table as your final report.
