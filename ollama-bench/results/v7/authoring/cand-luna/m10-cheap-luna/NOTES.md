Failure mode 10, variant (b): working with the environment as it is.

Distinguishing condition: the requested values are in UTF-8 files whose CRLF byte structure must
survive the edit. A text-only rewrite that silently normalizes newlines or encoding is wrong even
when the visible words look right.

The grader reads bytes, requires CRLF without lone LF bytes, checks the exact UTF-8 values and
unchanged lines, and tolerates only whitespace boundaries that the prompt does not specify. This
distinguishes a correct byte-preserving edit from a plausible LF rewrite. The reference values and
all original bytes are directly present under seed/.

Answer polarity: positive (both values are updated).

Near-miss probe table (all from the correct answer):

| probe | outcome |
| --- | --- |
| no trailing newline | clean: correct |
| two trailing newlines | clean: correct |
| CRLF line endings | clean: correct |
| one leading blank line | clean: correct |
| trailing spaces on one line | clean: correct |
| reordered INI lines (order is not fixed) | clean: correct |
| reference solution | correct |
| wrong-but-plausible incomplete update | confidently_wrong |
| untouched sandbox | visibly_failed |
