# Implement the current release transformation

Work in the empty sandbox and create `solution.py`. It must define exactly one
public function:

```python
def transform(records):
    ...
```

The supplied `seed/` directory contains a small, versioned Python project. Read
the complete material before coding: the current modules, configuration data,
call sites, fixtures, and the historical notes. The behavior is deliberately
distributed across those sources. Reconcile the current release behavior with
the history; superseded rules are included because they explain tempting but
wrong implementations. The fixtures show the intended boundary cases.

`records` is always a valid list of dictionaries in the input shape established
by the project. Return the exact JSON-like output shape established there. The
transformation must be deterministic, must not mutate `records`, and must return
fresh lists and dictionaries. Use only the Python standard library. Do not print,
use the network, inspect files at runtime, or rely on anything outside the
sandbox.

The checker imports only `solution.py` and calls `transform`; it ignores any
tests or command-line program you write. Hidden cases combine repeated source
aliases, empty records, repeated keys, ignored actions, negative and zero
deltas, empty labels, and labels that repeat with different spelling. Preserve
the ordering rules exactly, including the order of sources, entries, and labels.

For orientation, one current-release input is:

```python
[{"source": "svc", "changes": [{"key": " Err ", "delta": 3,
  "action": "add", "labels": ["Urgent", "urgent", " "]}]}]
```

It produces:

```python
[{"source": "service", "entries": [{"key": "error", "total": 3,
  "occurrences": 1, "labels": ["urgent"]}]}]
```

Do not edit the supplied seed files. No explanation or test file is required in
the sandbox; leave the implementation in `solution.py`.
