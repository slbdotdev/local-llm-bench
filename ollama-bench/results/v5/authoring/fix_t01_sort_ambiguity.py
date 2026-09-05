"""State t01's output ordering exactly, because "ordered by path" is an unstated convention.

The defect. t01 requires its lines ordered by relative source-file path, and its checker
enforces Python's default string ordering -- byte order, so `README.md` precedes
`docs/links.md` because `R` (0x52) < `d` (0x64). The prompt never said which ordering it
meant. A reference model that produced all seven classifications CORRECTLY but sorted
case-insensitively scored 0/14 and was labelled `visibly_failed`.

That is a task defect, not difficulty. plan-2026-09-05 section 2.3 puts "unstated
conventions" among the things that are never on the difficulty ladder: a tighter output
contract is a legitimate lever only where the contract is stated exactly and is checkable.
So the prompt is made exact and the checker is left strict.

A changed prompt is a changed task, so any gate or discrimination row taken against the old
wording is invalidated by this edit and must be re-run.

Usage:  python3 fix_t01_sort_ambiguity.py <prompt.md> [<prompt.md> ...]
"""
import sys

NEW = ("ordered by the byte value of the POSIX relative source-file path\n"
       "(uppercase ASCII letters sort before lowercase, as `LC_ALL=C sort` and Python's default\n"
       "string ordering both do), and then by ascending 1-based line number.")

OLD = [
    "ordered by POSIX\nrelative source-file path and then ascending 1-based line number.",
    "ordered by relative source-file path and\nthen ascending 1-based line number.",
]
MARK = "byte value of the POSIX relative source-file path"


def patch(path):
    src = open(path, encoding="utf-8").read()
    if MARK in src:
        print(f"{path}: already patched")
        return 0
    for old in OLD:
        if old in src:
            open(path, "w", encoding="utf-8").write(src.replace(old, NEW, 1))
            print(f"{path}: patched")
            return 1
    print(f"{path}: NO MATCH -- inspect by hand")
    return -1


if __name__ == "__main__":
    bad = sum(1 for p in sys.argv[1:] if patch(p) < 0)
    sys.exit(1 if bad else 0)
