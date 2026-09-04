import sys
fails = []
def check(name, cond):
    if not cond: fails.append(name)
def ref(n):
    vals = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"), (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]
    out = ""
    for v, s in vals:
        while n >= v: out += s; n -= v
    return out
try:
    import roman
    for n in range(1, 4000):
        r = ref(n)
        if roman.to_roman(n) != r: fails.append(f"to_roman({n})"); break
    for n in range(1, 4000):
        if roman.from_roman(ref(n)) != n: fails.append(f"from_roman({ref(n)})"); break
    for bad in [0, 4000, -1, 3.0, "10", True, 10**9]:
        try:
            roman.to_roman(bad); fails.append(f"to_roman({bad!r}) accepted")
        except ValueError:
            pass
        except TypeError:
            fails.append(f"to_roman({bad!r}) TypeError not ValueError")
    for bad in ["IIII", "VX", "IC", "XXXX", "IVI", "MMMM", "", "iv", "ABC", "IIV", "XM", "LL", "DD", "VV", "MCMXCIXI", " X", "X "]:
        try:
            roman.from_roman(bad); fails.append(f"from_roman({bad!r}) accepted")
        except ValueError:
            pass
except Exception as e:
    fails.append(f"exception: {e!r}")
if fails:
    print("FAIL", fails[:10]); sys.exit(1)
print("PASS")
