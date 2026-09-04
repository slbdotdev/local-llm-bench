# Haiku difficulty probe (tasks-v3 hard subset + tasks-v4 52-61)

Takers: Claude Code subagents on Haiku, 3 trials per task, 45 runs. Zero OpenRouter spend.
Grading is identical to `pibench.run_pi`: hidden `test.py` copied in as `_hidden_test.py`,
`python _hidden_test.py` with cwd=sandbox, `PYTHONUTF8=1 PYTHONIOENCODING=utf-8`, 60 s timeout
with process-tree kill; pass iff rc==0 and "PASS" in stdout; score = last `SCORE n/m` as a fraction.

fp8 columns are qwen/qwen3.8-27b from existing files only: low = `results/v3-low.json`,
medium = `results/v3-hard-ref-medium.json`. Tasks 52-61 have no fp8 runs in
`results/v4-ref-medium.json` (it only covers 40-47) — **not yet smoked**.

| task | Haiku pass k/3 | Haiku mean SCORE | fp8 low pass | fp8 low SCORE | fp8 medium pass | fp8 medium SCORE |
|---|---|---|---|---|---|---|
| 34_tmplfix | 0/3 | 0.954 | 2/3 | 0.880 | 2/2 | 1.000 |
| 27_semver | 2/3 | 0.989 | 5/6 | 0.994 | n/a | n/a |
| 31_stackvm | 3/3 | 1.000 | 5/6 | 0.996 | n/a | n/a |
| 32_wirefmt | 1/3 | 0.646 | 3/3 | 1.000 | 1/2 | 0.985 |
| 35_ledger | 1/3 | 0.981 | 3/3 | 1.000 | 1/2 | 0.986 |
| 52_reengine | 0/3 | 0.677 | n/a | n/a | n/a | n/a |
| 53_gitattr | 0/3 | 0.800 | n/a | n/a | n/a | n/a |
| 54_sedlite | 0/3 | 0.611 | n/a | n/a | n/a | n/a |
| 55_minilang | 0/3 | 0.796 | n/a | n/a | n/a | n/a |
| 56_tmpl | 0/3 | 0.460 | n/a | n/a | n/a | n/a |
| 57_stateful | 0/3 | 0.308 | n/a | n/a | n/a | n/a |
| 58_bencode | 3/3 | 1.000 | n/a | n/a | n/a | n/a |
| 59_uri | 1/3 | 0.889 | n/a | n/a | n/a | n/a |
| 60_numlit | 0/3 | 0.611 | n/a | n/a | n/a | n/a |
| 61_codecs | 0/3 | 0.867 | n/a | n/a | n/a | n/a |

Haiku overall: 11/45 pass (24%), mean SCORE 0.773.

## Haiku failure modes (from grader tails)

- **34_tmplfix** (0/3, 0.954): all three miss `type errors from for iterables`; two also miss `mismatched branch tags`. Fixes the obvious visible bugs, misses the error-path bugs.
- **27_semver** (2/3): one run failed only `parse leading zeros in numeric prerelease`.
- **31_stackvm** (3/3): clean.
- **32_wirefmt** (1/3, 0.646): t2 missed the encode type-error and the `delim` error kind; t3 was killed by the memory guard at 8.5 GB (runaway/quadratic decoder) and scored 0.
- **35_ledger** (1/3, 0.981): two runs raise `TypeError` when `Entry` is built with 6 named fields and `dest` defaulting to None — a constructor-signature miss.
- **52_reengine** (0/3, 0.677): fails nearly every randomised differential bucket (character classes, escapes, anchors/boundaries, groups/alternation, bounded quantifiers) plus `nothing_to_repeat` kind and capture semantics across repetitions.
- **53_gitattr** (0/3, 0.800): passes crafted examples, fails all randomised buckets (mixed files, macro-heavy, class-heavy patterns, files with invalid lines); one also gets `a**b == a*b` wrong.
- **54_sedlite** (0/3, 0.611): worst v3/v4 spread. Ranges (numeric, regex, `+N`), negation with `!`, `a`/`i` queued text, `d`/`p`/`q` cycle interactions, and randomised malformed-script error kinds all fail.
- **55_minilang** (0/3, 0.796): error-kind exactness and parse-before-runtime error precedence, plus all randomised error-kind/mutation buckets. One run also tripped the "does not import ast or use eval/exec/compile" ban check.
- **56_tmpl** (0/3, 0.460): positions and precedence of `unknown_tag`/`unexpected_tag`, statement- and expression-level syntax errors, filter error ordering within one tag, `set` scoping; t3 hung and hit the 60 s grader timeout.
- **57_stateful** (0/3, 0.308): weakest task overall. State-machine legality table, abort/reset/close-drain, sequence wraparound/dup/window bounds, timeout boundary semantics, and corrupt-framing differentials all fail.
- **58_bencode** (3/3): clean.
- **59_uri** (1/3, 0.889): t1 fails all normalize/resolve/error-kind differentials; t3 misses only the `'//'`-path-with-no-authority `/.`-prefix rule.
- **60_numlit** (0/3, 0.611): canonical text for radix ints and floats, `underscore` and `suffix` error kinds, exact-tie rounding under every mode, negative zero; t2 hung into the grader timeout.
- **61_codecs** (0/3, 0.867): base64/base32 padding rules and padding-run lengths, quoted-printable `eol`/`trunc`/`char` kinds and offsets, and the randomised mutation differentials for both.

The pattern is consistent: Haiku gets the happy path right and loses points on exact error
*kinds*, error *positions/offsets*, error *precedence*, and randomised differential buckets —
exactly the parts of these specs that are only stated in prose and never shown in an example.
Three runs (32_wirefmt/t3, 56_tmpl/t3, 60_numlit/t2) were also non-terminating enough to hit
the memory guard or the 60 s grader timeout, which fp8 also does occasionally.

## Verdict

Haiku is a usable proxy for a weaker model: it fails where fp8 fails (34_tmplfix, 32_wirefmt,
35_ledger are exactly the v3 tasks fp8 medium also drops), it fails substantially more often
(11/45 = 24% vs fp8 low's ~87% on the v3 subset), and it fails with a wide partial-credit spread
(mean SCORE 0.773, per-task means from 0.31 to 1.00) rather than collapsing to zero — so
52-61 discriminate rather than floor, and the v4 tasks are hard enough to be worth smoking on fp8.
