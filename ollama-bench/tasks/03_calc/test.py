import sys, math, inspect
fails = []
def check(name, cond):
    if not cond: fails.append(name)
try:
    import calc
    src = inspect.getsource(calc)
    import re
    check("no eval", not re.search(r"(?<![\w.])(?<!def )(eval|exec)\s*\(", src) and "import ast" not in src and "from ast" not in src)
    cases = {
        "2+3*4": 14, "(2+3)*4": 20, "-3*-2": 6, "10/4": 2.5, "2*(3+(4-1))/3": 4,
        "1 - 2 - 3": -4, "8/2/2": 2, "  7  ": 7, "3.5*2": 7, ".5+.5": 1, "-(2+3)": -5,
        "2*-(3)": -6, "--4": 4, "100 - 3 * (2 + 8) / 5": 94, "((((1))))": 1, "0.1+0.2": 0.30000000000000004,
    }
    for e, want in cases.items():
        try:
            got = calc.evaluate(e)
            check(f"{e!r} -> {got}", isinstance(got, (int, float)) and math.isclose(got, want, rel_tol=1e-9, abs_tol=1e-9))
        except Exception as ex:
            fails.append(f"{e!r} raised {ex!r}")
    for bad in ["", "2+", "(2+3", "2+3)", "2 3", "abc", "3 * * 2", "1/", "()", "2 $ 3"]:
        try:
            calc.evaluate(bad); fails.append(f"no ValueError for {bad!r}")
        except ValueError:
            pass
        except Exception as ex:
            fails.append(f"{bad!r} raised {type(ex).__name__}")
    try:
        calc.evaluate("1/0"); fails.append("no ZeroDivisionError")
    except ZeroDivisionError:
        pass
    except Exception as ex:
        fails.append(f"1/0 raised {type(ex).__name__}")
except Exception as e:
    fails.append(f"exception: {e!r}")
if fails:
    print("FAIL", fails[:10]); sys.exit(1)
print("PASS")
