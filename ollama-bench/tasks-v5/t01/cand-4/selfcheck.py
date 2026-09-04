import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


_ROOT = Path(__file__).resolve().parent
_EXPECTED = [
    ("README.md", 3, "UPDATE", "/srv/ops/oncall/handbook.md", "/srv/ops/oncall/runbook.md"),
    ("docs/links.md", 5, "UPDATE", "/srv/ops/oncall/handbook.md", "/srv/ops/oncall/runbook.md"),
    ("history/2025-move.md", 3, "LEAVE", "/srv/ops/oncall/handbook.md", "-"),
    ("history/postmortem.md", 3, "LEAVE", "/srv/ops/oncall/handbook.md", "-"),
    ("runbooks/incident.md", 5, "UPDATE", "/srv/ops/oncall/handbook.md", "/srv/ops/oncall/runbook.md"),
    ("runbooks/incident.md", 9, "LEAVE", "/srv/ops/oncall/handbook.md", "-"),
    ("runbooks/recovery.md", 7, "UPDATE", "/srv/ops/oncall/handbook.md", "/srv/ops/oncall/runbook.md"),
]


def _run(kind):
    with tempfile.TemporaryDirectory(dir=_ROOT) as name:
        box = Path(name)
        shutil.copytree(_ROOT / "seed", box, dirs_exist_ok=True)
        shutil.copy(_ROOT / "test.py", box / "_hidden_test.py")
        if kind == "reference":
            shutil.copy(_ROOT / "ref" / "solve.py", box / "solve.py")
            made = subprocess.run([sys.executable, "solve.py"], cwd=box,
                                  text=True, capture_output=True, timeout=10)
            if made.returncode:
                return made.returncode, made.stdout + made.stderr
        elif kind == "near-miss":
            lines = ["UPDATE\t%s\t%d\t%s\t%s" %
                     (row[0], row[1], row[3], row[4] if row[2] == "UPDATE"
                      else "/srv/ops/oncall/runbook.md") for row in _EXPECTED]
            (box / "reference_audit.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
        result = subprocess.run([sys.executable, "_hidden_test.py"], cwd=box,
                                text=True, capture_output=True, timeout=50)
        return result.returncode, result.stdout + result.stderr


def _format_template_examples_work():
    samples = [
        "UPDATE<TAB>path/to/file.md<TAB>8<TAB>/old/path.md<TAB>/new/path.md",
        "LEAVE<TAB>path/to/archive.md<TAB>19<TAB>/old/path.md<TAB>-",
    ]
    pattern = r"(?:UPDATE|LEAVE)\t[^/][^\t]*\.md\t[1-9][0-9]*\t/[^\t]+\t(?:/[^\t]+|-)"
    return all(re.fullmatch(pattern, sample.replace("<TAB>", "\t")) for sample in samples)


def main():
    checks = [("format examples", _format_template_examples_work())]
    rc, out = _run("reference")
    checks.append(("reference -> correct", rc == 0 and "SCORE 14/14" in out
                   and "PASS" in out and "VERDICT correct" in out))
    rc, out = _run("near-miss")
    checks.append(("near-miss -> confidently_wrong", rc != 0
                   and "VERDICT confidently_wrong" in out))
    rc, out = _run("empty")
    checks.append(("empty sandbox -> visibly_failed", rc != 0
                   and "VERDICT visibly_failed" in out))
    for label, ok in checks:
        print("%s: %s" % (label, "PASS" if ok else "FAIL"))
    if not all(ok for _, ok in checks):
        sys.exit(1)


if __name__ == "__main__":
    main()
