import ast
import os
import shutil
import subprocess
import sys
import tempfile

root = os.path.dirname(__file__)
ref = os.path.join(root, "ref", "invoice.py")
seed = os.path.join(root, "seed", "invoice.py")
checker = os.path.join(root, "test.py")


def run(source):
    with tempfile.TemporaryDirectory() as d:
        shutil.copy(os.path.join(root, "seed", "check_style.py"), d + "/check_style.py")
        if source is not None:
            shutil.copy(source, d + "/invoice.py")
        return subprocess.run([sys.executable, checker], cwd=d, text=True,
                              capture_output=True, timeout=10)


def expect(label, source, code, verdict):
    r = run(source)
    lines = r.stdout.splitlines()
    okay = r.returncode == code and any(x == "VERDICT " + verdict for x in lines)
    print(label + ": " + ("ok" if okay else "BAD") + " :: " + r.stdout.replace("\n", " | "))
    if not okay:
        raise SystemExit(1)


# The near miss preserves syntax and style but changes only the tax constant.
with tempfile.TemporaryDirectory() as d:
    near = os.path.join(d, "invoice.py")
    text = open(ref, encoding="utf-8").read().replace('Decimal("0.0825")', 'Decimal("0.0800")')
    open(near, "w", encoding="utf-8").write(text)
    expect("reference", ref, 0, "correct")
    expect("near-miss", near, 1, "confidently_wrong")
expect("empty sandbox", None, 1, "visibly_failed")
