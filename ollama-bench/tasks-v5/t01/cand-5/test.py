import os
import sys
import threading
from pathlib import Path

_ORA_OLD = "//infra/handbook/oncall.md"
_ORA_NEW = "//infra/runbooks/oncall.md"
_ORA_ROWS = [
    ("README.md", 17, "UPDATE"),
    ("archive/incident-2025.md", 20, "LEAVE"),
    ("archive/incident-2025.md", 50, "LEAVE"),
    ("archive/legacy-guide.md", 20, "LEAVE"),
    ("archive/legacy-guide.md", 50, "LEAVE"),
    ("archive/quarterly-review.md", 20, "LEAVE"),
    ("archive/quarterly-review.md", 50, "LEAVE"),
    ("current/data-handling.md", 27, "UPDATE"),
    ("current/data-handling.md", 110, "UPDATE"),
    ("current/operations.md", 27, "UPDATE"),
    ("current/operations.md", 110, "LEAVE"),
    ("current/operations.md", 152, "UPDATE"),
    ("current/release.md", 27, "UPDATE"),
    ("current/release.md", 110, "UPDATE"),
    ("current/release.md", 152, "UPDATE"),
    ("current/reliability.md", 27, "UPDATE"),
    ("current/reliability.md", 110, "UPDATE"),
    ("current/reliability.md", 152, "UPDATE"),
    ("current/security.md", 27, "UPDATE"),
    ("current/security.md", 110, "LEAVE"),
    ("current/security.md", 152, "UPDATE"),
    ("history/2026-06-release.md", 20, "LEAVE"),
    ("history/2026-06-release.md", 50, "LEAVE"),
    ("history/2026-07-postmortem.md", 20, "LEAVE"),
    ("history/2026-07-postmortem.md", 50, "LEAVE"),
    ("history/2026-08-31-relocation.md", 20, "LEAVE"),
    ("history/2026-08-31-relocation.md", 50, "LEAVE"),
    ("ops/access-review.md", 27, "UPDATE"),
    ("ops/access-review.md", 110, "UPDATE"),
    ("ops/change-calendar.md", 27, "UPDATE"),
    ("ops/change-calendar.md", 110, "UPDATE"),
    ("ops/migration-status.md", 27, "UPDATE"),
    ("ops/migration-status.md", 110, "LEAVE"),
    ("ops/observability.md", 27, "UPDATE"),
    ("ops/observability.md", 110, "UPDATE"),
    ("services/edge/overview.md", 27, "UPDATE"),
    ("services/edge/overview.md", 110, "UPDATE"),
    ("services/edge/runbook.md", 27, "UPDATE"),
    ("services/edge/runbook.md", 110, "UPDATE"),
    ("services/identity/overview.md", 27, "UPDATE"),
    ("services/identity/overview.md", 110, "UPDATE"),
    ("services/identity/runbook.md", 27, "UPDATE"),
    ("services/identity/runbook.md", 110, "UPDATE"),
    ("services/ledger/overview.md", 27, "UPDATE"),
    ("services/ledger/overview.md", 110, "LEAVE"),
    ("services/ledger/runbook.md", 27, "UPDATE"),
    ("services/ledger/runbook.md", 110, "UPDATE"),
    ("services/search/overview.md", 27, "UPDATE"),
    ("services/search/overview.md", 110, "UPDATE"),
    ("services/search/runbook.md", 27, "UPDATE"),
    ("services/search/runbook.md", 110, "LEAVE"),
    ("services/warehouse/overview.md", 27, "UPDATE"),
    ("services/warehouse/overview.md", 110, "UPDATE"),
    ("services/warehouse/runbook.md", 27, "UPDATE"),
    ("services/warehouse/runbook.md", 110, "LEAVE"),
]
_ORA_TOTAL = len(_ORA_ROWS)
_ORA_FAILS = []
_ORA_DONE = 0
_ORA_LOCK = threading.Lock()


def _ora_watchdog():
    score = max(0, min(_ORA_TOTAL, _ORA_DONE - len(_ORA_FAILS)))
    print("SCORE %d/%d" % (score, _ORA_TOTAL))
    print("FAIL ['grader timed out (candidate too slow or hung)']")
    print("VERDICT visibly_failed")
    sys.stdout.flush()
    os._exit(1)


_ORA_TIMER = threading.Timer(45.0, _ora_watchdog)
_ORA_TIMER.daemon = True
_ORA_TIMER.start()


def _ora_is_standalone_filename(name):
    return (name and not name.startswith("/") and not name.startswith("./")
            and "\\" not in name
            and all(part not in ("", ".", "..") for part in name.split("/")))


def _ora_parse():
    try:
        raw = Path("reference_audit.txt").read_text(encoding="utf-8")
    except Exception:
        return None
    # Blank lines, line ending style, and a final newline are intentionally irrelevant.
    # Strip only record-edge whitespace so the five tab-separated fields stay exact.
    lines = [line.strip() for line in raw.splitlines() if line.strip()]
    if len(lines) != _ORA_TOTAL:
        return None
    parsed = []
    seen = set()
    for line in lines:
        fields = line.split("\t")
        if len(fields) != 5:
            return None
        action, filename, line_no, old, replacement = fields
        if action not in ("UPDATE", "LEAVE") or not _ora_is_standalone_filename(filename):
            return None
        if not line_no.isdigit() or int(line_no) < 1 or old != _ORA_OLD:
            return None
        if action == "UPDATE" and replacement != _ORA_NEW:
            return None
        if action == "LEAVE" and replacement != "-":
            return None
        key = (filename, int(line_no))
        if key in seen:
            return None
        seen.add(key)
        parsed.append((filename, int(line_no), action))
    return parsed


def _ora_finish(parsed):
    global _ORA_DONE
    if parsed is None:
        print("SCORE 0/%d" % _ORA_TOTAL)
        print("FAIL [unparseable reference_audit.txt]")
        print("VERDICT visibly_failed")
        sys.exit(1)
    score = 0
    failures = []
    expected = _ORA_ROWS
    for got, want in zip(parsed, expected):
        if got == want:
            score += 1
        else:
            failures.append("%s:%d_expected_%s" % (want[0], want[1], want[2].lower()))
        with _ORA_LOCK:
            _ORA_DONE += 1
    if len(parsed) != len(expected):
        failures.append("record_count")
    print("SCORE %d/%d" % (score, _ORA_TOTAL))
    if failures:
        print("FAIL [" + ", ".join(failures[:12]) + "]")
        print("VERDICT confidently_wrong")
        sys.exit(1)
    print("PASS")
    print("VERDICT correct")
    sys.exit(0)


try:
    _ora_finish(_ora_parse())
finally:
    _ORA_TIMER.cancel()
