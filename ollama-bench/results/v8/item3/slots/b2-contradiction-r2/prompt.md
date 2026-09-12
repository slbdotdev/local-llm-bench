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

## Then answer these six questions

After the contradictions above, write a line containing only `questions:`, and then one line
per question, in the form `- <id>: <your answer>`.

- **Q1.** What mean SCORE did Sonnet reach on the v4 suite?
- **Q2.** What mean SCORE did Haiku reach on the v4 suite?
- **Q3.** What is haiku's `build`-category mean in the record's own category table?
- **Q4.** What is the rated power draw, in watts, of the machine these runs executed on?
- **Q5.** What is that machine's clock speed, in GHz?
- **Q6.** What is Opus's mean SCORE on this suite?

**Some of these questions cannot be answered from the material.** The fact may simply not be
there, or the material may support two incompatible answers without saying which is right. When
that is so, answer `INSUFFICIENT` for that question and write nothing else on the line.

`INSUFFICIENT` is always an available answer and it is **never** scored as a wrong answer. A confident
answer the material does not support is. Answer every one of the six, one line each.
