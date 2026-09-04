import sys, subprocess, hashlib

TOTAL = 11
VISIBLE_SHA256 = "00c5e06fb7eaf55a4a812f92b4a727d0924ba2476fd0b9510dd9f63fd44b4c89"
fails = []


def check(name, fn):
    try:
        ok = fn()
    except Exception as e:
        ok = False
        name = f"{name} raised {type(e).__name__}"
    if not ok:
        fails.append(name)


def _visible_untouched():
    with open("test_schema.py", "rb") as f:
        return hashlib.sha256(f.read()).hexdigest() == VISIBLE_SHA256


def _visible_pass():
    r = subprocess.run([sys.executable, "test_schema.py"], capture_output=True, text=True, timeout=30)
    return r.returncode == 0 and "ALL TESTS PASSED" in r.stdout


validate = None
try:
    from schema import validate
except Exception as e:
    fails.append(f"import failed: {e!r}")

if validate is not None:
    check("visible tests untouched", _visible_untouched)
    check("visible tests pass", _visible_pass)

    # Additional hidden tests for edge cases
    check("bool is not integer", lambda: validate(False, {"type": "integer"}) == False)
    check("bool is not number", lambda: validate(True, {"type": "number"}) == False)
    check("bool is boolean", lambda: validate(False, {"type": "boolean"}) == True)
    check("negative minimum", lambda: validate(-5, {"type": "number", "minimum": -10}) == True)
    check("float is number", lambda: validate(3.14, {"type": "number"}) == True)
    check("float is not integer", lambda: validate(3.14, {"type": "integer"}) == False)
    check("empty string minLength 0", lambda: validate("", {"type": "string", "minLength": 0}) == True)
    check("empty array minItems 0", lambda: validate([], {"type": "array", "minItems": 0}) == True)
    check("nested objects", lambda: validate(
        {"user": {"name": "Alice", "age": 25}},
        {"type": "object", "properties": {"user": {"type": "object", "properties": {"name": {"type": "string"}}}}}
    ) == True)

    n = max(0, min(TOTAL, TOTAL - len(fails)))
else:
    n = 0

print(f"SCORE {n}/{TOTAL}")
if fails:
    print("FAIL", fails[:10])
    sys.exit(1)
print("PASS")
