# m08 rebuild report

Candidate dir to create: `ollama-bench/results/v7/authoring/cand-glm/m08-main-glm/`
Spec file to create: `ollama-bench/results/v7/authoring/r5/specs/m08_main_glm.py`

Initial `ls ollama-bench/results/v7/authoring/cand-glm/` (m08-main-glm absent):

```
m01-main-glm
m02-cheap-glm
m03-main-glm
m04-main-glm
m05-main-glm
m06-main-glm
m07-main-glm
m08-cheap-glm
m09-main-glm
m10-main-glm
n02-main-glm
n06-main-glm
n08-cheap-glm
p01-main-glm
p04-main-glm
q09-main-glm
```

## Outcome

Built the new `m08-main-glm` candidate from scratch as a mode-9, main-band serial-state task. A solver must read a complete procedure, follow a shuffled predecessor-linked 20-row log, retrieve two figures from each of 20 independently framed folios, and apply each non-commutative modular transition to the prior state. The candidate is 35,485 material tokens in 97 seed files; the build declares 15 load-bearing paths across 15 hops and a full 35,490-token sweep (100.0%).

Changed only the pinned spec, candidate, and this report. The spec writes the procedure, sealed log, decision record, and 20 folios; the builder writes the prompt, reference, grader, selfcheck, notes, and manifest. The reference has six ordered keys and ten subchecks. No GPU, network, commit, or q09/shelved-m08 artifact was used.

## Four build-time closures

1. Rule containment: `_procedure_replay(ctx) == _replay(ordered, figures)` is asserted after parsing the procedure's opening figure and modulus and rereading the log/folios. This proves the handbook-only replay produces the exact key sequence; the assembler record contains no answer figures.

2. Order and arithmetic: for every log field, `position mod k` for `k=2..8`, and every affine position map `((a*i+b) % 20)` for `a=-64..64`, the reconstructed order is asserted unequal to the predecessor walk. A position-sorted replay with the link column effectively ignored is asserted to miss. Every row is perturbed and must change the final state; every contiguous segment of length at least two is shuffled three times (identity shuffles are rotated) and must miss its exit state.

3. Frame separation: every figure line is asserted nonterminal; all 40 top offsets and EOF offsets are unique (`max(...count) <= 1`), shared stripped value-line frames occur at most four times, and every pair of labels has no shared two-character fragment. The independently drawn charge/reserve sequences are asserted to have no repeating step cycle.

4. Harvest/rung-0: all 40 declared per-folio figures are reread from real folios and are distinct; `sweep_paths()` covers the entire seed; output-key vocabulary is distributed through three ordinary generated docs so no key is a one-file shortcut. The final harvest assertions are H1=0.000, H2=0.000, H3=0.050, H4=0.000.

## Adversarial sweeps

The final manual battery captured at most 1/40 figures on any fixed line position (line 9 was the maximum), 0/40 by the best single prompt-vocabulary substring at the C=2 window, 0/40 by the roster-label regex, and 0/40 by `tail -n1` over all folios. The checker’s wider C=5 substring capture was 2/40; its shared-frame capture was 0/40. All 40 values were four-digit literals, so a bare digit-shape grep is reported by the checker but is not a gated vocabulary shortcut.

## Final checker results

Every command below exited 0 under both `python3` and `/mnt/c/Users/slb/scoop/apps/python/current/python.exe`:

- `selfcheck.py`: all 10 cases pass; reference 10/10 `correct`, untouched 1/10 `visibly_failed`, two plausible arithmetic errors 9/10 `confidently_wrong`, reversed order 3/10 `confidently_wrong`, and all five whitespace/line-ending probes 10/10 `correct`.
- `probe_candidate.py`: `CLEAN`; reference 10/10 `correct`, empty 1/10 `visibly_failed`, all perturbations 10/10 `correct`.
- `probe_idempotence.py`: 10/10 `correct` on both grades; `ok`, 1 candidate, 0 not idempotent.
- `check_rung0.py`: `rung 0 clear`; no prompt word reaches every load-bearing file.
- `check_index_leak.py`: 0 candidates leak a decisive constant (the spec declares none).
- `check_load_bearing.py`: 15 paths, 15 hops, 4,869 load-bearing tokens, 13.7% floor coverage; declaration complete.
- `check_harvest.py --verbose`: `harvest clear`, H1=0.000/H2=0.000/H3=0.050/H4=0.000, 40 distinct values over 40 units, 0 derived, 0 indistinct.
- `check_tools.py --verbose`: `tools clear`; all 17 generated tools run with no arguments, print 0 scored values and 0/40 declared unit values.

The same checker verdicts held under the Windows interpreter; its UTF-8 output replaces a few punctuation glyphs in diagnostics but all exit codes and verdicts are unchanged. The stock `r5/build.py m08-main-glm` filters legacy `q*` modules and built zero candidates, so the equivalent shared `common.build` call was used directly for the pinned `m08_main_glm.py` spec; the resulting candidate is the one validated above.
