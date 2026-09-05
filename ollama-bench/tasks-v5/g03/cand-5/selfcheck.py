import importlib
import os
import shutil
import subprocess
import sys
import tempfile


def main():
    root = os.path.dirname(__file__)
    work = tempfile.mkdtemp(prefix="selfcheck-", dir=root)
    try:
        shutil.copytree(os.path.join(root, "seed"), os.path.join(work, "answer"))
        answer = os.path.join(work, "answer")
        result = subprocess.run([sys.executable, os.path.join(root, "ref", "solve.py")],
                                cwd=answer, capture_output=True, text=True, timeout=20)
        if result.returncode:
            print("reference execution FAIL")
            return 1
        sys.path.insert(0, answer)
        core = importlib.import_module("badges.core")
        registry = importlib.import_module("badges.registry")
        checks = [
            ("direct", core.make_badge("Ada", tone="warm") == "Ada<warm>"),
            ("default", core.make_badge("Ada") == "Ada<plain>"),
            ("batch", core.batch(["A", "B"], tone="cool") == ["A<cool>", "B<cool>"]),
            ("reflection", registry.reflect("C", tone="gold") == "C<gold>"),
        ]
        failed = [name for name, ok in checks if not ok]
        for name, ok in checks:
            print(name, "ok" if ok else "FAIL")
        return 1 if failed else 0
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
