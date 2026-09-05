import json
import sys

sys.path.insert(0, "ref")
import releaseplan


def compact(value):
    return json.dumps(value, separators=(",", ":"))


catalog = compact([{"name": "app", "version": "9.9", "deps": [],
                   "platforms": ["*"], "priority": 1}])
lock = compact([{"name": "app", "version": "1.0", "deps": []}])
history = "[]"

examples = [
    ("positive one-package plan", releaseplan.build_plan(
        catalog, lock, "[]", history, "app", "linux", "2025-03"),
     "release=2025-03 platform=linux\ntarget=app\n- app@1.0 requires=\n"),
    ("negative active deny", releaseplan.build_plan(
        catalog, lock,
        compact([{"package": "app", "platform": "*", "effect": "deny",
                  "start": "0000-00", "end": "9999-99", "revision": 1}]),
        history, "app", "linux", "2025-03"), ""),
]

failed = False
for name, actual, expected in examples:
    ok = actual == expected
    print(name + ": " + ("PASS" if ok else "FAIL"))
    if not ok:
        failed = True
sys.exit(1 if failed else 0)
