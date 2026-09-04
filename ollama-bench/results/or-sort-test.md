# OpenRouter provider sort: "price" vs "balanced" (default)

Date: 2026-09-03. Key usage before test: **USD 18.356737381**, after: see below.
Policy held constant in every config tested: `zdr: true`, `data_collection: "deny"`.

## 1. Endpoint tables

`GET /api/v1/models/<id>/endpoints`. Note: the endpoints API does **not** expose
a ZDR flag per endpoint, and `?zdr=true` / `?data_collection=deny` query params
are ignored (identical lists returned). ZDR eligibility was therefore inferred
from which provider OpenRouter actually returned when `provider.zdr=true` was
sent on a real request. `status: -2` = deranked/unavailable at listing time.

### qwen/qwen3.8-27b (USD per 1M tokens)

| provider | quant | ctx | in | out | status |
|---|---|---|---|---|---|
| Parasail | fp8 | 262144 | 0.25 | 2.20 | 0 |
| Reka | fp8 | 262144 | 0.25 | 2.55 | 0 |
| Chutes | fp8 | 262144 | 0.32 | 2.50 | 0 |
| AkashML | fp8 | 262144 | 0.32 | 2.50 | 0 |
| Ionstream | fp8 | 262144 | 0.35 | 2.55 | 0 |
| Phala | unknown | 262144 | 0.40 | 3.00 | 0 |
| CoreWeave | fp8 | 262144 | 0.40 | 3.00 | 0 |
| Novita | unknown | 1000000 | 0.42 | 3.00 | 0 |
| Alibaba | unknown | 1000000 | 0.425 | 2.55 | 0 |
| Io Net | fp8 | 65536 | 0.432 | 3.06 | 0 |
| Cloudflare | unknown | 262144 | 0.45 | 3.20 | -2 |
| Venice | fp8 | 262144 | 0.45 | 3.20 | 0 |

### z-ai/glm-5.3-flash (USD per 1M tokens)

| provider | quant | ctx | in | out | status |
|---|---|---|---|---|---|
| GMICloud | fp8 | 1048576 | 0.075 | 0.25 | -2 |
| Novita | fp8 | 1048576 | 0.075 | 0.25 | 0 |
| DeepInfra | fp8 | 1048576 | 0.075 | 0.25 | 0 |
| Z.AI | fp8 | 1048576 | 0.075 | 0.25 | -2 |
| Wafer | unknown | 1048576 | 0.10 | 0.35 | -2 |
| Morph | fp8 | 1048576 | 0.13 | 0.45 | 0 |
| Makora | unknown | 1048576 | 0.14 | 0.47 | 0 |
| Modal | fp8 | 1048576 | 0.15 | 0.50 | 0 |
| Sail Research / StreamLake / NextBit / Fireworks / Phala / Friendli / SiliconFlow / DigitalOcean / Together / Reka / Parasail / BaseTen / Venice / Io Net / Cloudflare | mixed | 262144-1310720 | 0.15 | 0.50 | mixed |

## 2. Which provider each sort actually selects

Four 5-token probes via `chat/completions` with `provider: {zdr, data_collection, [sort]}`,
then `GET /api/v1/generation?id=`:

| model | sort | provider chosen | probe cost USD |
|---|---|---|---|
| qwen/qwen3.8-27b | price | **Parasail** (0.25 / 2.20) | 0.0000245 |
| qwen/qwen3.8-27b | balanced (no sort) | **Reka** (0.25 / 2.55) | 0.0000263 |
| z-ai/glm-5.3-flash | price | **Z.AI** (0.075 / 0.25) | 0.0000023 |
| z-ai/glm-5.3-flash | balanced (no sort) | **Z.AI** (0.075 / 0.25) | 0.0000023 |

## 3. Test agent dirs

`results/pi-agent-sort-price` and `results/pi-agent-sort-balanced` are copies of
`results/pi-agent-v4` with the qwen `only`/`allow_fallbacks` pin removed and
only the sort key changed:

price:
```json
"openRouterRouting": { "data_collection": "deny", "sort": "price", "zdr": true }
```
balanced:
```json
"openRouterRouting": { "data_collection": "deny", "zdr": true }
```

## 4. Bench runs (tasks-v3, medium thinking, 1 trial, qwen/qwen3.8-27b)

| task | sort | provider | pass | SCORE | wall s | in tok | out tok | est cost USD |
|---|---|---|---|---|---|---|---|---|
| 27_semver | price | Parasail | PASS | 29/29 (1.00) | 73.6 | 62538 | 4949 | ~0.019 |
| 34_tmplfix | price | Parasail | PASS | 36/36 (1.00) | 442.7 | 1342637 | 28792 | ~0.286 |
| 27_semver | balanced | Reka | PASS | 29/29 (1.00) | 27.4 | 22725 | 1690 | ~0.006 |
| 34_tmplfix | balanced | Reka | PASS | 36/36 (1.00) | 291.3 | 325279 | 15629 | ~0.066 |

No generation id is recoverable from pibench's event stream, so per-task costs are
estimates (endpoint price x pibench tokens, scaled to the measured per-run total);
the per-run totals below are exact key-usage deltas.

Key usage checkpoints (USD):

| checkpoint | usage |
|---|---|
| start of test | 18.356737381 |
| before price run | 18.369522781 |
| after price run | 18.673981831 |
| before balanced run | 18.677156631 |
| after balanced run | 18.749258681 |
| after 2 GLM pi-run probes | 18.762626631 |

- price bench run (both tasks): **USD 0.304459**
- balanced bench run (both tasks): **USD 0.072102**
- GLM pi-run probe (price agent dir): USD 0.013368; balanced probe registered USD 0.000000 (prompt cache hit / not billed)
- **total spend by this test: USD 0.406159 (final settled key usage 18.762895881)**

Important: the 4.2x cost gap between the two bench runs is **agent-loop variance,
not price** - the price run happened to take 43 vs 19 turns on 34_tmplfix and burned
~2x the output tokens and ~4x the input tokens. Per token, Parasail (what `price`
picks) is strictly cheaper than Reka (what `balanced` picks): same input rate,
14% cheaper output. Accuracy was identical (4/4 PASS, full SCORE on every run).

## 5. Decision

- **qwen/qwen3.8-27b: `sort: "price"`, and keep the Parasail pin in the bench dirs.**
  `price` resolves to Parasail, the cheapest ZDR fp8 endpoint; `balanced` resolves to
  Reka at a 14% higher completion rate with no accuracy gain. The explicit
  `only: ["parasail"] / allow_fallbacks: false` pin stays in the bench agent dirs
  because a bench wants a fixed, cheapest endpoint for comparability.
- **z-ai/glm-5.3-flash: `sort: "price"`.** Both sorts land on Z.AI at 0.075/0.25 today,
  so cost is a wash right now, but `price` guarantees the 0.075/0.25 tier
  (Novita/DeepInfra/GMICloud) rather than letting the default drift to the crowded
  0.15/0.50 tier, which is 2x the price for the same fp8 1M-context model.

## 6. Routing block for the fleet default (~/.pi/agent/models.json via ansible-slb)

```json
{
  "providers": {
    "openrouter": {
      "compat": {
        "openRouterRouting": {
          "data_collection": "deny",
          "sort": "price",
          "zdr": true
        },
        "sendSessionAffinityHeaders": true,
        "sessionAffinityFormat": "openrouter"
      },
      "modelOverrides": {
        "z-ai/glm-5.3-flash": {
          "compat": {
            "openRouterRouting": { "ignore": ["reka", "io-net"] }
          },
          "contextWindow": 1048576
        }
      }
    }
  }
}
```

(The `ignore` list still matters: Reka and Io Net only serve 262k context for GLM.)

## 7. Files changed

- `results/pi-agent-v3/models.json`: `sort` "throughput" -> "price" (qwen Parasail pin kept)
- `results/pi-agent-v4/models.json`: `sort` "throughput" -> "price" (qwen Parasail pin kept)
- new: `results/pi-agent-sort-price/`, `results/pi-agent-sort-balanced/` (test dirs)
- new: `results/sort-price.json|.md`, `results/sort-balanced.json|.md` (run records)

Nothing under `~/.pi`, `~/.claude` or `ansible-slb` was touched.
