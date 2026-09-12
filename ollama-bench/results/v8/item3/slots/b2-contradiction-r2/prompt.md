# Contradiction hunt: a draft against the record

`authority/` holds the record. `draft/handoff.md` is a draft someone wrote from it by hand. The
record is authoritative wherever the two disagree.

Find every figure in the draft that the record **contradicts**.

A figure is contradicted only when the record states a different value for **the same thing
under the same qualifier**. A figure the record also states — for the rung, quant, window,
instrument, date or unit the draft names — is **not** a contradiction, even when the record
states some different value for the same bare key somewhere else under a different qualifier.
The record carries more than one value for several keys on purpose, because they describe
different rungs, different instruments, different cell sets or a figure before and after a
correction. Reading the key and not its qualifier will produce a list of things that are not
wrong.

Write `contradictions.txt` in the root of the workspace:

- one contradiction per line, in the form `- <what it is>: <the figure the draft gives>`;
- write the draft's figure exactly as the draft gives it;
- **list only the contradictions.** Do not list a figure you checked and cleared, and do not
  explain your reasoning in the file: a cleared figure on a line in this file is read as a
  reported contradiction and counts against you;
- nothing else in the file: no heading, no preamble, no counts. It may end with a newline or not,
  and the order of the lines does not matter.

**Every number and identifier you write must appear somewhere in `authority/` or
`draft/handoff.md`.** Do not compute, round, convert or infer a number that is not there.

Do not modify or delete any file under `authority/` or `draft/`. Create no file other than
`contradictions.txt`.

Work until the list is complete, then stop.
