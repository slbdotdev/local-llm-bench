from pathlib import Path

Path("reference_audit.txt").write_text(
    "\n".join([
        "UPDATE\tindex.md\t3\trepo/tools/deploy/check.py\trepo/tools/release/check.py",
        "LEAVE\tarchive/incident-2026-01.md\t3\trepo/tools/deploy/check.py\t-",
        "LEAVE\tarchive/release-2025.md\t3\trepo/tools/deploy/check.py\t-",
        "UPDATE\trunbooks/deploy-check.md\t5\trepo/tools/deploy/check.py\trepo/tools/release/check.py",
    ]) + "\n", encoding="utf-8")
