"""Selfcheck for m02-cheap-glm.

Runs every example in prompt.md against ref/, independently of test.py:

1. Recomputes the expected answer straight from seed/ with an independent
   implementation of the rule as stated in prompt.md, and compares it with
   the reference deliverable ref/reorder-check.txt.
2. Runs the prompt's hypothetical example (QM-9999 at 5 with point 5)
   against the reference stock module and checks it is reported, and that
   the example SKU really is absent from the material.
3. Checks the reference's stock module gives the same list as step 1.
4. Builds a sandbox (seed/ + ref/) and runs test.py there, asserting the
   full printed contract: SCORE 7/7, PASS, VERDICT correct, exit 0.

Exits 0 only when all of that holds.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOTAL = 7


def seed_path(*parts):
    return os.path.join(HERE, "seed", *parts)


def read_text(path):
    with open(path, encoding="utf-8", newline="") as fh:
        raw = fh.read()
    if raw.startswith("\ufeff"):
        raw = raw[1:]
    return raw.replace("\r\n", "\n").replace("\r", "\n")


def independent_recompute():
    """The answer, derived only from seed/ and the rule stated in prompt.md."""
    rows = []
    with open(seed_path("data", "inventory.csv"), encoding="utf-8",
              newline="") as fh:
        import csv
        for row in csv.DictReader(fh):
            rows.append((row["sku"], int(row["on_hand"])))
    with open(seed_path("config", "reorder_points.json"), encoding="utf-8") as fh:
        points = json.load(fh)["reorder_points"]
    return [sku for sku, on_hand in rows if on_hand <= int(points[sku])]


def load_ref_module():
    here = HERE
    src = os.path.join(here, "ref", "src", "quartermaster", "stock.py")
    import importlib.util
    spec = importlib.util.spec_from_file_location("qm_stock_ref", src)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_test_py(sandbox):
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    proc = subprocess.run([sys.executable, os.path.join(HERE, "test.py")],
                          cwd=sandbox, env=env, capture_output=True,
                          text=True, encoding="utf-8", errors="replace",
                          timeout=60)
    return proc.returncode, proc.stdout, proc.stderr


def main():
    problems = []

    expected = independent_recompute()
    ref_report = [ln.strip() for ln
                  in read_text(os.path.join(HERE, "ref", "reorder-check.txt"))
                  .split("\n") if ln.strip()]
    if ref_report != ["ITEMS AT OR BELOW REORDER POINT: %d" % len(expected)] + expected:
        problems.append("ref/reorder-check.txt %r does not match the "
                        "independently recomputed answer %r"
                        % (ref_report, expected))

    inventory = load_ref_module().load_inventory(
        seed_path("data", "inventory.csv"))
    if any(r["sku"] == "QM-9999" for r in inventory):
        problems.append("prompt's hypothetical SKU QM-9999 exists in the "
                        "material; the example is not hypothetical")
    hypothetical = load_ref_module().low_stock(
        [{"sku": "QM-9999", "on_hand": 5}], {"QM-9999": 5})
    if hypothetical != ["QM-9999"]:
        problems.append("prompt's example (5 on hand, point 5) does not "
                        "report QM-9999 under the reference module: %r"
                        % (hypothetical,))

    mod = load_ref_module()
    got = mod.low_stock(inventory, mod.load_reorder_points(
        seed_path("config", "reorder_points.json")))
    if got != expected:
        problems.append("reference stock module %r != recompute %r"
                        % (got, expected))

    sandbox = tempfile.mkdtemp(prefix="m02selfchk_")
    try:
        shutil.copytree(os.path.join(HERE, "seed"), sandbox,
                        dirs_exist_ok=True)
        shutil.copytree(os.path.join(HERE, "ref"), sandbox, dirs_exist_ok=True)
        code, out, err = run_test_py(sandbox)
        if code != 0 or "PASS" not in out or "SCORE 7/7" not in out \
                or "VERDICT correct" not in out:
            problems.append("test.py in the ref sandbox gave rc=%d out=%r "
                            "err=%r" % (code, out, err[-200:]))
    finally:
        shutil.rmtree(sandbox, ignore_errors=True)

    if problems:
        for p in problems:
            print("SELFCHK FAIL: %s" % p)
        return 1
    print("SELFCHK PASS: recompute=%r matches ref deliverable, example and "
          "module agree, test.py scores 7/7 in the ref sandbox"
          % (expected,))
    return 0


if __name__ == "__main__":
    sys.exit(main())
