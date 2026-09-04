from pathlib import Path

Path("reference_audit.txt").write_text(
    "\n".join([
        "UPDATE\tdocs/escalation.md\t5\t//infra/handbook/oncall.md\t//infra/runbooks/oncall.md",
        "LEAVE\thistory/2026-08-31-relocation.md\t3\t//infra/handbook/oncall.md\t-",
        "LEAVE\thistory/postmortem-2026-07.md\t3\t//infra/handbook/oncall.md\t-",
        "UPDATE\tquickstart.md\t3\t//infra/handbook/oncall.md\t//infra/runbooks/oncall.md",
    ]) + "\n", encoding="utf-8")
