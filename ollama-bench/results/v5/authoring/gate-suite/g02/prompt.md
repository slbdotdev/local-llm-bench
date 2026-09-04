# Fix the bounded manifest migration

The sandbox contains `manifest_migrate.py` and `test_manifest_migrate.py`. One
test fails. Find the localized defect and fix the implementation so all tests
pass. Do not edit, delete, or weaken the tests; the hidden checker uses an
independent test suite. Use only the standard library.

This is a deliberately bounded transformation. `migrate(text, mapping)` renames
exact `key: value` record keys in the editable prefix. The literal line
`# FROZEN BELOW`, when present, begins an immutable suffix: the marker and
every byte after it must be returned unchanged. Values, comments, blank lines,
and keys that merely have the old key as a prefix are not renamed.

Examples:

```python
manifest_migrate.migrate("title: old\n# FROZEN BELOW\nold: keep\n", {"title": "name", "old": "new"})
# "name: old\n# FROZEN BELOW\nold: keep\n"

manifest_migrate.migrate("old.extra: a\nold: b\n", {"old": "new"})
# "old.extra: a\nnew: b\n"

manifest_migrate.migrate("# note old: x\n", {"old": "new"})
# "# note old: x\n"
```

Run `python test_manifest_migrate.py`, make the smallest
correct implementation change, and rerun the complete suite.
