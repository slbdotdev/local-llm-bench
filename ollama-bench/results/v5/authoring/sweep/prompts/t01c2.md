# Audit references to a moved path

The workspace contains a small documentation tree. Do not edit any of its documents. Locate
every standalone occurrence of this exact old path:

`repo/tools/deploy/check.py`

The path moved to:

`repo/tools/release/check.py`

Classify each occurrence from its context:

- `UPDATE`: a live, current link, command, checklist, or other instruction that should point to
  the new location.
- `LEAVE`: a dated archive, changelog, incident report, or history section that truthfully
  records the old location. Such records are correct and must remain unchanged.

Inspect every Markdown file under the workspace, including nested folders. There are exactly
four standalone occurrences of the old path. Do not count the new path or near-matches such as a
different directory or filename. Sort your output by relative source-file path, then by
1-based line number.

Write exactly four lines to `reference_audit.txt`, and write no header, bullets, code fences, or
extra lines. Each line has five fields separated by literal tab characters (U+0009):

`ACTION<TAB>RELATIVE_FILE<TAB>LINE<TAB>OLD_PATH<TAB>REPLACEMENT`

`ACTION` is exactly `UPDATE` or `LEAVE`. `RELATIVE_FILE` is the POSIX path from the workspace
root, with no leading `./` and no `seed/` prefix. `LINE` is a positive decimal line number.
`OLD_PATH` is the exact moved path. For `UPDATE`, `REPLACEMENT` is the exact new path; for
`LEAVE`, it is exactly `-`.

The following syntax examples show `<TAB>` visibly in place of one literal tab; do not put the
marker text into your output:

```text
UPDATE<TAB>path/to/file.md<TAB>8<TAB>/old/path.md<TAB>/new/path.md
LEAVE<TAB>path/to/archive.md<TAB>19<TAB>/old/path.md<TAB>-
```

Those names and paths are placeholders only. Use the actual four references you discover. Do
not alter the seed documents; once the output file is complete, stop.
