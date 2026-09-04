# Local LLM Benchmarks

This repository contains local LLM benchmark harnesses.
Each harness lives in its own directory, with more to come.

## First harness

[`ollama-bench/`](ollama-bench/) is a task-based coding benchmark.
It grades local GGUF quants served by Ollama on an RTX 5080,
alongside hosted reference models:

- Claude Sonnet/Haiku
- gpt-5.6-luna via Codex
- GLM via OpenRouter

## Layout

All paths below are inside `ollama-bench/`.

- `tasks/`, `tasks-v2/`, `tasks-v3/`, and `tasks-v4/` are versioned
  task suites. Each task directory holds a prompt and a hidden `test.py`.
- `tasks-v4-rejected/` contains authoring evidence.
- `results/` holds per-campaign output.
- `results/v5/` contains the in-flight v5 plan.
- `pibench.py` is the harness.

## Grading

The hidden `test.py` is copied into the sandbox as `_hidden_test.py` and
run with `cwd=sandbox` and `PYTHONUTF8=1 PYTHONIOENCODING=utf-8`, under a
60 s timeout with a process-tree kill.

A run passes iff `rc==0` AND `'PASS'` appears in stdout.
The score is the last `SCORE n/m` line as a fraction.
A grader timeout is a fail with score 0.

## Provenance

This tree was pruned from 29 MB to 7.3 MB before its first commit.
Full taker transcripts, pi overseer JSONL transcripts, llama-server logs,
and ollama pull logs were dropped.
The findings extracted from them live in the ansible-slb repo at
`org/bench-v4-carryover-2026-09-03.md`.
