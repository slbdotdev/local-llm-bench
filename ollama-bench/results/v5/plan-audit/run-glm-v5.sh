#!/usr/bin/env bash
# GLM audit of the v5 plan.
#
# Routing: the owner granted a ONE-TIME exception to route by THROUGHPUT for this
# audit. It is done by copying ~/.pi/agent to a temp dir, changing that COPY's
# providers.openrouter.sort from "price" to "throughput", and pointing pi at the
# copy with PI_CODING_AGENT_DIR (documented at
# pi-coding-agent/docs/environment-variables.md:81, implemented in
# dist/config.js:404-414). The managed ~/.pi/agent is NOT touched.
#
# The copy's mcp.json is emptied so the run cannot reach the Unity hub or the
# owner's live Blender instance.
set -u
export PATH="$HOME/scoop/persist/nodejs-lts/bin:$HOME/scoop/apps/nodejs-lts/current:$PATH"
export PI_CODING_AGENT_DIR="$HOME/AppData/Local/Temp/v5-pi-agent-throughput"

OUT="/c/Users/slb/ollama-bench/results/v5/plan-audit"
cd /c/Users/slb/ollama-bench

read -r -d '' P <<'PROMPT'
You are an adversarial auditor advising a control session that stays in command. You change
nothing: do not edit or create any file, do not run any benchmark, model, Unity editor, Blender
instance or git command that writes. Read only.

Read results/v5/plan-2026-09-03.md in full. It is a plan for v5 of a local-LLM coding benchmark
that adds live-Unity and headless-Blender avatar tasks to a suite that was previously pure-file
Python. For context you may also read: results/plan-2026-09-03.md (the v4 live plan),
results/v4-authoring/brief.md and report.md (the v4 task-authoring rules and outcome),
results/sonnet-v4/report.md, results/v4-local-medium.json and .log, pibench.py,
pi-agent/settings.json and pi-agent/models.json. The VRCA-Bench code the plan depends on is at
D:\avatars\tools\bench (bench/runner.py, bench/projects.py, bench/gateway.py,
bench/contestants.py, bench/tasks/, docs/design.md, results/runs.jsonl); its runtime is
D:\VRCA-Bench. Read what you need there.

Audit the plan for:

1. Whether the task inventory in section 1 is a fair reading of results/runs.jsonl, especially the
   "builds-worse is saturated on the control" verdict, and whether any keep/drop/rework call is
   wrong.
2. Whether the section 7a root-cause claim is correct: that pi's clampMaxTokensToContext hands the
   model the whole residual context window as max_tokens, that reasoning and the answer share it,
   and that this - not a model defect - produced the Q2_K_L one-turn zero-tool-call runs. Check the
   arithmetic and the cited source. If it is wrong, say exactly where.
3. Whether the section 7b token budget is right, and whether the conclusion "a Unity task cannot
   run locally at 32k at all" follows. Consider what the plan may have missed that would make it
   survivable at 32k.
4. Whether the 8-15 candidate tasks in section 4 are actually gradeable as described, which ones
   have a grader that every model would fail identically (the known failure mode), and which SCORE
   schemes are miscalibrated for a target mean of about 0.50.
5. Whether the validation campaign in section 5 can deliver what it claims: the Haiku/Sonnet gate
   logic, the editor/concurrency/port-8080 rules, the 4th-editor requirements, and the cost and
   wall-clock estimates.
6. Containment: the Blender decision (headless only, because the owner has a live Blender holding
   unsaved work), the D:\avatars blocked-path model, policy.json, the pi guard hook. What is still
   reachable that should not be?
7. Anything the final report to the owner will be unable to deliver, and any place the plan claims
   comparability it has not earned.

Number each finding F1, F2, ... Rate each HIGH / MED / LOW. Quote the evidence as file:line or an
exact quotation. Give a concrete fix a control session can apply without commits and without fleet
config changes. Call out explicitly any place the plan states something as measured that you could
not verify. Finish with a one-paragraph verdict on whether the campaign should start as written.
PROMPT

bash ~/.claude/skills/pi-run/scripts/pi-run \
  --model z-ai/glm-5.3-flash --effort high \
  --cwd /c/Users/slb/ollama-bench --timeout 2400 --no-context-files \
  "$P" > "$OUT/review-glm-v5.md" 2> "$OUT/review-glm-v5.err"
rc=$?
echo "rc=$rc $(date -Is)" >> "$OUT/review-glm-v5.err"
echo "AUDITDONE" >> "$OUT/review-glm-v5.err"
