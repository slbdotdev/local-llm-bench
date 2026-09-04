Work in the empty sandbox and implement the requested transformation.

First inspect the seed-provided specification material. Find the Python specification file by looking for the module docstring that describes the transformation and contains worked examples, and read that file completely. It is the source of truth for every boundary condition; do not invent additional normalization rules.

Create `solution.py` with the one specified public function, using only the Python standard library:

```python
def transform(text: str) -> str:
    ...
```

The hidden tests will import `solution.py` and call `transform` with ordinary strings. Keep the implementation deterministic, preserve text that the specification says to preserve, and return a string. Do not modify the seed files. You do not need to write a command-line interface or tests.
