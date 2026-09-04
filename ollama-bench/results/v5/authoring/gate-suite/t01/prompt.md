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

**"Standalone occurrence" means:** the exact literal path string above, appearing anywhere in a
`.md` file — running prose, a list item, a link target, a code span, a fenced code block, a block
quotation or a comment all count equally, and none of them is excluded. What does **not** count is
the string appearing as a proper prefix or substring of a longer path (for example a path that
continues with a further segment or a file-extension suffix), or any near-miss that is not
character-for-character the path above.

Search all `.md` files recursively. Exactly four standalone occurrences exist. Ignore the new
path and similar-looking text that is not the exact old path. A sweep is not permission to edit
the documents: your only deliverable is the classification file.

Create `reference_audit.txt` with exactly four lines, ordered by relative source-file path and
then ascending 1-based line number. Use no header or other text. Each line must have exactly five
fields separated by literal tab characters (U+0009):

`ACTION<TAB>RELATIVE_FILE<TAB>LINE<TAB>OLD_PATH<TAB>REPLACEMENT`

Use `UPDATE` or `LEAVE` exactly for `ACTION`. Use a POSIX path relative to the workspace root for
`RELATIVE_FILE`, without `./` or `seed/`. Use a positive decimal line number.

`OLD_PATH` and `REPLACEMENT` are **copied verbatim from the two paths given at the top of this
task**, character for character. Do not normalise, shorten, rewrite or otherwise alter their
leading slashes or any other part of them. So `OLD_PATH` is always exactly the old path above;
`REPLACEMENT` is exactly the new path above for `UPDATE`, and exactly `-` for `LEAVE`.

Here are syntax examples. In this block `<TAB>` visibly stands for one literal tab and must be
replaced by that tab in the output:

```text
UPDATE<TAB>path/to/file.md<TAB>8<TAB>//example/old/thing.md<TAB>//example/new/thing.md
LEAVE<TAB>path/to/archive.md<TAB>19<TAB>//example/old/thing.md<TAB>-
```

The example paths are placeholders, not clues about the seed; note only that they are reproduced
unaltered in both fields, which is what your output must also do with the real paths. Use the four actual occurrences,
preserve the historical ones, and stop after the output file is complete.
