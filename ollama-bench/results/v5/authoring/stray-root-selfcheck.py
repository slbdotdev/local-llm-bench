import importlib.util
import pathlib
import sys


ROOT = pathlib.Path(__file__).resolve().parent


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    reference = load(ROOT / "ref" / "solution.py", "reference_solution")
    specification = load(ROOT / "seed" / "specification.py", "seed_specification")
    failed = False
    for index, (source, expected) in enumerate(specification.EXAMPLES, 1):
        actual = reference.transform(source)
        ok = actual == expected
        print("example %d: %s" % (index, "ok" if ok else "FAIL"))
        if not ok:
            print("  expected:", repr(expected))
            print("  actual:  ", repr(actual))
            failed = True
    if failed:
        return 1
    print("selfcheck: PASS (%d examples)" % len(specification.EXAMPLES))
    return 0


if __name__ == "__main__":
    sys.exit(main())
