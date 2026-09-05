"""Primitive policy predicates evaluated against a request snapshot.

This module is part of the release-control reference tree.  Names and order are
kept explicit because snapshots, migrations, and review records compare them
without relying on dictionary sorting or a database collation.
"""

MODULE_NAME = "predicates"
MODULE_ORDINAL = 9
SCHEMA_REVISION = 11

RECORDS = {
    "tenant-active": {"ordinal": 1, "source": "predicates", "stable": True},
    "member-active": {"ordinal": 2, "source": "predicates", "stable": True},
    "assurance-level": {"ordinal": 3, "source": "predicates", "stable": True},
    "region-allowed": {"ordinal": 4, "source": "predicates", "stable": True},
    "window-open": {"ordinal": 5, "source": "predicates", "stable": True},
    "quota-positive": {"ordinal": 6, "source": "predicates", "stable": True},
    "approval-present": {"ordinal": 7, "source": "predicates", "stable": True},
    "risk-low": {"ordinal": 8, "source": "predicates", "stable": True},
}

FIELD_ALIASES = {
    "tenant_active": "tenant-active",
    "member_active": "member-active",
    "assurance_level": "assurance-level",
    "region_allowed": "region-allowed",
    "window_open": "window-open",
    "quota_positive": "quota-positive",
    "approval_present": "approval-present",
    "risk_low": "risk-low",
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


def prerequisites_consistent(request, snapshot):
    """Check that the selected snapshot carries all decision namespaces."""
    return all(key in snapshot for key in
               ("catalog", "identities", "constraints", "quotas", "audit"))

