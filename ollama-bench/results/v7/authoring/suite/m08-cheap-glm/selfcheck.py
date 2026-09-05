"""Selfcheck for m08-cheap-glm.

Runs every example in prompt.md against ref/, independently of test.py:

1. Recomputes the K-7 balance and excluded-row count straight from seed/
   with an independent implementation of the rule as stated in prompt.md,
   and compares with ref/audit-reply.txt.
2. Checks the prompt's hypothetical example (a REVERSED 12.00 invoice and
   its REVERSAL) really is hypothetical: no such row exists in the seed.
3. Checks the claimed figure and the prompt's format example are mutually
   consistent with a DISAGREE answer.
4. Builds a sandbox (seed/ + ref/) and runs test.py there, asserting
   SCORE 5/5, PASS, VERDICT correct, exit 0.

Exits 0 only when all of that holds.
"""
import csv
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOTAL = 5


def read_text(path):
    with open(path, encoding="utf-8", newline="") as fh:
        raw = fh.read()
    if raw.startswith("\ufeff"):
        raw = raw[1:]
    return raw.replace("\r\n", "\n").replace("\r", "\n")


def independent_recompute():
    """(balance, excluded) derived only from seed/ and the prompt's rule."""
    total = 0.0
    counted = 0
    excluded = 0
    ledger = os.path.join(HERE, "seed", "ledger")
    for name in ("2026-07.csv", "2026-08.csv", "2026-09.csv"):
        with open(os.path.join(ledger, name), encoding="utf-8",
                  newline="") as fh:
            for row in csv.DictReader(fh):
                if row["account"] != "K-7":
                    continue
                if row["status"] in ("REVERSED", "REVERSAL"):
                    excluded += 1
                    continue
                total += float(row["amount"])
                counted += 1
    return total, excluded, counted


def run_test_py(sandbox):
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    proc = subprocess.run([sys.executable, os.path.join(HERE, "test.py")],
                          cwd=sandbox, env=env, capture_output=True,
                          text=True, encoding="utf-8", errors="replace",
                          timeout=60)
    return proc.returncode, proc.stdout, proc.stderr


def main():
    problems = []

    balance, excluded, counted = independent_recompute()
    if ("%.2f" % balance) != "3516.00":
        problems.append("independent recompute gives balance %.2f, the "
                        "reference asserts 3516.00" % balance)
    if excluded != 2:
        problems.append("independent recompute excludes %d rows, the "
                        "reference asserts 2" % excluded)
    if counted != 10:
        problems.append("independent recompute counts %d K-7 rows, "
                        "expected 10" % counted)

    claimed = 0.0
    ledger = os.path.join(HERE, "seed", "ledger")
    for name in ("2026-07.csv", "2026-08.csv", "2026-09.csv"):
        with open(os.path.join(ledger, name), encoding="utf-8",
                  newline="") as fh:
            for row in csv.DictReader(fh):
                if row["account"] == "K-7" and row["entry"] in \
                        ("OPENING", "INV-2041", "CN-2044", "INV-2053",
                         "INV-2088", "INV-2093", "CN-2101", "INV-2147",
                         "TR-2160", "INV-2164", "CN-2166"):
                    claimed += float(row["amount"])
    if ("%.2f" % claimed) != "3696.00":
        problems.append("the claimed figure 3696.00 is not reproducible as "
                        "counting the reversed original: got %.2f" % claimed)

    for name in ("2026-07.csv", "2026-08.csv", "2026-09.csv"):
        with open(os.path.join(ledger, name), encoding="utf-8",
                  newline="") as fh:
            for row in csv.DictReader(fh):
                if row["account"] == "K-7" and float(row["amount"]) == 12.00:
                    problems.append("prompt's hypothetical 12.00 K-7 row "
                                    "exists in %s" % name)
                if row["entry"] in ("INV-9999", "REV-9999", "CN-9998"):
                    problems.append("ledger/README's fictional example "
                                    "entries exist in %s" % name)

    prompt = read_text(os.path.join(HERE, "prompt.md"))
    if "3696.00" not in prompt or "BALANCE 1234.05" not in prompt:
        problems.append("prompt.md lost the claimed figure or the format "
                        "example the selfcheck pins")

    ref = [ln.strip() for ln
           in read_text(os.path.join(HERE, "ref", "audit-reply.txt"))
           .split("\n") if ln.strip()]
    if ref != ["DISAGREE", "BALANCE 3516.00", "EXCLUDED 2"]:
        problems.append("ref/audit-reply.txt is %r" % (ref,))
    if re.match(r"^-?\d+\.\d\d$", "3516.00") is None:
        problems.append("balance format no longer matches the prompt's "
                        "stated shape")

    sandbox = tempfile.mkdtemp(prefix="m08selfchk_")
    try:
        shutil.copytree(os.path.join(HERE, "seed"), sandbox,
                        dirs_exist_ok=True)
        shutil.copytree(os.path.join(HERE, "ref"), sandbox, dirs_exist_ok=True)
        code, out, err = run_test_py(sandbox)
        if code != 0 or "PASS" not in out or "SCORE 5/5" not in out \
                or "VERDICT correct" not in out:
            problems.append("test.py in the ref sandbox gave rc=%d out=%r "
                            "err=%r" % (code, out, err[-200:]))
    finally:
        shutil.rmtree(sandbox, ignore_errors=True)

    if problems:
        for p in problems:
            print("SELFCHK FAIL: %s" % p)
        return 1
    print("SELFCHK PASS: independent recompute (balance 3516.00, excluded "
          "2, counted 10) matches ref; claim and example consistent; "
          "test.py scores 5/5")
    return 0


if __name__ == "__main__":
    sys.exit(main())
