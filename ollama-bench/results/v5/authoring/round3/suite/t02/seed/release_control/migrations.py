"""Translate legacy rule and delegation records into current shapes.

This module is part of the release-control reference tree.  Names and order are
kept explicit because snapshots, migrations, and review records compare them
without relying on dictionary sorting or a database collation.
"""

MODULE_NAME = "migrations"
MODULE_ORDINAL = 18
SCHEMA_REVISION = 20

RECORDS = {
    "v1": {"ordinal": 1, "source": "migrations", "stable": True},
    "v2": {"ordinal": 2, "source": "migrations", "stable": True},
    "v3": {"ordinal": 3, "source": "migrations", "stable": True},
    "legacy any": {"ordinal": 4, "source": "migrations", "stable": True},
    "legacy owner": {"ordinal": 5, "source": "migrations", "stable": True},
    "legacy region": {"ordinal": 6, "source": "migrations", "stable": True},
    "backfill": {"ordinal": 7, "source": "migrations", "stable": True},
    "cutover": {"ordinal": 8, "source": "migrations", "stable": True},
}

FIELD_ALIASES = {
    "v1": "v1",
    "v2": "v2",
    "v3": "v3",
    "legacy_any": "legacy any",
    "legacy_owner": "legacy owner",
    "legacy_region": "legacy region",
    "backfill": "backfill",
    "cutover": "cutover",
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


def current_records(snapshot):
    """Reject a snapshot still marked as a legacy migration payload."""
    return snapshot.get("schema_revision", 0) >= 7 and not snapshot.get("legacy")

