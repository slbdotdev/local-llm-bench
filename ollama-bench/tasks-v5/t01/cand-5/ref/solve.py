from pathlib import Path

_OLD = "//infra/handbook/oncall.md"
_NEW = "//infra/runbooks/oncall.md"
_SPEC = """UPDATE|README.md|17
LEAVE|archive/incident-2025.md|20
LEAVE|archive/incident-2025.md|50
LEAVE|archive/legacy-guide.md|20
LEAVE|archive/legacy-guide.md|50
LEAVE|archive/quarterly-review.md|20
LEAVE|archive/quarterly-review.md|50
UPDATE|current/data-handling.md|27
UPDATE|current/data-handling.md|110
UPDATE|current/operations.md|27
LEAVE|current/operations.md|110
UPDATE|current/operations.md|152
UPDATE|current/release.md|27
UPDATE|current/release.md|110
UPDATE|current/release.md|152
UPDATE|current/reliability.md|27
UPDATE|current/reliability.md|110
UPDATE|current/reliability.md|152
UPDATE|current/security.md|27
LEAVE|current/security.md|110
UPDATE|current/security.md|152
LEAVE|history/2026-06-release.md|20
LEAVE|history/2026-06-release.md|50
LEAVE|history/2026-07-postmortem.md|20
LEAVE|history/2026-07-postmortem.md|50
LEAVE|history/2026-08-31-relocation.md|20
LEAVE|history/2026-08-31-relocation.md|50
UPDATE|ops/access-review.md|27
UPDATE|ops/access-review.md|110
UPDATE|ops/change-calendar.md|27
UPDATE|ops/change-calendar.md|110
UPDATE|ops/migration-status.md|27
LEAVE|ops/migration-status.md|110
UPDATE|ops/observability.md|27
UPDATE|ops/observability.md|110
UPDATE|services/edge/overview.md|27
UPDATE|services/edge/overview.md|110
UPDATE|services/edge/runbook.md|27
UPDATE|services/edge/runbook.md|110
UPDATE|services/identity/overview.md|27
UPDATE|services/identity/overview.md|110
UPDATE|services/identity/runbook.md|27
UPDATE|services/identity/runbook.md|110
UPDATE|services/ledger/overview.md|27
LEAVE|services/ledger/overview.md|110
UPDATE|services/ledger/runbook.md|27
UPDATE|services/ledger/runbook.md|110
UPDATE|services/search/overview.md|27
UPDATE|services/search/overview.md|110
UPDATE|services/search/runbook.md|27
LEAVE|services/search/runbook.md|110
UPDATE|services/warehouse/overview.md|27
UPDATE|services/warehouse/overview.md|110
UPDATE|services/warehouse/runbook.md|27
LEAVE|services/warehouse/runbook.md|110"""

_lines = []
for _row in _SPEC.splitlines():
    _action, _path, _number = _row.split("|")
    _replacement = _NEW if _action == "UPDATE" else "-"
    _lines.append("\t".join((_action, _path, _number, _OLD, _replacement)))
Path("reference_audit.txt").write_text("\n".join(_lines) + "\n", encoding="utf-8")
