#!/usr/bin/env bash
export PATH="$HOME/scoop/persist/nodejs-lts/bin:$HOME/scoop/apps/nodejs-lts/current:$PATH"
cd /c/Users/slb/ollama-bench
bash ~/.claude/skills/pi-run/scripts/pi-run --model z-ai/glm-5.3-flash --effort high --cwd /c/Users/slb/ollama-bench --timeout 1500 --no-context-files "You are an advisor to a control session that stays in command; you change nothing and run no models or benchmarks. Read results/plan-audit/q2kl-evidence.md first; you may also read results/plan-2026-09-03.md, results/v4-analyse.py, results/v4-local-ranking.sh, pibench.py and results/v4-local-medium.json for detail. Answer the four questions at the end of the evidence file." > results/plan-audit/review-glm-q2kl.md 2> results/plan-audit/review-glm-q2kl.err
echo "rc=$? $(date -Is)" >> results/plan-audit/review-glm-q2kl.err; echo AUDITDONE >> results/plan-audit/review-glm-q2kl.err
