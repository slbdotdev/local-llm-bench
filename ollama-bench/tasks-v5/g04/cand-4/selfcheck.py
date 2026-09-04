import os
import shutil
import subprocess
import sys
import tempfile

root = os.path.dirname(__file__)
checker = os.path.join(root, "test.py")


def run(source):
    with tempfile.TemporaryDirectory() as d:
        shutil.copy(os.path.join(root, "seed", "check_style.py"),
                    os.path.join(d, "check_style.py"))
        if source is not None:
            shutil.copy(source, os.path.join(d, "policy.py"))
        return subprocess.run([sys.executable, checker], cwd=d, text=True,
                              capture_output=True, timeout=10)


def expect(label, source, code, verdict):
    result = run(source)
    okay = (result.returncode == code
            and "VERDICT " + verdict in result.stdout.splitlines())
    print(label + ": " + ("ok" if okay else "BAD") + " :: "
          + result.stdout.replace("\n", " | "))
    if not okay:
        raise SystemExit(1)


with tempfile.TemporaryDirectory() as d:
    near = os.path.join(d, "policy.py")
    text = open(os.path.join(root, "ref", "policy.py"), encoding="utf-8").read()
    # A clean but plausible near miss: truthiness supplies the default effect,
    # losing explicit empty, zero, and None effects.
    text = text.replace('return rule.get("effect", "deny")',
                        'return rule.get("effect") or "deny"')
    open(near, "w", encoding="utf-8").write(text)
    expect("reference", os.path.join(root, "ref", "policy.py"), 0, "correct")
    expect("near-miss", near, 1, "confidently_wrong")
expect("empty sandbox", None, 1, "visibly_failed")
