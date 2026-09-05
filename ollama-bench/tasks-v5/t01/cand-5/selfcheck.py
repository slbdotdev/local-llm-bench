import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
_OLD = "//infra/handbook/oncall.md"
_NEW = "//infra/runbooks/oncall.md"
_ROWS = [
    ("README.md", 17, "UPDATE", "//infra/handbook/oncall.md", "//infra/runbooks/oncall.md"),
    ("archive/incident-2025.md", 20, "LEAVE", "//infra/handbook/oncall.md", "-"),
    ("archive/incident-2025.md", 50, "LEAVE", "//infra/handbook/oncall.md", "-"),
    ("archive/legacy-guide.md", 20, "LEAVE", "//infra/handbook/oncall.md", "-"),
    ("archive/legacy-guide.md", 50, "LEAVE", "//infra/handbook/oncall.md", "-"),
    ("archive/quarterly-review.md", 20, "LEAVE", "//infra/handbook/oncall.md", "-"),
    ("archive/quarterly-review.md", 50, "LEAVE", "//infra/handbook/oncall.md", "-"),
    ("current/data-handling.md", 27, "UPDATE", "//infra/handbook/oncall.md", "//infra/runbooks/oncall.md"),
    ("current/data-handling.md", 110, "UPDATE", "//infra/handbook/oncall.md", "//infra/runbooks/oncall.md"),
    ("current/operations.md", 27, "UPDATE", "//infra/handbook/oncall.md", "//infra/runbooks/oncall.md"),
    ("current/operations.md", 110, "LEAVE", "//infra/handbook/oncall.md", "-"),
    ("current/operations.md", 152, "UPDATE", "//infra/handbook/oncall.md", "//infra/runbooks/oncall.md"),
    ("current/release.md", 27, "UPDATE", "//infra/handbook/oncall.md", "//infra/runbooks/oncall.md"),
    ("current/release.md", 110, "UPDATE", "//infra/handbook/oncall.md", "//infra/runbooks/oncall.md"),
    ("current/release.md", 152, "UPDATE", "//infra/handbook/oncall.md", "//infra/runbooks/oncall.md"),
    ("current/reliability.md", 27, "UPDATE", "//infra/handbook/oncall.md", "//infra/runbooks/oncall.md"),
    ("current/reliability.md", 110, "UPDATE", "//infra/handbook/oncall.md", "//infra/runbooks/oncall.md"),
    ("current/reliability.md", 152, "UPDATE", "//infra/handbook/oncall.md", "//infra/runbooks/oncall.md"),
    ("current/security.md", 27, "UPDATE", "//infra/handbook/oncall.md", "//infra/runbooks/oncall.md"),
    ("current/security.md", 110, "LEAVE", "//infra/handbook/oncall.md", "-"),
    ("current/security.md", 152, "UPDATE", "//infra/handbook/oncall.md", "//infra/runbooks/oncall.md"),
    ("history/2026-06-release.md", 20, "LEAVE", "//infra/handbook/oncall.md", "-"),
    ("history/2026-06-release.md", 50, "LEAVE", "//infra/handbook/oncall.md", "-"),
    ("history/2026-07-postmortem.md", 20, "LEAVE", "//infra/handbook/oncall.md", "-"),
    ("history/2026-07-postmortem.md", 50, "LEAVE", "//infra/handbook/oncall.md", "-"),
    ("history/2026-08-31-relocation.md", 20, "LEAVE", "//infra/handbook/oncall.md", "-"),
    ("history/2026-08-31-relocation.md", 50, "LEAVE", "//infra/handbook/oncall.md", "-"),
    ("ops/access-review.md", 27, "UPDATE", "//infra/handbook/oncall.md", "//infra/runbooks/oncall.md"),
    ("ops/access-review.md", 110, "UPDATE", "//infra/handbook/oncall.md", "//infra/runbooks/oncall.md"),
    ("ops/change-calendar.md", 27, "UPDATE", "//infra/handbook/oncall.md", "//infra/runbooks/oncall.md"),
    ("ops/change-calendar.md", 110, "UPDATE", "//infra/handbook/oncall.md", "//infra/runbooks/oncall.md"),
    ("ops/migration-status.md", 27, "UPDATE", "//infra/handbook/oncall.md", "//infra/runbooks/oncall.md"),
    ("ops/migration-status.md", 110, "LEAVE", "//infra/handbook/oncall.md", "-"),
    ("ops/observability.md", 27, "UPDATE", "//infra/handbook/oncall.md", "//infra/runbooks/oncall.md"),
    ("ops/observability.md", 110, "UPDATE", "//infra/handbook/oncall.md", "//infra/runbooks/oncall.md"),
    ("services/edge/overview.md", 27, "UPDATE", "//infra/handbook/oncall.md", "//infra/runbooks/oncall.md"),
    ("services/edge/overview.md", 110, "UPDATE", "//infra/handbook/oncall.md", "//infra/runbooks/oncall.md"),
    ("services/edge/runbook.md", 27, "UPDATE", "//infra/handbook/oncall.md", "//infra/runbooks/oncall.md"),
    ("services/edge/runbook.md", 110, "UPDATE", "//infra/handbook/oncall.md", "//infra/runbooks/oncall.md"),
    ("services/identity/overview.md", 27, "UPDATE", "//infra/handbook/oncall.md", "//infra/runbooks/oncall.md"),
    ("services/identity/overview.md", 110, "UPDATE", "//infra/handbook/oncall.md", "//infra/runbooks/oncall.md"),
    ("services/identity/runbook.md", 27, "UPDATE", "//infra/handbook/oncall.md", "//infra/runbooks/oncall.md"),
    ("services/identity/runbook.md", 110, "UPDATE", "//infra/handbook/oncall.md", "//infra/runbooks/oncall.md"),
    ("services/ledger/overview.md", 27, "UPDATE", "//infra/handbook/oncall.md", "//infra/runbooks/oncall.md"),
    ("services/ledger/overview.md", 110, "LEAVE", "//infra/handbook/oncall.md", "-"),
    ("services/ledger/runbook.md", 27, "UPDATE", "//infra/handbook/oncall.md", "//infra/runbooks/oncall.md"),
    ("services/ledger/runbook.md", 110, "UPDATE", "//infra/handbook/oncall.md", "//infra/runbooks/oncall.md"),
    ("services/search/overview.md", 27, "UPDATE", "//infra/handbook/oncall.md", "//infra/runbooks/oncall.md"),
    ("services/search/overview.md", 110, "UPDATE", "//infra/handbook/oncall.md", "//infra/runbooks/oncall.md"),
    ("services/search/runbook.md", 27, "UPDATE", "//infra/handbook/oncall.md", "//infra/runbooks/oncall.md"),
    ("services/search/runbook.md", 110, "LEAVE", "//infra/handbook/oncall.md", "-"),
    ("services/warehouse/overview.md", 27, "UPDATE", "//infra/handbook/oncall.md", "//infra/runbooks/oncall.md"),
    ("services/warehouse/overview.md", 110, "UPDATE", "//infra/handbook/oncall.md", "//infra/runbooks/oncall.md"),
    ("services/warehouse/runbook.md", 27, "UPDATE", "//infra/handbook/oncall.md", "//infra/runbooks/oncall.md"),
    ("services/warehouse/runbook.md", 110, "LEAVE", "//infra/handbook/oncall.md", "-"),
]


def _correct_lines():
    return ["%s\t%s\t%d\t%s\t%s" % (action, p, n, old, repl)
            for p, n, action, old, repl in _ROWS]


def _run(label, lines=None, reference=False):
    with tempfile.TemporaryDirectory(dir=_ROOT) as name:
        box = Path(name)
        shutil.copytree(_ROOT / "seed", box, dirs_exist_ok=True)
        shutil.copy(_ROOT / "test.py", box / "_hidden_test.py")
        if reference:
            shutil.copy(_ROOT / "ref" / "solve.py", box / "solve.py")
            made = subprocess.run([sys.executable, "solve.py"], cwd=box,
                                  text=True, capture_output=True, timeout=10)
            if made.returncode:
                return False, label + ": reference failed"
        elif lines is not None:
            (box / "reference_audit.txt").write_text(lines, encoding="utf-8")
        result = subprocess.run([sys.executable, "_hidden_test.py"], cwd=box,
                                text=True, capture_output=True, timeout=50)
        return result.returncode, result.stdout + result.stderr


def main():
    correct = "\n".join(_correct_lines()) + "\n"
    cases = [
        ("correct reference", None, True),
        ("no trailing newline", correct.rstrip("\n"), False),
        ("two trailing newlines", correct + "\n", False),
        ("CRLF line endings", correct.replace("\n", "\r\n"), False),
        ("one leading blank line", "\n" + correct, False),
        ("trailing spaces on one line", correct.replace("\t" + _NEW + "\n", "\t" + _NEW + "   \n", 1), False),
        ("ordering violation", "\n".join(reversed(_correct_lines())) + "\n", False),
        ("plausible wrong all updates", "\n".join(
            ("UPDATE\t" + line.split("\t", 1)[1].rsplit("\t", 1)[0] + "\t" + _NEW)
            if line.startswith("LEAVE\t") else line
            for line in correct.splitlines()) + "\n", False),
        ("untouched sandbox", None, False),
    ]
    results = []
    for label, lines, reference in cases:
        rc, out = _run(label, lines, reference)
        results.append((label, rc, out))
    checks = [
        ("correct reference", results[0][1] == 0 and "SCORE 55/55" in results[0][2]
         and "PASS" in results[0][2] and "VERDICT correct" in results[0][2]),
        ("no trailing newline", results[1][1] == 0 and "VERDICT correct" in results[1][2]),
        ("two trailing newlines", results[2][1] == 0 and "VERDICT correct" in results[2][2]),
        ("CRLF line endings", results[3][1] == 0 and "VERDICT correct" in results[3][2]),
        ("one leading blank line", results[4][1] == 0 and "VERDICT correct" in results[4][2]),
        ("trailing spaces on one line", results[5][1] == 0 and "VERDICT correct" in results[5][2]),
        ("ordering violation", results[6][1] != 0 and "VERDICT" in results[6][2]),
        ("plausible wrong all updates", results[7][1] != 0 and "VERDICT confidently_wrong" in results[7][2]),
        ("untouched sandbox", results[8][1] != 0 and "VERDICT visibly_failed" in results[8][2]
         and "Traceback" not in results[8][2]),
    ]
    for label, ok in checks:
        print("%s: %s" % (label, "PASS" if ok else "FAIL"))
    if not all(ok for _, ok in checks):
        for label, rc, out in results:
            print("---", label, rc, repr(out))
        sys.exit(1)


if __name__ == "__main__":
    main()
