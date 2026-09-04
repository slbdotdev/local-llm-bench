import os
import inspect
import sys

root = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(root, "ref"))
import event_core
import event_view

examples = [
    ("doctest", lambda: __import__("doctest").testmod(event_core, verbose=False).failed == 0),
    ("signature", lambda: list(inspect.signature(event_core.publish_event).parameters) == ["payload", "kind", "channel", "stamped"] and inspect.signature(event_core.publish_event).parameters["channel"].kind is inspect.Parameter.KEYWORD_ONLY and inspect.signature(event_core.publish_event).parameters["stamped"].kind is inspect.Parameter.KEYWORD_ONLY),
    ("direct", lambda: event_core.publish_event("payload", "kind", channel="ops") == "ops|kind|payload"),
    ("stamped", lambda: event_core.publish_event("payload", "kind", channel="ops", stamped=True) == "STAMP ops|kind|payload"),
    ("batch", lambda: event_core.batch([("a", "one"), ("b", "two")]) == ["main|a|one", "main|b|two"]),
    ("batch stamped", lambda: event_core.batch([("a", "one"), ("b", "two")], channel="audit", stamped=True) == ["STAMP audit|a|one", "STAMP audit|b|two"]),
    ("reflection", lambda: event_view.reflected(("notice", "cache"), channel="audit", stamped=True) == "STAMP audit|notice|cache"),
]

bad = []
for name, fn in examples:
    try:
        ok = bool(fn())
    except Exception:
        ok = False
    print(name, "ok" if ok else "FAIL")
    if not ok:
        bad.append(name)
sys.exit(1 if bad else 0)
