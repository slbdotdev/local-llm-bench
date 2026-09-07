# Public benchmark survey for the traversal axis
*Renamed 2026-09-06 from `v7/public-benchmarks-2026-09-07.md`: the campaign labelled rounds by planned campaign day, not by the calendar date they were written.*

Scope: sources checked 2026-09-05. “Context” means the published task input or budget, not a
model's advertised window. “Reuse” is a practical reading of the cited repository and data terms,
not legal advice. A blank or unclear licence is reported as unclear.

## 1. Benchmarks and task shapes

| Benchmark | Year | What it measures; task shape and grading | Context size | Licence and reuse | Source |
|---|---:|---|---|---|---|
| SWE-bench | 2023/24 | GitHub issue plus pre-fix repo; patch must pass issue and regression tests, hidden from the model | No fixed window | MIT harness; task code is upstream-repository-specific, verify each licence | SWE-bench paper [R1], repo [R2] |
| SWE-bench Verified | 2024 | 500 human-reviewed SWE-bench tasks; same patch plus hidden tests | No fixed window | Dataset reuse terms not stated as one blanket licence; verify upstream repos | Verified report [R3] |
| SWE-bench Pro | 2025 | Human-augmented long-horizon issues; multi-file patch in Docker, test-based pass/fail | No fixed window; 1,865 tasks, 41 repos | MIT public repo; task content and upstream licences still need per-repo review | Pro paper [R4], repo [R5] |
| SWE-bench Multimodal | 2024/25 | Visual JavaScript issue with images plus repo; patch graded by executable tests | No fixed window | MIT harness; image, repo, and task terms are component-specific | Multimodal paper [R6], repo [R2] |
| SWE-bench Live | 2025/26 | Fresh GitHub issues, automated curation, containerized environments, test-based patch grading; now multi-language and multi-OS | No fixed window; initial paper release 1,319 tasks | MIT repository; upstream snapshots and dataset terms need checking | Live paper/repo [R7] |
| Aider Polyglot | 2024 | 225 Exercism exercises in six languages; agent edits starter files and all exercise tests must pass | Exercise-sized, no fixed window | Selected Exercism tracks are mainly MIT; retain notices and verify each track | Aider harness/repo [R8], Exercism terms [R24] |
| LongBench v2 | 2024/25 | 503 reviewed multiple-choice questions over single/multi-document, dialogue, code-repo, and structured data tasks; exact choice accuracy | 8k to 2M words | Project site CC BY-SA 4.0; underlying datasets and questions need source-level review | Paper/site [R9] |
| RULER | 2024 | Synthetic retrieval, multiple needles, multi-hop tracing, aggregation, and QA; deterministic answer matching | Configurable 4k to 128k in the cited release | Apache-2.0 code; generated cases are the safest direct adaptation | Paper/repo [R10] |
| NoLiMa | 2025 | Needle in book haystack with minimal question/needle lexical overlap, including two-hop associations; answer contains the correct name | 250 to 32k in paper evaluation; repo reports extensions to 128k | Adobe Research License for code and needle sets, non-commercial research only; haystack licences vary | Paper/repo [R11] |
| LoCoDiff | 2025 | Git history for one file across branches and merges; reconstruct exact final file, no partial credit | Sampled prompts up to 100k tokens; final file at most 12k tokens | Licence not clear on the benchmark page; do not copy data without checking repo terms | Benchmark page [R12] |
| Long Code Arena | 2024 | Six repo-wide families: library generation, CI repair, project completion, commit messages, bug localization, module summaries; EM, Pass@1, IR metrics, or assessor score | Small/medium/large/huge snapshots; exact per-task length varies | Research use only when resulting publication is open access; source repos are permissive but not one licence | Paper/HF task descriptions [R13] |
| RepoBench | 2023/24 | RepoBench-R retrieves cross-file snippets, -C predicts next line, -P combines retrieval and completion; rank and exact-completion metrics | Repository snapshot, no fixed model window stated | Repo/data terms need source-level review | Paper/repo [R14] |
| CrossCodeEval | 2023 | Cross-file cursor completion in Python, Java, TypeScript, C#; exact token match and retrieval metrics; at least one local API use is required | Up to 512 BPE tokens of retrieved context in the cited setup, plus repo/in-file context | Apache-2.0 code; source repositories were selected as permissively licensed | Paper/repo [R15] |
| BrowseComp / BrowseComp-Plus | 2025/26 | Entangled multi-hop web questions; Plus fixes a human-verified corpus of about 100k documents and controls retrieval, with answer accuracy | Fixed corpus, not one concatenated context; Plus paper reports 830 queries | BrowseComp terms and corpus/document licences require review; Plus repo terms do not grant every source document | OpenAI paper/page [R16], Plus paper/repo [R17] |
| Agent Retrieval Bench | 2026 | Workflow signal to gold files: code2test, comment2context, trace2code, edit2ripple, and no-gold abstention; MRR, Recall@20, and budgeted coverage | BCY budgets 4k, 8k, 16k, 32k; 427 samples, 25 repos | Evaluator, metadata, docs MIT; repository snapshots retain upstream licences | Paper/site/repo [R18] |
| RepoReasoner | 2026 | Cross-file output prediction and call-chain prediction under noisy context; exact/Pass@1-style scoring, with rewritten I/O controls | Experiments include 10k and 30k contexts; exact task distribution is source-dependent | Paper marks copyright/CC metadata; dataset reuse terms are not clear from the cited paper | Paper [R19] |
| RepoProbe | 2026 | Discussion-derived architectural Q&A; answers split into atomic checklist facts rather than scalar judge scores | Not stated in the cited paper; 500 samples, 225 with merged external context | Dataset README says CC BY 4.0 for benchmark data; verify repository source terms | Paper/repo [R20] |
| OctoBench | 2026 | Heterogeneous scaffold instructions persist across interactions; 217 tasks, 34 environments, 7,098 objective checklist items, full-trajectory scoring | Not stated in abstract | Release licence not established from the cited abstract; inspect repo before reuse | Paper [R21] |
| CTXbench / Evaluating AGENTS.md | 2026 | 138 issue tasks from 12 repos with developer context files; paired no-context, generated-context, and developer-context runs; tests plus trajectory/resource analysis | No fixed window stated | Paper/code terms require inspection; use only upstream-permitted repos | Paper [R22] |
| CodeIPI | 2026 | Legitimate bug fix with malicious instructions in issue text, comments, README, or config; injection resistance, completion, and false-positive rates | Not stated | Inspect Evals code terms and each fixture's source terms | Benchmark page [R23] |

## 2. Traversal designs for the ten failure modes

Each idea names the material, the deciding facts, why the prompt does not give a lexical route, and a hidden-checker target. Use two independent seeds per mode.

1. **Requirement stated once, far from code.** LoCoDiff-like branch history plus a dated decision note: the governing rule is in an old merge resolution, while current symbols are renamed. The prompt names the user-visible outcome, not the old term or file. Hidden checker compares the final file and a regression fixture, including the superseded near-miss.
   A second variant puts the requirement in a release-note paragraph cited by a test helper and contradicted by a nearby README. Grade behavior plus an exact change manifest, not a prose explanation.

2. **Staying inside the given scope.** BrowseComp-Plus-style evidence packet: issue, API contract, and security boundary live in three unrelated files, while the prompt names only the endpoint. The answer needs the boundary file to avoid changing a sibling service. Hidden checker tests the patch and rejects any touched path outside the allowed closure.
   Use ARB `edit2ripple`: give one anchored file and require a coordinated change in the actual dependents, while forbidding a tempting global refactor. Grade expected paths, forbidden paths, and tests separately.

3. **Instructions found in repository content.** OctoBench-style persistent instructions: a nested policy file requires a safe command and a no-network rule; a README contains a plausible but stale shortcut. Neither filename nor policy keyword appears in the prompt. Hidden checker records commands, changed paths, network attempts, and final tests, classifying a correct patch that violates policy as unsafe.
   Add a CodeIPI benign/injected pair in comments or config. The legitimate task remains solvable, but hidden checks require resisting the instruction while completing the fix.

4. **Checking before claiming.** CTXbench-style task with a test command documented in a distant workflow file and a fixture generated by another module. The prompt says “make the change” but does not name the command or fixture. Hidden checker requires the artifact plus a verifier-produced marker or passing hidden test; an unsupported final claim is `unverified_claim`.
   Put a stale visible test beside the real integration check, as in SWE-bench's issue/regression split. Grade the final tree and whether the required hidden check was actually run, without rewarding a confident report.

5. **Documentation disagrees with code.** LongBench multi-document pattern: API behavior is split across a design record, implementation, migration note, and test expectation, with one stale document. Prompt vocabulary names the product behavior only. Hidden checker runs the API and checks that the edited documentation cites the current source of truth, not the stale prose.
   Use RepoProbe's atomic checklist: require separate facts for current behavior, compatibility exception, and authoritative file. Award no full pass when a fluent answer gets one decisive fact wrong.

6. **Fixing code rather than test.** RepoReasoner output-prediction seed: implementation is correct but a cross-file pytest assertion encodes a changed contract; the traceback points toward the tempting implementation. Prompt describes the observed failure without naming the contract owner. Hidden checker requires only the intended test/fixture edits and runs hidden tests against unchanged production behavior.
   Use Long Code Arena CI-repair shape with a failing build and a distant CI configuration rule. Grade that the test is repaired for the stated new contract, while a production workaround is `confidently_wrong`.

7. **Multi-file consistency.** CrossCodeEval plus ARB `code2test`: a public API rename requires updating an adapter, registry, serializer, docs example, and regression test. The prompt gives the new scenario, not any identifier or path. Hidden checker imports every edge, runs end-to-end tests, and checks a manifest of all load-bearing files.
   Add one semantic alias in a third module and one stale call site with a different vocabulary. Grade runtime behavior, static reference closure, and no leftover old contract.

8. **Finishing.** SWE-bench Pro long-horizon shape: a task has a primary fix, a migration consequence, and a compatibility test described in separate artifacts. Prompt asks for the feature, but completion is only reached when all three are coherent. Hidden checker runs the full suite and inspects required files, with an explicit timeout/step budget applied after artifact grading.
   LoCoDiff-style history can require carrying a merge-resolution decision through the last dependent file. Grade the complete final state, not an early plausible patch or a final message claiming done.

9. **Reading past the first screen.** NoLiMa-style semantic bridge: the prompt's “regional retention” maps to a domain term in a glossary, then to a policy record, then to a code constant; each bridge uses different words. Place distractor definitions first and the deciding amendment late. Hidden checker tests the exact value and a two-hop counterexample.
   RULER multi-needle/aggregation variant: distribute three independently named facts and require their intersection, with decoy needles sharing surface tokens. Grade the aggregate tuple, not any single retrieved fact.

10. **Working with the environment as it is.** SWE-bench Multimodal/Live-inspired sandbox: a fixture's CRLF, UTF-8 name, platform path, and generated file convention are load-bearing, but the prompt mentions only the requested edit. Hidden checker compares bytes, line endings, file set, and behavior under the declared interpreter.
    Add an ARB `trace2code` failure whose visible path is a test while the root cause is environment configuration elsewhere. Grade the fix on a clean machine with no network and reject silent normalization or undeclared files.

## 3. Acceptance and difficulty tests

No source found that gates a candidate on an agent's achieved prompt occupancy. The closest published controls are:

- LoCoDiff bins accuracy by actual prompt token length, samples evenly up to 100k, claims every history segment is needed, and gives exact-match final-file grading [R12]. Use this as the empirical length curve, not as proof that an agent read the repository.
- ARB defines workflow gold files and reports BCY@4k/8k/16k/32k after ranked files are packed into a token budget [R18]. Adapt it to require at least `k` distinct load-bearing files and coverage of each causal hop, not merely many bytes.
- NoLiMa defines base accuracy at 250/500/1k and effective length as the largest length retaining 85% of base accuracy [R11]. This supports a clean short-context control before attributing failures to traversal.
- CTXbench holds task, repo revision, agent, tools, budgets, and hidden tests constant across paired context-file conditions, then analyzes file traversal and cost [R22]. Use the same fresh-sandbox and paired-run discipline.

Proposed v7 gate: reference passes; an untouched sandbox visibly fails; six whitespace/environment near-misses are tolerant where unspecified; then one workhorse trial must reach a predeclared peak prompt fraction of material and read a minimum number of gold files spanning every causal hop. Record occupancy and file reads as diagnostics, never as a substitute for the hidden checker.

## 4. Three directly adaptable families

1. **RULER multi-needle, multi-hop, and aggregation**: Apache-2.0 code [R10]. Generate a coherent sandbox corpus instead of a flat text haystack; put each fact in a different file with semantic bridges, expose only the task prompt, and make hidden `test.py` check the exact aggregate and forbidden shortcut answers.
2. **CrossCodeEval cross-file completion**: Apache-2.0 code and permissively licensed source repositories [R15]. Turn each cursor case into a small repository-edit task, retain the static-analysis requirement that a local API is necessary, move expected completion and checks behind `test.py`, and add unrelated files until every causal hop is required.
3. **Aider Polyglot / selected Exercism tracks**: the cited Exercism track repositories are mainly MIT, but exercise-level notices must be retained [R8, R24]. Combine related stubs, docs, tests, and a compatibility rule into one sandbox; hide the checker and reference; preserve attribution and remove any visible answer leakage.

## 5. What not to copy

- Do not use SWE-bench Verified as a clean frontier signal. OpenAI reports that all tested frontier models could reproduce some gold patches or task specifics, and an audit found material test or description problems in 59.4% of 138 hard cases [R3].
- Do not assume a public repo snapshot is uncontaminated. Original SWE-bench, Aider/Exercism, LongBench v2, LoCoDiff, and CrossCodeEval expose task materials or source histories; CrossCodeEval's anti-overlap filtering is a useful control, not a guarantee for later models [R8, R9, R12, R15].
- Do not copy literal NIAH. NoLiMa documents the lexical-match shortcut and fixes it with latent associations, but it still measures one answer in a book haystack, not repository traversal [R11].
- Do not treat public leaderboard difficulty as fairness. LoCoDiff was generated and run by one coding agent, Long Code Arena mixes metrics and research-only terms, and SWE-bench variants have environment-sensitive tests. Re-run references and wrong-but-plausible patches in the exact target interpreter.
- Prefer Live/Pro freshness and held-out sources, but note that Live's public fixed splits and Pro's public subset can still age into training data; use post-cutoff or newly generated self-contained seeds for the main claim [R4, R7].

## References

[R1] SWE-bench paper: https://arxiv.org/abs/2310.06770
[R2] SWE-bench repository and task harness: https://github.com/SWE-bench/SWE-bench
[R3] OpenAI, “Why SWE-bench Verified no longer measures frontier coding capabilities”: https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/
[R4] SWE-bench Pro paper: https://arxiv.org/abs/2509.16941
[R5] SWE-bench Pro public repository: https://github.com/scaleapi/SWE-bench_Pro-os
[R6] SWE-bench Multimodal paper: https://arxiv.org/abs/2410.03859
[R7] SWE-bench Live paper and repository: https://github.com/microsoft/SWE-bench-Live
[R8] Aider Polyglot benchmark and harness: https://github.com/Aider-AI/aider/tree/main/benchmark
[R9] LongBench v2 paper and project: https://longbench2.github.io/
[R10] RULER paper and repository: https://github.com/NVIDIA/RULER
[R11] NoLiMa paper and repository: https://github.com/adobe-research/NoLiMa
[R12] LoCoDiff benchmark page: https://abanteai.github.io/LoCoDiff-bench/
[R13] Long Code Arena task descriptions: https://huggingface.co/spaces/JetBrains-Research/long-code-arena
[R14] RepoBench paper: https://arxiv.org/abs/2306.03091
[R15] CrossCodeEval paper and repository: https://github.com/amazon-science/cceval
[R16] BrowseComp paper/page: https://openai.com/index/browsecomp/
[R17] BrowseComp-Plus paper and repository: https://github.com/texttron/BrowseComp-Plus
[R18] Agent Retrieval Bench paper, data, and source: https://agent-retrieval-bench.github.io/
[R19] RepoReasoner paper: https://arxiv.org/abs/2607.25996
[R20] RepoProbe paper and repository: https://arxiv.org/abs/2608.04783
[R21] OctoBench paper: https://arxiv.org/abs/2601.10343
[R22] Evaluating AGENTS.md / CTXbench: https://arxiv.org/abs/2602.11988
[R23] CodeIPI benchmark: https://ukgovernmentbeis.github.io/inspect_evals/evals/ipi_coding_agent/
[R24] Exercism licensing: https://exercism.org/docs/using/licenses
