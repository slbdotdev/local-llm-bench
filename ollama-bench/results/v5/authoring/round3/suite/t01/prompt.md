# Classify references after a relocation

Work in the documentation tree copied into the current workspace. Do not rewrite any document.
Find every standalone occurrence of this exact old path:

`//infra/handbook/oncall.md`

It has moved to:

`//infra/runbooks/oncall.md`

For each occurrence, read its surrounding section and the document's status to decide whether it is a live pointer or historical record:

- `UPDATE` a current operational link, instruction, index entry, or runbook pointer that directs present-day work to the old location.
- `LEAVE` a dated history entry, changelog, postmortem, incident transcript, archived record, or quoted evidence that accurately records what was true before the move. Historical evidence must not be rewritten, even when it appears inside a current document.

A current document can contain a quoted historical passage; classify that occurrence by the passage's role, not by the filename alone. Conversely, a current migration or rollout procedure is a live instruction and must be updated. The tree contains current guidance, service modules, operations records, and history/archive material; inspect enough surrounding context to distinguish them.

“Standalone occurrence” means the exact literal path string above appearing anywhere in a `.md` file. Prose, lists, link targets, code spans, fenced code, quotations, and comments all count. Do not count the string when it is a proper prefix or substring of a longer path, filename, or near-miss. Search all `.md` files recursively. There are exactly 55 standalone occurrences.

Create `reference_audit.txt` with exactly 55 non-empty records, ordered by relative source-file path and then ascending 1-based line number. Use no header or other text. Each record has exactly five fields separated by literal tab characters (U+0009):

`ACTION<TAB>RELATIVE_FILE<TAB>LINE<TAB>OLD_PATH<TAB>REPLACEMENT`

Use `UPDATE` or `LEAVE` exactly for `ACTION`. Use a POSIX path relative to the workspace root for `RELATIVE_FILE`, without `./` or `seed/`. Use a positive decimal line number. Copy the two paths above verbatim into `OLD_PATH` and, for `UPDATE`, `REPLACEMENT`; use `-` as `REPLACEMENT` for `LEAVE`.

The output order and field spelling are part of the contract. Do not modify the source documents. Stop after the output file is complete.

