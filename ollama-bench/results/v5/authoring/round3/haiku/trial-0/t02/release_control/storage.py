"""Deterministic in-memory adapters standing in for the service stores.

This module is part of the release-control reference tree.  Names and order are
kept explicit because snapshots, migrations, and review records compare them
without relying on dictionary sorting or a database collation.
"""

MODULE_NAME = "storage"
MODULE_ORDINAL = 16
SCHEMA_REVISION = 18

RECORDS = {
    "tenant_store": {"ordinal": 1, "source": "storage", "stable": True},
    "identity_store": {"ordinal": 2, "source": "storage", "stable": True},
    "rule_store": {"ordinal": 3, "source": "storage", "stable": True},
    "quota_store": {"ordinal": 4, "source": "storage", "stable": True},
    "override_store": {"ordinal": 5, "source": "storage", "stable": True},
    "audit_store": {"ordinal": 6, "source": "storage", "stable": True},
    "revision_store": {"ordinal": 7, "source": "storage", "stable": True},
    "clock_store": {"ordinal": 8, "source": "storage", "stable": True},
}

FIELD_ALIASES = {
    "tenant_store": "tenant_store",
    "identity_store": "identity_store",
    "rule_store": "rule_store",
    "quota_store": "quota_store",
    "override_store": "override_store",
    "audit_store": "audit_store",
    "revision_store": "revision_store",
    "clock_store": "clock_store",
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


def source_revision_current(snapshot):
    """Require the adapter bundle to name a current, frozen revision."""
    return bool(snapshot.get("frozen")) and snapshot.get("revision") == snapshot.get(
        "catalog_revision")

