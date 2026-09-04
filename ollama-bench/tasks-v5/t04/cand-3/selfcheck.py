import pathlib
import subprocess
import sys

root = pathlib.Path(__file__).parent
result = subprocess.run(
    [sys.executable, str(root / "test.py")],
    cwd=str(root / "ref"),
    capture_output=True,
    text=True,
)
expected = ("SCORE 4/4", "PASS", "VERDICT correct")
lines = result.stdout.splitlines()
ok = result.returncode == 0 and all(item in lines for item in expected)
print("reference -> %s" % ("correct" if ok else "FAILED"))
if not ok:
    print(result.stdout, end="")
    print(result.stderr, end="")
    raise SystemExit(1)
