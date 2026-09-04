# Fix the manifest rewriter

This sandbox contains a small Python module and its tests. One test is
currently failing. Find the localized implementation defect and fix the module
so the complete test suite passes. Do not edit, delete, or weaken the tests;
the checker uses an independent copy of them. Do not add dependencies.

Run `python test_manifest.py` while investigating. The public
API is in `manifest.py`; the input format is a sectioned text document with
`[section]` headers and `key=value` records. Comments beginning with `#`, blank
lines, the spelling of names, and the spacing around an existing `=` are
meaningful and should remain as the module's docstring specifies.

Examples of the intended behavior:

```python
manifest.rewrite("[Deploy]\nTimeout = 30\n", {("deploy", "timeout"): 45})
# "[Deploy]\nTimeout = 45\n"

manifest.rewrite("[app]\nname=demo\n", {("app", "port"): 80})
# "[app]\nname=demo\nport=80\n"

manifest.remove_keys("[a]\nx=1\ny=2\n[b]\nx=3\n", [("A", "X")])
# "[a]\ny=2\n[b]\nx=3\n"
```

Make the smallest correct code change, then rerun the full tests.
