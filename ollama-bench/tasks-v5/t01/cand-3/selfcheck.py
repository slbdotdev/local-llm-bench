import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
_EXPECTED = [
    ("docs/escalation.md", 5, "UPDATE", "//infra/handbook/oncall.md", "//infra/runbooks/oncall.md"),
    ("history/2026-08-31-relocation.md", 3, "LEAVE", "//infra/handbook/oncall.md", "-"),
    ("history/postmortem-2026-07.md", 3, "LEAVE", "//infra/handbook/oncall.md", "-"),
    ("quickstart.md", 3, "UPDATE", "//infra/handbook/oncall.md", "//infra/runbooks/oncall.md"),
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
            new_path = next(row[4] for row in _EXPECTED if row[2] == "UPDATE")
            lines = ["UPDATE\t%s\t%d\t%s\t%s" % (row[0], row[1], row[3], new_path)
                     for row in _EXPECTED]
            (box / "reference_audit.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
        result = subprocess.run([sys.executable, "_hidden_test.py"], cwd=box,
                                text=True, capture_output=True, timeout=50)
        return result.returncode, result.stdout + result.stderr


def _has_format_examples():
    samples = [
        "UPDATE<TAB>path/to/file.md<TAB>8<TAB>/old/path.md<TAB>/new/path.md",
        "LEAVE<TAB>path/to/archive.md<TAB>19<TAB>/old/path.md<TAB>-",
    ]
    return all(re.fullmatch(
        r"(?:UPDATE|LEAVE)\t[^/][^\t]*\.md\t[1-9][0-9]*\t/[^\t]+\t(?:/[^\t]+|-)",
        sample.replace("<TAB>", "\t")) for sample in samples)


def main():
    outcomes = [("format example", _has_format_examples())]
    rc, out = _run("reference")
    outcomes.append(("reference -> correct", rc == 0 and "SCORE 8/8" in out
                     and "PASS" in out and "VERDICT correct" in out))
    rc, out = _run("near-miss")
    outcomes.append(("near-miss -> confidently_wrong", rc != 0
                     and "VERDICT confidently_wrong" in out))
    rc, out = _run("empty")
    outcomes.append(("empty sandbox -> visibly_failed", rc != 0
                     and "VERDICT visibly_failed" in out))
    for label, ok in outcomes:
        print("%s: %s" % (label, "PASS" if ok else "FAIL"))
    if not all(ok for _, ok in outcomes):
        sys.exit(1)


if __name__ == "__main__":
    main()
