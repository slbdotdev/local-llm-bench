# Classify references after a relocation

Work in the documentation tree copied into the current workspace. Do not rewrite any document.
Find every standalone occurrence of this exact old path:

`//infra/handbook/oncall.md`

It has moved to:

`//infra/runbooks/oncall.md`

For each occurrence, read enough context to decide whether it is a pointer or a record:

- `UPDATE` a live, currently applicable link or instruction that should use the new path.
- `LEAVE` a dated history entry, changelog, postmortem, or other historical account of the
  former location. It is correct history and must not be changed, even if the old path appears
  in a code span or quotation.

Search all `.md` files recursively. Exactly four standalone occurrences exist. Ignore the new
path and similar-looking text that is not the exact old path. A sweep is not permission to edit
the documents: your only deliverable is the classification file.

Create `reference_audit.txt` with exactly four lines, ordered by relative source-file path and
then ascending 1-based line number. Use no header or other text. Each line must have exactly five
fields separated by literal tab characters (U+0009):

`ACTION<TAB>RELATIVE_FILE<TAB>LINE<TAB>OLD_PATH<TAB>REPLACEMENT`

Use `UPDATE` or `LEAVE` exactly for `ACTION`. Use a POSIX path relative to the workspace root for
`RELATIVE_FILE`, without `./` or `seed/`. Use a positive decimal line number. `OLD_PATH` must
match the moved path exactly. Put the new path in `REPLACEMENT` for `UPDATE`, and put exactly
`-` there for `LEAVE`.

Here are syntax examples. In this block `<TAB>` visibly stands for one literal tab and must be
replaced by that tab in the output:

```text
UPDATE<TAB>path/to/file.md<TAB>8<TAB>/old/path.md<TAB>/new/path.md
LEAVE<TAB>path/to/archive.md<TAB>19<TAB>/old/path.md<TAB>-
```

The example paths are placeholders, not clues about the seed. Use the four actual occurrences,
preserve the historical ones, and stop after the output file is complete.
