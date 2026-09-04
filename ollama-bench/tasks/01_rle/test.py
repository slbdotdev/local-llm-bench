import sys, random, string
fails = []
def check(name, cond):
    if not cond: fails.append(name)
try:
    import rle
    check("enc basic", rle.encode("aaabccdddd") == "3a1b2c4d")
    check("enc empty", rle.encode("") == "")
    check("enc single", rle.encode("z") == "1z")
    check("enc long run", rle.encode("a" * 123 + "b") == "123a1b")
    check("dec basic", rle.decode("3a1b2c4d") == "aaabccdddd")
    check("dec empty", rle.decode("") == "")
    check("dec multi", rle.decode("12x1y") == "x" * 12 + "y")
    random.seed(7)
    for i in range(50):
        s = "".join(random.choice("abc") * random.randint(1, 15) for _ in range(random.randint(0, 6)))
        check(f"roundtrip {i}", rle.decode(rle.encode(s)) == s)
except Exception as e:
    fails.append(f"exception: {e!r}")
if fails:
    print("FAIL", fails[:8]); sys.exit(1)
print("PASS")
