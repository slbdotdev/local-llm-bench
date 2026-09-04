import copy
import os
import sys
import threading


TOTAL = 24
fails = []
done = 0
_lock = threading.Lock()
_ora_exception = False
_ora_malformed = False
_ora_wrong = False


def check(name, fn):
    global done, _ora_exception, _ora_malformed, _ora_wrong
    try:
        result = fn()
        if result is True:
            pass
        elif result is False:
            fails.append(name)
            _ora_wrong = True
        else:
            fails.append(name)
            _ora_malformed = True
    except Exception as exc:
        fails.append("%s raised %s" % (name, type(exc).__name__))
        _ora_exception = True
    with _lock:
        done += 1


def _ora_shape(value):
    if not isinstance(value, list):
        return False
    for group in value:
        if not isinstance(group, dict) or set(group) != {"group", "entries"}:
            return False
        if not isinstance(group["group"], str) or not isinstance(group["entries"], list):
            return False
        for entry in group["entries"]:
            if not isinstance(entry, dict) or set(entry) != {"key", "total", "occurrences"}:
                return False
            if (not isinstance(entry["key"], str)
                    or not isinstance(entry["total"], int)
                    or isinstance(entry["total"], bool)
                    or not isinstance(entry["occurrences"], int)
                    or isinstance(entry["occurrences"], bool)):
                return False
    return True


def _ora_transform(records):
    groups = []
    positions = {}
    keys = []
    for record in records:
        name = record["group"]
        if name not in positions:
            positions[name] = len(groups)
            groups.append({"group": name, "entries": []})
            keys.append({})
        group_index = positions[name]
        output = groups[group_index]["entries"]
        key_positions = keys[group_index]
        for item in record["entries"]:
            key = item["key"]
            if key not in key_positions:
                key_positions[key] = len(output)
                output.append({"key": key, "total": item["delta"], "occurrences": 1})
            else:
                previous = output[key_positions[key]]
                previous["total"] += item["delta"]
                previous["occurrences"] += 1
    return groups


_ORA_CASES = [
    ("empty input", []),
    ("single entry", [{"group": "b", "entries": [{"key": "x", "delta": 4}]}]),
    ("group first appearance order", [
        {"group": "z", "entries": []}, {"group": "a", "entries": []},
        {"group": "m", "entries": []},
    ]),
    ("repeated group", [
        {"group": "g", "entries": [{"key": "a", "delta": 1}]},
        {"group": "g", "entries": [{"key": "b", "delta": 2}]},
    ]),
    ("key first appearance order", [
        {"group": "g", "entries": [
            {"key": "z", "delta": 1}, {"key": "a", "delta": 2}, {"key": "m", "delta": 3},
        ]},
    ]),
    ("nonadjacent duplicate key", [
        {"group": "g", "entries": [
            {"key": "a", "delta": 1}, {"key": "b", "delta": 10}, {"key": "a", "delta": 2},
        ]},
    ]),
    ("duplicate across records", [
        {"group": "g", "entries": [{"key": "a", "delta": 5}]},
        {"group": "g", "entries": [{"key": "a", "delta": -8}]},
    ]),
    ("zero counts", [{"group": "g", "entries": [{"key": "a", "delta": 0}]}]),
    ("negative totals", [{"group": "g", "entries": [
        {"key": "a", "delta": -2}, {"key": "a", "delta": -3},
    ]}]),
    ("empty group", [{"group": "", "entries": [{"key": "x", "delta": 1}]}]),
    ("empty key", [{"group": "g", "entries": [{"key": "", "delta": 1}]}]),
    ("both empty", [{"group": "", "entries": [{"key": "", "delta": 0}]}]),
    ("empty record retained", [{"group": "g", "entries": []}]),
    ("empty record between duplicates", [
        {"group": "g", "entries": [{"key": "a", "delta": 1}]},
        {"group": "g", "entries": []},
        {"group": "g", "entries": [{"key": "b", "delta": 2}]},
    ]),
    ("same key separate groups", [
        {"group": "b", "entries": [{"key": "x", "delta": 1}]},
        {"group": "a", "entries": [{"key": "x", "delta": 2}]},
    ]),
    ("repeated equal deltas", [{"group": "g", "entries": [
        {"key": "a", "delta": 4}, {"key": "a", "delta": 4}, {"key": "a", "delta": 4},
    ]}]),
    ("mixed signs and keys", [{"group": "g", "entries": [
        {"key": "c", "delta": -1}, {"key": "a", "delta": 8},
        {"key": "c", "delta": 1}, {"key": "b", "delta": 0},
    ]}]),
    ("spaces are ordinary strings", [{"group": " ", "entries": [
        {"key": "a b", "delta": 3}, {"key": "a b", "delta": -1},
    ]}]),
    ("many group returns", [
        {"group": "c", "entries": [{"key": "q", "delta": 1}]},
        {"group": "a", "entries": [{"key": "q", "delta": 2}]},
        {"group": "c", "entries": [{"key": "p", "delta": 3}]},
        {"group": "b", "entries": []},
        {"group": "a", "entries": [{"key": "p", "delta": 4}]},
    ]),
    ("large integer", [{"group": "g", "entries": [
        {"key": "n", "delta": 10 ** 18}, {"key": "n", "delta": -1},
    ]}]),
    ("empty input does not alias", []),
    ("input remains unchanged", [
        {"group": "g", "entries": [{"key": "a", "delta": 2}]},
    ]),
    ("all empty records", [
        {"group": "b", "entries": []}, {"group": "", "entries": []},
        {"group": "b", "entries": []},
    ]),
    ("full combination", [
        {"group": "z", "entries": [
            {"key": "", "delta": 0}, {"key": "k", "delta": 2}, {"key": "", "delta": -2},
        ]},
        {"group": "a", "entries": []},
        {"group": "z", "entries": [{"key": "k", "delta": 5}, {"key": "j", "delta": 0}]},
    ]),
]


def _ora_watchdog():
    n = max(0, min(TOTAL, done - len(fails)))
    print("SCORE %d/%d" % (n, TOTAL))
    print("FAIL ['grader timed out (candidate too slow or hung)']")
    print("VERDICT visibly_failed")
    sys.stdout.flush()
    os._exit(1)


_timer = threading.Timer(45.0, _ora_watchdog)
_timer.daemon = True
_timer.start()

try:
    import solution as _candidate
except Exception as exc:
    fails = ["import failed: %s" % type(exc).__name__] + ["not run"] * (TOTAL - 1)
    _timer.cancel()
    print("SCORE 0/%d" % TOTAL)
    print("FAIL", fails[:10])
    print("VERDICT visibly_failed")
    sys.exit(1)


def _ora_run_case(records):
    before = copy.deepcopy(records)
    result = _candidate.transform(records)
    if records != before or not _ora_shape(result):
        return None
    return result == _ora_transform(before)


for _name, _records in _ORA_CASES:
    check(_name, lambda records=_records: _ora_run_case(records))

_timer.cancel()
n = max(0, min(TOTAL, TOTAL - len(fails)))
print("SCORE %d/%d" % (n, TOTAL))
if fails:
    print("FAIL", fails[:10])
    if _ora_exception or _ora_malformed:
        print("VERDICT visibly_failed")
    elif _ora_wrong:
        print("VERDICT confidently_wrong")
    else:
        print("VERDICT visibly_failed")
    sys.exit(1)
print("PASS")
print("VERDICT correct")
sys.exit(0)
