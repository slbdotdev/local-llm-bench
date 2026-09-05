"""Run every worked fixture and the prompt's orientation example."""

import copy
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _orientation():
    records = [{"source": "svc", "changes": [{
        "key": " Err ", "delta": 3, "action": "add",
        "labels": ["Urgent", "urgent", " "],
    }]}]
    expected = [{"source": "service", "entries": [{
        "key": "error", "total": 3, "occurrences": 1,
        "labels": ["urgent"],
    }]}]
    return "prompt orientation", records, expected


def main():
    reference = _load(ROOT / "ref" / "solution.py", "candidate_5_reference")
    fixtures = _load(ROOT / "seed" / "tests" / "fixtures.py", "candidate_5_fixtures")
    examples = [_orientation()]
    examples.extend((name, value[0], value[1]) for name, value in fixtures.CASES.items())
    failed = 0
    for number, (name, records, expected) in enumerate(examples, 1):
        before = copy.deepcopy(records)
        actual = reference.transform(records)
        ok = actual == expected and records == before
        print("example %d (%s): %s" % (number, name, "PASS" if ok else "FAIL"))
        if not ok:
            failed += 1
    print("selfcheck: %s (%d examples)" % ("PASS" if not failed else "FAIL", len(examples)))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
