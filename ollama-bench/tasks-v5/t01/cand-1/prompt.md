# Audit references to a moved path

You are auditing the documentation tree that was copied into your current workspace. Do not
modify any seed document. Find every standalone occurrence of this exact old path:

`/workspace/ops/runbook.md`

It moved to:

`/workspace/operations/runbook.md`

Read the surrounding document and classify each occurrence:

- `UPDATE` means the occurrence is a live, currently applicable pointer: a current link,
  navigation entry, command, or operational instruction that should use the new path.
- `LEAVE` means the occurrence is a correct historical record, such as a dated changelog,
  migration note, incident report, or history section describing where something used to live.
  Historical records must not be rewritten.

Search all Markdown files in the workspace, including nested directories. There are four exact
occurrences. Ignore the new path and text that merely resembles the old path without being the
exact path. Decide from document meaning, not just from whether the old path looks stale.

Write the result only to `reference_audit.txt`. It must contain exactly four lines, one for each
occurrence, sorted by relative source-file path and then by 1-based line number. Do not write a
header, bullets, code fences, or extra lines. Fields are separated by literal tab characters
(U+0009), not spaces. The exact five-field format is:

`ACTION<TAB>RELATIVE_FILE<TAB>LINE<TAB>OLD_PATH<TAB>REPLACEMENT`

`ACTION` must be exactly `UPDATE` or `LEAVE`. `RELATIVE_FILE` is the POSIX path from the
workspace root, without a leading `./` or `seed/`. `LINE` is a positive decimal line number.
`OLD_PATH` must be the moved path exactly. For `UPDATE`, `REPLACEMENT` must be the new path
exactly. For `LEAVE`, `REPLACEMENT` must be a single hyphen (`-`).

Format examples below use `<TAB>` as a visible stand-in for one literal tab; the marker itself
must not appear in your file:

```text
UPDATE<TAB>path/to/file.md<TAB>8<TAB>/old/path.md<TAB>/new/path.md
LEAVE<TAB>path/to/archive.md<TAB>19<TAB>/old/path.md<TAB>-
```

The examples are illustrative syntax only. Your four lines must use the actual files, line
numbers, and paths you discover. Work until the file is complete, then stop.
