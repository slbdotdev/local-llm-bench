#!/usr/bin/env bash
# Launch the GLM 5.3 Flash overseer for the luna-max-v4 campaign.
#
# NOT launched through pi-run: that wrapper exports AGENT_RUN_DEPTH into pi, and
# the campaign's own driver has to call codex-run, which would then be refused
# (by design). So pi is started the way pibench.py starts it - node + the pi
# cli.js bundle - with the managed ~/.pi/agent (default price routing, ZDR-only)
# and no depth marker in the environment.
#
# Deviations from pibench.py's run_pi, on purpose:
#   * no PI_CODING_AGENT_DIR  -> the managed ~/.pi/agent, not ./pi-agent
#   * no PI_OFFLINE           -> this run must reach OpenRouter
#   * context files ON        -> the AGENTS.md chain, as a normal fleet agent
#   * --no-extensions         -> no MCP bridge, so the run cannot reach the
#                               owner's live Blender or a Unity editor
set -u
export MSYS_NO_PATHCONV=1

NODE_BIN=$HOME/scoop/apps/nodejs-lts/current
# node.exe is native Windows and MSYS_NO_PATHCONV=1 stops Git Bash converting
# argv, so the bundle path has to be handed over already in Windows form.
PI_CLI=$(cygpath -w "$HOME/scoop/persist/nodejs-lts/bin/node_modules/@earendil-works/pi-coding-agent/dist/bundle/cli.js")
OUT=/c/Users/slb/ollama-bench/results/luna-max-v4
export PATH="$NODE_BIN:$NODE_BIN/bin:$PATH"
export PI_SKIP_VERSION_CHECK=1
export PYTHONIOENCODING=utf-8
unset PI_CODING_AGENT_DIR AGENT_RUN_DEPTH 2>/dev/null || true

read -r -d '' P <<'PROMPT'
You are the overseer of a small benchmark campaign. You run it yourself; the control session that
launched you is only going to verify your results afterwards. Work in the current directory,
C:\Users\slb\ollama-bench\results\luna-max-v4.

The campaign: three tasks from a Python coding benchmark (56_tmpl, 57_stateful, 55_minilang - the
three longest prompts in tasks-v4), two trials each, six runs total. The taker for each run is the
Codex CLI on model gpt-5.6-luna at reasoning effort max. Sandboxes and a manifest already exist.

Do exactly these steps, in order, and nothing else:

1. Run: python run.py setup
   (idempotent; it rebuilds the six sandboxes from the task seeds and writes manifest.json.)

2. Start the driver detached, so it survives the end of the shell call that starts it:
      cd /c/Users/slb/ollama-bench/results/luna-max-v4 && nohup bash _driver.sh > _driver.log 2>&1 &
   That command must return immediately. The driver launches the six Codex takers, at most three
   at a time, each with a 1800 s timeout. Expect roughly 30-70 minutes in total.
   The driver is resume-safe: a sandbox that already has a _done file is skipped. So if you find
   that no codex process is running and _ALLDONE is absent and no new _done file has appeared for
   more than 35 minutes, the driver shell was killed - relaunch it with the same command, at most
   twice, and say in report.md that you had to.

3. Wait for the driver to finish. It writes the file _ALLDONE in this directory when every run is
   done. Poll for it - sleep for a minute or two between checks, do not busy-loop, and do not give
   up before 100 minutes have passed. Per-run progress markers are <task>/t<n>/_done.

4. Run: python run.py collect
   This reads each sandbox's _rc and _codex_stderr.log and writes runs.json with, per run: rc,
   wall_s, total_tokens, tokens_blocks, nested_refusals (and input/output/reasoning token counts if
   Codex reported them).

5. Run: python run.py grade
   This copies each task's hidden test in and writes grades.json with pass/score per run.

6. Write report.md in this directory. It must contain:
   a. A per-run table: task, trial, pass, score, wall seconds, total tokens, nested-call refusals.
   b. Per-task pass rate (x/2) and mean SCORE.
   c. Mean and total tokens across the six runs.
   d. A comparison table for the same three tasks against:
      - results/codex-luna-v4 (the same taker at effort MEDIUM, 3 trials: 55_minilang 1/3 pass,
        mean SCORE 0.946; 57_stateful 1/3 pass, mean SCORE 0.808; 56_tmpl was not run there);
      - results/sonnet-v4/grades.json and results/haiku-v4/grades.json (read them; take only the
        three tasks in this campaign);
      - the local fp8 reference results/v4-ref-medium-1800.json (a dict keyed by model with a
        "runs" list; take the entries whose "task" is one of the three).
      Say plainly which cells are missing rather than inventing them.
   e. A short section on the nesting guard. Background: on 2026-09-02 Codex takers discovered the
      deployed codex-run skill and called it recursively, up to 11 nested calls in a single run.
      Since commit 3ce8f44 the codex-run and pi-run wrappers export AGENT_RUN_DEPTH and refuse any
      nested call with the line "refusing nested run" on stderr and exit status 2. Report how many
      such refusals appear across the six stderr logs (run.py collect counts them) and how many
      "tokens used" blocks each log has - exactly one per log means no nested run happened at all.
   f. Anything you could not do, or that looked wrong. Be specific.

Hard rules:
  * Do NOT modify run.py, _driver.sh, anything under ..\..\tasks-v4, or any file outside
    C:\Users\slb\ollama-bench\results\luna-max-v4. You may read anything under
    C:\Users\slb\ollama-bench.
  * Do NOT call codex-run or pi-run yourself, and do not invoke the codex-run or pi-run skills.
    The only thing allowed to start a Codex process is _driver.sh.
  * Do NOT touch the local GPU, Ollama, or any other running benchmark process on this machine.
  * Do NOT run git commands that write, and do not commit anything.
  * If a step fails, or the driver stalls, or a Codex run reports that the ChatGPT plan usage
    window is exhausted (the wrapper prints "the ChatGPT plan usage window is exhausted"), STOP,
    write what you have into report.md, and say so clearly. Do not work around it, do not retry
    with a different model, and do not fabricate results.
  * Everything you report must come from a file you actually read. Do not estimate a number you
    could have measured.

When you are finished, your final message should be a short summary: the per-task pass rate and
mean score, total and mean tokens, the nesting-guard outcome, and anything that went wrong.
PROMPT

cd "$OUT" || exit 3

t0=$(date +%s)
timeout -k 10 7200 node "$PI_CLI" \
    -p --no-session --no-extensions --mode json \
    --model openrouter/z-ai/glm-5.3-flash --thinking medium \
    -- "$P" > "$OUT/_overseer.jsonl" 2> "$OUT/_overseer.err" < /dev/null
rc=$?
t1=$(date +%s)
printf 'rc=%d wall_s=%d\n' "$rc" "$((t1 - t0))" >> "$OUT/_overseer.err"
echo "OVERSEERDONE rc=$rc wall=$((t1 - t0))s"
