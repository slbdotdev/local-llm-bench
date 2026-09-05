#!/usr/bin/env python3
"""t04/cand-5 scored a correct identification as confidently_wrong on an exact span equality.

Diagnosis. The checker required the cited span to be EXACTLY `(6, 20)`:

    _ora_check("contiguous implementation span", lambda: _ora_parsed is not None and
                _ora_parsed[1] == (6, 20))

`app/request_path.py` lines 6-20 are `def process_login(...)` (6), its docstring (7) and the
body (8-20). The prompt asks for "one contiguous line span in one current runtime file that
contains the largest part of the implementation itself, **not a caller, helper declaration,
configuration value, documentation, comment, or test**". That wording actively invites a model
to exclude the `def` line and the docstring, so `8-20` is a defensible reading of the same
correct finding -- and it was scored `FAIL 4/5 confidently_wrong`, the worst label the
instrument has, for a boundary choice the prompt itself made ambiguous. Measured across the
round-3 reference arms: every arm that cited `6-20` passed and every arm that cited `8-20`
failed, with identical PATH and an explanation naming all three behaviours.

That is checker format bias wearing the costume of comprehension, and under plan section 6 --
where the confidently-wrong rate outranks pass rate -- it is the single most damaging kind of
defect this suite can carry.

Fix. Accept any contiguous span that
  * lies inside the function, `6 <= first` and `last <= 20`, so a shotgun "1-100" still fails;
  * and actually covers all three required operations: the pre-verification lockout check
    (lines 9-11), the 60-second record (13-17) and the clear on success (18) -- i.e.
    `first <= 9 and last >= 18`.

Everything else stays strict. Idempotent.
"""
import sys

OLD = '''_ora_check("contiguous implementation span", lambda: _ora_parsed is not None and
            _ora_parsed[1] == (6, 20))'''

NEW = '''# The span must sit inside process_login (lines 6-20) and cover all three required
# operations: the pre-verification lockout check (9-11), the 60 s record (13-17) and the
# clear on success (18). The prompt tells the model to cite "the implementation itself, not
# a ... declaration", so excluding the `def` line and the docstring is a correct reading and
# must not be scored as a wrong answer. A shotgun span still fails on the 6 <= first bound.
_ora_check("contiguous implementation span", lambda: _ora_parsed is not None and
            isinstance(_ora_parsed[1], tuple) and
            6 <= _ora_parsed[1][0] <= 9 and 18 <= _ora_parsed[1][1] <= 20)'''

for path in sys.argv[1:]:
    src = open(path, encoding="utf-8").read()
    if "must not be scored as a wrong answer" in src:
        print(f"{path}: already patched")
        continue
    if OLD not in src:
        print(f"{path}: NO MATCH -- inspect by hand")
        continue
    open(path, "w", encoding="utf-8", newline="\n").write(src.replace(OLD, NEW, 1))
    print(f"{path}: patched (t04 span equality)")
