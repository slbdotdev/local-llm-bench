Work in the empty sandbox and implement the requested transformation.

First inspect the seed-provided specification material. Find the Python specification file by looking for the module docstring that describes the transformation and contains worked examples, and read that file completely. It is the source of truth for every lexical boundary, escaping rule, stopping rule, and preservation requirement; do not invent additional parsing behavior.

Create `solution.py` in the sandbox root with the one specified public function:

```python
def transform(text: str) -> str:
    ...
```

The hidden checker will import it and call `transform` with ordinary strings. Use only the Python standard library. Keep the transformation deterministic, return exactly the type required by the specification, preserve all characters the specification says to preserve, and do not modify the supplied seed files. You do not need to write a command-line interface or tests.
