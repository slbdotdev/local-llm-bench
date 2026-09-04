Candidate 1 is for careful reading of a compact transformation contract. The main traps are that LF is the only record separator, empty records are meaningful, repeated leading slashes collapse to one, trailing slashes are conditionally preserved, and `..` has separate absolute/relative behavior. A conventional `posixpath.normpath` implementation is a plausible near-miss because it handles ordinary dot segments correctly while differing at the specified boundaries.

Selfcheck outcome: exit 0; examples 01 through 12 each printed `ok`; final line was `all examples passed`.

Reference checker outcome (exit 0):

```
SCORE 24/24
PASS
VERDICT correct
```

Near-miss checker outcome (exit 1):

```
SCORE 15/24
FAIL ['empty record', 'empty records around LF', 'ending LF', 'trailing slash', 'trailing slash after parent', 'double leading slash', 'carriage return is data', 'LF with absolute record', 'ordinary named dot']
VERDICT confidently_wrong
```

Empty-sandbox checker outcome (exit 1):

```
SCORE 0/24
FAIL ['import failed: ModuleNotFoundError', 'not run', 'not run', 'not run', 'not run', 'not run', 'not run', 'not run', 'not run', 'not run']
VERDICT visibly_failed
```

Reference size: 33 lines, 104 whitespace-delimited words, roughly 250 output tokens. No known uncertainty.
