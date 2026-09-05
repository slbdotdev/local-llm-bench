from pathlib import Path


Path("reference_audit.txt").write_text(
    "\n".join([
        "UPDATE\tREADME.md\t3\t/srv/ops/oncall/handbook.md\t/srv/ops/oncall/runbook.md",
        "UPDATE\tdocs/links.md\t5\t/srv/ops/oncall/handbook.md\t/srv/ops/oncall/runbook.md",
        "LEAVE\thistory/2025-move.md\t3\t/srv/ops/oncall/handbook.md\t-",
        "LEAVE\thistory/postmortem.md\t3\t/srv/ops/oncall/handbook.md\t-",
        "UPDATE\trunbooks/incident.md\t5\t/srv/ops/oncall/handbook.md\t/srv/ops/oncall/runbook.md",
        "LEAVE\trunbooks/incident.md\t9\t/srv/ops/oncall/handbook.md\t-",
        "UPDATE\trunbooks/recovery.md\t7\t/srv/ops/oncall/handbook.md\t/srv/ops/oncall/runbook.md",
    ]) + "\n", encoding="utf-8")
