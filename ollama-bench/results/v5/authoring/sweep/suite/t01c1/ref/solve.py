from pathlib import Path

Path("reference_audit.txt").write_text(
    "\n".join([
        "UPDATE\tREADME.md\t3\t/workspace/ops/runbook.md\t/workspace/operations/runbook.md",
        "UPDATE\tdocs/deploy.md\t5\t/workspace/ops/runbook.md\t/workspace/operations/runbook.md",
        "LEAVE\tdocs/history/2026-08-18-move.md\t3\t/workspace/ops/runbook.md\t-",
        "LEAVE\tdocs/history/incidents.md\t5\t/workspace/ops/runbook.md\t-",
    ]) + "\n", encoding="utf-8")
