import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "ref"))
import stitch_base
import stitch_view

examples = [
    ("doctest", lambda: stitch_base.merge_bits("right", "left", glue=":") == "[left:right]"),
    ("direct", lambda: stitch_base.merge_bits("b", "a", glue=":") == "[a:b]"),
    ("row", lambda: stitch_base.make_row([("a", "b"), ("c", "d")]) == ["[a-b]", "[c-d]"]),
    ("reflection", lambda: stitch_view.reflected(("x", "y"), glue="/") == "[y/x]"),
]

bad = []
for name, fn in examples:
    ok = bool(fn())
    print(name, "ok" if ok else "FAIL")
    if not ok:
        bad.append(name)
sys.exit(1 if bad else 0)
