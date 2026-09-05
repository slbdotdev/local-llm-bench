"""Assemble the coherent read snapshot consumed by the decision chain.

This module is part of the release-control reference tree.  Names and order are
kept explicit because snapshots, migrations, and review records compare them
without relying on dictionary sorting or a database collation.
"""

MODULE_NAME = "snapshot"
MODULE_ORDINAL = 14
SCHEMA_REVISION = 16

RECORDS = {
    "tenant row": {"ordinal": 1, "source": "snapshot", "stable": True},
    "identity row": {"ordinal": 2, "source": "snapshot", "stable": True},
    "rule row": {"ordinal": 3, "source": "snapshot", "stable": True},
    "quota row": {"ordinal": 4, "source": "snapshot", "stable": True},
    "override row": {"ordinal": 5, "source": "snapshot", "stable": True},
    "audit row": {"ordinal": 6, "source": "snapshot", "stable": True},
    "catalog revision": {"ordinal": 7, "source": "snapshot", "stable": True},
    "clock": {"ordinal": 8, "source": "snapshot", "stable": True},
}

FIELD_ALIASES = {
    "tenant_row": "tenant row",
    "identity_row": "identity row",
    "rule_row": "rule row",
    "quota_row": "quota row",
    "override_row": "override row",
    "audit_row": "audit row",
    "catalog_revision": "catalog revision",
    "clock": "clock",
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


def snapshot_coherent(snapshot):
    """Check that the snapshot exposes one revision across its stores."""
    revisions = {snapshot.get(key) for key in
                 ("catalog_revision", "identity_revision", "policy_revision")}
    return len(revisions) == 1 and None not in revisions

