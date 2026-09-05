# Fix the import source transformer

The sandbox contains `imports.py` and `test_imports.py`. Exactly one test is
failing. Diagnose the localized implementation bug and fix the module so the
entire test suite passes. Edit only implementation code: do not edit or delete
tests, and do not add dependencies. The checker runs its own tests.

`rewrite_source(source, mapping)` must rewrite mapped absolute module prefixes
inside Python `import ...` and `from ... import ...` statements, while leaving
comments, string literals, relative imports, aliases, formatting, and
similarly-prefixed module names alone. It is a source-to-source transformation,
so preserve every character outside the module name being changed.

Examples:

```python
imports.rewrite_source("from oldpkg.widgets import Button\n", {"oldpkg": "newpkg"})
# "from newpkg.widgets import Button\n"

imports.rewrite_source('# import oldpkg\nvalue = "oldpkg"\nimport oldpkg\n', {"oldpkg": "newpkg"})
# '# import oldpkg\nvalue = "oldpkg"\nimport newpkg\n'

imports.rewrite_source("import oldpkgx\n", {"oldpkg": "newpkg"})
# "import oldpkgx\n"
```

Run `python test_imports.py` before and after the smallest
correct fix.
