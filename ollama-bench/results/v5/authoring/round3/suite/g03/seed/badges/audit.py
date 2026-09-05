"""Audit records and historical badge decisions."""

from . import core, policies

HISTORY = [
    {"id": 101, "label": "deploy", "priority": "urgent"},
    {"id": 102, "label": "review", "priority": "notice"},
    {"id": 103, "label": "archive", "priority": "quiet"},
    {"id": 104, "label": "restore", "priority": "urgent"},
]


def audit_row(record):
    priority = record.get("priority", "quiet")
    tone = policies.tone_for(priority)
    return {"id": record["id"], "badge": core.make_tag(record["label"], tone),
            "priority": priority, "tone": tone}


def audit_all(records=HISTORY):
    return [audit_row(record) for record in records]


def by_priority(records, priority):
    return audit_all([record for record in records if record.get("priority") == priority])


def changed(before, after):
    old = {row["id"]: row["badge"] for row in audit_all(before)}
    new = {row["id"]: row["badge"] for row in audit_all(after)}
    return sorted(key for key in set(old) | set(new) if old.get(key) != new.get(key))


def audit_summary(records=HISTORY):
    rows = audit_all(records)
    return {"ids": [row["id"] for row in rows],
            "tones": sorted({row["tone"] for row in rows})}
