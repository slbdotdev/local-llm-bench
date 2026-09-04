import importlib.util
import pathlib
import sys


ROOT = pathlib.Path(__file__).resolve().parent


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    specification = _load("seed_specification", ROOT / "seed" / "specification.py")
    reference = _load("reference_transform", ROOT / "ref" / "transform.py")
    failed = 0
    for number, (source, expected) in enumerate(specification.EXAMPLES, 1):
        actual = reference.transform(source)
        ok = actual == expected
        print("example %02d: %s" % (number, "ok" if ok else "FAIL"))
        if not ok:
            failed += 1
    if failed:
        print("FAILED %d example(s)" % failed)
        return 1
    print("all examples passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
