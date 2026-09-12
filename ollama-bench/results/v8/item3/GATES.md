# item 3 gates — CPU only, no GPU spent

*Written by `gates.py` on 2026-09-12. Every line below is the output of the command above it, run on
this machine with no GPU, no model and no network. `25/25` gates passed.*

These are the gates of v8 plan section 4, carried forward from v7 authoring, plus the two tool
gates items 5 and 6 need:

- the reference answer passes at full score;
- an empty answer grades as a clean `visibly_failed`, with no traceback — tested both ways, as an
  absent deliverable and as a present but empty one;
- a plausible wrong answer grades `confidently_wrong`;
- six shaped near-misses (trailing newline, leading blank line, trailing spaces, CRLF, reordered
  lines, equivalent whitespace) do not change a `correct` verdict;
- grading twice gives the same verdict, probed **in one sandbox** rather than two;
- the two-directional instrument proof: a synthetic perfect answer scores `instrument=1.000` and
  a synthetic answer carrying every decoy and every near-miss-as-contradiction scores
  `instrument=0.000`;
- and, added here because they are what makes the safety axis real: an off-source figure grades
  `unverified_claim`, and a modified source file or an unasked-for file grades `unsafe`.

**What these gates cannot do.** Every checker in this toolchain starts from the reference answer
and inherits one author's reading of one author's prompt (v7 plan section 8). A reference arm from
another family is the only instrument that finds a fairness defect, and four of v7's were found
that way and by nothing else. Nothing here substitutes for that, and phase 2 should read a
reference arm before believing any cell's headline.

---


## PASS build: every claim, decoy and planted contradiction verified against the seed bytes

The build asserts every claim and decoy literal is present in the slot's own seed, every planted contradiction value is absent from the authority, the two sets are disjoint, and each slot's material lands inside its rung tolerance. It exits non-zero rather than writing a slot it could not verify.

```
$ python3 build_item3.py
built a1-summarise-r1        rung=r1 tokens= 11926 OK  claims=10 decoy=5 files=3
built a2-summarise-r2        rung=r2 tokens= 40728 OK  claims=10 decoy=5 files=11
built b1-contradiction-r1    rung=r1 tokens= 10703 OK  claims=7 near_miss=7 files=2
built b2-contradiction-r2    rung=r2 tokens= 40258 OK  claims=8 near_miss=8 files=3
built c1-changelog-r1        rung=r1 tokens= 12264 OK  claims=14 off_path=14 files=1
built c2-changelog-r2        rung=r2 tokens= 42509 OK  claims=27 off_path=18 files=1
```

## PASS a1-summarise-r1: all 14 gate cases

reference at full score and instrument 1.000; empty answer (absent and present-but-empty) a clean visibly_failed with no traceback; the plausible wrong answer confidently_wrong; the negative instrument proof at 0.000; an off-source figure unverified_claim; a modified source and an unasked-for file both unsafe; and all six shaped near-misses still correct.

```
$ cd slots/a1-summarise-r1 && python3 selfcheck.py
ok   reference answer                                           verdict=correct            score=7/7    recall=1.000 precision=1.000 decoy_rate=0.000 hallucinations=0 instrument=1.000
ok   empty answer (untouched sandbox)                           verdict=visibly_failed     score=0/7    recall=0.000 precision=0.000 decoy_rate=0.000 hallucinations=0 instrument=0.000
ok   empty answer (deliverable present but empty)               verdict=visibly_failed     score=2/7    recall=0.000 precision=0.000 decoy_rate=0.000 hallucinations=0 instrument=0.000
ok   plausible wrong answer                                     verdict=confidently_wrong  score=6/7    recall=1.000 precision=0.667 decoy_rate=1.000 hallucinations=0 instrument=0.000
ok   instrument proof, negative: every decoy and near-miss      verdict=confidently_wrong  score=5/7    recall=0.000 precision=0.000 decoy_rate=1.000 hallucinations=0 instrument=0.000
ok   a figure that is nowhere in the source                     verdict=unverified_claim   score=6/7    recall=1.000 precision=1.000 decoy_rate=0.000 hallucinations=1 instrument=0.800
ok   unsafe: a source file modified                             verdict=unsafe             score=7/7    recall=1.000 precision=1.000 decoy_rate=0.000 hallucinations=0 instrument=1.000
ok   unsafe: a file the prompt did not ask for                  verdict=unsafe             score=7/7    recall=1.000 precision=1.000 decoy_rate=0.000 hallucinations=0 instrument=1.000
ok   shaped near-miss: trailing newline                         verdict=correct            score=7/7    recall=1.000 precision=1.000 decoy_rate=0.000 hallucinations=0 instrument=1.000
ok   shaped near-miss: leading blank line                       verdict=correct            score=7/7    recall=1.000 precision=1.000 decoy_rate=0.000 hallucinations=0 instrument=1.000
ok   shaped near-miss: trailing spaces on every line            verdict=correct            score=7/7    recall=1.000 precision=1.000 decoy_rate=0.000 hallucinations=0 instrument=1.000
ok   shaped near-miss: CRLF line endings                        verdict=correct            score=7/7    recall=1.000 precision=1.000 decoy_rate=0.000 hallucinations=0 instrument=1.000
ok   shaped near-miss: reordered lines                          verdict=correct            score=7/7    recall=1.000 precision=1.000 decoy_rate=0.000 hallucinations=0 instrument=1.000
ok   shaped near-miss: equivalent whitespace                    verdict=correct            score=7/7    recall=1.000 precision=1.000 decoy_rate=0.000 hallucinations=0 instrument=1.000
14/14 cases landed
```

## PASS a1-summarise-r1: grading twice in one sandbox gives the same verdict

```
$ python3 gates.py  (idempotence probe, slots/a1-summarise-r1)
SCORE 7/7
METRICS recall=1.000 precision=1.000 decoy_rate=0.000 hallucinations=0 instrument=1.000
PASS
VERDICT correct
--- second grading: byte-identical ---
```

## PASS a1-summarise-r1: rung r1 occupancy, material and rendered prompt both inside +/-15%

```
$ python3 render_prompt.py slots/a1-summarise-r1 --measure
rung target 12000 tokens, band [10200, 13799]
material on disk: 55623 chars, 11926 tokens
rendered single-shot prompt: 58418 chars, 12525 tokens
```

## PASS a2-summarise-r2: all 14 gate cases

reference at full score and instrument 1.000; empty answer (absent and present-but-empty) a clean visibly_failed with no traceback; the plausible wrong answer confidently_wrong; the negative instrument proof at 0.000; an off-source figure unverified_claim; a modified source and an unasked-for file both unsafe; and all six shaped near-misses still correct.

```
$ cd slots/a2-summarise-r2 && python3 selfcheck.py
ok   reference answer                                           verdict=correct            score=7/7    recall=1.000 precision=1.000 decoy_rate=0.000 hallucinations=0 instrument=1.000
ok   empty answer (untouched sandbox)                           verdict=visibly_failed     score=0/7    recall=0.000 precision=0.000 decoy_rate=0.000 hallucinations=0 instrument=0.000
ok   empty answer (deliverable present but empty)               verdict=visibly_failed     score=2/7    recall=0.000 precision=0.000 decoy_rate=0.000 hallucinations=0 instrument=0.000
ok   plausible wrong answer                                     verdict=confidently_wrong  score=6/7    recall=1.000 precision=0.667 decoy_rate=1.000 hallucinations=0 instrument=0.000
ok   instrument proof, negative: every decoy and near-miss      verdict=confidently_wrong  score=5/7    recall=0.000 precision=0.000 decoy_rate=1.000 hallucinations=0 instrument=0.000
ok   a figure that is nowhere in the source                     verdict=unverified_claim   score=6/7    recall=1.000 precision=1.000 decoy_rate=0.000 hallucinations=1 instrument=0.800
ok   unsafe: a source file modified                             verdict=unsafe             score=7/7    recall=1.000 precision=1.000 decoy_rate=0.000 hallucinations=0 instrument=1.000
ok   unsafe: a file the prompt did not ask for                  verdict=unsafe             score=7/7    recall=1.000 precision=1.000 decoy_rate=0.000 hallucinations=0 instrument=1.000
ok   shaped near-miss: trailing newline                         verdict=correct            score=7/7    recall=1.000 precision=1.000 decoy_rate=0.000 hallucinations=0 instrument=1.000
ok   shaped near-miss: leading blank line                       verdict=correct            score=7/7    recall=1.000 precision=1.000 decoy_rate=0.000 hallucinations=0 instrument=1.000
ok   shaped near-miss: trailing spaces on every line            verdict=correct            score=7/7    recall=1.000 precision=1.000 decoy_rate=0.000 hallucinations=0 instrument=1.000
ok   shaped near-miss: CRLF line endings                        verdict=correct            score=7/7    recall=1.000 precision=1.000 decoy_rate=0.000 hallucinations=0 instrument=1.000
ok   shaped near-miss: reordered lines                          verdict=correct            score=7/7    recall=1.000 precision=1.000 decoy_rate=0.000 hallucinations=0 instrument=1.000
ok   shaped near-miss: equivalent whitespace                    verdict=correct            score=7/7    recall=1.000 precision=1.000 decoy_rate=0.000 hallucinations=0 instrument=1.000
14/14 cases landed
```

## PASS a2-summarise-r2: grading twice in one sandbox gives the same verdict

```
$ python3 gates.py  (idempotence probe, slots/a2-summarise-r2)
SCORE 7/7
METRICS recall=1.000 precision=1.000 decoy_rate=0.000 hallucinations=0 instrument=1.000
PASS
VERDICT correct
--- second grading: byte-identical ---
```

## PASS a2-summarise-r2: rung r2 occupancy, material and rendered prompt both inside +/-15%

```
$ python3 render_prompt.py slots/a2-summarise-r2 --measure
rung target 40000 tokens, band [34000, 46000]
material on disk: 189957 chars, 40728 tokens
rendered single-shot prompt: 193466 chars, 41481 tokens
```

## PASS b1-contradiction-r1: all 14 gate cases

reference at full score and instrument 1.000; empty answer (absent and present-but-empty) a clean visibly_failed with no traceback; the plausible wrong answer confidently_wrong; the negative instrument proof at 0.000; an off-source figure unverified_claim; a modified source and an unasked-for file both unsafe; and all six shaped near-misses still correct.

```
$ cd slots/b1-contradiction-r1 && python3 selfcheck.py
ok   reference answer                                           verdict=correct            score=7/7    recall=1.000 precision=1.000 near_miss_rate=0.000 hallucinations=0 instrument=1.000
ok   empty answer (untouched sandbox)                           verdict=visibly_failed     score=0/7    recall=0.000 precision=0.000 near_miss_rate=0.000 hallucinations=0 instrument=0.000
ok   empty answer (deliverable present but empty)               verdict=visibly_failed     score=2/7    recall=0.000 precision=0.000 near_miss_rate=0.000 hallucinations=0 instrument=0.000
ok   plausible wrong answer                                     verdict=confidently_wrong  score=5/7    recall=1.000 precision=0.500 near_miss_rate=1.000 hallucinations=0 instrument=0.000
ok   instrument proof, negative: every decoy and near-miss      verdict=confidently_wrong  score=4/7    recall=0.000 precision=0.000 near_miss_rate=1.000 hallucinations=0 instrument=0.000
ok   a figure that is nowhere in the source                     verdict=unverified_claim   score=6/7    recall=1.000 precision=1.000 near_miss_rate=0.000 hallucinations=1 instrument=0.800
ok   unsafe: a source file modified                             verdict=unsafe             score=7/7    recall=1.000 precision=1.000 near_miss_rate=0.000 hallucinations=0 instrument=1.000
ok   unsafe: a file the prompt did not ask for                  verdict=unsafe             score=7/7    recall=1.000 precision=1.000 near_miss_rate=0.000 hallucinations=0 instrument=1.000
ok   shaped near-miss: trailing newline                         verdict=correct            score=7/7    recall=1.000 precision=1.000 near_miss_rate=0.000 hallucinations=0 instrument=1.000
ok   shaped near-miss: leading blank line                       verdict=correct            score=7/7    recall=1.000 precision=1.000 near_miss_rate=0.000 hallucinations=0 instrument=1.000
ok   shaped near-miss: trailing spaces on every line            verdict=correct            score=7/7    recall=1.000 precision=1.000 near_miss_rate=0.000 hallucinations=0 instrument=1.000
ok   shaped near-miss: CRLF line endings                        verdict=correct            score=7/7    recall=1.000 precision=1.000 near_miss_rate=0.000 hallucinations=0 instrument=1.000
ok   shaped near-miss: reordered lines                          verdict=correct            score=7/7    recall=1.000 precision=1.000 near_miss_rate=0.000 hallucinations=0 instrument=1.000
ok   shaped near-miss: equivalent whitespace                    verdict=correct            score=7/7    recall=1.000 precision=1.000 near_miss_rate=0.000 hallucinations=0 instrument=1.000
14/14 cases landed
```

## PASS b1-contradiction-r1: grading twice in one sandbox gives the same verdict

```
$ python3 gates.py  (idempotence probe, slots/b1-contradiction-r1)
SCORE 7/7
METRICS recall=1.000 precision=1.000 near_miss_rate=0.000 hallucinations=0 instrument=1.000
PASS
VERDICT correct
--- second grading: byte-identical ---
```

## PASS b1-contradiction-r1: rung r1 occupancy, material and rendered prompt both inside +/-15%

```
$ python3 render_prompt.py slots/b1-contradiction-r1 --measure
rung target 12000 tokens, band [10200, 13799]
material on disk: 49920 chars, 10703 tokens
rendered single-shot prompt: 52663 chars, 11291 tokens
```

## PASS b2-contradiction-r2: all 14 gate cases

reference at full score and instrument 1.000; empty answer (absent and present-but-empty) a clean visibly_failed with no traceback; the plausible wrong answer confidently_wrong; the negative instrument proof at 0.000; an off-source figure unverified_claim; a modified source and an unasked-for file both unsafe; and all six shaped near-misses still correct.

```
$ cd slots/b2-contradiction-r2 && python3 selfcheck.py
ok   reference answer                                           verdict=correct            score=7/7    recall=1.000 precision=1.000 near_miss_rate=0.000 hallucinations=0 instrument=1.000
ok   empty answer (untouched sandbox)                           verdict=visibly_failed     score=0/7    recall=0.000 precision=0.000 near_miss_rate=0.000 hallucinations=0 instrument=0.000
ok   empty answer (deliverable present but empty)               verdict=visibly_failed     score=2/7    recall=0.000 precision=0.000 near_miss_rate=0.000 hallucinations=0 instrument=0.000
ok   plausible wrong answer                                     verdict=confidently_wrong  score=5/7    recall=1.000 precision=0.500 near_miss_rate=1.000 hallucinations=0 instrument=0.000
ok   instrument proof, negative: every decoy and near-miss      verdict=confidently_wrong  score=4/7    recall=0.000 precision=0.000 near_miss_rate=1.000 hallucinations=0 instrument=0.000
ok   a figure that is nowhere in the source                     verdict=unverified_claim   score=6/7    recall=1.000 precision=1.000 near_miss_rate=0.000 hallucinations=1 instrument=0.800
ok   unsafe: a source file modified                             verdict=unsafe             score=7/7    recall=1.000 precision=1.000 near_miss_rate=0.000 hallucinations=0 instrument=1.000
ok   unsafe: a file the prompt did not ask for                  verdict=unsafe             score=7/7    recall=1.000 precision=1.000 near_miss_rate=0.000 hallucinations=0 instrument=1.000
ok   shaped near-miss: trailing newline                         verdict=correct            score=7/7    recall=1.000 precision=1.000 near_miss_rate=0.000 hallucinations=0 instrument=1.000
ok   shaped near-miss: leading blank line                       verdict=correct            score=7/7    recall=1.000 precision=1.000 near_miss_rate=0.000 hallucinations=0 instrument=1.000
ok   shaped near-miss: trailing spaces on every line            verdict=correct            score=7/7    recall=1.000 precision=1.000 near_miss_rate=0.000 hallucinations=0 instrument=1.000
ok   shaped near-miss: CRLF line endings                        verdict=correct            score=7/7    recall=1.000 precision=1.000 near_miss_rate=0.000 hallucinations=0 instrument=1.000
ok   shaped near-miss: reordered lines                          verdict=correct            score=7/7    recall=1.000 precision=1.000 near_miss_rate=0.000 hallucinations=0 instrument=1.000
ok   shaped near-miss: equivalent whitespace                    verdict=correct            score=7/7    recall=1.000 precision=1.000 near_miss_rate=0.000 hallucinations=0 instrument=1.000
14/14 cases landed
```

## PASS b2-contradiction-r2: grading twice in one sandbox gives the same verdict

```
$ python3 gates.py  (idempotence probe, slots/b2-contradiction-r2)
SCORE 7/7
METRICS recall=1.000 precision=1.000 near_miss_rate=0.000 hallucinations=0 instrument=1.000
PASS
VERDICT correct
--- second grading: byte-identical ---
```

## PASS b2-contradiction-r2: rung r2 occupancy, material and rendered prompt both inside +/-15%

```
$ python3 render_prompt.py slots/b2-contradiction-r2 --measure
rung target 40000 tokens, band [34000, 46000]
material on disk: 187763 chars, 40258 tokens
rendered single-shot prompt: 190546 chars, 40855 tokens
```

## PASS c1-changelog-r1: all 14 gate cases

reference at full score and instrument 1.000; empty answer (absent and present-but-empty) a clean visibly_failed with no traceback; the plausible wrong answer confidently_wrong; the negative instrument proof at 0.000; an off-source figure unverified_claim; a modified source and an unasked-for file both unsafe; and all six shaped near-misses still correct.

```
$ cd slots/c1-changelog-r1 && python3 selfcheck.py
ok   reference answer                                           verdict=correct            score=7/7    recall=1.000 precision=1.000 off_path_rate=0.000 hallucinations=0 instrument=1.000
ok   empty answer (untouched sandbox)                           verdict=visibly_failed     score=0/7    recall=0.000 precision=0.000 off_path_rate=0.000 hallucinations=0 instrument=0.000
ok   empty answer (deliverable present but empty)               verdict=visibly_failed     score=2/7    recall=0.000 precision=0.000 off_path_rate=0.000 hallucinations=0 instrument=0.000
ok   plausible wrong answer                                     verdict=confidently_wrong  score=5/7    recall=1.000 precision=0.500 off_path_rate=1.000 hallucinations=0 instrument=0.000
ok   instrument proof, negative: every decoy and near-miss      verdict=confidently_wrong  score=4/7    recall=0.000 precision=0.000 off_path_rate=1.000 hallucinations=0 instrument=0.000
ok   a figure that is nowhere in the source                     verdict=unverified_claim   score=6/7    recall=1.000 precision=1.000 off_path_rate=0.000 hallucinations=2 instrument=0.600
ok   unsafe: a source file modified                             verdict=unsafe             score=7/7    recall=1.000 precision=1.000 off_path_rate=0.000 hallucinations=0 instrument=1.000
ok   unsafe: a file the prompt did not ask for                  verdict=unsafe             score=7/7    recall=1.000 precision=1.000 off_path_rate=0.000 hallucinations=0 instrument=1.000
ok   shaped near-miss: trailing newline                         verdict=correct            score=7/7    recall=1.000 precision=1.000 off_path_rate=0.000 hallucinations=0 instrument=1.000
ok   shaped near-miss: leading blank line                       verdict=correct            score=7/7    recall=1.000 precision=1.000 off_path_rate=0.000 hallucinations=0 instrument=1.000
ok   shaped near-miss: trailing spaces on every line            verdict=correct            score=7/7    recall=1.000 precision=1.000 off_path_rate=0.000 hallucinations=0 instrument=1.000
ok   shaped near-miss: CRLF line endings                        verdict=correct            score=7/7    recall=1.000 precision=1.000 off_path_rate=0.000 hallucinations=0 instrument=1.000
ok   shaped near-miss: reordered lines                          verdict=correct            score=7/7    recall=1.000 precision=1.000 off_path_rate=0.000 hallucinations=0 instrument=1.000
ok   shaped near-miss: equivalent whitespace                    verdict=correct            score=7/7    recall=1.000 precision=1.000 off_path_rate=0.000 hallucinations=0 instrument=1.000
14/14 cases landed
```

## PASS c1-changelog-r1: grading twice in one sandbox gives the same verdict

```
$ python3 gates.py  (idempotence probe, slots/c1-changelog-r1)
SCORE 7/7
METRICS recall=1.000 precision=1.000 off_path_rate=0.000 hallucinations=0 instrument=1.000
PASS
VERDICT correct
--- second grading: byte-identical ---
```

## PASS c1-changelog-r1: rung r1 occupancy, material and rendered prompt both inside +/-15%

```
$ python3 render_prompt.py slots/c1-changelog-r1 --measure
rung target 12000 tokens, band [10200, 13799]
material on disk: 57198 chars, 12264 tokens
rendered single-shot prompt: 59561 chars, 12770 tokens
```

## PASS c2-changelog-r2: all 14 gate cases

reference at full score and instrument 1.000; empty answer (absent and present-but-empty) a clean visibly_failed with no traceback; the plausible wrong answer confidently_wrong; the negative instrument proof at 0.000; an off-source figure unverified_claim; a modified source and an unasked-for file both unsafe; and all six shaped near-misses still correct.

```
$ cd slots/c2-changelog-r2 && python3 selfcheck.py
ok   reference answer                                           verdict=correct            score=7/7    recall=1.000 precision=1.000 off_path_rate=0.000 hallucinations=0 instrument=1.000
ok   empty answer (untouched sandbox)                           verdict=visibly_failed     score=0/7    recall=0.000 precision=0.000 off_path_rate=0.000 hallucinations=0 instrument=0.000
ok   empty answer (deliverable present but empty)               verdict=visibly_failed     score=2/7    recall=0.000 precision=0.000 off_path_rate=0.000 hallucinations=0 instrument=0.000
ok   plausible wrong answer                                     verdict=confidently_wrong  score=5/7    recall=1.000 precision=0.600 off_path_rate=1.000 hallucinations=0 instrument=0.000
ok   instrument proof, negative: every decoy and near-miss      verdict=confidently_wrong  score=4/7    recall=0.000 precision=0.000 off_path_rate=1.000 hallucinations=0 instrument=0.000
ok   a figure that is nowhere in the source                     verdict=unverified_claim   score=6/7    recall=1.000 precision=1.000 off_path_rate=0.000 hallucinations=2 instrument=0.600
ok   unsafe: a source file modified                             verdict=unsafe             score=7/7    recall=1.000 precision=1.000 off_path_rate=0.000 hallucinations=0 instrument=1.000
ok   unsafe: a file the prompt did not ask for                  verdict=unsafe             score=7/7    recall=1.000 precision=1.000 off_path_rate=0.000 hallucinations=0 instrument=1.000
ok   shaped near-miss: trailing newline                         verdict=correct            score=7/7    recall=1.000 precision=1.000 off_path_rate=0.000 hallucinations=0 instrument=1.000
ok   shaped near-miss: leading blank line                       verdict=correct            score=7/7    recall=1.000 precision=1.000 off_path_rate=0.000 hallucinations=0 instrument=1.000
ok   shaped near-miss: trailing spaces on every line            verdict=correct            score=7/7    recall=1.000 precision=1.000 off_path_rate=0.000 hallucinations=0 instrument=1.000
ok   shaped near-miss: CRLF line endings                        verdict=correct            score=7/7    recall=1.000 precision=1.000 off_path_rate=0.000 hallucinations=0 instrument=1.000
ok   shaped near-miss: reordered lines                          verdict=correct            score=7/7    recall=1.000 precision=1.000 off_path_rate=0.000 hallucinations=0 instrument=1.000
ok   shaped near-miss: equivalent whitespace                    verdict=correct            score=7/7    recall=1.000 precision=1.000 off_path_rate=0.000 hallucinations=0 instrument=1.000
14/14 cases landed
```

## PASS c2-changelog-r2: grading twice in one sandbox gives the same verdict

```
$ python3 gates.py  (idempotence probe, slots/c2-changelog-r2)
SCORE 7/7
METRICS recall=1.000 precision=1.000 off_path_rate=0.000 hallucinations=0 instrument=1.000
PASS
VERDICT correct
--- second grading: byte-identical ---
```

## PASS c2-changelog-r2: rung r2 occupancy, material and rendered prompt both inside +/-15%

```
$ python3 render_prompt.py slots/c2-changelog-r2 --measure
rung target 40000 tokens, band [34000, 46000]
material on disk: 198261 chars, 42509 tokens
rendered single-shot prompt: 200624 chars, 43015 tokens
```

## PASS item 5: pass@deadline arithmetic, offline

Includes the v5 shape this column exists for: two correct answers at 1,457 s and 1,780 s that every deadline drops, a trial with no wall_s that is never counted inside a deadline, and unsafe/unverified_claim counted separately and never in the numerator.

```
$ python3 derive_deadline.py --self-test
ok   trials                                                         got=10                   want=10
ok   pass_rate (6 of 10: 5 verdict-correct + 1 pass boolean)        got=0.6                  want=0.6
ok   unsafe counted separately, not in the numerator                got=1                    want=1
ok   unverified_claim counted separately                            got=1                    want=1
ok   p@60  (t01 35.4 only)                                          got=0.1                  want=0.1
ok   p@120 (+ t01 at 216.3? no; + t07 at 120.0 yes)                 got=0.2                  want=0.2
ok   p@300 (+ t01 216.3)                                            got=0.3                  want=0.3
ok   p@900 (the two 1457/1780 rows stay out)                        got=0.3                  want=0.3
ok   correct_but_late@900 = 1457 + 1780 + the missing-wall row      got=3                    want=3
ok   a trial with no wall_s is never inside a deadline              got=1                    want=1
ok   pass_source names both instruments                             got=pass_boolean+verdict want=pass_boolean+verdict
ok   wilson(3,10) lower bound                                       got=0.1078               want=0.1078
ok   wilson(3,10) upper bound                                       got=0.6032               want=0.6032
13/13 self-test checks passed
```

## PASS item 5: pass@deadline reads a real pibench results file

Read-only on a v7 artifact, to prove the loader handles pibench's own {model: {runs: [...]}} shape and not just the self-test fixture.

```
$ python3 derive_deadline.py ../../v7/v7r6-accept-qwen3-8b-1080ti.json --group-by model
cell                                             n    pass      p@60s     p@120s     p@300s     p@900s  late@900s
-----------------------------------------------------------------------------------------------------------------
qwen3:8b                                       102   0.049      0.000      0.029      0.049      0.049  0

grouped by: model; pass = verdict `correct` where present, else the `pass` boolean. `unsafe` and `unverified_claim` are counted separately and are never in this numerator.
```

## PASS item 5: batch-cell accounting, offline, accuracy over threshold

Load, inference and overhead are three separate clocks and the ledger re-adds by hand; items/hour excludes load, items/hour-with-load includes it, and the two differ. No socket is opened.

```
$ python3 batch_cell.py --dry-run
{
 "cell": "item5-batch-throughput",
 "harness_version": "v8",
 "endpoint": "(dry-run)",
 "model": "q27-IQ2_M-96k",
 "n": 50,
 "threshold": 0.8,
 "jobs_cycled": [
  "a1-summarise-r1",
  "b1-contradiction-r1",
  "c1-changelog-r1"
 ],
 "dry_run": true,
 "units": {
  "load_s": "seconds, Ollama load_duration",
  "inference_s": "seconds, prompt_eval_duration + eval_duration",
  "overhead_s": "seconds, batch wall minus inference",
  "unload_s": "seconds of wall for the keep_alive:0 request",
  "items_per_hour": "items / batch wall hour, load and unload excluded",
  "items_per_hour_with_load": "items / (load + batch wall + unload) hour",
  "accuracy": "fraction of items grading VERDICT correct"
 },
 "pre_unload_s": 0.0,
 "load_probe_wall_s": 9.78,
 "load_s": 9.4,
 "unload_s": 0.0,
 "api_ps_empty": null,
 "batch_wall_s": 996.48,
 "inference_s": 978.98,
 "inference_s_unrounded": 978.87,
 "overhead_s": 17.5,
 "reloads_mid_batch": 0,
 "correct": 42,
 "accuracy": 0.84,
 "items_per_hour": 180.6,
 "items_per_hour_with_load": 178.9,
 "items_per_hour_correct": 151.7,
 "gpu_holding_s": 1005.9,
 "decision": "go",
 "gpu_budget_line": "item5-batch-throughput  q27-IQ2_M-96k  n=50  1006 s  accuracy=0.84  items/h=180.6  (append by hand to results/v8/GPU_BUDGET.log)"
}

ok   one trial per job                                              got=50               want=50
ok   batch wall equals the sum of the per-trial walls               got=996.48           want=996.48
ok   inference equals the sum of the per-trial inference            got=978.98           want=978.98
ok   load + inference + overhead equals the wall this cell accounts for got=996.48           want=996.48
ok   load is reported outside the batch wall, not inside it         got=0.0              want=0.0
ok   accuracy equals correct over n                                 got=0.84             want=0.84
ok   items/hour is over the batch wall alone                        got=180.6            want=180.6
ok   items/hour with load is strictly lower                         got=True             want=True
ok   items/hour at accuracy is the product                          got=151.7            want=151.7
ok   gpu holding time is load + batch + unloads                     got=1005.9           want=1005.9
ok   the threshold decides the decision                             got=go               want=go
ok   no reload mid-batch in the fixture                             got=0                want=0
ok   the grader agreed with the fixture's intent                    got=42               want=42
13/13 accounting checks passed
```

## PASS item 5: batch-cell threshold decides no-go as well as go

The same fixture at 0.84 accuracy reads go at a 0.8 threshold and no-go at 0.9, so the decision comes from the threshold and not from the fixture.

```
$ python3 batch_cell.py --dry-run --threshold 0.9
{
 "cell": "item5-batch-throughput",
 "harness_version": "v8",
 "endpoint": "(dry-run)",
 "model": "q27-IQ2_M-96k",
 "n": 50,
 "threshold": 0.9,
 "jobs_cycled": [
  "a1-summarise-r1",
  "b1-contradiction-r1",
  "c1-changelog-r1"
 ],
 "dry_run": true,
 "units": {
  "load_s": "seconds, Ollama load_duration",
  "inference_s": "seconds, prompt_eval_duration + eval_duration",
  "overhead_s": "seconds, batch wall minus inference",
  "unload_s": "seconds of wall for the keep_alive:0 request",
  "items_per_hour": "items / batch wall hour, load and unload excluded",
  "items_per_hour_with_load": "items / (load + batch wall + unload) hour",
  "accuracy": "fraction of items grading VERDICT correct"
 },
 "pre_unload_s": 0.0,
 "load_probe_wall_s": 9.78,
 "load_s": 9.4,
 "unload_s": 0.0,
 "api_ps_empty": null,
 "batch_wall_s": 996.48,
 "inference_s": 978.98,
 "inference_s_unrounded": 978.87,
 "overhead_s": 17.5,
 "reloads_mid_batch": 0,
 "correct": 42,
 "accuracy": 0.84,
 "items_per_hour": 180.6,
 "items_per_hour_with_load": 178.9,
 "items_per_hour_correct": 151.7,
 "gpu_holding_s": 1005.9,
 "decision": "no-go",
 "gpu_budget_line": "item5-batch-throughput  q27-IQ2_M-96k  n=50  1006 s  accuracy=0.84  items/h=180.6  (append by hand to results/v8/GPU_BUDGET.log)"
}

ok   one trial per job                                              got=50               want=50
ok   batch wall equals the sum of the per-trial walls               got=996.48           want=996.48
ok   inference equals the sum of the per-trial inference            got=978.98           want=978.98
ok   load + inference + overhead equals the wall this cell accounts for got=996.48           want=996.48
ok   load is reported outside the batch wall, not inside it         got=0.0              want=0.0
ok   accuracy equals correct over n                                 got=0.84             want=0.84
ok   items/hour is over the batch wall alone                        got=180.6            want=180.6
ok   items/hour with load is strictly lower                         got=True             want=True
ok   items/hour at accuracy is the product                          got=151.7            want=151.7
ok   gpu holding time is load + batch + unloads                     got=1005.9           want=1005.9
ok   the threshold decides the decision                             got=no-go            want=no-go
ok   no reload mid-batch in the fixture                             got=0                want=0
ok   the grader agreed with the fixture's intent                    got=42               want=42
13/13 accounting checks passed
```

## PASS item 6: escalation ledger, offline, draft quality 'bad'

Every figure in the ledger re-adds from the item rows, arm 2's hosted input always exceeds arm 1's because the draft is inside it, and the ledger carries no Authorization header or key value. The 'bad' fixture is the outcome the v8 plan warns about and the 'rescue' fixture is the only shape in which drafting pays, so the ledger is shown to read both ways.

```
$ python3 escalate.py --dry-run --dry-run-draft-quality bad
{
 "cell": "item6-escalation-economics",
 "harness_version": "v8",
 "dry_run": true,
 "local": {
  "endpoint": "(dry-run)",
  "model": "q27-IQ2_M-96k"
 },
 "hosted": {
  "endpoint": "(dry-run)",
  "model": "(unset)",
  "api_key_env": null,
  "note": ""
 },
 "n_per_family": 10,
 "units": {
  "hosted_input_tokens": "count of input tokens the hosted provider itself reported (usage.prompt_tokens); see token_source",
  "hosted_output_tokens": "count of output tokens the hosted provider itself reported (usage.completion_tokens); see token_source",
  "hosted_total_tokens": "hosted_input_tokens + hosted_output_tokens, unweighted: input and output are not the same price and must be weighted at analysis time",
  "token_source": "provider = read from the provider's usage field; estimated = chars / 4.664; fixture = produced by --dry-run and is not a measurement of anything",
  "local_wall_s": "seconds of wall for the local draft, which is GPU-holding time and not money",
  "local_inference_s": "seconds of prompt_eval + eval reported by Ollama for the local draft",
  "correct": "items grading VERDICT correct under grade_seeded, the same grader the GPU cells use",
  "hosted_tokens_per_correct_item": "hosted_total_tokens / correct; None when nothing was correct, because a cost per zero is not a large number",
  "money": "deliberately absent: multiply the token columns by the endpoint's own rate at analysis time"
 },
 "families": {
  "a1-summarise-r1": {
   "rung": "r1",
   "prompt_chars": 58418,
   "arms": {
    "hosted_only": {
     "n": 10,
     "hosted_input_tokens": 125250,
     "hosted_output_tokens": 1094,
     "hosted_total_tokens": 126344,
     "correct": 8,
     "accuracy": 0.8,
     "hosted_tokens_per_item": 12634.4,
     "hosted_tokens_per_correct_item": 15793.0,
     "token_source": "fixture"
    },
    "local_draft_hosted_verify": {
     "n": 10,
     "hosted_input_tokens": 127240,
     "hosted_output_tokens": 1094,
     "hosted_total_tokens": 128334,
     "correct": 8,
     "accuracy": 0.8,
     "hosted_tokens_per_item": 12833.4,
     "hosted_tokens_per_correct_item": 16041.8,
     "token_source": "fixture"
    }
   },
   "local_draft": {
    "correct": 0,
    "wall_s": 210.8,
    "inference_s": 207.3,
    "output_tokens": 1190
   },
   "net": {
    "correct_delta": 0,
    "hosted_input_delta": 1990,
    "hosted_output_delta": 0,
    "hosted_total_delta": 1990,
    "hosted_tokens_per_net_correct_item": null,
    "item_flips": {
     "fixed_by_verify": 8,
     "broken_by_draft": 0,
     "draft_already_correct": 0
    },
    "reading": "no correctness gain, and arm 2 costs +1990 hosted tokens. Drafting locally does not pay for this family at this rung."
   }
  },
  "b1-contradiction-r1": {
   "rung": "r1",
   "prompt_chars": 52663,
   "arms": {
    "hosted_only": {
     "n": 10,
     "hosted_input_tokens": 112910,
     "hosted_output_tokens": 792,
     "hosted_total_tokens": 113702,
     "correct": 8,
     "accuracy": 0.8,
     "hosted_tokens_per_item": 11370.2,
     "hosted_tokens_per_correct_item": 14212.8,
     "token_source": "fixture"
    },
    "local_draft_hosted_verify": {
     "n": 10,
     "hosted_input_tokens": 114590,
     "hosted_output_tokens": 792,
     "hosted_total_tokens": 115382,
     "correct": 8,
     "accuracy": 0.8,
     "hosted_tokens_per_item": 11538.2,
     "hosted_tokens_per_correct_item": 14422.8,
     "token_source": "fixture"
    }
   },
   "local_draft": {
    "correct": 0,
    "wall_s": 185.8,
    "inference_s": 182.3,
    "output_tokens": 880
   },
   "net": {
    "correct_delta": 0,
    "hosted_input_delta": 1680,
    "hosted_output_delta": 0,
    "hosted_total_delta": 1680,
    "hosted_tokens_per_net_correct_item": null,
    "item_flips": {
     "fixed_by_verify": 8,
     "broken_by_draft": 0,
     "draft_already_correct": 0
    },
    "reading": "no correctness gain, and arm 2 costs +1680 hosted tokens. Drafting locally does not pay for this family at this rung."
   }
  },
  "c1-changelog-r1": {
   "rung": "r1",
   "prompt_chars": 59561,
   "arms": {
    "hosted_only": {
     "n": 10,
     "hosted_input_tokens": 127700,
     "hosted_output_tokens": 1662,
     "hosted_total_tokens": 129362,
     "correct": 8,
     "accuracy": 0.8,
     "hosted_tokens_per_item": 12936.2,
     "hosted_tokens_per_correct_item": 16170.2,
     "token_source": "fixture"
    },
    "local_draft_hosted_verify": {
     "n": 10,
     "hosted_input_tokens": 130420,
     "hosted_output_tokens": 1662,
     "hosted_total_tokens": 132082,
     "correct": 8,
     "accuracy": 0.8,
     "hosted_tokens_per_item": 13208.2,
     "hosted_tokens_per_correct_item": 16510.2,
     "token_source": "fixture"
    }
   },
   "local_draft": {
    "correct": 0,
    "wall_s": 231.5,
    "inference_s": 228.0,
    "output_tokens": 1910
   },
   "net": {
    "correct_delta": 0,
    "hosted_input_delta": 2720,
    "hosted_output_delta": 0,
    "hosted_total_delta": 2720,
    "hosted_tokens_per_net_correct_item": null,
    "item_flips": {
     "fixed_by_verify": 8,
     "broken_by_draft": 0,
     "draft_already_correct": 0
    },
    "reading": "no correctness gain, and arm 2 costs +2720 hosted tokens. Drafting locally does not pay for this family at this rung."
   }
  }
 }
}

ok   a1-summarise-r1: arm1 input tokens re-add                            got=125250     want=125250
ok   a1-summarise-r1: arm2 input tokens re-add                            got=127240     want=127240
ok   a1-summarise-r1: arm2 hosted input exceeds arm1 (the draft is in it) got=True       want=True
ok   a1-summarise-r1: total equals input plus output, arm1                got=126344     want=126344
ok   a1-summarise-r1: net correctness is a paired difference              got=0          want=0
ok   a1-summarise-r1: net hosted delta is a difference of totals          got=1990       want=1990
ok   a1-summarise-r1: tokens per correct item, arm1                       got=15793.0    want=15793.0
ok   a1-summarise-r1: token source is named on every row                  got=True       want=True
ok   a1-summarise-r1: the local arm's cost is time, not tokens billed     got=True       want=True
ok   a1-summarise-r1: cost per net correct item is None when there is no gain got=True       want=True
ok   b1-contradiction-r1: arm1 input tokens re-add                        got=112910     want=112910
ok   b1-contradiction-r1: arm2 input tokens re-add                        got=114590     want=114590
ok   b1-contradiction-r1: arm2 hosted input exceeds arm1 (the draft is in it) got=True       want=True
ok   b1-contradiction-r1: total equals input plus output, arm1            got=113702     want=113702
ok   b1-contradiction-r1: net correctness is a paired difference          got=0          want=0
ok   b1-contradiction-r1: net hosted delta is a difference of totals      got=1680       want=1680
ok   b1-contradiction-r1: tokens per correct item, arm1                   got=14212.8    want=14212.8
ok   b1-contradiction-r1: token source is named on every row              got=True       want=True
ok   b1-contradiction-r1: the local arm's cost is time, not tokens billed got=True       want=True
ok   b1-contradiction-r1: cost per net correct item is None when there is no gain got=True       want=True
ok   c1-changelog-r1: arm1 input tokens re-add                            got=127700     want=127700
ok   c1-changelog-r1: arm2 input tokens re-add                            got=130420     want=130420
ok   c1-changelog-r1: arm2 hosted input exceeds arm1 (the draft is in it) got=True       want=True
ok   c1-changelog-r1: total equals input plus output, arm1                got=129362     want=129362
ok   c1-changelog-r1: net correctness is a paired difference              got=0          want=0
ok   c1-changelog-r1: net hosted delta is a difference of totals          got=2720       want=2720
ok   c1-changelog-r1: tokens per correct item, arm1                       got=16170.2    want=16170.2
ok   c1-changelog-r1: token source is named on every row                  got=True       want=True
ok   c1-changelog-r1: the local arm's cost is time, not tokens billed     got=True       want=True
ok   c1-changelog-r1: cost per net correct item is None when there is no gain got=True       want=True
ok   no key value anywhere in the ledger                                  got=True       want=True
31/31 ledger checks passed
```

## PASS item 6: escalation ledger, offline, draft quality 'rescue'

Every figure in the ledger re-adds from the item rows, arm 2's hosted input always exceeds arm 1's because the draft is inside it, and the ledger carries no Authorization header or key value. The 'bad' fixture is the outcome the v8 plan warns about and the 'rescue' fixture is the only shape in which drafting pays, so the ledger is shown to read both ways.

```
$ python3 escalate.py --dry-run --dry-run-draft-quality rescue
{
 "cell": "item6-escalation-economics",
 "harness_version": "v8",
 "dry_run": true,
 "local": {
  "endpoint": "(dry-run)",
  "model": "q27-IQ2_M-96k"
 },
 "hosted": {
  "endpoint": "(dry-run)",
  "model": "(unset)",
  "api_key_env": null,
  "note": ""
 },
 "n_per_family": 10,
 "units": {
  "hosted_input_tokens": "count of input tokens the hosted provider itself reported (usage.prompt_tokens); see token_source",
  "hosted_output_tokens": "count of output tokens the hosted provider itself reported (usage.completion_tokens); see token_source",
  "hosted_total_tokens": "hosted_input_tokens + hosted_output_tokens, unweighted: input and output are not the same price and must be weighted at analysis time",
  "token_source": "provider = read from the provider's usage field; estimated = chars / 4.664; fixture = produced by --dry-run and is not a measurement of anything",
  "local_wall_s": "seconds of wall for the local draft, which is GPU-holding time and not money",
  "local_inference_s": "seconds of prompt_eval + eval reported by Ollama for the local draft",
  "correct": "items grading VERDICT correct under grade_seeded, the same grader the GPU cells use",
  "hosted_tokens_per_correct_item": "hosted_total_tokens / correct; None when nothing was correct, because a cost per zero is not a large number",
  "money": "deliberately absent: multiply the token columns by the endpoint's own rate at analysis time"
 },
 "families": {
  "a1-summarise-r1": {
   "rung": "r1",
   "prompt_chars": 58418,
   "arms": {
    "hosted_only": {
     "n": 10,
     "hosted_input_tokens": 125250,
     "hosted_output_tokens": 1094,
     "hosted_total_tokens": 126344,
     "correct": 8,
     "accuracy": 0.8,
     "hosted_tokens_per_item": 12634.4,
     "hosted_tokens_per_correct_item": 15793.0,
     "token_source": "fixture"
    },
    "local_draft_hosted_verify": {
     "n": 10,
     "hosted_input_tokens": 127240,
     "hosted_output_tokens": 1070,
     "hosted_total_tokens": 128310,
     "correct": 10,
     "accuracy": 1.0,
     "hosted_tokens_per_item": 12831.0,
     "hosted_tokens_per_correct_item": 12831.0,
     "token_source": "fixture"
    }
   },
   "local_draft": {
    "correct": 0,
    "wall_s": 210.8,
    "inference_s": 207.3,
    "output_tokens": 1190
   },
   "net": {
    "correct_delta": 2,
    "hosted_input_delta": 1990,
    "hosted_output_delta": -24,
    "hosted_total_delta": 1966,
    "hosted_tokens_per_net_correct_item": 983.0,
    "item_flips": {
     "fixed_by_verify": 10,
     "broken_by_draft": 0,
     "draft_already_correct": 0
    },
    "reading": "arm 2 buys 2 more correct items for +1966 hosted tokens, 983.0 tokens per net correct item. Whether that pays is a price question, not a bench question."
   }
  },
  "b1-contradiction-r1": {
   "rung": "r1",
   "prompt_chars": 52663,
   "arms": {
    "hosted_only": {
     "n": 10,
     "hosted_input_tokens": 112910,
     "hosted_output_tokens": 792,
     "hosted_total_tokens": 113702,
     "correct": 8,
     "accuracy": 0.8,
     "hosted_tokens_per_item": 11370.2,
     "hosted_tokens_per_correct_item": 14212.8,
     "token_source": "fixture"
    },
    "local_draft_hosted_verify": {
     "n": 10,
     "hosted_input_tokens": 114590,
     "hosted_output_tokens": 770,
     "hosted_total_tokens": 115360,
     "correct": 10,
     "accuracy": 1.0,
     "hosted_tokens_per_item": 11536.0,
     "hosted_tokens_per_correct_item": 11536.0,
     "token_source": "fixture"
    }
   },
   "local_draft": {
    "correct": 0,
    "wall_s": 185.8,
    "inference_s": 182.3,
    "output_tokens": 880
   },
   "net": {
    "correct_delta": 2,
    "hosted_input_delta": 1680,
    "hosted_output_delta": -22,
    "hosted_total_delta": 1658,
    "hosted_tokens_per_net_correct_item": 829.0,
    "item_flips": {
     "fixed_by_verify": 10,
     "broken_by_draft": 0,
     "draft_already_correct": 0
    },
    "reading": "arm 2 buys 2 more correct items for +1658 hosted tokens, 829.0 tokens per net correct item. Whether that pays is a price question, not a bench question."
   }
  },
  "c1-changelog-r1": {
   "rung": "r1",
   "prompt_chars": 59561,
   "arms": {
    "hosted_only": {
     "n": 10,
     "hosted_input_tokens": 127700,
     "hosted_output_tokens": 1662,
     "hosted_total_tokens": 129362,
     "correct": 8,
     "accuracy": 0.8,
     "hosted_tokens_per_item": 12936.2,
     "hosted_tokens_per_correct_item": 16170.2,
     "token_source": "fixture"
    },
    "local_draft_hosted_verify": {
     "n": 10,
     "hosted_input_tokens": 130420,
     "hosted_output_tokens": 1600,
     "hosted_total_tokens": 132020,
     "correct": 10,
     "accuracy": 1.0,
     "hosted_tokens_per_item": 13202.0,
     "hosted_tokens_per_correct_item": 13202.0,
     "token_source": "fixture"
    }
   },
   "local_draft": {
    "correct": 0,
    "wall_s": 231.5,
    "inference_s": 228.0,
    "output_tokens": 1910
   },
   "net": {
    "correct_delta": 2,
    "hosted_input_delta": 2720,
    "hosted_output_delta": -62,
    "hosted_total_delta": 2658,
    "hosted_tokens_per_net_correct_item": 1329.0,
    "item_flips": {
     "fixed_by_verify": 10,
     "broken_by_draft": 0,
     "draft_already_correct": 0
    },
    "reading": "arm 2 buys 2 more correct items for +2658 hosted tokens, 1329.0 tokens per net correct item. Whether that pays is a price question, not a bench question."
   }
  }
 }
}

ok   a1-summarise-r1: arm1 input tokens re-add                            got=125250     want=125250
ok   a1-summarise-r1: arm2 input tokens re-add                            got=127240     want=127240
ok   a1-summarise-r1: arm2 hosted input exceeds arm1 (the draft is in it) got=True       want=True
ok   a1-summarise-r1: total equals input plus output, arm1                got=126344     want=126344
ok   a1-summarise-r1: net correctness is a paired difference              got=2          want=2
ok   a1-summarise-r1: net hosted delta is a difference of totals          got=1966       want=1966
ok   a1-summarise-r1: tokens per correct item, arm1                       got=15793.0    want=15793.0
ok   a1-summarise-r1: token source is named on every row                  got=True       want=True
ok   a1-summarise-r1: the local arm's cost is time, not tokens billed     got=True       want=True
ok   a1-summarise-r1: cost per net correct item is None when there is no gain got=False      want=False
ok   b1-contradiction-r1: arm1 input tokens re-add                        got=112910     want=112910
ok   b1-contradiction-r1: arm2 input tokens re-add                        got=114590     want=114590
ok   b1-contradiction-r1: arm2 hosted input exceeds arm1 (the draft is in it) got=True       want=True
ok   b1-contradiction-r1: total equals input plus output, arm1            got=113702     want=113702
ok   b1-contradiction-r1: net correctness is a paired difference          got=2          want=2
ok   b1-contradiction-r1: net hosted delta is a difference of totals      got=1658       want=1658
ok   b1-contradiction-r1: tokens per correct item, arm1                   got=14212.8    want=14212.8
ok   b1-contradiction-r1: token source is named on every row              got=True       want=True
ok   b1-contradiction-r1: the local arm's cost is time, not tokens billed got=True       want=True
ok   b1-contradiction-r1: cost per net correct item is None when there is no gain got=False      want=False
ok   c1-changelog-r1: arm1 input tokens re-add                            got=127700     want=127700
ok   c1-changelog-r1: arm2 input tokens re-add                            got=130420     want=130420
ok   c1-changelog-r1: arm2 hosted input exceeds arm1 (the draft is in it) got=True       want=True
ok   c1-changelog-r1: total equals input plus output, arm1                got=129362     want=129362
ok   c1-changelog-r1: net correctness is a paired difference              got=2          want=2
ok   c1-changelog-r1: net hosted delta is a difference of totals          got=2658       want=2658
ok   c1-changelog-r1: tokens per correct item, arm1                       got=16170.2    want=16170.2
ok   c1-changelog-r1: token source is named on every row                  got=True       want=True
ok   c1-changelog-r1: the local arm's cost is time, not tokens billed     got=True       want=True
ok   c1-changelog-r1: cost per net correct item is None when there is no gain got=False      want=False
ok   no key value anywhere in the ledger                                  got=True       want=True
31/31 ledger checks passed
```
