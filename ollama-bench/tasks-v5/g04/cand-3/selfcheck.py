import os
import shutil
import subprocess
import sys
import tempfile

root = os.path.dirname(__file__)
checker = os.path.join(root, "test.py")


def run(source):
    with tempfile.TemporaryDirectory() as d:
        shutil.copy(os.path.join(root, "seed", "check_style.py"), d + "/check_style.py")
        if source is not None:
            shutil.copy(source, d + "/report.py")
        return subprocess.run([sys.executable, checker], cwd=d, text=True,
                              capture_output=True, timeout=10)


def expect(label, source, code, verdict):
    r = run(source)
    okay = r.returncode == code and "VERDICT " + verdict in r.stdout.splitlines()
    print(label + ": " + ("ok" if okay else "BAD") + " :: " + r.stdout.replace("\n", " | "))
    if not okay:
        raise SystemExit(1)


with tempfile.TemporaryDirectory() as d:
    near = os.path.join(d, "report.py")
    text = open(os.path.join(root, "ref", "report.py"), encoding="utf-8").read()
    # A plausible near miss: it silently drops rows containing None instead of preserving
    # the documented header/row layout, while retaining a clean style report.
    text = text.replace('        if row is None:\n            continue\n', '        if row is None:\n            writer.writerow(["", ""])\n            continue\n')
    open(near, "w", encoding="utf-8").write(text)
    expect("reference", os.path.join(root, "ref", "report.py"), 0, "correct")
    expect("near-miss", near, 1, "confidently_wrong")
expect("empty sandbox", None, 1, "visibly_failed")
