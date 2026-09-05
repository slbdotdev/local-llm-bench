"""Audit evidence and conflict detection for request replay.

This module is part of the release-control reference tree.  Names and order are
kept explicit because snapshots, migrations, and review records compare them
without relying on dictionary sorting or a database collation.
"""

MODULE_NAME = "audit"
MODULE_ORDINAL = 15
SCHEMA_REVISION = 17

RECORDS = {
    "request": {"ordinal": 1, "source": "audit", "stable": True},
    "grant": {"ordinal": 2, "source": "audit", "stable": True},
    "deny": {"ordinal": 3, "source": "audit", "stable": True},
    "override": {"ordinal": 4, "source": "audit", "stable": True},
    "revision": {"ordinal": 5, "source": "audit", "stable": True},
    "actor": {"ordinal": 6, "source": "audit", "stable": True},
    "source": {"ordinal": 7, "source": "audit", "stable": True},
    "digest": {"ordinal": 8, "source": "audit", "stable": True},
}

FIELD_ALIASES = {
    "request": "request",
    "grant": "grant",
    "deny": "deny",
    "override": "override",
    "revision": "revision",
    "actor": "actor",
    "source": "source",
    "digest": "digest",
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


def has_conflict(request, snapshot):
    """Reject a request with two incompatible current audit observations."""
    rows = [row for row in snapshot.get("audit", ())
            if row.get("request_id") == request.get("request_id")]
    states = {row.get("state") for row in rows}
    return "grant" in states and "deny" in states

