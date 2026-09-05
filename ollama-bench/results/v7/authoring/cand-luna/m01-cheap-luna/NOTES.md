Failure mode 1: a requirement stated once, far from the code.

Distinguishing condition: a model that follows only the schema module will omit or incorrectly
implement the new publishing operation, while the policy material elsewhere in the tree requires
descending order only for that public view; the grader also checks that internal and envelope
snapshots stay ascending.

The grader imports the implementation and checks all three orderings, so a plausible global
reversal is rejected. An untouched source is visibly_failed; a changed but still wrong source is
confidently_wrong. The reference answer's values (the two key orders and the schema source
location) are all stated or directly represented in seed/.

Answer polarity: positive (the implementation is fixed).

Near-miss probe table (all from the correct answer):

| probe | outcome |
| --- | --- |
| no trailing newline | clean: correct |
| two trailing newlines | clean: correct |
| CRLF line endings | clean: correct |
| one leading blank line | clean: correct |
| trailing spaces on one line | clean: correct |
| ordering violation (prompt fixes order) | clean: confidently_wrong |
| reference solution | correct |
| wrong-but-plausible insertion-order answer | confidently_wrong |
| untouched sandbox | visibly_failed |
