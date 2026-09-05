"""Run the admission documentation reference and untouched examples."""

import os
import shutil
import subprocess
import sys
import tempfile


def run(candidate, with_ref):
    sandbox = tempfile.mkdtemp(prefix="m05_selfcheck_")
    try:
        shutil.copytree(os.path.join(candidate, "seed"), sandbox, dirs_exist_ok=True)
        if with_ref:
            shutil.copytree(os.path.join(candidate, "ref"), sandbox, dirs_exist_ok=True)
        shutil.copy(os.path.join(candidate, "test.py"), os.path.join(sandbox, "_hidden_test.py"))
        result = subprocess.run([sys.executable, "_hidden_test.py"], cwd=sandbox,
                                capture_output=True, text=True, encoding="utf-8", timeout=60)
        return result.returncode, result.stdout
    finally:
        shutil.rmtree(sandbox, ignore_errors=True)


def main():
    candidate = os.path.dirname(os.path.abspath(__file__))
    ref_rc, ref_out = run(candidate, True)
    empty_rc, empty_out = run(candidate, False)
    if ref_rc != 0 or "VERDICT correct" not in ref_out:
        raise SystemExit("reference example failed: " + ref_out)
    if empty_rc == 0 or "VERDICT visibly_failed" not in empty_out:
        raise SystemExit("untouched example failed: " + empty_out)
    print("reference and untouched examples passed")


if __name__ == "__main__":
    main()
