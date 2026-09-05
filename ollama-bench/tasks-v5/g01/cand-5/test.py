import copy
import os
import sys
import threading


_MULTIPLIERS = {"add": 1, "remove": -1, "adjust": 1, "hold": 0}
_SOURCES = {
    "core": "platform", "svc": "service", "web": "frontend",
    "ui": "frontend", "jobs": "worker", "batch": "worker",
}
_GLOBALS = {"err": "error", "warn": "warning", "lat": "latency",
            "dur": "duration", "cfg": "config"}
_LOCAL = {
    "platform": {"compile": "build", "compilation": "build"},
    "service": {"request": "requests", "req": "requests"},
    "frontend": {"paint": "render", "draw": "render"},
    "worker": {"job": "jobs", "task": "jobs"},
}

_ora_exception = False
_ora_malformed = False
_ora_wrong = False
_fails = []
_done = 0
_lock = threading.Lock()


def _ora_transform(records):
    result = []
    source_positions = {}
    entry_positions = []
    for record in records:
        raw = record["source"].strip(" ")
        source = _SOURCES.get(raw, raw)
        if source not in source_positions:
            source_positions[source] = len(result)
            result.append({"source": source, "entries": []})
            entry_positions.append({})
        bucket_index = source_positions[source]
        bucket = result[bucket_index]
        positions = entry_positions[bucket_index]
        for change in record["changes"]:
            action = change["action"]
            if action not in _MULTIPLIERS:
                continue
            key = change["key"].strip(" ").casefold()
            key = _GLOBALS.get(key, key)
            key = _LOCAL.get(source, {}).get(key, key)
            amount = change["delta"] * _MULTIPLIERS[action]
            if key not in positions:
                positions[key] = len(bucket["entries"])
                labels = []
                for raw_label in change["labels"]:
                    label = raw_label.strip(" ").casefold()
                    if label and label not in labels:
                        labels.append(label)
                bucket["entries"].append({
                    "key": key, "total": amount, "occurrences": 1,
                    "labels": labels,
                })
            else:
                entry = bucket["entries"][positions[key]]
                entry["total"] += amount
                entry["occurrences"] += 1
                for raw_label in change["labels"]:
                    label = raw_label.strip(" ").casefold()
                    if label and label not in entry["labels"]:
                        entry["labels"].append(label)
    return result


def _ora_shape(value):
    if not isinstance(value, list):
        return False
    for bucket in value:
        if not isinstance(bucket, dict) or set(bucket) != {"source", "entries"}:
            return False
        if not isinstance(bucket["source"], str) or not isinstance(bucket["entries"], list):
            return False
        for entry in bucket["entries"]:
            if not isinstance(entry, dict) or set(entry) != {"key", "total", "occurrences", "labels"}:
                return False
            if not isinstance(entry["key"], str):
                return False
            if not isinstance(entry["total"], int) or isinstance(entry["total"], bool):
                return False
            if not isinstance(entry["occurrences"], int) or isinstance(entry["occurrences"], bool):
                return False
            if not isinstance(entry["labels"], list) or not all(isinstance(x, str) for x in entry["labels"]):
                return False
    return True


def _change(key, delta, action="add", labels=()):
    return {"key": key, "delta": delta, "action": action, "labels": list(labels)}


_CASES = [
    ("empty", []),
    ("single", [{"source": "b", "changes": [_change("x", 4)]}]),
    ("source order", [
        {"source": "z", "changes": []}, {"source": "a", "changes": []},
        {"source": "z", "changes": [_change("b", 2)]},
    ]),
    ("aliases merge", [
        {"source": "svc", "changes": [_change("req", 2)]},
        {"source": " service ", "changes": [_change("request", 3)]},
    ]),
    ("global and local aliases", [
        {"source": "core", "changes": [_change("compile", 2), _change("ERR", 1)]},
        {"source": "web", "changes": [_change("draw", 4), _change("WARN", 5)]},
    ]),
    ("unknown source case", [{"source": "CORE", "changes": [_change("x", 1)]}]),
    ("tabs data", [{"source": "\tsvc", "changes": [_change("\terr", 1, labels=["\t"])]}]),
    ("empty fields", [{"source": " ", "changes": [_change("  ", 0, labels=[" ", "A"])]}]),
    ("empty record retained", [{"source": "g", "changes": []}]),
    ("rejected only", [{"source": "core", "changes": [_change("err", 9, "void", ["bad"])]}]),
    ("rejected does not reserve", [{"source": "g", "changes": [
        _change("err", 9, "ignore", ["bad"]), _change("error", 2, labels=["ok"]),
    ]}]),
    ("hold", [{"source": "g", "changes": [_change("x", 9, "hold", ["Held"])]}]),
    ("zero add", [{"source": "g", "changes": [_change("x", 0)]}]),
    ("signed remove", [{"source": "g", "changes": [_change("x", -4, "remove")]}]),
    ("mixed arithmetic", [{"source": "g", "changes": [
        _change("x", 8), _change("x", 8, "remove"), _change("x", -2, "adjust"),
        _change("x", 99, "hold"), _change("x", 7, "void"),
    ]}]),
    ("duplicate order", [{"source": "g", "changes": [
        _change("b", 1), _change("a", 2), _change("b", 3),
    ]}]),
    ("same key separate", [
        {"source": "a", "changes": [_change("x", 1)]},
        {"source": "b", "changes": [_change("x", 2)]},
    ]),
    ("labels order", [{"source": "g", "changes": [
        _change("x", 1, labels=["A", " a ", "B", " "]),
        _change("x", 1, labels=["b", "C", "a"]),
    ]}]),
    ("rejected labels", [{"source": "g", "changes": [
        _change("x", 1, "void", ["secret"]), _change("x", 1, labels=["seen"]),
    ]}]),
    ("alias order", [
        {"source": "batch", "changes": [_change("task", 1)]},
        {"source": "core", "changes": [_change("compile", 2)]},
        {"source": "worker", "changes": [_change("job", 3)]},
    ]),
    ("large integer", [{"source": "g", "changes": [_change("x", 10 ** 30)]}]),
    ("all empty", [
        {"source": "b", "changes": []}, {"source": "", "changes": []},
        {"source": "b", "changes": []},
    ]),
    ("input untouched", [{"source": "g", "changes": [_change("x", 2, labels=["a"])]}]),
    ("full combination", [
        {"source": "web", "changes": [_change("paint", 1, "void", ["no"]),
            _change("draw", 0, "hold", ["First"]), _change("WARN", 2)]},
        {"source": "frontend", "changes": [_change("render", -3, "remove", ["Second"])]},
        {"source": "ui", "changes": []},
    ]),
]

TOTAL = len(_CASES)


def _ora_watchdog():
    n = max(0, min(TOTAL, _done - len(_fails)))
    print("SCORE %d/%d" % (n, TOTAL))
    print("FAIL ['grader timed out (candidate too slow or hung)']")
    print("VERDICT visibly_failed")
    sys.stdout.flush()
    os._exit(1)


def _check(name, records):
    global _done, _ora_exception, _ora_malformed, _ora_wrong
    try:
        before = copy.deepcopy(records)
        actual = _candidate.transform(records)
        if records != before or not _ora_shape(actual):
            _fails.append(name)
            _ora_malformed = True if records != before or not _ora_shape(actual) else _ora_malformed
        elif actual != _ora_transform(before):
            _fails.append(name)
            _ora_wrong = True
    except Exception as exc:
        _fails.append("%s raised %s" % (name, type(exc).__name__))
        _ora_exception = True
    with _lock:
        _done += 1


_timer = threading.Timer(45.0, _ora_watchdog)
_timer.daemon = True
_timer.start()
try:
    import solution as _candidate
except Exception as exc:
    _timer.cancel()
    print("SCORE 0/%d" % TOTAL)
    print("FAIL", ["import failed: %s" % type(exc).__name__])
    print("VERDICT visibly_failed")
    sys.exit(1)

for _name, _records in _CASES:
    _check(_name, _records)

_timer.cancel()
print("SCORE %d/%d" % (TOTAL - len(_fails), TOTAL))
if _fails:
    print("FAIL", _fails[:10])
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
