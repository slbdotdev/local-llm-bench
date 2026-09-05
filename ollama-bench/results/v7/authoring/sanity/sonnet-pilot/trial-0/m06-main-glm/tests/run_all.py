"""Run every behavioural check in this directory. Standard library only.

    python tests/run_all.py

Prints one line per check, then a summary. Exits 0 and prints ALL TESTS PASSED
when every check passes; exits 1 and prints how many failed otherwise.
"""
import importlib.util
import os
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "src"))


def main():
    passed = 0
    failed = 0
    for name in sorted(os.listdir(HERE)):
        if not (name.startswith("test_") and name.endswith(".py")):
            continue
        path = os.path.join(HERE, name)
        spec = importlib.util.spec_from_file_location(name[:-3], path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for attr in sorted(dir(module)):
            if not attr.startswith("test_"):
                continue
            fn = getattr(module, attr)
            if not callable(fn):
                continue
            label = "%s.%s" % (name[:-3], attr)
            try:
                fn()
            except Exception:
                failed += 1
                print("FAIL %s" % label)
                traceback.print_exc()
            else:
                passed += 1
                print("ok   %s" % label)
    print("")
    if failed:
        print("%d of %d checks FAILED" % (failed, passed + failed))
        return 1
    print("ALL TESTS PASSED (%d checks)" % passed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
