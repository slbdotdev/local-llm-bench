import random
import sys

TOTAL = 32
fails = []


def check(name, fn):
    try:
        ok = fn()
    except Exception as e:
        ok = False
        name = "%s raised %s" % (name, type(e).__name__)
    if not ok:
        fails.append(name)


def check_raises(name, fn, exc=ValueError):
    def probe():
        try:
            fn()
        except exc:
            return True
        except Exception:
            return False
        return False
    check(name, probe)


def report():
    n = max(0, min(TOTAL, TOTAL - len(fails)))
    print("SCORE %d/%d" % (n, TOTAL))
    if fails:
        print("FAIL", fails[:12])
        sys.exit(1)
    print("PASS")
    sys.exit(0)


try:
    import mdtable
except Exception as e:
    fails = ["import failed: %r" % (e,)] + ["not run"] * (TOTAL - 1)
    report()


def _missing(*a, **k):
    raise AttributeError("attribute missing from mdtable")


pt = getattr(mdtable, "parse_table", _missing)
ft = getattr(mdtable, "format_table", _missing)
nz = getattr(mdtable, "normalize", _missing)

# --- parse_table (10) --------------------------------------------------
check("parse basic", lambda: pt("| a | b |\n| c | d |") == ([["a", "b"], ["c", "d"]], None))
check("parse single pipe", lambda: pt("|") == ([[""]], None))
check("parse double pipe", lambda: pt("||") == ([[""]], None))
check("parse alignment lr",
      lambda: pt("| x | y |\n| :- | --: |\n| 1 | 22 |")
      == ([["x", "y"], ["1", "22"]], ["left", "right"]))
check("parse alignment center",
      lambda: pt("| a | b |\n| :-: | - |") == ([["a", "b"]], ["center", "left"]))
check("parse escapes", lambda: pt("| a\\|b | c\\\\ |") == ([["a|b", "c\\"]], None))
check("parse other backslash kept", lambda: pt("| a\\nb |") == ([["a\\nb"]], None))
check("parse trailing lone backslash", lambda: pt("| a\\ |") == ([["a\\"]], None))
check("parse blank lines ignored", lambda: pt("\n  | a |\n\n") == ([["a"]], None))
check("parse non-alignment second line",
      lambda: pt("| a | b |\n| - | x |") == ([["a", "b"], ["-", "x"]], None))

# --- parse_table errors (5) --------------------------------------------
for bad in ["a | b |", "| a | b", "a|b", "| a | b |\n| c |", "| a | b |\n| --- |"]:
    check_raises("parse ValueError %r" % (bad,), lambda bad=bad: pt(bad))

# --- format_table (8) --------------------------------------------------
check("format basic",
      lambda: ft([["b", "aa"], ["1", "2"]]) == "| b   | aa  |\n| :-- | :-- |\n| 1   | 2   |")
check("format right",
      lambda: ft([["x", "y"]], ["left", "right"]) == "| x   |   y |\n| :-- | --: |")
check("format center", lambda: ft([["x"]], ["center"]) == "|  x  |\n| :-: |")
check("format width 4",
      lambda: ft([["x", "y"], ["ab", "z"]], ["center", "right"])
      == "|  x  |   y |\n| :-: | --: |\n| ab  |   z |")
check("format escape out", lambda: ft([["a|b"]]) == "| a\\|b |\n| :--- |")
check("format backslash out", lambda: ft([["a\\b"]]) == "| a\\\\b |\n| :--- |")
check("format empty", lambda: ft([], None) == "")
check("format normalize empty", lambda: nz("") == "")

# --- format_table errors (4) -------------------------------------------
for bad_rows, bad_aligns in [
    ([["a", "b"], ["c"]], None),
    ([["a"]], ["left", "right"]),
    ([["a"]], ["middle"]),
    ([["a"]], []),
]:
    check_raises("format ValueError %r %r" % (bad_rows, bad_aligns),
                 lambda r=bad_rows, a=bad_aligns: ft(r, a))

# --- worked-example round trips (3) ------------------------------------
check("normalize example1",
      lambda: nz("| b | aa |\n| 1 | 2 |") == "| b   | aa  |\n| :-- | :-- |\n| 1   | 2   |")
check("normalize example2", lambda: nz("| a\\|b |") == "| a\\|b |\n| :--- |")
check("normalize aligns kept",
      lambda: nz("| x | y |\n| :- | --: |\n| 1 | 22 |")
      == "| x   |   y |\n| :-- | --: |\n| 1   |  22 |")

# --- seeded random round-trip + idempotence (2) ------------------------
random.seed(2929)


def rc():
    s = "".join(random.choice("abcxyz09-") for _ in range(random.randint(0, 5)))
    if len(s) >= 2 and random.random() < 0.35:
        k = random.randint(1, len(s) - 1)
        s = s[:k] + random.choice([" ", "|", "\\|", "\\\\", "\\n"]) + s[k:]
    return s


bad_rt = bad_id = 0
trials = 0
for _ in range(60):
    nrows = random.randint(1, 3)
    ncols = random.randint(1, 3)
    rows = [[rc() for _ in range(ncols)] for _ in range(nrows)]
    aligns = (
        None
        if random.random() < 0.4
        else [random.choice(["left", "right", "center"]) for _ in range(ncols)]
    )
    try:
        t = ft(rows, aligns)
        rows2, aligns2 = pt(t)
        want_aligns = aligns if aligns is not None else ["left"] * ncols
        trials += 1
        if rows2 != rows or aligns2 != want_aligns:
            bad_rt += 1
        n1 = nz(t)
        n2 = nz(n1)
        if n1 != n2:
            bad_id += 1
    except Exception:
        bad_rt += 1
        bad_id += 1

check("random roundtrip", lambda: trials > 40 and bad_rt == 0)
check("random idempotent", lambda: trials > 40 and bad_id == 0)

report()
