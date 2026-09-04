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

P=$(cat "$OUT/_overseer2-prompt.txt")

cd "$OUT" || exit 3

t0=$(date +%s)
timeout -k 10 7200 node "$PI_CLI" \
    -p --no-session --no-extensions --mode json \
    --model openrouter/z-ai/glm-5.3-flash --thinking medium \
    -- "$P" > "$OUT/_overseer2.jsonl" 2> "$OUT/_overseer2.err" < /dev/null
rc=$?
t1=$(date +%s)
printf 'rc=%d wall_s=%d\n' "$rc" "$((t1 - t0))" >> "$OUT/_overseer2.err"
echo "OVERSEERDONE rc=$rc wall=$((t1 - t0))s"
