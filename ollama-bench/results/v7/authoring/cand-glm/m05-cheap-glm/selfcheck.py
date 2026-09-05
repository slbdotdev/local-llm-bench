"""Selfcheck for m05-cheap-glm.

Runs every example in prompt.md against ref/, independently of test.py:

1. Recomputes the card's arithmetic independently (a second implementation
   of R1-R8 written from the card text) and checks ref's rates.py against
   it on the card's worked examples and the grader scenarios.
2. Checks the card's printed worked-example totals (18.48, 21.77) really
   appear in seed/docs/rate-card.md and match both implementations, so the
   examples are consistent with the code and hide nothing.
3. Checks ref/fixlog.txt against the independently derived set of
   disagreeing rules, and checks the prompt's illustrative example
   (R3/R7) is a different set, so the example cannot be mistaken for the
   answer.
4. Builds a sandbox (seed/ + ref/) and runs test.py there, asserting
   SCORE 5/5, PASS, VERDICT correct, exit 0.

Exits 0 only when all of that holds.
"""
import importlib.util
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


def pct(x, p):
    return (x * p + 50) // 100


def base_cents(w):
    if w <= 1:
        return 600
    if w <= 5:
        return 600 + 180 * (w - 1)
    return 1320 + 110 * (w - 5)


def quote_card(weight, l, w, h, zone, res, sat):
    """R1-R8 implemented directly from docs/rate-card.md, independently."""
    vol = (l * w * h + 4999) // 5000
    billable = max(weight, vol)
    zoned = pct(base_cents(billable),
                {"A": 100, "B": 115, "C": 130, "D": 155}[zone])
    fuel = pct(zoned, 12)
    total = zoned + fuel
    if res:
        total += 450
    if billable > 25:
        total += 1400
    if sat:
        total += 900
    return total


def load_module(path):
    spec = importlib.util.spec_from_file_location("m_%d" % id(path), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


CASES = [
    (8, 30, 20, 10, "A", False, False),    # card worked example 1
    (4, 25, 15, 12, "A", False, True),     # card worked example 2
    (3, 40, 40, 40, "A", False, False),    # grader s1
    (12, 20, 20, 10, "D", True, False),    # grader s2
    (26, 20, 20, 20, "B", False, True),    # grader s3
]


def run_test_py(sandbox):
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    proc = subprocess.run([sys.executable, os.path.join(HERE, "test.py")],
                          cwd=sandbox, env=env, capture_output=True,
                          text=True, encoding="utf-8", errors="replace",
                          timeout=60)
    return proc.returncode, proc.stdout, proc.stderr


def main():
    problems = []

    card = read_text(os.path.join(HERE, "seed", "docs", "rate-card.md"))
    for total in ("18.48", "21.77"):
        if total not in card:
            problems.append("card no longer prints worked-example total %s"
                            % total)
    for text, weight, want in (("9.60", 3, 960), ("13.20", 5, 1320),
                               ("18.70", 10, 1870), ("20.90", 12, 2090)):
        if text not in card:
            problems.append("card no longer prints R1 worked weight %s" % text)
        if base_cents(weight) != want:
            problems.append("independent R1 gives %d for %d kg, card table "
                            "says %s" % (base_cents(weight), weight, text))

    ref = load_module(os.path.join(HERE, "ref", "src", "kestrel", "rates.py"))
    for args in CASES:
        got = ref.quote(*args)
        want = quote_card(*args)
        if got != want:
            problems.append("ref.quote%r gave %d, card gives %d"
                            % (args, got, want))

    # the conflicts must really exist in the seed, and only where fixlog
    # says: the seed's code must agree with the card on both worked
    # examples (neither exercises a conflict) and disagree on s1 (R2) and
    # s2/s3 (R5).
    seed_mod = load_module(os.path.join(HERE, "seed", "src", "kestrel",
                                        "rates.py"))
    if seed_mod.quote(*CASES[0]) != quote_card(*CASES[0]) \
            or seed_mod.quote(*CASES[1]) != quote_card(*CASES[1]):
        problems.append("seed code disagrees with the card on a worked "
                        "example; the examples no longer hide the "
                        "conflicts")
    for args, rule in ((CASES[2], "R2"), (CASES[3], "R5"), (CASES[4], "R5")):
        if seed_mod.quote(*args) == quote_card(*args):
            problems.append("seed code agrees with the card on %r; the %s "
                            "conflict the fixlog asserts does not exist"
                            % (args, rule))

    try:
        if ref.returns_label("A") != 580:
            problems.append("ref.returns_label('A') != 580")
        ref.returns_label("C")
        problems.append("ref.returns_label('C') did not raise")
    except ValueError:
        pass
    except Exception as exc:
        problems.append("ref.returns_label('C') raised %s, expected "
                        "ValueError" % exc.__class__.__name__)

    fixlog = [ln.strip() for ln
              in read_text(os.path.join(HERE, "ref", "fixlog.txt"))
              .split("\n") if ln.strip()]
    expected_fixlog = ["R1 MATCHES", "R2 CORRECTED", "R3 MATCHES",
                       "R4 MATCHES", "R5 CORRECTED", "R6 MATCHES",
                       "R7 MATCHES", "R8 MATCHES"]
    if fixlog != expected_fixlog:
        problems.append("ref/fixlog.txt %r != %r" % (fixlog, expected_fixlog))
    illustrative = set(re.findall(r"R(\d) CORRECTED",
                                  read_text(os.path.join(HERE,
                                                         "prompt.md"))))
    if illustrative == {"2", "5"}:
        problems.append("prompt's illustrative example accidentally states "
                        "the real answer set")

    sandbox = tempfile.mkdtemp(prefix="m05selfchk_")
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
    print("SELFCHK PASS: card examples and scenarios agree between the "
          "independent card implementation and ref/rates.py; fixlog and "
          "prompt example consistent; test.py scores 5/5")
    return 0


if __name__ == "__main__":
    sys.exit(main())
