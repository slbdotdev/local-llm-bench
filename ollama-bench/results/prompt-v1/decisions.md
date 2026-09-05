# Decisions — pi system-prompt campaign v1 (overnight 2026-09-05/06)

Manager: Opus subagent on FRACTAL/WSL. Every model call goes to the Z.ai GLM Coding
Plan (`--provider zai --models glm-5.3-flash`). No OpenRouter. Scratch clone
`/home/slb/bench-prompt`, variants under `C:\Users\slb\bench-prompt-variants\`.

## D0 — 2026-09-05 04:44 UTC (2026-09-04 22:44 MDT) — setup and the key path

- `ZAI_API_KEY` is **not** in this session's inherited environment even though
  `~/.bashrc` sources `~/.config/devbox/env`; `OPENROUTER_API_KEY` is. Every launch
  script therefore sources `~/.config/devbox/env` itself rather than trusting the
  environment. Verified the key then crosses interop with
  `WSLENV="ZAI_API_KEY:PIBENCH_PI_ARGS${WSLENV:+:$WSLENV}"` (a Windows python printed
  `ZAI_API_KEY len=49`; the value was never printed).
- Managed `C:\Users\slb\.pi\agent\models.json` carries provider `zai`
  (`baseUrl https://api.z.ai/api/anthropic`, `apiKey $ZAI_API_KEY`,
  `api anthropic-messages`) and `settings.json` has `defaultProvider zai`,
  `defaultModel glm-5.3-flash`. Read only; not modified.
- Results are tagged `prompt-v1/<name>`, so `pibench.py` writes straight into
  `results/prompt-v1/`. Nothing outside that directory is staged.

## D1 — 2026-09-05 04:44 UTC — quota endpoint and the budget

`GET https://api.z.ai/api/monitor/usage/quota/limit` with `Authorization: Bearer <key>`
returns 200. Reader: `results/prompt-v1/zai-quota.py`, which prints numbers only and
archives each raw response under `results/prompt-v1/quota/`.

| reading | 5h window (cap 2000) | week (cap 10000) |
| --- | --- | --- |
| campaign-start 04:44 UTC | 9 used, 0.45% | 9 used, 0.09% |

5h window resets 08:50 UTC; the week resets 2026-09-12 03:43 UTC. Gates as briefed:
do not start a variant with the 5h window over 80%, and never take the week past 60%
(6000 credits). Plan level `lite`.

## D2 — 04:45–04:46 UTC — the two proofs the brief demands

1. **Bad `-e` path fails loudly.** `PIBENCH_PI_ARGS='-e C:/Users/slb/bench-prompt-variants/NOPE.ts'`
   on one tiny task (`t03`): `rc 1`, `wall 0.4 s`, and the trial's own `stderr` field reads
   `Failed to load extension "C:\Users\slb\bench-prompt-variants\NOPE.ts": Extension path does
   not exist`. So the hook's argv demonstrably reaches pi. Tag `prompt-v1/negctl`.
2. **The real trial runs on the plan.** A `capture.ts` extension logged, from inside
   `before_agent_start` on a real `t03` trial (tag `prompt-v1/capture`, PASS, score 1.00):
   `provider=zai`, `modelId=glm-5.3-flash`, `modelName=GLM 5.3 Flash (Z.ai coding plan)`,
   `contextWindow=1000000`, `thinkingLevel=medium`. **No trial in this campaign reports
   provider `openrouter`.** Written to `variants/baseline-proof.json`.

## D3 — 04:46 UTC — thinking level `medium`, not the managed `high`

The reference GLM rows (`results/pirun/pirun-sanity-2026-09-05.md`, the reference-arms page)
were all taken at `--think medium`, and `pibench.py` sets the level per run. Holding medium
keeps every row in this campaign comparable with those, and every variant here is compared
against a baseline measured the same way. Caveat carried to the handoff: `pi-run` deploys at
`high`, so an effect measured at medium is not proven at high.

## D4 — 04:46 UTC — the baseline prompt, captured verbatim

pi's default system prompt under the bench's flags (`--no-context-files --no-skills
--no-prompt-templates --no-extensions`) is **2,685 characters**, 4 tools, 0 skills, 0 context
files. Saved as `variants/baseline.md` with the trailing sandbox path replaced by a
`<<<CWD>>>` token (2,650 chars), since the real cwd differs per trial. Its shape: a one-line
role sentence, a four-tool list, ten guidelines (eight of them about how to use `edit`), and
a ~1,200-character block of pi's own documentation paths — **and nothing at all about
finishing the task**: no output-format rule, no "read the whole specification", no
verification step. That is the headroom this campaign is aiming at.

Variant machinery: each variant is `variants/<name>.md` plus a generated `<name>.ts`
(`mkvariant.sh`) that reads the sibling `.md` at load time through
`path.dirname(fileURLToPath(import.meta.url))` and returns `{ systemPrompt }` from
`before_agent_start`, substituting `<<<CWD>>>` with `event.systemPromptOptions.cwd`.
`import.meta.url` resolves inside a pi extension (proved in `baseline-proof.json`).

## D5 — 04:47 UTC — variant H, the published five guidelines

Fetched `https://heyneo.com/blog/pi-agent-quixbugs-optimization` and cloned
`https://github.com/dakshjain-1616/Pi-agent-optimisation-`. The H3 revision is the repo's
single content commit `f089a6e`; `pi/packages/coding-agent/src/core/system-prompt.ts` holds
the five guidelines **verbatim** in `buildSystemPrompt`, appended after `Be concise` and
`Show file paths clearly`. Variant `H` is `baseline.md` with exactly those five bullets
inserted at exactly that point, pi's tool descriptions kept (3,787 chars). Their reported
result: QuixBugs dev 82%→95%, sealed holdout 80%→95%, on `openrouter/z-ai/glm-5.3-flash`.
Note their pi is older than ours — our baseline already carries six `edit`-tool guidelines
theirs lacks — so H here is our prompt plus their five, not their prompt.
