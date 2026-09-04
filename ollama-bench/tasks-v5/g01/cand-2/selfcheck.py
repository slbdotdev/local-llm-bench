"""Run every worked example in seed/specification.py against the reference."""

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    reference = _load(ROOT / "ref" / "solution.py", "candidate_2_reference")
    specification = _load(ROOT / "seed" / "specification.py", "candidate_2_spec")
    failed = 0
    for number, (records, expected) in enumerate(specification.EXAMPLES, 1):
        original = repr(records)
        actual = reference.transform(records)
        ok = actual == expected and repr(records) == original
        print("example %d: %s" % (number, "PASS" if ok else "FAIL"))
        if not ok:
            failed += 1
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
