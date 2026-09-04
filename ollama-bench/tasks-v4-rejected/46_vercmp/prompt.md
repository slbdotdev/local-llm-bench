Create `vercmp.py`: a version-string comparator and constraint-range evaluator.

```python
class VersionError(ValueError): ...          # every malformed input raises this

def parse(text: str) -> dict                 # {"epoch": int, "release": list,
                                             #  "pre": list | None, "build": str | None}
def compare(a: str, b: str) -> int           # -1, 0 or 1
def satisfies(version: str, constraint: str) -> bool
def best_match(versions: list[str], constraint: str) -> str | None
def sort_versions(versions: list[str]) -> list[str]
```

Anything that is not a `str` where a `str` is required raises `VersionError`.

## 1. Version grammar

```
version := [ EPOCH ":" ] RELEASE [ "-" PRERELEASE ] [ "+" BUILD ]
```

Split the string in exactly this order: first at the FIRST `:` (epoch), then at the
FIRST `+` in what remains (build), then at the FIRST `-` in what remains (prerelease).
Whatever is left is the release. There is no whitespace anywhere in a version string;
whitespace (or any other character not allowed below) makes it malformed.

* `EPOCH` is one or more ASCII digits. Leading zeros are allowed (`01:` means epoch 1).
  If there is no `EPOCH:` prefix the epoch is `0`, so `0:1.2.3` and `1.2.3` are the SAME
  version and `compare("0:1.2.3", "1.2.3") == 0`.
* `RELEASE` is one or more segments separated by `.`. Each segment must be non-empty and
  made only of ASCII alphanumerics `[0-9A-Za-z]`. A segment of all digits is a NUMERIC
  segment and `parse` reports it as an `int` (leading zeros allowed: `1.02.3` parses to
  `[1, 2, 3]`); any other segment is an ALPHANUMERIC segment and `parse` reports it as
  the `str` exactly as written.
* `PRERELEASE` is one or more identifiers separated by `.`, each identifier non-empty and
  made only of `[0-9A-Za-z]`, reported by `parse` as a list using the same int/str rule as
  release segments (`1.0.0-01.beta` gives `pre == [1, "beta"]`). `pre` is `None` when there
  is no `-` part.
* `BUILD` is one or more identifiers separated by `.`, each identifier non-empty and made
  only of `[0-9A-Za-z-]` (hyphens ARE allowed inside build identifiers, because build is
  split off before the prerelease `-`). `parse` reports `build` as the raw text after the
  `+`, unchanged, or `None` when there is no `+` part.
* Any empty piece is malformed: `""`, `"1."`, `".1"`, `"1..2"`, `"1.0-"`, `"1.0+"`,
  `":1.0"`, `"a:1.0"`, `"1.0-alpha+"`, `"1.0-+x"` all raise `VersionError`.
  A second `:` is malformed too (`"1:2:3"`), because `2:3` is not a valid release.

## 2. Total ordering (`compare`)

`compare(a, b)` returns `-1` if `a` sorts before `b`, `1` if after, `0` if they are equal.

1. Compare the epochs as integers. Higher epoch is greater.
2. Compare the release segment lists. If they have different lengths, ZERO-PAD the shorter
   one on the right with NUMERIC `0` segments until both have the same length; then compare
   segment by segment, left to right. So `1.0` and `1.0.0` and `1` are all EQUAL, while
   `1.0.a` is GREATER than `1.0` (because `1.0` pads to `1.0.0` and numeric `0` is lower
   than the alphanumeric `a` -- see the next rule).
3. Two segments compare like this: two numeric segments compare as integers; two
   alphanumeric segments compare as ASCII strings (so `"Z" < "a"`, uppercase first); a
   numeric segment is always LOWER than an alphanumeric segment.
4. If epoch and release are equal, a version WITHOUT a prerelease is GREATER than one with
   a prerelease: `1.0.0-alpha < 1.0.0`. If neither has one, they are equal.
5. If both have a prerelease, compare the identifier lists element by element with the same
   segment rule as step 3 (numeric < alphanumeric; `1.0.0-1 < 1.0.0-alpha`). NO zero-padding
   here: if every compared identifier is equal, the LONGER list is greater
   (`1.0.0-alpha < 1.0.0-alpha.0 < 1.0.0-alpha.beta`).
6. BUILD metadata is completely ignored by the ordering: `compare("1.0.0+a", "1.0.0+zzz")`
   and `compare("1.0.0", "1.0.0+9")` are both `0`. It still has to parse.

## 3. Constraints

```
constraint := and_list ( "||" and_list )*
and_list   := comparator ( "," comparator )*
```

Before parsing, delete every ASCII whitespace character (space, tab, newline, `\r`, `\f`,
`\v`) from the constraint string, so `">= 1.2.3 , < 2.0.0"` is the same as
`">=1.2.3,<2.0.0"`. An empty constraint, an empty `and_list` (`"1.0,,2.0"`, `"1.0,"`,
`"||1.0"`) or an empty comparator is a `VersionError`.

A comparator is an operator followed by an operand version, or one of the wildcard forms.
The operators are `>=`, `>`, `<=`, `<`, `=`, `==`, `!=`, `^`, `~`. An operand with no
operator at all means `=`. `=` and `==` mean the same thing. `=`, `==`, `!=`, `>=`, `>`,
`<=` and `<` take any valid version as operand (build metadata allowed and ignored) and
test `compare(version, operand)` in the obvious way.

**Wildcards.** The only wildcard forms are exactly `*`, `N.*` and `N.M.*`, where `N` and `M`
are strings of ASCII digits. No operator, no epoch, no prerelease and no build may be
combined with a wildcard (`>=1.2.*`, `1:1.*`, `1.*.3`, `*.1`, `1.2.3.*` all raise
`VersionError`). They desugar to:

* `*`        matches every version (no bounds at all).
* `N.*`      becomes `>=N.0.0, <(N+1).0.0`
* `N.M.*`    becomes `>=N.M.0, <N.(M+1).0`

**Caret and tilde.** The operand of `^` or `~` must have an all-NUMERIC release of 1, 2 or 3
segments; it may carry an epoch, a prerelease and build metadata. Anything else (an
alphanumeric segment, 4 or more segments) raises `VersionError`. Write the operand as
`E:a[.b[.c]]`. The LOWER bound is `>=` the operand itself, zero-filled to three segments,
keeping its epoch and its prerelease if it has one. The UPPER bound is `<` the version shown
below, with the same epoch and never a prerelease. Whether `b` and `c` were actually WRITTEN
matters:

* `^a`      with a != 0 gives `<(a+1).0.0`; `^0` gives `<1.0.0`
* `^a.b`    with a != 0 gives `<(a+1).0.0`; `^0.b` with b != 0 gives `<0.(b+1).0`;
  `^0.0` gives `<0.1.0`
* `^a.b.c`  with a != 0 gives `<(a+1).0.0`; `^0.b.c` with b != 0 gives `<0.(b+1).0`;
  `^0.0.c` gives `<0.0.(c+1)`
* `~a`      gives `>=a.0.0, <(a+1).0.0`
* `~a.b`    gives `>=a.b.0, <a.(b+1).0`
* `~a.b.c`  gives `>=a.b.c, <a.(b+1).0`

So `^1.2.3` is `>=1.2.3,<2.0.0`, `^0.2.3` is `>=0.2.3,<0.3.0`, `^0.0.3` is `>=0.0.3,<0.0.4`,
`~1.2` is `>=1.2.0,<1.3.0` and `~1.2.3` is `>=1.2.3,<1.3.0`.

**Prereleases.** `satisfies(version, constraint)` is `True` when at least one `and_list`
accepts `version`. An `and_list` accepts `version` when BOTH of these hold:

1. **The prerelease gate.** If `version` HAS a prerelease, then at least one comparator in
   THAT SAME `and_list` must have been written with an operand version that (a) itself has a
   prerelease and (b) has the same epoch and the same release as `version` (release equality
   uses the zero-padding of rule 2.2). Otherwise the `and_list` rejects `version` outright,
   whatever the individual comparisons say. Only operands the user actually WROTE count: the
   generated upper bound of a `^`/`~`/wildcard never has a prerelease, and neither does the
   generated lower bound of a wildcard. An operand of a `!=` comparator does count. If
   `version` has no prerelease, this gate does nothing.
2. Every comparator in the `and_list` is satisfied, using `compare` (so build metadata never
   matters, and `=1.0.0+x` accepts `1.0.0+y`).

## 4. `best_match` and `sort_versions`

`sort_versions(versions)` returns a NEW list holding the same strings, sorted ascending by
`compare`. The sort is STABLE: strings that compare equal (for example versions differing
only in build metadata, or `1.0` and `1.0.0`) keep their relative order from the input.

`best_match(versions, constraint)` returns the greatest version in `versions` that satisfies
`constraint`, as the ORIGINAL string from the list, or `None` if none does. If several
matching versions compare equal, return the one that appears EARLIEST in `versions`.

Both raise `VersionError` if any element is not a valid version string, and `best_match`
also raises it for a malformed constraint.

## Examples

```python
parse("2:1.02.3-beta.4+build.1") == {"epoch": 2, "release": [1, 2, 3],
                                     "pre": ["beta", 4], "build": "build.1"}
compare("1.2.3", "1.10.0") == -1
compare("1.0.0-alpha", "1.0.0") == -1

satisfies("1.4.2", "^1.2.3") is True
satisfies("2.0.0", "^1.2.3") is False
satisfies("1.2.9", ">=1.0.0,<1.2.0 || ~1.2.5") is True

best_match(["1.0.0", "1.4.0", "2.1.0"], "1.*") == "1.4.0"
sort_versions(["1.10", "1.2", "1.2.0-rc"]) == ["1.2.0-rc", "1.2", "1.10"]
```

Write a few quick checks of your own and run them with `python`, then reply "done".
