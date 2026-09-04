import sys
from pkgver import parse, compare, sort_versions, latest, satisfies

fails = []
def check(name, cond):
    if not cond:
        fails.append(name); print("FAIL:", name)

def val(f):
    """Evaluate f(), turning an exception into a sentinel string."""
    try:
        return f()
    except Exception as e:
        return "ERR:%s: %s" % (type(e).__name__, e)

check("parse release", parse("1.2.3") == (1, 2, 3, ()))
check("parse prerelease words", parse("1.2.3-alpha.beta") == (1, 2, 3, ("alpha", "beta")))
check("parse numeric prerelease id is int", parse("1.0.0-2") == (1, 0, 0, (2,)))
check("parse mixed prerelease", parse("1.0.0-rc.1") == (1, 0, 0, ("rc", 1)))
check("parse hyphen in prerelease", parse("1.0.0-alpha-1") == (1, 0, 0, ("alpha-1",)))
check("parse rejects leading zero", isinstance(val(lambda: parse("01.2.3")), str))
check("parse rejects short core", isinstance(val(lambda: parse("1.2")), str))
check("parse rejects empty prerelease", isinstance(val(lambda: parse("1.2.3-")), str))

check("compare core numeric", compare("1.10.0", "1.9.0") == 1)
check("compare equal", compare("1.2.3", "1.2.3") == 0)
check("compare release beats prerelease", compare("1.0.0", "1.0.0-alpha") == 1)
check("compare prerelease loses to release", compare("1.0.0-alpha", "1.0.0") == -1)
check("compare numeric prerelease ids numerically", compare("1.0.0-2", "1.0.0-10") == -1)
check("compare numeric ranks below alphanumeric", compare("1.0.0-1", "1.0.0-alpha") == -1)
check("compare prefix is smaller", compare("1.0.0-alpha", "1.0.0-alpha.1") == -1)

vs = ["1.0.0", "1.0.0-alpha", "0.9.9", "1.0.0-rc.1", "1.0.0-alpha.1"]
check("sort", sort_versions(vs) == ["0.9.9", "1.0.0-alpha", "1.0.0-alpha.1", "1.0.0-rc.1", "1.0.0"])
check("sort does not mutate", vs == ["1.0.0", "1.0.0-alpha", "0.9.9", "1.0.0-rc.1", "1.0.0-alpha.1"])
check("latest", latest(vs) == "1.0.0")
check("latest empty", latest([]) is None)

check("satisfies ge", val(lambda: satisfies("1.2.3", ">=1.0.0")) is True)
check("satisfies le", val(lambda: satisfies("1.2.3", "<=1.2.3")) is True)
check("satisfies range", val(lambda: satisfies("1.2.3", ">=1.0.0, <2.0.0")) is True)
check("satisfies range excludes", val(lambda: satisfies("2.0.0", ">=1.0.0, <2.0.0")) is False)
check("satisfies ne", val(lambda: satisfies("1.2.3", "!=1.2.3")) is False)
check("satisfies empty spec", val(lambda: satisfies("1.2.3", "  ")) is True)
check("satisfies bad operator", isinstance(val(lambda: satisfies("1.2.3", "~1.0.0")), str))

if fails:
    print("%d failing" % len(fails)); sys.exit(1)
print("ALL OK")
