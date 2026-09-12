# Models

`CLAUDE.md` and `group_vars/all/vars.yml` are canonical for model settings.
This page records the active roster, routing boundaries, and measured
observations. The effort audit is `effort-level-audit-2026-08-26.md`.

**A model reachable on a plan is never routed through OpenRouter, and every
plan model uses its native harness.** GPT-6 and GPT-5.6 use Codex; Claude
models use Claude Code; GLM 5.3 uses pi on the Z.ai Coding Plan. OpenRouter is
metered per token and reserved for approved routes. The ZCode route was retired
with the worker runtime on 2026-09-10.

## Active roster

| model | route | default for | effort | status |
| --- | --- | --- | --- | --- |
| Fable 5.1 (`claude-fable-5-1`) | Anthropic, Claude Code | advisor and auditor on the owner's say-so | high | default |
| Opus 5 (`claude-opus-5`) | Anthropic, Claude Code | Claude subagents; the fallback worker; Opus reviewer when the seat orders one | high | default |
| GPT-6 Astra (`gpt-6-astra`) | — | — | — | retired from use; no pin names it |
| Sonnet 5 | Anthropic, Claude Code | — | — | bench gate only |
| Haiku 4.5 | Anthropic, Claude Code | — | — | bench gate only |
| GPT-5.6 Luna | Codex | the ChatGPT seat's TUI, delegated worker, and web research | high | default |
| GPT-5.6 Sol | Codex CLI | — | high | on demand |
| GPT-5.6 Terra | Codex CLI | — | high | on demand |
| GLM 5.3 Flash (`zai/glm-5.3-flash`) | Z.ai Coding Plan, pi | pi | high | plan default |
| GLM 5.3 (`zai/glm-5.3`) | Z.ai Coding Plan, pi | — | high | on demand |
| GLM 5.3 Flash (`z-ai/glm-5.3-flash`) | OpenRouter, pi | — | high | only approved OpenRouter model |
| DeepSeek Flash (`deepseek-flash`) | DeepSeek API, pi | — | — | approved 2026-09-09 as V4.1; re-keyed to the GA id 2026-09-10; served build not API-provable |
| `local/q27-IQ2_M-96k` | Ollama on the Windows desktop's Tailscale interface | slbh leaf agents | — | local workhorse default |

The only OpenRouter entry in `agent_config_pi_models` is GLM 5.3 Flash, with a
context-window pin and a managed price ceiling. Its request pins are
`zdr: true`, `data_collection: deny`, and `sort: throughput`; a model without a
permitted ZDR endpoint fails rather than falling back. These pins apply to
OpenRouter only — the Z.ai Coding Plan is a separate native route and makes no
OpenRouter ZDR claim. Read current prices from openrouter.ai's model card; the
`or-price` script that used to print them, with an authenticated `zdr` column,
went with the `pi-run` skill on 2026-09-10. Nothing checks the ceiling before a
run any more either — it is policy in the managed `models.json` rather than a
preflight (`agent-harnesses.md`, OpenRouter routing).

`q27-*` are local Qwen3.8-27B quants. No model blob is ansible-managed; the
grading harness is the `local-llm-bench` checkout on the desktop. `slbh` now
routes the real Ollama tag `q27-IQ2_M-96k` through its `local` provider and
uses it as the default leaf model. Current placement evidence is
`local-quants-2026-09-05.md`; the workhorse selection and its 96k rung are in
`local-workhorse-plan-2026-09-06.md`.
The route is live on the Windows desktop's Tailscale interface, not loopback:
from devbox, MagicDNS resolved `fractal.wyvern-temperature.ts.net` to the
desktop tailnet address, `ip route get` selected `tailscale0`, and Ollama's
`/v1/models` returned `q27-IQ2_M-96k:latest` on 2026-09-11. The Windows
listener is persisted by the Ansible-managed Ollama server task; `/api/ps`
was empty after the verification.

GPT-5.6 Pro tiers remain unreachable under the native-harness policy:
Codex has no `-pro` variant.

DeepSeek V4 Flash 0731 and `qwen/qwen3.8-27b` are historic benchmark rows,
not active roster entries. DeepSeek remains unapproved on OpenRouter since
2026-09-05 (v4: 9/21, mean 0.862, USD 4.61 against GLM's 7/21 at USD 0.90;
local-llm-bench `ollama-bench/results/v5/decisions.md`); qwen was retired from
v5 as too expensive. That retirement was an OpenRouter route and it still
stands. DeepSeek V4.1 Flash is a different, native route — pi's built-in
`deepseek` provider on `https://api.deepseek.com`, on the key the fleet
already deploys — approved by the owner on 2026-09-09 as a named `--model`
and not as a worker family. DeepSeek had published no V4.1 specification on
the day of approval, but the specification was obtainable from the model
itself, which answers on this fleet's key: direct probes returned a 1048576
context window, 393216 maximum output, and a native `none, minimal, low,
medium, high, xhigh, max` thinking enum. A managed `models` entry carries
those measured values. General availability landed 2026-09-10 and the
permanent id is `deepseek-flash`, re-keyed the same day. The name alone was
ambiguous — the retiring alias and `deepseek-v4-flash` both answer with
`"model":"deepseek-flash"` — and nothing reachable settles it. The seat
argued the build from its effort enum and a cross-family check refuted that,
twice: DeepSeek's request parser names the same seven variants when
`deepseek-v4-pro` refuses an invalid one, and the V4 reference documents
`medium` and `xhigh` as accepted and mapped to `high`. So the entry asserts
the id and the measured behaviour — all seven effort values, the context and
output ceilings — and asserts no version. Two fields still wait: a published
V4.1 rate card, the entry meanwhile carrying DeepSeek's off-peak V4-Flash
figures as a labelled placeholder, and the served build itself.
`deepseek-v41-2026-09-09.md` holds the measurements, the two risks that
argue for a measured pass before it carries real work, and the briefing
failure that delayed it.

## Historic observations

These rows describe measured behavior; they approve no route and add no model
to the roster. Each points to its evidence so it can be replaced by a newer
measurement rather than becoming policy by repetition.

| model or arm | observed result | evidence |
| --- | --- | --- |
| GLM 5.3 Flash, ZCode | v5 14/16 against pi's 12/16; plan throttled above one or two concurrent runs on LITE — its five-hour window rose from 5% to 99% with two other workloads sharing the key; that concurrency claim is Lite-era; its THROUGHPUT half remeasured on Pro 2026-09-08 on the fleet's own unshared key: output tok/s did not degrade at N=2/N=4, aggregate 1.0x/2.7x/3.8x (glm-tps-pro-2026-09-08.md addendum); the shared-key quota-burn mechanism remains untested and the shared-key guidance stands — would be settled by concurrent runs while a second consumer is live on the same key, watching the five-hour window | `zcode-arm-2026-09-05.md` |
| GLM 5.3 Flash, ZCode in the campaign window | Sep 3-20, 08:00-18:00 PT (09:00-19:00 MDT): twelve ZCode runs moved neither counter, the same task cost one credit outside the window and through pi inside it; Lite caps were 2,000 / 10,000, so the vendor's "doubled quota" was not a cap change — the plan moved to PRO on 2026-09-08 (owner, verified via plan-usage): 12,000 five-hour / 60,000 weekly credits; small pools of 2-4 ran unthrottled with an unshared key, which does not move the Lite-era concurrency guidance by itself | `zai-flash-campaign-2026-09-06.md` |
| GPT-5.6 Luna | v5 tiny 8/8, large 7/8; one lexical failure and two commits inside worker sandboxes; about 0.07 point of the Plus weekly window per million input tokens; 55M tokens aggregate cost a quarter cent of the $20 plan and concurrency has never bound (owner, 2026-09-09) | `closing-audit-2026-09-04.md`; `astra-control-trial-2026-09-05.md` |
| GPT-6 Astra, control session | one 73-minute session: Coach merge deployed on three hosts and an audited close in 19 minutes, rules kept; 60 points of the Plus weekly window at `medium` effort, about 30 times Luna per token; reverted the owner's effort setting as drift and shipped edits from a reviewer run it had killed | `astra-control-trial-2026-09-05.md` |
| GLM 5.3 Flash, pi | v5 12/16; about $0.20 per pass; resilience recovered one provider error, while three of four trial arms hit the cap | `wrt-trial-results-2026-09-04.md`; `pi-harness-trial-2026-09-04.md` |
| Opus subagent | manager for v6, v7, and calibration; $26.13 list cost in the trial — superseded for new projects 2026-09-08 (owner): a GLM controller may call a GLM manager, preferred over an Opus manager when a project manager runs multiple Lunas; Opus stays the fallback elsewhere | `wrt-trial-results-2026-09-04.md`; `leaked-waiters-2026-09-05.md` |
| OpenRouter smoke, none approved | Ling 3.0 Flash 7/8; Nemotron 3 Nano 5/8; Mercury 2.5 4/8; Solar Pro eliminated | `local-llm-bench/ollama-bench/results/or-smoke/`; `pending.md` |
| IQ2_M local quant | v7 19/20; five 64k timeouts in the earlier v5 placement | `local-quants-2026-09-05.md` |

The Opus solver ran the v5 tiny band 8/8 blind at about four minutes a task
as the sanity check beside the OpenRouter smoke (2026-09-04); no file in
`results/or-smoke/` records it, so this line is the record.
Earlier subagent measurements: `opus-subagents-2026-09-02.md`. The 64k KV comparison remains a separate
held benchmark question; its plan is `ollama-bench/results/v5/kv-probe-plan-2026-09-03.md`.

- 2026-09-06: a published Qwen3.8-27B quant survey was read against
  `local-quants-2026-09-05.md`; five points recorded there (revision pinning,
  tensor protection, the MTP draft head, chat-template nesting, default
  reasoning mode). Nothing here changes.
