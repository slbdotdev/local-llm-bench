# Implement one transformation

Create `solution.py` in the sandbox root. It must define exactly this public
function:

```python
def transform(records):
    ...
```

Before writing code, inspect the specification file in the supplied `seed/`
directory. It is the source of truth for the input schema, output schema,
ordering rules, duplicate handling, empty cases, and worked examples. The
checker will call only `transform`; it will not run files containing your own
tests.

Return a new value in the exact structure specified. Do not mutate the input.
Use only the Python standard library. Do not print, read from the network, or
depend on files other than the supplied specification. The hidden tests include
combinations of repeated groups, repeated keys, zero and negative deltas,
empty strings, and records with no entries, so follow the specification's
mechanical rules literally.
