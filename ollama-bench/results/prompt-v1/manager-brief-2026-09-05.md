# Manager brief: the pi system-prompt campaign, overnight 2026-09-05/06

You are an Opus manager subagent in WSL on FRACTAL. Invoke the `org` skill before your first action and read `~/ansible-slb/org/README.md` as it says. Then read whole, once each: `~/ansible-slb/org/pi-packages-2026-09-05.md` (the survey that motivates this), `~/ansible-slb/skills/pi-run/SKILL.md`, `~/ansible-slb/skills/pi-run/scripts/pi-resilience.ts` (the fleet's production extension; your variants load beside it), and in the bench clone you make below: `ollama-bench/pibench.py`, `ollama-bench/results/pirun/pirun-sanity-2026-09-05.md` (how GLM was last run through this bench), `ollama-bench/results/v5/authoring/reference-arms-2026-09-05.md` (the reference scores) and `ollama-bench/results/v6/plan-2026-09-05.md` sections 4 and 5 (timeouts and the data fields).

Do NOT invoke `pi-run` or `codex-run`. Do not touch the GPU, the Ollama daemon, `~/ansible-slb` (read only), `~/.pi`, `C:\Users\slb\.pi`, `~/.agent-runs`, or the vault. Never print `ZAI_API_KEY` or any key. Another Opus manager owns the GPU and commits into `/mnt/d/local-llm-bench` tonight; you share the Windows interpreter with it and nothing else. Nothing here is gated on the owner; every decision is yours, recorded in `results/prompt-v1/decisions.md` as you take it.

## The owner's order

Improve pi's **system prompt only**, for GLM 5.3 Flash, using **plan usage only**: every model call goes to the Z.ai GLM Coding Plan, never OpenRouter. No tool changes, no settings changes, no packages; the deliverable is a prompt, as a pi extension file, with the evidence that it is better.

## Setup

```
git clone /mnt/d/local-llm-bench /home/slb/bench-prompt
cd /home/slb/bench-prompt/ollama-bench
mkdir -p results/prompt-v1
cp /home/slb/bench-prompt-work/manager-brief-2026-09-05.md results/prompt-v1/
```

- The bench is Windows-only: run it from WSL through `PY=/mnt/c/Users/slb/scoop/apps/python/current/python.exe`, never ssh, exactly as `run_bend_large.sh` and the pirun pages do. `pibench.py --provider zai --models glm-5.3-flash` makes pi's model `zai/glm-5.3-flash` and uses the managed Windows agent directory, whose `models.json` now carries the `zai` provider and whose default is the plan.
- Environment that must cross interop, before every launch:
  ```
  export WSLENV="ZAI_API_KEY:PIBENCH_PI_ARGS${WSLENV:+:$WSLENV}"
  export PIBENCH_PI_ARGS='-e C:/Users/slb/.claude/skills/pi-run/scripts/pi-resilience.ts'
  ```
  `PIBENCH_PI_ARGS` is whitespace-split into pi's argv, so a variant is one more `-e C:/...` on that line, and no path in it may contain a space. Prove both once at the start on one tiny task: a deliberately wrong `-e` path must fail with `Failed to load extension`, and the first real trial's pi output must show provider `zai` and model `glm-5.3-flash` (pibench records pi's JSON events; check the model line there or the session file). If anything reports provider `openrouter`, stop and fix before another call: that is spend the owner forbade.
- Timeouts: tiny band 300 s, large band 600 s. Bands: tiny `results/v5/authoring/round2/suite-0` (24k), large `results/v5/authoring/round3/suite` (64k); grading is pibench's own (hidden `test.py`, `SCORE n/m`, verdicts `correct`, `confidently_wrong`, `visibly_failed`).
- Plan quota is the budget. Read it before each variant with the plan's quota endpoint, `GET https://api.z.ai/api/monitor/usage/quota/limit`, key from `ZAI_API_KEY` in a small Python script that reads the environment and prints only the numbers (find the exact auth header from Z.ai's docs; Bearer is the documented form for the plan). Rules: if the 5-hour window is over 80% used, wait for its reset rather than run; never take the weekly window past 60%, because the owner works on this plan tomorrow; record every reading in `decisions.md`. If the endpoint cannot be read, fall back to a token ledger from pibench's results and stop at 3M input tokens per 5 hours.

## How a variant is applied

A pi extension that replaces the system prompt in `before_agent_start`: read `~/.local/lib/node_modules/@earendil-works/pi-coding-agent/docs/extensions.md` sections `before_agent_start` and `ctx.getSystemPrompt()`. Each variant is a pair of files under `results/prompt-v1/variants/`: `<name>.md` (the prompt text) and `<name>.ts` (a ten-line extension that reads the sibling `.md` at load time and returns `{ systemPrompt }`), loaded with `-e C:/Users/slb/bench-prompt/...`? No: the Windows interpreter cannot see `/home/slb`; keep the variants under `C:\Users\slb\bench-prompt-variants\` (WSL `/mnt/c/Users/slb/bench-prompt-variants/`) and copy each into `results/prompt-v1/variants/` for the record. First, capture pi's **current default system prompt** verbatim through the same hook (log `ctx.getSystemPrompt()` once) and save it as `variants/baseline.md`; every variant is a diff against it, and the ledger says what each changed and why.

## Protocol

1. **Baseline**: the default prompt, tiny band, three trials. Record per task: pass, verdict, wall, turns, tool calls, in/out tokens, and whether resilience fired. Three trials because the sanity and baseline pages show a one-trial tiny score moving between 5/8 with different tasks failing; the score is the pass count over 24.
2. **Seed variant H**: the published five-guideline prompt from the QuixBugs experiment (fetch `https://heyneo.com/blog/pi-agent-quixbugs-optimization` and its repository, file `pi/packages/coding-agent/src/core/system-prompt.ts` at the H3 revision; take the guidelines, keep pi's tool descriptions). Three trials tiny.
3. **Analysis**: read every failed trial's transcript from baseline and H, whole, once. Classify each failure (did not find the requirement; found it and contradicted it; ran long and hit the length stop; misread the checker's format; gave up early; tool misuse). Then write at most six variants, each one hypothesis, each a small edit, named for the hypothesis. Three trials tiny each, best-first by expected effect. A variant that loses to baseline on pass count after three trials is dropped and its lesson recorded.
4. **Selection**: rank by pass count over 24, then by confidently-wrong count (lower is better: a visible failure costs a retry, a confident one costs the verification delegation was meant to save), then by mean output tokens. Combine the two best single edits into one variant and run it three times; keep whichever of the three is best.
5. **Holdout, once, never iterated on**: the large band, one trial each, for the baseline prompt and the best variant. If the quota allows, the runner-up too. A variant that regresses the large band is not recommended whatever the tiny band said.
6. **Hand off**: `results/prompt-v1/handoff-2026-09-06.md`: the ledger table (variant, hypothesis, tiny pass/24, confidently-wrong count, mean tokens, large pass/8), the baseline and best prompts side by side as a diff, the quota readings, the transcripts' three most surprising observations, and a plain recommendation: deploy, deploy with a caveat, or do not deploy. The deliverable file for the fleet is `results/prompt-v1/pi-system-prompt.ts` plus `pi-system-prompt.md`, in the shape `pi-run` could load with `-e` beside `pi-resilience.ts`; do not deploy it yourself.

Commit and push after every phase from `/home/slb/bench-prompt`: stage only `ollama-bench/results/prompt-v1/`, message one lowercase line, then `cd /mnt/d/local-llm-bench && git pull -q --rebase` and copy the directory in and commit there the same way, retrying on an index lock every 30 s up to five times, because the other manager commits there tonight. Never modify `pibench.py` in either clone; if the bench needs a change to do this, make it in your scratch clone only and say so in the handoff.

## Traps

A multi-line program never goes inline through a heredoc or nested `wsl.exe`/`cmd.exe`; write the file, run the file. Every interop command gets `< /dev/null`. Never poll with `pgrep -f`; poll pibench's JSON reaching N tasks or watch a bracket class. Up to three pibench processes may run at once with different `--tag`s if the quota window allows; more than that and the plan's rate limit will show as errors, not speed. Read a finished trial from its JSON, never from the tail of a console. Stop the whole campaign, leave the record consistent, and write the handoff if the plan quota rules above are hit and cannot recover before 06:00.

Final report: the ledger table and the recommendation.
