# Q2_K_L early-exit question (10:35, control session)

Owner instruction: "If Q2_K_L is broken, early exit. Ask GLM as advisor." The control session decides.

## Facts
- Controlled ranking config: q27-Q2_K_L, num_ctx 32768 (Modelfile), KV q8_0, flash attention, medium thinking,
  pi maxTokens 32768, timeout 1800 s, 7 tasks x 3 trials. Runs so far (results/v4-local-medium.json):

| task | trial | pass | score | wall s | turns | tool calls | in tok | out tok | final text |
|---|---|---|---|---|---|---|---|---|---|
| 52_reengine | 0 | no | 0.0 | 454 | 1 | 0 | 5245 | 24151 | empty |
| 52_reengine | 1 | no | 0.0 | 451 | 1 | 0 | 5244 | 24151 | empty |
| 52_reengine | 2 | no | 0.0 | 452 | 1 | 0 | 5245 | 24151 | empty |
| 55_minilang | 0 | no | 0.19 | 429 | 2 | 1 | 18367 | 22763 | empty |
| 55_minilang | 1 | no | 0.0 | 448 | 1 | 0 | 5887 | 23780 | empty |
| 55_minilang | 2 | no | 0.0 | 448 | 1 | 0 | 5885 | 23780 | empty |
| 56_tmpl | 0 | no | 0.0 | 428 | 1 | 0 | 6970 | 22513 | empty |
| 56_tmpl | 1 | no | 0.0 | 428 | 1 | 0 | 6969 | 22513 | empty |
| 56_tmpl | 2 | running | | | | | | | |

- Ollama server.log for these runs: "stop processing: n_tokens = 29666, truncated = 0" (and 29664, 29482,
  29481): prompt + generation reaches about 29.5k of the 32768 slot and generation stops; no error.
  Generation speed 54 tok/s. The output is all thinking; no visible text, no tool call.
- Outputs are byte-identical across trials of the same task (same out token count to the token), so the
  serving path is deterministic at this config; three trials replicate nothing for single-turn runs.
- The same quant on v3 hard tasks earlier today (1 trial, results/v3-hard-local-medium.json, two of the runs
  under an older 16000 maxTokens cap): 32_wirefmt FAIL 1 turn 16000 out (old cap); 33_spanmap 0.83 with 22
  turns; 34_tmplfix PASS 18 turns; 35_ledger PASS 17 turns; 36_minilang FAIL 2 turns 24224 out. So Q2_K_L
  can work multi-turn with tools; it fails when it thinks past its context on the first turn.
- fp8 reference on the same 52_reengine: trial 0 TIMEOUT 1800 s (34 turns), trial 1 PASS 789 s (69 turns).
  Sonnet 2/3, Haiku 0/3 on 52.
- Remaining for Q2_K_L: 56 t2 (running), 57_stateful, 59_uri, 60_numlit, 61_codecs x 3 = 13 runs, about
  1.6 h at 450 s each if the pattern holds. Then Q3_K_S and Q3_K_M (the latter slow, 15-22 tok/s).
- Mechanism available: killing the pibench python process tree for Q2_K_L makes the wrapper proceed to
  Q3_K_S immediately; pibench resumes losslessly later (skips completed task/trial pairs), so the skipped
  Q2_K_L runs can be filled in afterwards if wanted. Plan file: results/plan-2026-09-03.md.

## Questions for the advisor
1. Is "Q2_K_L thinks past a 32k context on the first turn and returns nothing" a broken quant at this config,
   or a legitimate measured result that the ranking should record as 0?
2. Early exit now, versus finishing the 13 remaining runs: what does each option cost in validity of the
   ranking (all-or-nothing three trials, bootstrap over tasks, paired comparison)?
3. Given deterministic outputs, should local quants run 1 trial instead of 3 (time saved goes to Q3_K_M or an
   at-best-config pass), and what would that do to the fp8 comparison, which is not deterministic?
4. Is there a cheap diagnostic (no ranking change) that distinguishes "quant too damaged to stop thinking" from
   "prompt plus medium thinking overflows 32k for any 27B model", e.g. running one Q2_K_L task at low thinking
   or at 64k ctx as a labelled side probe after the controlled pass?
Answer with numbered recommendations, each with the evidence it rests on, and a one-line verdict first.
