Failure mode 7: multi-file consistency.

Distinguishing condition: the public watermark factory must be renamed in all ordinary references,
including one configuration-template string that is easy to miss when following imports. A model
that edits the module, tests, and prose but misses that string leaves the old name behind.

The grader imports the renamed factory, checks behavior, scans every seed file for the old name,
and parses the template configuration. This separates a complete rename from the plausible
partial rename. The reference's names and limit value are all derivable from seed/.

Answer polarity: positive (the API is renamed).

Near-miss probe table (all from the correct answer):

| probe | outcome |
| --- | --- |
| no trailing newline | clean: correct |
| two trailing newlines | clean: correct |
| CRLF line endings | clean: correct |
| one leading blank line | clean: correct |
| trailing spaces on one line | clean: correct |
| reordered JSON keys (order is not fixed) | clean: correct |
| reference solution | correct |
| wrong-but-plausible incomplete rename | confidently_wrong |
| untouched sandbox | visibly_failed |
