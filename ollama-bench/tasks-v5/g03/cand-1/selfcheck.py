import os
import sys

root = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(root, "ref"))
import badge_core
import badge_registry

examples = [
    ("doctest", lambda: badge_core.make_badge("Ada", tone="warm") == "Ada<warm>"),
    ("direct", lambda: badge_core.make_badge("A", tone="red") == "A<red>"),
    ("batch", lambda: badge_core.batch(["A", "B"], tone="blue") == ["A<blue>", "B<blue>"]),
    ("reflection", lambda: badge_registry.reflect("C", tone="green") == "C<green>"),
]

bad = []
for name, fn in examples:
    ok = bool(fn())
    print(name, "ok" if ok else "FAIL")
    if not ok:
        bad.append(name)
sys.exit(1 if bad else 0)
