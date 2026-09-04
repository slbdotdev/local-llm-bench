# Audit references after a path move

The documentation workspace has been copied into the current directory. Do not modify any
document. Find every exact, standalone occurrence of this old path in Markdown files:

`/srv/ops/oncall/handbook.md`

It moved to:

`/srv/ops/oncall/runbook.md`

Classify every occurrence by the meaning of the surrounding text:

- `UPDATE` is a live, currently applicable pointer or instruction that should use the new path.
- `LEAVE` is historical evidence: a dated migration note, archive, postmortem, incident account,
  or quoted record of what someone used before the move. Historical evidence must not be rewritten.

Search every `.md` file recursively. The exact old path may occur in prose, a link, a table, an
inline code span, or a fenced code block; all of those count. Do not count the new path, a path
with an extra suffix such as `.bak`, a path that continues with another segment, or any other
near-match. An exact occurrence in a current document can still be `LEAVE` if its surrounding
sentence is explicitly historical. There are exactly seven occurrences.

Create `reference_audit.txt` with exactly seven lines, one line per occurrence, ordered by POSIX
relative source-file path and then ascending 1-based line number. Do not write a header, bullets,
code fences, or any other content. Each line has exactly five fields separated by literal tab
characters (U+0009):

`ACTION<TAB>RELATIVE_FILE<TAB>LINE<TAB>OLD_PATH<TAB>REPLACEMENT`

`ACTION` must be exactly `UPDATE` or `LEAVE`. `RELATIVE_FILE` is the POSIX path from the workspace
root, without a leading `./`, without a `seed/` prefix, and without parent-directory components.
`LINE` is the positive decimal source line number. Copy `OLD_PATH` exactly as shown above. For an
`UPDATE`, `REPLACEMENT` is the new path exactly as shown above; for a `LEAVE`, it is exactly `-`.

The visible marker `<TAB>` in the format description means one literal tab in the output; do not
write the marker text. Use the actual files, coordinates, and classifications you discover. Work
until the output is complete, then stop.
