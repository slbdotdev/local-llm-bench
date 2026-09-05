# Fix the call-site source transformer

The sandbox contains `calls.py` and its tests. Exactly one test is failing.
Find the localized implementation defect and fix the module so the complete
test suite passes. Do not edit, delete, or weaken the tests; the checker uses
an independent copy of them. Use only the standard library.

`rewrite_calls(source, mapping)` must rename an exact dotted callee in Python
source. A callee is a maximal sequence of `NAME` tokens joined by dots whose
next token is `(`. Match the whole sequence exactly: a mapping for `oldpkg.run`
does not match `oldpkg.runner`, `oldpkg.run.extra`, or a subexpression inside
`obj.oldpkg.run()`. Rewrite only call sites; ordinary attribute access,
definitions, comments, and string literals stay unchanged. A newline that ends
the statement means the name is not a call. Preserve every character outside
the callee expression, including formatting and line endings.

The public helpers must retain their documented behavior too: `called_names`
lists maximal dotted callee names in source order, `call_count` counts all
calls or exact matches for a supplied name, and `rewrite_many` applies the same
mapping independently to each source string.

Examples:

```python
calls.rewrite_calls("oldpkg.run(1)\n", {"oldpkg.run": "newpkg.run"})
# "newpkg.run(1)\n"

calls.rewrite_calls('# oldpkg.run()\nvalue = oldpkg.run\noldpkg.run()\n',
                    {"oldpkg.run": "newpkg.call"})
# '# oldpkg.run()\nvalue = oldpkg.run\nnewpkg.call()\n'

calls.rewrite_calls("oldpkg.runner()\nobj.oldpkg.run()\n",
                    {"oldpkg.run": "newpkg.call"})
# "oldpkg.runner()\nobj.oldpkg.run()\n"
```

Run `python test_calls.py` before and after the smallest correct fix, then
rerun the complete suite.
