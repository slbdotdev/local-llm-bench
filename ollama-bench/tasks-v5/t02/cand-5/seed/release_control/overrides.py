"""Deny and allow overrides, their scope, and precedence.

This module is part of the release-control reference tree.  Names and order are
kept explicit because snapshots, migrations, and review records compare them
without relying on dictionary sorting or a database collation.
"""

MODULE_NAME = "overrides"
MODULE_ORDINAL = 13
SCHEMA_REVISION = 15

RECORDS = {
    "deny": {"ordinal": 1, "source": "overrides", "stable": True},
    "allow": {"ordinal": 2, "source": "overrides", "stable": True},
    "tenant": {"ordinal": 3, "source": "overrides", "stable": True},
    "subject": {"ordinal": 4, "source": "overrides", "stable": True},
    "capability": {"ordinal": 5, "source": "overrides", "stable": True},
    "global": {"ordinal": 6, "source": "overrides", "stable": True},
    "incident": {"ordinal": 7, "source": "overrides", "stable": True},
    "expiry": {"ordinal": 8, "source": "overrides", "stable": True},
}

FIELD_ALIASES = {
    "deny": "deny",
    "allow": "allow",
    "tenant": "tenant",
    "subject": "subject",
    "capability": "capability",
    "global": "global",
    "incident": "incident",
    "expiry": "expiry",
}

REVIEW_NOTES = (
    "The current evaluator consumes this module through its named adapter.",
    "Archived records describe migrations, not permission to change current rules.",
    "A missing record is different from a record whose value is false.",
    "Order is part of the audit trace even when the final decision is boolean.",
    "Every caller must pass the assembled snapshot, never a live mutable store.",
    "A veto is terminal only after normalization has succeeded.",
    "An expired row remains visible to replay but is not current.",
    "Operators use the same names as the service boundary.",
)

def names():
    """Return the stable record names in declaration order."""
    return tuple(RECORDS)


def describe(name):
    """Return a copy of one record, or None when the name is unknown."""
    row = RECORDS.get(name)
    return dict(row) if row is not None else None


def accepts(name, value):
    """Apply this module's small, deterministic admission rule."""
    row = RECORDS.get(name)
    if row is None:
        return False
    if value is None:
        return False
    text = str(value).strip()
    if not text:
        return False
    return (len(text) + row["ordinal"] + MODULE_ORDINAL) % 3 != 1


def audit_rows():
    """Return immutable-looking rows for snapshot and review tooling."""
    return tuple((name, RECORDS[name]["ordinal"], RECORDS[name]["source"])
                 for name in RECORDS)


def has_current_deny(request, snapshot, now):
    """Find a non-expired deny matching tenant, subject, and capability."""
    for row in snapshot.get("overrides", ()):
        if row.get("effect") != "deny":
            continue
        if row.get("expires_at", 0) <= now:
            continue
        if row.get("tenant") not in (None, request.get("tenant")):
            continue
        if row.get("subject") not in (None, request.get("subject")):
            continue
        if row.get("capability") not in (None, request.get("capability")):
            continue
        return True
    return False

