# Local workhorse integration v1, plan

*Drafted 2026-09-06 by an Opus project manager under the Fable control
session, from a Luna research run (`wr-wsl-20260906T230829Z-efba2f6966ef`;
report in the control session's scratch at `local-workhorse/RESEARCH.md`),
from a Luna probe of the CachyOS host, and from the manager's own
verification of every load-bearing number in both. Reviewed blind by Luna
(`wr-wsl-20260906T233546Z-d1b43272b6a7`), verdict REVISE; section 14 records
what was taken and what was not. The owner's decisions of 2026-09-06 are
section 12. Plan, not specification: it says what v1 does and why, and leaves
how to the build. Nothing here is implemented; no play has been run and
nothing on any host has been changed.*

**Current-state note (2026-09-11):** the pre-build claims in this dated plan
are historical. The endpoint/provider integration landed and was verified;
the addendum at the end records the live route and its remaining scope.

## 1. Three findings that shape v1

**The two-stream target cannot be bought with an Ollama setting.** Ollama's
scheduler forces `num_parallel` to 1 for a fixed list of model architectures,
and `qwen35` — the architecture every `q27-*` tag reports — is on it:

```go
// Some architectures are not safe with num_parallel > 1.
// ref: https://github.com/ollama/ollama/issues/4165
if slices.Contains([]string{"mllama", "qwen3vl", "qwen3vlmoe", "qwen35",
    "qwen35moe", "qwen3next", "lfm2", "lfm2moe", "nemotron_h",
    "nemotron_h_moe", "nemotron_h_omni"}, req.model.Config.ModelFamily) &&
    numParallel != 1 {
    numParallel = 1
    slog.Warn("model architecture does not currently support parallel requests", ...)
}
```

`server/sched.go` around line 507, byte-identical at `v0.32.15`, at `v0.33.3`
— the version the desktop actually runs — and on `main`; the reviewer fetched
all three and found one SHA-256 between them. So this is standing upstream
policy, not a version quirk: `OLLAMA_NUM_PARALLEL=2` is accepted, logged as a
warning and ignored, and no API field or runner option defeats it. The list is
the hybrid-recurrent and vision architectures, which is consistent — each
carries per-sequence state that llama.cpp's multi-slot path has been unsafe
with. **Through Ollama there is no setting that gives this model two slots.**
A direct `llama-server` has a `--parallel` flag and is a different question,
answered in section 4 and phase 6. The bounded probe agrees with the clamp:
two concurrent 1,552-token requests were served strictly one after the other,
each at about 61 tok/s, 10.07 s of wall for both and 32.6 tok/s aggregate.

**The card would have taken two slots if the runtime would.** From the model's
own metadata — `block_count` 65 with `full_attention_interval` 4 and one
`nextn` draft block, `head_count_kv` 4, key and value length 256 — sixteen of
the sixty-four ordinary layers carry a KV cache, at 16 x 4 x (256+256) =
32,768 elements per token, which at q8_0's 34 bytes per 32 elements is
**34.0 MiB per 1,024 tokens**. Two independent checks favour sixteen over the
seventeen attention blocks the tensor list shows: sixteen predicts a
q8_0-minus-q4_0 difference of 1,024 MiB at 64k where `kv-64k-2026-09-06.md`
measured 960 MiB (seventeen predicts 1,088 MiB), and weights-plus-KV at
sixteen lands within 1% of the measured resident sizes of IQ2_M at 96k and
Q2_K at 64k where seventeen overshoots both. The seventeenth block is
`blk.64`, the `nextn` MTP draft head, which no current runtime decodes; **if a
future build enables speculative decoding the count becomes seventeen and
every budget here rises about 6%**. The roster's **39 MB per 1k** is the same
quantity plus the per-context compute buffers and is the number to budget
with. Against the 14.2 GB fair-weather resident line of
`local-llm-bench-desaturation-2026-09-05.md`, IQ2_M's 10.13 GiB of weights
leave room for roughly 100k tokens of total KV once a derived — not measured —
allowance of about 150 MB per slot for the model's recurrent state is
subtracted. So **two slots of 48k each budget to fit inside the same 13.27 GB
envelope one slot of 96k already occupies.** That is an estimate, not a
measurement: equal total KV tokens do not prove equal VRAM, because the
recurrent state and the compute buffers may scale per sequence in ways only
phase 6 can show. It is recorded because it is what makes phase 6 worth
running: the constraint is the scheduler, not the card.

**48k is where this model behaves best.** The `v7r5-48k` cell of
`decisions-r5-2026-09-06.md` ran the same ten tasks, the same quant and the
same harness at both windows: 64k gave pooled 0.833 [0.704, 0.913] with three
confidently-wrong verdicts in 48 trials, 48k gave 0.900 [0.744, 0.965] with
none in 30. The intervals overlap, so the *rate* difference is not
established; what changed is the shape of the misses, from confident wrong
answers at 64k to visible `stop=length` truncations at 48k. For a workhorse
that is the right trade, and it is why every band in this plan is capped.

## 2. What v1 does, and why

v1 adds one thing: a **`local` model family, reachable from `pi-run` only**,
serving read-only drafting work off the desktop's Ollama, behind an
availability signal, with a paid family as the fail-closed fallback. It buys
back paid-plan capacity on the highest-volume, lowest-consequence work the org
does, and nothing else. It is not a new harness, not a reviewer of record, and
not a route for anything that writes.

pi is the only harness that can carry it. Codex and Claude Code are
plan-bound native harnesses under `agent-harnesses.md` — Codex on the ChatGPT
login, Claude Code on the Anthropic subscription — and neither has a provider
seam. `pi-run` does, and it already has a keyless-plan precedent in `zai`.

The unit of value is a **draft whose source is retained**. Every v1 use hands
back something a manager or the owner reads beside the material it came from,
so a confidently wrong answer costs a re-read rather than a wrong decision.
Nothing in v1 is the last reader of anything.

## 3. The two quants

Both tags exist on the desktop; both were confirmed by `ollama list`, by
`ollama show`, and by their blob sizes under `D:\ollama\models\blobs`.

| slot | tag | weights (blob) | context | resident | gen tok/s |
| --- | --- | ---: | ---: | --- | ---: |
| long-context | `q27-IQ2_M-96k` | 10.13 GiB | **96k** (98,304) | 13.27 GB **measured at 96k** | 41.9 at 96k |
| short-context | `q27-Q2_K-48k` | 11.03 GiB | **48k** (49,152) | about 12.5 GB **derived** | 45.1 **measured at 64k** |

The weight figures are exact blob sizes read off the desktop, not from a page;
`ollama list` rounds them to 10 GB and 11 GB. **Q2_K's 13.07 GB resident and
45.1 tok/s in `local-quants-2026-09-05.md` are its 64k rung, not its 48k rung,
and the 48k rung is unmeasured** — subtracting 16k of KV from the 64k figure
gives about 12.5 GB, which is arithmetic, not evidence. Measuring it is a
phase 2 item.

**IQ2_M is the long-context quant and it is not in doubt.** It is the
campaign's workhorse, the smallest resident finalist, the only tag with a
measured 96k operating point under the headroom line, 19/20 on the v7
calibration, and 4% confidently wrong against UDQ3KXL's 25% on the
thirty-three shared finalist cells of v6. Its 96k placement is a capacity
result; the quality evidence stops at 64k, so 96k is for reading and 48k is
for reasoning.

**The second quant is a second family, not a quality tier, and the plan says
so plainly.** On the v7 calibration IQ2_M, Q2_K and UDQ3KXL scored 19, 19 and
20 out of 20 at one trial each — which the campaign itself now refuses to
treat as a task property — and on the shared v6 cells the only quant that
separated did so in the wrong direction. Higher point estimates than IQ2_M do
exist in the record (Q2_K_L's 7 of 8 on the v5 large band, UDQ3KXL's one-trial
20/20); none of them is separable at these sample sizes. So the accurate claim
is that **there is no *established* quality tier above IQ2_M on this roster**,
not that no higher number has ever been recorded. What a second quant does buy
is a different quantisation family: Q2_K is a k-quant where IQ2_M is an
i-quant, so running both over the same bounded job and comparing is a cheap
detector for exactly the failure the confidently-wrong tail represents. Q2_K
at 48k earns the slot on being v7-scored, the fastest on the roster, light
enough to leave real headroom, and pinned to the band where the workhorse is
best behaved.

The research recommended `q27-Q2_K_L-64k`. That was not taken: Q2_K_L has no
v7 evidence at all, its 13.35 GB is the heaviest resident on the roster and
the closest to the owner's own headroom, and its placement figures are v5 and
v6 only. `q27-UDQ3KXL-48k` is the alternative if the owner wants a nominal-bit
step up and accepts the v6 tail figure; the recommendation is against it for
that reason. The choice is section 13's third question.

**They cannot both be resident.** 10.13 + 11.03 GiB of weights alone is 21.2
GiB on a 15.9 GiB card, and no pair on the roster fits.
`OLLAMA_MAX_LOADED_MODELS` stays at 1 and the two quants are a swap pair. **The
swap cost is not measured for these tags**: the only load times in the record
are the KV probe's 6.6 s and 30.6 s, on different quants, through a direct
`llama-server` rather than Ollama. They set the order of magnitude — seconds,
rising sharply when the allocator works near the ceiling — and phase 2
measures the real figure. Until then a batch drains one quant before it
touches the other, and `keep_alive: 0` ends it.

## 4. The stream shape

**One resident quant, one Ollama slot, an external interactive-first queue,
and a batch lane that runs only while the card is idle.** Ollama's scheduler
is FIFO and offers no priority, so the priority lives outside it: the queue
stops admitting batch work the moment an interactive request arrives, and a
third request waits rather than being dropped. That external queue needs its
own size, deadline and cancellation rules; `OLLAMA_MAX_QUEUE` bounds Ollama's
internal queue only and is a backstop, not the mechanism.

Two further shapes are on the map and neither is v1.

**Two real slots on the desktop, by direct `llama-server`.** The vendored
`llama-server.exe` — which the KV probe already drives with Ollama stopped and
drained — has a `--parallel` flag and is the only route to two sequences on
this model. The arithmetic in section 1 says 48k + 48k budgets to fit. It is
phase 6 and it is gated on its own measurement, because Ollama's guard exists
for a reason and a hybrid model's per-sequence recurrent state is where that
reason lives.

**A second host: cachy, the CachyOS box.** A Luna probe of 2026-09-06 found a
GTX 1080 Ti with 11,264 MiB, of which 1,829 MiB is held by its Plasma session
and Firefox, leaving 9,435 MiB free; a Ryzen 5 5600X with 15 GiB of RAM;
Ollama 0.33.3 already installed and running as a service with `ollama-cuda` in
the repos and no llama.cpp package; sleep targets masked; and 484 GB/s of
memory bandwidth against the 5080's 960, so roughly half the decode ceiling
and less in practice on a Pascal card. Three corrections to that probe's own
figures, and they change the answer:

- **With the desktop session logged in, nothing on the roster fits.** The
  probe budgeted a 9 GB artifact; the smallest tag on the roster is IQ2_M at
  10,369 MiB of weights, against 9,435 MiB free. So cachy is a **headless-only**
  option, not a dual-desktop one.
- **Logged out it is roughly 16k to 20k of context, not 24k to 32k.** About
  11,060 MiB free less 10,369 MiB of weights leaves about 690 MiB, which at
  34 MiB per 1k is about 20k tokens before compute buffers.
- **q8_0 KV is Windows-only managed state today.** `OLLAMA_KV_CACHE_TYPE` and
  `OLLAMA_FLASH_ATTENTION` are set in `windows_ollama_environment` and nowhere
  else; the shared `ollama` role's unit sets neither, and cachy runs Arch's
  own unit. Unmanaged, cachy's KV defaults to f16 at twice the rate and flash
  attention is off, which would cut that 20k to about 10k. Managing both on
  Linux is a prerequisite for this option, and whether ggml's flash-attention
  path is worth having on Pascal at all is untested here.

So cachy is a candidate for **the overnight batch lane with the small quant at
a short context, headless**, and for nothing else: not the quality quant, not
the interactive lane, and not a second fast inference host. It is attractive
for one reason the desktop cannot match — it is not the owner's machine, so it
has no contention problem — and that is the whole of its case. Nothing has
been decided about it and nothing on it has been touched.

## 5. The capability envelope

From the v7 evidence and nothing else: **mean pass probability 0.887, pooled
0.898 with Wilson 95% [0.822, 0.944] over 98 trials, and a confidently-wrong
rate of 0.031 [0.010, 0.086]**. The bands are reported separately and never
merged. The calibration prompts occupied 4k to 17k tokens, 7 to 27% of a 64k
window, so material on disk is not context occupancy and the tested range is
much narrower than the window.

Three failure shapes are routed around rather than mitigated.

- **Long serial state** is the one shape that has separated this model from
  frontier arms: on the dropped `q09` candidate, four reference arms scored
  12/12 and the workhorse 1 of 3 with two confident wrong answers. That is one
  deliberately hard candidate, later dropped for a material shortcut, so it is
  a routing caution about a shape and not a rate for a class of work.
- **Large output** times out: 31,552 output tokens over 36 turns hit the 900 s
  cap. Anything approaching 30k output tokens is out of scope and long
  artifacts are staged.
- **Near-window input** is a risk the v7 record does not measure, because its
  prompts never approached the window. The `stop=length` events in the 48k
  cell are *output* length stops, not input truncation. The cap in section 6
  is therefore a precaution, not a measured boundary.

## 6. The routing rule

Caps are on the **total context**, not on input and output separately: an
input cap plus an output cap that together exceed the tag's `num_ctx` is not a
cap at all. For `q27-Q2_K-48k` the 49,152-token window carries the system
prompt, the tools, the input and the reserved output, so the working budget is
about **36k of input with 8k reserved for output**; for `q27-IQ2_M-96k` at
98,304 it is about **80k of input with 8k reserved**, and the 96k rung is for
reading rather than reasoning. As one sentence for `CLAUDE.md`:

> Bounded read-only drafting — summaries, extractions, contradiction checks,
> first-pass reviews and idle batches — may go to `pi-run`'s `local` family
> when its health check and the owner's availability signal are both true,
> within the tag's total-context budget and with the source retained and a
> paid family as the fail-closed fallback; nothing that writes, decides,
> deploys, carries a secret or is the last reader of anything goes there.

## 7. The ranked uses

Thirteen candidate uses were ranked in the research report by displaced plan
cost over risk. **No per-task cost figure exists.** `scripts/plan-usage.py`
reports aggregate pressure on four plans and no page itemises a workload, so
every "displaced per week" is unknown and **the ranking below is a judgement
about volume against consequence, not a measurement**. Building the ledger
that would replace it is phase 1's job.

The three to do first:

1. **Summarising worker run transcripts and final answers for a manager.**
   Batch, source retained. Every worker run in the three-layer pattern of
   `pi-slb-plan-v0.2.0.md` produces one, the manager layer reads all of them,
   and the cost of a wrong emphasis is a re-read against a transcript that is
   still there. Highest judged volume, lowest consequence.
2. **Contradiction and staleness checks across org pages.** Batch for sweeps,
   interactive for adjudication. Squarely inside the tested prompt range, the
   output is a candidate list a human adjudicates, and the work is currently
   unbudgeted because nobody wants to spend a plan on it — which is the
   clearest case of the local model doing work that otherwise does not happen.
3. **Handoff and changelog drafting from git history.** Interactive. Every
   claim in the output is verifiable line by line against the commits, so an
   invented change is caught by the same check that reads it.

Mechanical worker tasks rank next and are deliberately not in the first three:
they change files, so the confidently-wrong tail costs an edit rather than a
re-read. First-pass review as a fourth review family is the highest-value and
highest-risk candidate — a false approval — so it is phase 5 and never the
last reader. The research report ranked an idle overnight batch queue first;
that is the lane rather than a use, and it is section 4 and phase 3 here.

## 8. The integration surface

pi already talks to arbitrary OpenAI-compatible endpoints and Ollama serves
one at `/v1/`. The provider entry is the `zai` entry's shape — `baseUrl`,
`api`, a model list with `contextWindow` and zero costs — and the model ids
are the tags. What is not free is the guard layer:

- `skills/pi-run/scripts/pi-run` and `skills/agent-runtime/scripts/agent-supervisor`
  both restrict the resolved provider to `openrouter` and `zai` and raise on
  anything else, and the supervisor re-checks independently of the wrapper by
  design. **A `local` family is therefore a change to both programs in
  ansible-slb**, never a hand edit under `~/.pi`. Note the shape of the
  existing check: an unrecognised *prefix* is not rejected, it is silently
  treated as a bare OpenRouter model id, so the local branch has to be an
  explicit prefix and not a fall-through.
- Only `max_price` is applied per provider. The `zdr` and `data_collection`
  checks on the managed OpenRouter block run unconditionally, before provider
  resolution, so `zai` is not exempt from them and neither would `local` be.
  What the local branch needs is a `max_price` exemption and a pin check of
  its own modelled on `check_zai_pin`: the base URL, the API shape, and that
  **no secret is handed to it** — pi's custom-provider format still wants a
  placeholder `apiKey`, which the endpoint ignores, and the wrapper's existing
  stripping of every other provider's key from pi's environment is what makes
  "no secret" enforceable.
- Everything else stays: the `AGENT_RUN_DEPTH` nesting guard, the run
  directory and its lifecycle, `--timeout` and `--idle`, and the model name in
  the manifest so a local run is never mistaken for a paid one in accounting.

**Nothing can reach the desktop's Ollama today.** `Get-NetTCPConnection` on
the desktop shows 11434 listening on `127.0.0.1` and nothing else, and
`windows_ollama_environment` sets `OLLAMA_KV_CACHE_TYPE`,
`OLLAMA_FLASH_ATTENTION` and `OLLAMA_MODELS` and no bind. From WSL,
`127.0.0.1:11434` answers with an empty model list — that is WSL's own systemd
Ollama, the D6-35 fork the bench campaign already nearly lost a quant sweep
to. The research run reached the desktop only through a temporary ssh forward.
So v1 must choose deliberately between a tailnet-scoped bind, a supervised
tunnel, and running pi on Windows; that is section 13's first question.

The desktop's Ollama is **not version-pinned by ansible and self-updates**:
`ollama_version` governs the tarball hosts only and Windows takes the winget
package at `upgrade: false` because the tray app is the server. The desktop is
on 0.33.3 while the pinned lane is on 0.32.15, and `group_vars/all/vars.yml`
says in terms that this skew is expected rather than drift. It does mean a
plan resting on the scheduler's behaviour rests on a component that moves
without a converge.

Six environment variables the shape and the safety rules want, none of them
managed today: `OLLAMA_NUM_PARALLEL`, `OLLAMA_MAX_LOADED_MODELS`,
`OLLAMA_KEEP_ALIVE`, `OLLAMA_MAX_QUEUE`, `OLLAMA_GPU_OVERHEAD` and
`OLLAMA_NO_CLOUD`. `OLLAMA_GPU_OVERHEAD`, with `LLAMA_ARG_FIT_TARGET`, is what
can hold the fair-weather headroom mechanically instead of by convention.
`OLLAMA_NO_CLOUD` is a **requirement, not a nicety**: a family called "local"
that can silently reach Ollama's cloud inference or its web search is not
local, and the whole no-secret argument rests on the request staying on the
tailnet.

## 9. The fallback and safety contract

The plan names this contract because v1 has no meaning without it; the build
decides how.

- **Fail closed.** A health check that fails, is stale, or says the owner is
  busy means "local unavailable" and the work goes to the paid family. The
  default when anything is unknown is the paid family, never the local one.
- **Pre-dispatch and mid-request are different.** Before dispatch the router
  chooses once and records which family it chose. After dispatch a local
  failure or timeout is reported to the caller as a failure with the partial
  answer discarded; **the router does not silently re-issue to a paid family**,
  because a duplicate paid call that nobody asked for is exactly the cost this
  project exists to avoid. Re-issuing is the manager's decision, not the
  router's.
- **The external queue owns its own bounds** — size, per-job deadline,
  cancellation on interactive arrival, and what happens to a job the owner's
  return evicts.
- **No secret reaches an unauthenticated endpoint.** A concrete pre-dispatch
  check, not a rule in prose: the material a local job is handed is checked
  for key, token and vault content before it leaves, and a job that fails the
  check goes to the paid family rather than being redacted silently.

## 10. Risks and operating rules

- **The owner's card comes first, and availability is signalled rather than
  inferred.** Ollama answering is not consent. A small managed health record —
  available, owner busy or idle, model loaded, last successful check — is what
  the router reads. Reserve headroom mechanically with `OLLAMA_GPU_OVERHEAD`
  rather than trusting the queue to behave.
- **The desktop sleeps.** Nothing auto-wakes it and nothing retries forever.
- **The server runs elevated in session 0** and the ordinary user cannot stop
  it (`local-quants-2026-09-05.md`). Unloading is `keep_alive: 0` through the
  API; stopping is ansible's elevated WinRM path; ad-hoc process killing is
  neither, and the standing rule about `llama-server` sharing an image name
  with Ollama applies to phase 6.
- **The endpoint has no authentication, so the network is the boundary.**
  Tailnet only, firewall-scoped, never a public bind, never a guessed `100.x`
  literal in configuration.
- **q8_0 is the owner's decision and it is not free.** `kv-64k-2026-09-06.md`
  found no measurable quality gain over q4_0 at 64k — two fields in 128 — at a
  cost of about 960 MiB of VRAM, about 24 s of extra load time, and one cell
  (UDQ3KXL at 64k) that was unusable at q8_0 and fine at q4_0. This plan
  prices q8_0 exactly, as instructed, and records that the headroom in section
  1 and the context in section 3 would both be roughly doubled at q4_0. It is
  also **per-server global state, not per-model and not per-request**, so it
  cannot be varied per lane.
- **The confidently-wrong tail is the design constraint, not a caveat.** 3.1%
  is roughly one confident wrong answer in every thirty-two. Source-linked
  drafts, a retained original, a human or paid reader for anything
  consequential, and never the sole authority for a deployment, security,
  financial, destructive or policy decision.
- **Accounting replaces token cost with time.** Request count, wall seconds,
  queue seconds, model-load seconds, GPU seconds, resident model and context,
  fallback count, and reviewed error count. Plan relief is only real if the
  local wall cost and the owner's contention are visible beside it, and a
  `plan-usage.py` delta is evidence rather than the figure.

## 11. Phased sequence

1. **Reachability, the ledger, and one shadow summary.** Decide and build the
   route to the desktop's Ollama, add the health record and the accounting
   ledger, and run one real worker transcript through the local model while a
   paid reference answer is kept. Success: reachable from WSL and the devbox
   by MagicDNS name, an accurate available-or-busy signal, a source-linked
   summary its manager accepts, and the first wall, load and GPU seconds
   recorded.
2. **The `local` family, read-only shadow lane, and the missing measurements.**
   The `pi-run` and supervisor branch with its pin check and exemption. Measure
   what section 3 could not: Q2_K's resident size and tok/s at 48k, and the
   real Ollama swap cost between the two tags. Ten transcript summaries and ten
   contradiction checks in shadow beside the paid answer. Success: at least 9
   of 10 usable in each set, no leaked prompt, a p50/p95 wall and queue record,
   and both missing numbers on the page as a dated addendum.
3. **The idle-only batch lane.** The external queue with its own bounds and
   the owner-busy, sleeping, stale-health and interactive-arrival rules. Fifty
   low-risk jobs while the card is idle. Success: no interactive starvation,
   no model swap inside a same-quant batch, a measured queue-wait
   distribution, and a fall in paid fallbacks with no rise in reviewed errors.
4. **Handoff and changelog drafting.** The first use whose output is checked
   mechanically against its source. Success: every claim traceable to a
   commit, and a lower end-of-session cost on the Claude plan.
5. **Reviews and long reads.** The fourth review family and the third blind
   bench reader, within the total-context budget, never deciding alone.
   Success: agreement with an independent reader and no rise in false
   approvals.
6. **Only then, two real slots.** Direct `llama-server --parallel 2`, Ollama
   stopped and drained, 48k + 48k, on an idle card. Success: two
   simultaneously active slots, resident under 14.2 GB, aggregate throughput
   and p95 latency better than the serialized baseline, and quality on the v7
   suite not below the one-slot number. Anything short of all four keeps one
   slot and the external queue. Whether cachy joins as a headless batch host
   is a separate decision at this point, not before.

## 12. Decisions taken from the owner, 2026-09-06

Two quants are kept, one for short context and one for long. The KV cache
stays at **q8_0**, the `kv-64k-2026-09-06.md` recommendation of `q4_0`
notwithstanding, and this plan prices q8_0 exactly rather than re-arguing it.
Two concurrent streams is the target shape. The goal is to save paid-plan
cost. The local model's capability is settled and the question is integration,
not capability. `/mnt/d/local-llm-bench` is read-only to this work, the GPU
was touched exactly once by the bounded two-request probe, and cachy was not
touched at all.

## 13. Open questions for the owner — all answered 2026-09-06

1. **Answered — ruling 3 in the addendum: option 1, the tailnet bind**, with
   the Windows firewall rule scoped to the Tailscale interface rather than to
   an address. The ssh tunnel and pi-native-on-Windows are dropped. A
   decision, not an instruction to converge.
2. **Answered — ruling 1 in the addendum: yes, one slot**, and the two-slot
   `llama-server` work of phase 6 is dropped rather than deferred. The
   scheduler clamp in section 1 is upstream policy on `main` and nothing in
   v1 waits on it changing.
3. **Answered — ruling 2 in the addendum: no.** `q27-Q2_K-48k` is superseded
   by **`q27-mrIQ3M` at 32k** as the short-context quality quant, on the
   grounds that it is the only 3-bit quant with a q8_0 measurement on this
   card that completed. `q27-UDQ3KXL` is recommended against on two counts
   and `q27-UDIQ3S` remains unscored.
4. **Answered — ruling 5 in the addendum: accepted at one in thirty-two** for
   every draft-with-source use, so all three v1 uses stand. Two-quant
   agreement becomes a phase 2 upgrade rather than a v1 requirement.
5. **Answered — ruling 4 in the addendum: automatic, with a manual override
   either way.** Desktop locked or idle for a few minutes by default, read
   before every local run, and the model unloaded with `keep_alive: 0` when
   the flag flips to mine rather than merely denied new work.
6. **Answered — ruling 6 in the addendum: no, deferred.** Cachy is out of v1
   and revisited only after phase 5, headless and batch-only if ever.
7. **Answered — closed independently in `pending.md` on 2026-09-06.** The KV
   cache stays at q8_0; this plan and that page now agree.

## 14. Review

Blind Luna review (`wr-wsl-20260906T233546Z-d1b43272b6a7`), verdict REVISE,
twelve findings. Taken: the total-context budget replacing separate input and
output caps, which was a real error; Q2_K's figures being its 64k rung and its
48k rung unmeasured; the two-slot fit stated as a budget rather than a result;
"at any setting" scoped to Ollama with `llama-server --parallel` named; the
48k `stop=length` events being output stops and not near-window truncation;
`q09` as one dropped candidate rather than a rate; the guard wording, the
silent OpenRouter fall-through, `zdr`/`data_collection` being unconditional
and only `max_price` per provider, and "no secret" rather than "no key"; the
untraced load times; "no *established* quality tier" rather than "no measured
result"; the ranking marked as judgement; and the whole of section 9, which
did not exist before.

Not taken, with reasons. The reviewer called the future-dated names on the v7
and KV reports an impossible chronology and blocking; those are the fleet's
own records, cited as such by `pending.md` and `models.md`, and reconciling
them is not this plan's to do — it is reported upward as an anomaly instead.
The reviewer argued for seventeen KV-cached layers rather than sixteen,
counting the `nextn` block; both independent cross-checks in section 1 favour
sixteen, and the reviewer's own objection that runtime overhead is included in
the measured delta cuts the wrong way, since overhead would raise the measured
figure rather than lower it below both predictions. The seventeen-layer case
is recorded in section 1 as the number a speculative-decoding runtime would
make correct.

## Addendum, 2026-09-06 evening: two owner rulings and the 3-bit answer

*Two rulings from the owner and the answer to question 3. Sections 4 and 11
above are left as they stand and are read through this addendum.*

### Ruling 1: the two-slot shape is abandoned

**v1 is one slot, and it is not a stepping stone to two.** Phase 6 — direct
`llama-server --parallel 2` at 48k + 48k — is dropped, and with it the whole
two-slot line of argument in section 4. The arithmetic in section 1 that says
two 48k slots would budget to fit inside the 96k envelope stands as a recorded
fact about the card and is no longer a plan for anything. Cachy remains a
separate later decision on its own terms, unchanged by this. The phased
sequence is therefore phases 1 to 5, and phase 5 is the end of v1.

### Ruling 3: the desktop's Ollama binds to the tailnet

**Question 1 is answered: option 1.** Ollama binds to the desktop's tailnet
address, with a Windows firewall inbound rule for 11434 **scoped to the
Tailscale interface, never to an address** — an address moves on
re-registration and an interface does not — and both the bind and the rule are
ansible-managed state in the existing `windows_ollama_environment` and the
`windows_tailscale` firewall work, not host edits. The supervised ssh tunnel
and running pi natively on Windows are both dropped.

This is **a decision, not an instruction to implement**. Nothing is converged
and no rule is created until the owner clears phase 1. When it is, the
endpoint is unauthenticated and the interface scope is the entire security
boundary, so the operating rules in section 10 and the no-secret check in
section 9 are load-bearing rather than advisory from that moment on.

**Ruling 1 also answers question 2**: one slot is the accepted shape for v1.

### Ruling 4: the availability signal is automatic with a manual override

**Question 5 is answered.** The default signal is **automatic**: the desktop
session locked, or idle for a few minutes, means the card is available. It is
published as a **flag a dispatcher reads before every local run** — every run,
not once per batch — and a **manual override forces it either way**, "mine
until cleared" or "available", overriding whatever the automatic signal says
until the owner clears it.

**When the flag flips to mine, the model is unloaded with `keep_alive: 0`, not
merely denied new work.** Denying new work leaves 13 GB resident on the card
the owner has just sat down at, which is most of the problem the signal exists
to solve. Unloading is about two seconds (`org/README.md`).

Four consequences the build has to carry, none of them a change to this
ruling:

- **The guarantee is bounded, not instant.** `keep_alive: 0` takes effect
  after the request in flight completes, so the owner's worst case is one
  in-flight generation. The batch lane's per-job deadline in section 9 is what
  bounds that tail, and it is now load-bearing rather than housekeeping: a job
  with no deadline is a job that can hold the card after the owner has asked
  for it back.
- **Flapping is expensive and needs hysteresis on both sides.** Unload costs
  two seconds; the reload costs seconds to tens of seconds (section 3, and
  still unmeasured for the chosen tags). "Idle for a few minutes" supplies the
  dwell going one way; a matching dwell is needed before the flag returns to
  available, or a single keystroke during a batch costs two model loads.
- **Whatever publishes the flag runs in the owner's desktop session, not as
  the service.** Ollama runs elevated in session 0 and cannot see the desktop
  session's lock or idle state; a publisher that runs where the server runs
  will read the wrong thing or nothing.
- **"Mine until cleared" is durable state.** It survives a sleep, a reboot and
  a converge, or it is not what it says; and the dispatcher treats a flag it
  cannot read at all as "mine", per the fail-closed rule in section 9.

### Ruling 5: the confidently-wrong tail is accepted at one in thirty-two

**Question 4 is answered: accepted, for every draft-with-source use.** All
three v1 uses in section 7 stand as written — transcript summaries,
contradiction and staleness checks, handoff and changelog drafting — and v1
does not shrink to the mechanically checked two. The acceptance is explicitly
conditional on the shape of the work and not on the model: it holds where the
source is retained beside the draft and a human reads both, which is what
"draft-with-source" means, and it does not extend to anything that writes,
decides or is the last reader of something.

**Two-quant agreement is demoted from a v1 property to a phase 2 upgrade.**
Section 3 argued the second quant's value partly as a cross-family
disagreement detector against IQ2_M. That is no longer a v1 requirement:
running two quants over the same job doubles the wall cost and costs a model
swap, and the accepted tail does not need it. It becomes an upgrade to attempt
in phase 2 **once `q27-mrIQ3M-32k` has been created, measured and calibrated**,
and it is judged there on whether the disagreements it surfaces are actually
the confidently-wrong cases. Until then the second quant is simply the
short-context quality quant and nothing more.

### Ruling 6: cachy is deferred out of v1

**Question 6 is answered: no.** Cachy does not join v1 and is revisited only
after phase 5 — **headless and batch-only if ever**, on the terms in section
4: nothing on the roster fits with its Plasma session up, its headless ceiling
is about 16k to 20k of context, and `OLLAMA_KV_CACHE_TYPE` and
`OLLAMA_FLASH_ATTENTION` would have to be managed on Linux first, which they
are not. Section 4's cachy analysis stays on the page as the record of what
was measured and why the answer was no, not as a plan. Nothing on cachy has
been touched.

### Section 13 is now fully answered

All seven questions are closed: 1 by ruling 3, 2 by ruling 1, 3 by ruling 2,
4 by ruling 5, 5 by ruling 4, 6 by ruling 6, and 7 independently in
`pending.md` on 2026-09-06. **v1 is settled and no question blocks it.** What
remains before anything is built is the owner clearing phase 1; nothing here
is an instruction to converge.

**Phase 1 is gated, 2026-09-06.** Nothing starts until **pi-slb v0.2.0 is
released and converged**, so the `local` family arrives into the new runtime
rather than being retrofitted to it (`pi-slb-plan-v0.2.0.md`). No reachability
work, no bind, no firewall rule, no health record and no ledger before then.

**v1, in one paragraph.** One Ollama slot on the desktop, because the
scheduler clamps this architecture to one and no setting changes that.
`q27-IQ2_M-96k` for long-context reading and `q27-mrIQ3M` at 32k, a tag that
does not exist yet, as the short-context quality quant. The endpoint bound to
the tailnet with a firewall rule scoped to the Tailscale interface, managed by
ansible. Availability automatic on desktop lock or idle, overridable both ways
by hand, with the model unloaded rather than merely idled when the owner wants
the card. A `local` family in `pi-run` alone, fail-closed to a paid family,
carrying three draft-with-source uses at an accepted one-in-thirty-two
confidently-wrong rate. Phases 1 to 5; no phase 6, and no cachy.

### Ruling 2: the second quant is chosen for quality at short context

The second quant was picked under the org's 48k viability floor
(`org/README.md`: a local quant is viable only if it runs 48k without
degradation). The owner now wants a genuine **short-context quality quant**
and asks whether a well-tested 3-bit quant fits at **32k** under q8_0 KV.
This section answers that and **supersedes the choice of `q27-Q2_K-48k` in
section 3**; IQ2_M at 96k as the long-context quant is unchanged.

**One blob per quant, not per tag.** Every context tag of a quant resolves to
the same weight blob and differs only in a Modelfile `num_ctx`, verified for
all thirteen 3-bit tags. So the weight column below is per quant, and **no
3-bit tag at 32k exists on disk today** — the shortest 3-bit rung is
UDQ3KXL's 24k and everything else starts at 48k. Creating a 32k rung is an
`ollama create` from a one-line Modelfile, not a download.

#### Every 3-bit quant on disk, at q8_0 KV

Weights are exact blob sizes from `D:\ollama\models\blobs` in GiB. KV is
34.0 MiB per 1,024 tokens from section 1. The sums are weights plus KV and
exclude the compute buffers, which is why they are checked against the
measurement in the last column. The line is the 14.2 GiB fair-weather resident
threshold of `local-llm-bench-desaturation-2026-09-05.md`, and every figure in
this table is in GiB, because the measured 13.27 for IQ2_M at 96k matches
weights-plus-KV in GiB and not in decimal GB.

| quant | weights GiB | +24k | +32k | +40k | +48k | margin at 32k | measured resident |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| UD-IQ3_S (`q27-UDIQ3S-*`) | 11.21 | 12.01 | **12.28** | 12.54 | 12.81 | 1.92 | 13.03 at 64k, unscored |
| IQ3_XXS (`q27-IQ3_XXS-*`) | 11.76 | 12.56 | **12.82** | 13.09 | 13.35 | 1.38 | 13.07 at 48k |
| mrIQ3M (`q27-mrIQ3M-*`) | 11.89 | 12.69 | **12.95** | 13.22 | 13.49 | 1.25 | 13.25 at 48k |
| UDQ3KXL (`q27-UDQ3KXL-*`) | 12.24 | 13.04 | **13.31** | 13.57 | 13.84 | 0.89 | 13.45 at 48k |
| IQ3_XS (`q27-IQ3_XS-*`) | 12.41 | 13.21 | **13.48** | 13.74 | 14.01 | 0.72 | 14.34 at 48k, marginal |

**Every 3-bit quant on the roster fits at 32k, at 40k and at 48k under q8_0 by
this budget.** That is a weaker statement than it looks, and the last column
is why.

#### Where the model and the measurement disagree

Compared at each quant's own measured rung, the budget runs **0.24 to 0.39 GiB
above** the placement figure for four of the five — the model is conservative,
which is the direction to want — and **0.33 GiB below** for IQ3_XS, which is
the only quant where the budget flatters the model and the only one the
placement table calls *marginal* at 14.34. Two instruments, and they are not
the same instrument: the placement figures are Ollama's `/api/ps` resident
size, and the desaturation page records whole-device `nvidia-smi` running
about 1.8 GB higher again.

The third instrument is the one that matters most here and it is a failure.
`kv-64k-2026-09-06.md` ran two of these quants at q8_0 directly on
`llama-server` at 64k: **mrIQ3M loaded to 15,303 MiB and completed** at
93.75% (120 of 128 fields, Wilson [0.882, 0.968]), 28 of 32 all-four needles,
43.3 gen tok/s — but took 30.6 s to load. **UDQ3KXL loaded to 15,315 MiB on a
16,303 MiB card and then answered 1 of 32 needles before the 600 s safety cap**,
`partial: true` — the predicted WDDM spill arriving as a throughput collapse
rather than an out-of-memory error. The same quant at q4_0 scored the best
result of the whole sweep. **So the one hard measurement of a 3-bit quant at
q8_0 on this card at 64k is one pass with a stressed allocator and one
outright failure**, and dropping 64k to 32k returns 1,088 MiB to both.

#### The recommendation

**`q27-mrIQ3M` at 32k (32,768), created as a new tag from the existing blob.**

- **It is the only 3-bit quant with a direct q8_0 measurement on this card that
  completed.** 93.75% on the 32-needle probe at 64k, one full rung above the
  rung recommended here, with depth buckets 90.9 / 95.0 / 95.5 early, middle
  and late — the probe was not saturated, so it had room to show a failure and
  did not.
- **v6 placement: 48k, 13.25 GB resident, 42.7 gen tok/s** — on the curve, and
  the second-lightest well-tested 3-bit weight at 11.89 GiB.
- **1.25 GiB of margin at 32k**, and the budget is conservative by 0.24 GiB
  against its own measured rung.
- **v7: not in the calibration trio**, so it carries no v7 pass-probability
  number. That is the honest gap and phase 2 closes it.

**Against UDQ3KXL, which is the quant the word "quality" reaches for**: it
carries two independent strikes and both are about exactly the properties this
plan cares about. It is the quant whose q8_0 cell **failed outright** at 64k in
the KV run, and it is the quant measured **25% confidently wrong against
IQ2_M's 4%** on the thirty-three shared finalist cells of v6. Its one-trial
20/20 on the v7 calibration does not outweigh either, and the campaign itself
refuses to treat a single trial as a task property. Recommend against.

**IQ3_XXS is the alternative** if speed is worth more than the q8_0 evidence:
47.0 tok/s is the fastest on the entire roster, 1.38 GiB of margin at 32k, and
13.07 GB resident at 48k — but it has no q8_0-specific measurement and no v7
number at all. **IQ3_XS is excluded** by its own placement row: 26.7 tok/s,
about half the roster, and 14.34 GB at 48k, over the line. **UD-IQ3_S has the
best margin of all at 1.92 GiB and is excluded as unscored**, per the owner's
own definition of well-tested; if a quant is ever to be promoted out of
"unscored" it is the obvious candidate, and that is a separate decision.

#### Is the margin safe?

**Yes at 32k, with one qualification stated plainly.** 1.25 GiB under the
14.2 GiB fair-weather line, on a budget that has been conservative by 0.24 GiB
against this quant's own measured rung, is a margin worth calling safe — and
32k is 1,088 MiB below the 64k rung at which this quant was measured to load
and run correctly at q8_0. The qualification is that **the number is derived
and not yet measured**: no 3-bit tag at 32k exists, so nothing has ever read
`/api/ps` for this configuration. Creating `q27-mrIQ3M-32k` and reading its
resident size once, with the desktop session up, is a five-minute check and it
is the first item of phase 2. Until it is done the margin is arithmetic.

**Amended viability ruling, `org/README.md`, 2026-09-06.** The org's ruling now
names two quant roles with two floors — the long-context quant viable only at
48k or better with no degradation, the short-context quality quant viable only
at 24k with no degradation and a measured margin under the fair-weather line,
and a quant fitting neither role a candidate for removal. `q27-IQ2_M-96k`
clears the long-context floor and `q27-mrIQ3M` at 32k clears the 24k floor
with 1.25 GiB of margin, so the plan and the map agree; the paragraph below is
the reason the short-context role has a lower floor than the long-context one.

What is **not** safe is 48k at q8_0 for any 3-bit quant on this card without a
fresh measurement. The budget says all five fit; the KV run says one of the two
actually tried at q8_0 collapsed a rung above that, and the org's own 48k
viability floor was set from `/api/ps` figures rather than from device memory.
The short-context quant is short for this reason as well as for the
capability reason in section 1.

### Ruling 7: the goal is real work on local GPUs, not cost saving

- **2026-09-06, late evening.** The owner restated what this plan is for.
  Getting real work out of the local GPUs is an org goal in its own right,
  whether or not it saves money yet. Measured tonight, Luna on the ChatGPT
  plan costs under a quarter of a cent per million blended tokens, below the
  5080's electricity alone, so the local model does not undercut the default
  worker and is not expected to. Its case is capability and readiness: models
  that do real work on a 16 GB consumer card did not exist until recently,
  the curve points at Luna-grade work locally soon, and the integration
  surface built here (the `local` family, the endpoint, the availability
  signal, the ledger) is what lets a better model arrive as a tag swap. The
  plan's success measures are read accordingly: work landed locally and the
  Claude and Z.ai windows relieved, not dollars against Codex.
- **2026-09-07, on paper.** A GLM project manager with one Luna researcher and
  one Luna checker re-ran the cachy question from evidence only, no pull, no
  load, no benchmark (`org/evidence/cachy-quants-report.md`).
  Three findings change the picture in section 4. First, the Ollama on cachy
  is CPU-only: `/usr/lib/ollama` holds no CUDA or Vulkan backend, and the
  packaged `ollama-cuda` on Arch ships `cuda_v13` alone, which cannot drive a
  Pascal card; the only packaged GPU path is `ollama-vulkan`, on which flash
  attention and therefore q8_0 KV are unverified and likely unavailable.
  Upstream's own tarball may carry `cuda_v12` but its inventory was not found.
  Second, with a 512 MiB runtime margin the 27B IQ2_M fits headless at about
  5k of q8_0 KV context, 20k with no margin, and nothing at all with the
  Plasma session up; every other roster quant is out on weights alone. Third,
  the only things that fit with room are community distills of the family at
  2B, 4B and 9B, which reach the native 262k window on this card and have no
  fleet evidence of any kind. Coherence below 24k is unmeasured even for
  IQ2_M. Derived decode class for IQ2_M is about 26 tok/s against 41.9 on the
  5080; prefill falls further, Pascal having no tensor cores. The first smoke
  test, when allowed, needs a backend decision first, then a copied blob from
  `D:\ollama\models\blobs` over the tailnet and one `/api/ps` read to settle
  the margin. Ruling 6 stands: cachy is deferred, and on this evidence it is
  a candidate for small distills rather than for the 27B.

## Addendum, 2026-09-11: endpoint and provider integration landed

The pre-build statements at the top of this dated plan describe the state on
2026-09-06 and remain historical. The endpoint/provider portion is now live:
`slbh` commit `95eb7ef` adds the keyless `local` provider, the real model
`local/q27-IQ2_M-96k`, and the default leaf selection. `ansible-slb` commits
`bdf63aa`, `fe000fc`, `4adef6f`, `041be72` and `242724d` bind the Windows
Ollama server to its current Tailscale address, scope TCP/11434 to the
Tailscale interface, keep the server in an Ansible-managed SYSTEM scheduled
task, and verify the live catalog.

From devbox, MagicDNS resolved the desktop, the kernel selected `tailscale0`,
and `/v1/models` returned `q27-IQ2_M-96k:latest`. `/api/show` confirmed
`num_ctx 98304`; `/api/ps` was empty after the check. The full evidence is
`local-ollama-route-2026-09-11.md`.

This does not claim the later availability signal, queue, accounting, shadow
comparison or review phases complete. The plan's original pi-slb v0.2.0 gate
is superseded by the shipped slbh application, while the remaining phases are
future work rather than a reason to describe the live route as absent.
