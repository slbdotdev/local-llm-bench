# Inspiration survey — published evaluations adjacent to the v5 scope

Run 0 of plan section 6, the owner's explicit ruling in rev 5.9, and explicitly **low priority**.
Authored by Luna (`gpt-5.6-luna`, high, web search on) as run
`wr-wsl-20260904T092947Z-d6acaac569e0`. Full brief kept at `results/v5/briefs/inspiration.txt`.

**This page is inspiration and is never authority.** Nothing in it overrides section 4a, the
gate rules, or the trap requirement in section 4. It changed no task, no metric and no arity.
It is recorded because the owner asked for it and because two of its findings independently
converge on decisions this plan already took, which is worth knowing.

## Verification status

The shortlist is a claim, and it was checked rather than trusted. Five of the twelve citations
were spot-checked live against arxiv.org: 2504.17550 HalluLens, 2401.00396 RAGTruth, 2506.09038
AbstentionBench, 2404.06654 RULER, 2412.15204 LongBench v2 — **all five return HTTP 200 with
titles matching the names given**. No fabricated citations were found in the sample. The
remaining seven were not checked, and the *content* claims (what each mechanism does) were not
verified at all beyond the titles. Treat the mechanism descriptions as unverified.

## The two entries that matter, because they converge on decisions already taken

**Abstain-QA's answerable/unanswerable confusion matrix** (COLING 2025, public code) scores four
cells separately: correct answer, wrong answer, false refusal, correct refusal. **SimpleQA**
(OpenAI, public code) grades every short answer three ways — correct, incorrect, not attempted —
specifically so that guessing is distinguishable from abstention.

Section 7 predeclared three outcomes per trial (correct / visibly failed / confidently wrong)
before this survey was run, for the owner's own reason: a worker that fails visibly costs a
retry, one that is confidently wrong costs the verification the delegation was meant to save.
That two independent published benchmarks reach the same three-way shape is **confirmation of an
existing decision, not a change to one**, and it is recorded that way deliberately. No verdict
line moved.

**AbstentionBench** adds the one refinement worth naming: it reports abstention **precision** as
well as recall, precisely so that a model which refuses indiscriminately cannot score well by
refusing everything. The v5 suite already has this covered by construction rather than by
metric — t02 is authored with at least one candidate whose docstring is accurate, so a model
that has learned to always find a discrepancy fails it, and t04's negative candidate sits beside
positive ones. Worth stating explicitly in the final report: **the suite contains items whose
correct answer is positive, so a blanket-refusal strategy scores badly.** That sentence is
needed for the confidently-wrong rate to mean anything, and it is true of the suite as designed.

## Everything else, one line each

| entry | mechanism worth knowing about | why it is not used |
| --- | --- | --- |
| HalluLens | hallucination rate among *non-refused* answers; false-acceptance on nonexistent entities | needs generated data, external resources, an evaluator model in places |
| RAGTruth | span-level unsupported-content labels rather than one label per answer | RAG factuality, not quantization or context degradation; no confidence labels |
| Semantic Entropy (Nature) | sample n answers, cluster by meaning, entropy over clusters as uncertainty | n samples at 64k prompt each is unaffordable on this card; detects unstable confabulation, not stable-but-wrong |
| Verbalised uncertainty (ICLR 2024) | elicit a numeric confidence, score with ECE and AUROC against correctness | short tasks; verbal confidence needs recalibrating per quant and backend |
| RULER | same task regenerated at controlled lengths, degradation plotted per task | tasks stay partly retrieval-like; no abstention measure |
| BABILong | facts dispersed through long natural distractors, reasoning depth varied | recognisably synthetic distribution; still fact-reasoning rather than calibration |
| LongBench v2 | automatically scored MCQ over long documents | 503 items, MCQ permits guessing, contexts mostly outside 24k-64k |
| ProofWriter | depth-controlled True / False / **Unknown** under open-world semantics | short synthetic rulebases; no natural long-context degradation |
| Dettmers 2023, 4-bit precision | sweep precision 3-16 bits and plot quality against total bits, exposing the instability around 3 bits rather than one average | older non-instruct model families, no GGUF, no KV pressure, no long context |

## The one thing this survey did NOT find

Nothing on the list measures **quantization damage and long-context degradation together**, which
is exactly the v5 question. The quantization work (Dettmers) sweeps bits at short context; the
long-context work (RULER, BABILong, LongBench v2) holds precision fixed. The closest thing to
prior art for "does the quant needed to reach 64k already destroy quality before the context
pressure is applied" is the two literatures side by side, and nobody appears to have crossed
them at this scale on consumer hardware.

That is mildly encouraging for the exercise and it changes nothing about how it is run. It is
also the one claim on this page most worth doubting, because it is an absence, it came from a
single search run, and an absence is exactly what a search is worst at establishing.

## Method note, for the record

The first attempt at this run was refused by OpenAI's moderation before any turn started, on the
*phrasing of the brief* rather than its subject — it asked for constructions that "resist being
gamed" and described a checker "the model never sees". Reworded into plain academic terms the
identical request ran normally. That is a provider-side endpoint failure and is not evidence
about the model, per plan section 3 rule 8; see `decisions.md` for the full note.
