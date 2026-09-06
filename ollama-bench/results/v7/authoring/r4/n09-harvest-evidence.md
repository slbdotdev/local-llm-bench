# The grep-harvest check measured on n09-cheap-luna, the one row of nineteen that passed the coverage gate

Built through the round-four pipeline as `p99-cheap-luna` (n09's spec unchanged but for SLOT and
CORPUS_SEED, plus the `harvest_units()` declaration round four requires: one entry per stage,
the stage's reserved capacity, in the stage's own component document). Round three's checks all
pass on it; the new one does not. This is the instrument validated against real material rather
than against the synthetic pair in `r4/probe_harvest.py`.

```
p99-cheap-luna       rung 0 clear
    - prompt declares the pointer config/manifest.json (named_in_prompt)
    - release_stages: 6 file(s) contain every member of that value (README.md, config/manifest.json, docs/architecture.md) — a note, not a failure
    - narrowest covering prompt word 'record' hits 23 of 39 files; a word must hit at most 20 to count as a shortcut
    - 39 distinctive prompt words tested over 39 seed files

1 candidate(s), 0 failing plan section 2.1

p99-cheap-luna       3 PROBLEM(S)   H1=1.000 H2=1.000 H3=1.000
    - C=0: worst token 'capacity' harvests 8/8 (attestation, checkpoint, cursor, digest, dispatch, envelope); roster harvests 0/8
    - C=2: worst token 'capacity' harvests 8/8 (attestation, checkpoint, cursor, digest, dispatch, envelope); roster harvests 8/8
    - C=5: worst token 'capacity' harvests 8/8 (attestation, checkpoint, cursor, digest, dispatch, envelope); roster harvests 8/8
    - P2 = 1.000 at C=2 on stage + window_s — the best two-token union, reported and not gated
    - 8 unit(s), 8 scored, 0 derived (value never stated in seed/), 0 indistinct; 77 giveaway tokens over 39 files
    ! H1 = 1.000 at C=2 on the token 'capacity', the limit is 0.250 — one grep on a token the prompt or its declared pointers give away reaches that fraction of the per-unit values
    ! H2 = 1.000 at C=2, the limit is 0.400 — one grep alternating over the roster's own unit names reaches that fraction
    ! H3 = 1.000 at C=5 on the token 'capacity', the limit is 0.333 — the same attack with a five-line window

1 candidate(s), 1 failing the grep-harvest check (H1 < 0.250 and H2 < 0.400 at C=2, H3 < 0.333 at C=5)
```
