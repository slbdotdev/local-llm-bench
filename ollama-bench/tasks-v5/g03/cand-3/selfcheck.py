import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "ref"))
import note_core
import note_view

examples = [
    ("doctest", lambda: note_core.write_note("hello", channel="chat") == "chat:hello"),
    ("normal", lambda: note_core.write_note("hello", channel="chat") == "chat:hello"),
    ("urgent", lambda: note_core.write_note("hello", channel="chat", urgent=True) == "URGENT chat:hello"),
    ("bundle", lambda: note_core.bundle(["a", "b"], channel="inbox", urgent=True) == ["URGENT inbox:a", "URGENT inbox:b"]),
    ("reflection", lambda: note_view.reflected("x", channel="audit", urgent=True) == "URGENT audit:x"),
]

bad = []
for name, fn in examples:
    ok = bool(fn())
    print(name, "ok" if ok else "FAIL")
    if not ok:
        bad.append(name)
sys.exit(1 if bad else 0)
