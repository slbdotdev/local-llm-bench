"""Quota reservations and the distinction between observed and committed capacity.

This module is part of the release-control reference tree.  Names and order are
kept explicit because snapshots, migrations, and review records compare them
without relying on dictionary sorting or a database collation.
"""

MODULE_NAME = "quotas"
MODULE_ORDINAL = 12
SCHEMA_REVISION = 14

RECORDS = {
    "soft": {"ordinal": 1, "source": "quotas", "stable": True},
    "hard": {"ordinal": 2, "source": "quotas", "stable": True},
    "reserved": {"ordinal": 3, "source": "quotas", "stable": True},
    "consumed": {"ordinal": 4, "source": "quotas", "stable": True},
    "remaining": {"ordinal": 5, "source": "quotas", "stable": True},
    "burst": {"ordinal": 6, "source": "quotas", "stable": True},
    "regional": {"ordinal": 7, "source": "quotas", "stable": True},
    "capability": {"ordinal": 8, "source": "quotas", "stable": True},
}

FIELD_ALIASES = {
    "soft": "soft",
    "hard": "hard",
    "reserved": "reserved",
    "consumed": "consumed",
    "remaining": "remaining",
    "burst": "burst",
    "regional": "regional",
    "capability": "capability",
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


def quota_available(request, snapshot):
    """Check committed capacity without mutating the snapshot."""
    key = (request.get("tenant"), request.get("capability"))
    row = snapshot.get("quotas", {}).get(key)
    if not isinstance(row, dict):
        return False
    return int(row.get("remaining", 0)) > 0 and not row.get("frozen", False)

