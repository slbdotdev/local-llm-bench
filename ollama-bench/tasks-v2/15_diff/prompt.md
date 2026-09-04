Create `mydiff.py` in the current directory with two functions (no `difflib`):

- `diff(a: list[str], b: list[str]) -> list[tuple[str, str]]`: a minimal edit script turning `a` into `b`, as a list of `(op, line)` pairs where `op` is `"="` (line kept), `"-"` (line removed from `a`), or `"+"` (line added from `b`). The script must be minimal: the number of `-` plus `+` ops must equal `len(a) + len(b) - 2 * LCS(a, b)`, where LCS is the longest common subsequence length. Kept lines must appear in the same relative order they have in both inputs. Any minimal script is accepted.
- `apply(a: list[str], script) -> list[str]`: apply a script produced by `diff` to `a`, returning `b`. Raise `ValueError` if the script does not match `a` (a `=` or `-` op whose line differs from the current line of `a`, or leftover lines).

Use an O(len(a) * len(b)) dynamic programme or better; inputs up to 400 lines each must finish in well under a second.

Example: `diff(["a","b","c"], ["a","c","d"])` could return `[("=","a"),("-","b"),("=","c"),("+","d")]`.

Write a few quick checks of your own and run them with `python`, then reply "done".
