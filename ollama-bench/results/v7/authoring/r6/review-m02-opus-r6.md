verdict: REVISE
fair: yes — every fact the answer needs is stated somewhere in the tree, the two document/module divergences are pre-announced by the contract itself, and I reached the reference answer from the prompt alone with no guessing.
solved_it: yes — my blind answer (`changed: audit, compaction, envelope, schema` / `declined: attestation, digest` / `authority: SEC-CFG-4`, four table-row renames) matched `ref/` exactly; I nearly went wrong twice, once by taking the on-call team from the module docstring instead of the component document (it agrees, so it did not bite — see finding 1), and once by nearly putting the unpublished Delivery Engineering stages (backfill, checkpoint, reconcile) into `declined`, which the boundary's closing section settles.
checker: sound — ran `selfcheck.py`'s fourteen rows (reference 8/8 correct; "correct report, frozen document also edited" and "correct, scratch file left behind" both fire `unsafe` at 7/8; all five report-only perturbations land `correct` 8/8), and independently re-hashed all 81 `seed_hashes` against `seed/` and all 4 `editable` hashes against `ref/` — every one matches, and the 81+4 exactly covers the 85 seed files.
shortcut: 21 files, score 8/8 — `docs/api/config-contract.md` + `docs/security/boundary.md` + the 19 stage modules decide the entire answer; the 19 stage documents are needed only for the 4 that get edited (25 files touched in all). Well above the five-file bar, so not a rung-0 shortcut failure.
harvest: 19/19 by `grep -rn 'SLA_HEADROOM\|^Ownership:' seed/src/talus/` — 38 lines, both decisive facts for all nineteen stages on one screen, and the answer is then finishable without opening a single per-unit file. The frames are byte-identical at fixed offsets: `sed -n '7p;14p' seed/src/talus/*.py` returns the same 38 lines. The document-side harvest (`grep -rn 'sla_headroom' seed/docs/`, 19 values) is correctly poisoned — two of the nineteen are stale — so only the module-side grep works, which is also the only correct path.
tools: clear — all 19 seed modules run with no arguments, rc=0, 0 bytes, no scored or per-unit value printed.
notes_claims: failed — `NOTES.md:31` claims "The strict required traversal is **19557 measured tokens** across all nineteen stage documents and all nineteen modules." The arithmetic is right (19 docs 7353 + 19 modules 12204 = 19557, and the 21017 floor and its 70.2% both reconcile against `MANIFEST.json`), but the word *required* does not hold: the stage documents are not required for the decision, because each module's own docstring carries the same authoritative on-call team. The decisive minimum is 3 rulings + 19 modules = 13249 tokens, 44.3% of material. Every other number checks out — 6/2/4 published/declined/changed, 85 seed files, 139614 material chars, 29934 tokens at 4.664 chars/token, 96-char reference report, 42 load-bearing paths over 6 hops.
tiers: Haiku fails at the publication rule — it reads `sla_headroom` from the configuration table it is already editing (`seed/docs/schema.md:18`, 41) instead of `SLA_HEADROOM` from the module (`seed/src/talus/schema_flow.py:14`, 53), which silently drops `schema` from `changed` and adds `checkpoint` to `declined`; a careful Sonnet-class model is not caught, because the contract names that exact failure mode in bold and says "never the `sla_headroom` row in its component document".
workhorse_failure: real — the nearest step that could catch Sonnet is freezing by owner *name* rather than on-call *team*, which would wrongly decline `envelope` (M. Lindqvist, but Client Integrations) alongside `attestation` (M. Lindqvist, Delivery Engineering). That is a genuine reasoning failure the prompt and the boundary both warn against in as many words, not a defect in the material.
hard_to_do: yes — the reading is long and the decision is a two-rule reconciliation over nineteen units, but nothing is obfuscated, split across lines, encoded, or arithmetic-heavy; the revision made the task harder to *do*, not harder to *understand*.
fix: strip the on-call team from every module docstring in `seed/src/talus/*.py:7` (leave `Ownership: M. Lindqvist.`) so the team exists only where the prompt, the boundary and `NOTES.md` all say it is authoritative — the component document — and extend `_assert_ownership_layout` in `r2/specs/m02_main_claude.py:302` to assert no module carries a team name, the same way it already asserts `operations.md` carries none.

## Findings, most severe first

**1. `seed/src/talus/attestation_store.py:7` (and all 19 modules, line 7) — the second
cross-reference hop is duplicated into the module and collapses to zero extra files.**
The prompt says a freeze "names an on-call team, not a stage, so finding which stages a
freeze reaches takes one more cross-reference, into the authoritative per-stage ownership
statement carried by each stage's own component document", and
`r2/specs/m02_main_claude.py:302` asserts `docs/operations.md` carries no stage-to-team
index. But every module's docstring carries `Ownership: <name> (<team>).`, and for all
nineteen stages that team is byte-identical to the component document's `*On-call team:*`
line. The generator asserts this agreement at `r2/specs/m02_main_claude.py:112` and then
never removes it. Consequence: `grep -rn 'SLA_HEADROOM\|^Ownership:' seed/src/talus/`
returns 38 lines carrying *both* decisive facts for all nineteen stages, and — with the
contract and the boundary, which the prompt names by role — the whole answer follows
without opening one stage document. That is what makes the `19557 measured tokens` claim
at `NOTES.md:31` false and the 70.2% floor unearned; the truly decisive traversal is
44.3%. No wrong answer results (the two sources agree everywhere), so this is difficulty
erosion, not unfairness — but it erodes exactly the hop the task is built on.
*Fix:* as above — drop the parenthesised team from the module docstrings and assert its
absence.

**2. `seed/docs/security/boundary.md:31` — the deliverable's key `declined` is a one-hop
locator for a load-bearing file; `r5/check_rung0.py` fails on it.**
`python3 r5/check_rung0.py cand-claude/m02-main-claude` exits 1 with
`C2: the deliverable's key 'declined' appears in the prompt and greps to only 1 file(s),
one load-bearing: ['docs/security/boundary.md']`. The word reaches the ruling document in
one grep. It is the weaker form of the condition — the located file states a rule over a
team, not any decisive per-stage value, and the README already points at
`docs/security/boundary.md` by name and purpose, so the leak buys a solver nothing it did
not already have. It is nonetheless a hard `problems` entry on the revised build, on the
one checker that tests the rung-0 condition directly.
*Fix:* reword line 31 to avoid the report key, e.g. "A stage this clause freezes belongs in
the report's second field, never in the first and never silently omitted"; the sentence's
real work — telling the solver that a frozen stage is recorded rather than dropped — is
preserved.

**3. `seed/README.md:11`, `seed/README.md:46`, `seed/docs/operations.md:46` — three
references to a `docs/policy/` directory that does not exist.**
The README's reading order calls `docs/policy/` "the rules that outrank both of the above"
and its conventions say "a policy under `docs/policy/` outranks everything else" — i.e. it
would outrank the API contract and the security boundary, the two documents that decide
this task. There is no such directory. The absence is discoverable in one `ls`, so this
costs a careful solver a detour rather than the answer, but a dangling pointer to an
authority that would outrank the ruling documents is worth closing.
*Fix:* delete the three `docs/policy/` references from the base corpus, or point them at
`docs/security/`.

**Not defects, checked and cleared.** `probe_candidate.py` reports five "GRADER DEFECT"
rows (`crlf`, `extra_trailing_nl`, `leading_blank`, `no_trailing_newline`,
`trailing_spaces`, each 7/8 `confidently_wrong`). `NOTES.md` section 8 adjudicates these
and the adjudication holds: those rows perturb the four *edited documents*, and the prompt
grants newline latitude to `scope-report.txt` alone ("It may end with a newline or not")
while forbidding, for the documents, any change beyond the rename ("A change that reaches
further than the rename it was asked for has failed the task even when the report is
right"). The five report-only perturbations in `selfcheck.py` all land `correct` at 8/8,
which is the right line to draw. Also cleared: `probe_idempotence.py` (8/8 correct twice),
`r2/check_index_leak.py` (clean — `SLA_HEADROOM` appears only in each stage's own module),
`r2/check_load_bearing.py` (42 paths, 6 hops, 70.2%), `r5/check_tools.py` (clear). The
freeze/publication interaction is well built: the boundary's closing section explicitly
rules unpublished Delivery Engineering stages out of `declined`, and freezing by team
rather than by owner name is what separates `envelope` from `attestation` under the same
owner. Both edited and unedited documents mention `window_s` a second time in prose
(`seed/docs/schema.md:38`), which the prompt's "configuration table only" correctly excludes
and `ref/` correctly leaves alone.

verdict: REVISE
