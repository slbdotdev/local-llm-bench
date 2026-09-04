import sys, subprocess, hashlib, random

TOTAL = 29
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


def all_raise(fns, exc=ValueError):
    def probe():
        for f in fns:
            try:
                f()
                return False
            except exc:
                pass
            except Exception:
                return False
        return True
    return probe


def report():
    n = max(0, min(TOTAL, TOTAL - len(fails)))
    print("SCORE %d/%d" % (n, TOTAL))
    if fails:
        print("FAIL", fails[:10])
        sys.exit(1)
    print("PASS")
    sys.exit(0)


# --- 1-2: the visible test file ----------------------------------------
def visible_untouched():
    with open("test_pkgver.py", "rb") as f:
        h = hashlib.sha256(f.read()).hexdigest()
    return h == "a0d4f4c7a4e3d775f5184f827fa5ccdd8352cb9288a8c9b1089a139852561852"


def visible_pass():
    r = subprocess.run([sys.executable, "test_pkgver.py"], capture_output=True,
                       text=True, timeout=60)
    return r.returncode == 0 and "ALL OK" in r.stdout


check("visible tests untouched", visible_untouched)
check("visible tests pass", visible_pass)

try:
    import pkgver
except Exception as e:
    fails += ["import failed: %r" % (e,)] + ["not run"] * (TOTAL - len(fails) - 1)
    report()


def _missing(*a, **k):
    raise AttributeError("attribute missing from pkgver")


parse = getattr(pkgver, "parse", _missing)
compare = getattr(pkgver, "compare", _missing)
sort_versions = getattr(pkgver, "sort_versions", _missing)
latest = getattr(pkgver, "latest", _missing)
satisfies = getattr(pkgver, "satisfies", _missing)

# --- 3-9: parse --------------------------------------------------------
check("parse plain versions",
      lambda: parse("0.0.0") == (0, 0, 0, ()) and parse("10.20.30") == (10, 20, 30, ()))
check("parse prerelease identifiers",
      lambda: parse("1.0.0-0") == (1, 0, 0, (0,))
      and parse("1.0.0-x.7.y") == (1, 0, 0, ("x", 7, "y"))
      and parse("1.0.0--") == (1, 0, 0, ("-",)))
check("parse rejects leading zeros in core",
      all_raise([lambda: parse("1.02.3"), lambda: parse("1.2.03"),
                 lambda: parse("00.1.2")]))
check("parse leading zeros in numeric prerelease",
      lambda: (parse("0.0.0-0") == (0, 0, 0, (0,))
               and all_raise([lambda: parse("1.0.0-01")])()))
check("parse rejects wrong core shape",
      all_raise([lambda: parse("1.2.3.4"), lambda: parse("1.2.x"),
                 lambda: parse("")]))
check("parse rejects prefixes and stray whitespace",
      all_raise([lambda: parse("v1.2.3"), lambda: parse(" 1.2.3"),
                 lambda: parse("1.2.3-al pha")]))
check("parse rejects empty identifiers and build metadata",
      all_raise([lambda: parse("1.2.3-a..b"), lambda: parse("1.2.3-a.b+meta")]))

# --- 10-15: compare ----------------------------------------------------
check("compare core numbers",
      lambda: compare("2.0.0", "1.999.999") == 1 and compare("1.2.10", "1.2.9") == 1
      and compare("1.2.3", "1.3.0") == -1 and compare("0.0.1", "0.0.1") == 0)
check("compare prerelease is lower than release",
      lambda: compare("1.0.0-alpha", "1.0.0") == -1
      and compare("1.0.0", "1.0.0-alpha") == 1
      and compare("1.0.0-rc.99", "1.0.0") == -1)
check("compare core wins over prerelease",
      lambda: compare("1.0.0", "0.9.9-zzz") == 1
      and compare("1.0.0-alpha", "1.0.1-alpha") == -1)
check("compare numeric prerelease identifiers numerically",
      lambda: compare("1.0.0-2", "1.0.0-10") == -1
      and compare("1.0.0-11", "1.0.0-9") == 1
      and compare("1.0.0-1", "1.0.0-1") == 0)
check("compare numeric below alphanumeric, ASCII order",
      lambda: compare("1.0.0-99", "1.0.0-a") == -1
      and compare("1.0.0-Z", "1.0.0-a") == -1
      and compare("1.0.0-alpha", "1.0.0-beta") == -1)
check("compare identifier count breaks ties",
      lambda: compare("1.0.0-alpha.1", "1.0.0-alpha.beta") == -1
      and compare("1.0.0-alpha.beta.1", "1.0.0-alpha.beta") == 1)

chain = ["1.0.0-alpha", "1.0.0-alpha.1", "1.0.0-alpha.beta", "1.0.0-beta",
         "1.0.0-beta.2", "1.0.0-beta.11", "1.0.0-rc.1", "1.0.0"]

# --- 16-17: the full spec ordering -------------------------------------
check("spec ordering chain ascending",
      lambda: all(compare(chain[i], chain[i + 1]) == -1 for i in range(len(chain) - 1)))
check("spec ordering chain descending",
      lambda: all(compare(chain[i + 1], chain[i]) == 1 for i in range(len(chain) - 1)))

# --- 18-21: sort_versions and latest -----------------------------------
random.seed(3)
shuffled = list(chain)
random.shuffle(shuffled)
check("sort_versions orders the spec chain", lambda: sort_versions(shuffled) == chain)
check("sort_versions edge cases",
      lambda: sort_versions([]) == []
      and sort_versions(("1.0.1", "1.0.0")) == ["1.0.0", "1.0.1"]
      and sort_versions(["1.0.0", "1.0.0"]) == ["1.0.0", "1.0.0"])


def sort_does_not_mutate():
    src = ["2.0.0", "1.0.0", "1.5.0"]
    copy = list(src)
    sort_versions(src)
    return src == copy


check("sort_versions does not mutate its argument", sort_does_not_mutate)
check("latest",
      lambda: latest(chain) == "1.0.0"
      and latest(["1.0.0-alpha", "1.0.0-beta"]) == "1.0.0-beta"
      and latest([]) is None and latest(["1.0.0"]) == "1.0.0"
      and latest(["1.2.3", "1.2.3"]) == "1.2.3")

# --- 22-28: satisfies --------------------------------------------------
check("satisfies inequality operators",
      lambda: bool(satisfies("1.2.3", ">=1.2.3")) is True
      and bool(satisfies("1.2.3", ">1.2.3")) is False
      and bool(satisfies("1.2.4", ">1.2.3")) is True
      and bool(satisfies("1.2.3", "<=1.2.3")) is True
      and bool(satisfies("1.2.3", "<1.2.3")) is False)
check("satisfies equality operators",
      lambda: bool(satisfies("1.2.3", "==1.2.3")) is True
      and bool(satisfies("1.2.3", "!=1.2.4")) is True
      and bool(satisfies("1.2.3", "!=1.2.3")) is False)
check("satisfies respects prerelease precedence",
      lambda: bool(satisfies("1.0.0-rc.1", "<1.0.0")) is True
      and bool(satisfies("1.0.0-rc.1", ">=1.0.0")) is False)
check("satisfies conjunctions with whitespace",
      lambda: bool(satisfies("1.5.0", " >= 1.0.0 , < 2.0.0 ")) is True
      and bool(satisfies("2.0.0", ">=1.0.0,<2.0.0")) is False
      and bool(satisfies("1.5.0", ">=1.0.0,<2.0.0,!=1.5.0")) is False)
check("satisfies empty spec is always true",
      lambda: bool(satisfies("1.2.3", "")) is True
      and bool(satisfies("1.2.3", "   ")) is True)
check("satisfies rejects missing or unknown operators",
      all_raise([lambda: satisfies("1.2.3", "1.0.0"),
                 lambda: satisfies("1.2.3", "~1.0.0")]))
check("satisfies rejects malformed constraints",
      all_raise([lambda: satisfies("1.2.3", ">=1.0.0,"),
                 lambda: satisfies("1.2.3", ">=1.0")]))
check_raises("satisfies rejects a malformed version",
             lambda: satisfies("nope", ">=1.0.0"))

report()
