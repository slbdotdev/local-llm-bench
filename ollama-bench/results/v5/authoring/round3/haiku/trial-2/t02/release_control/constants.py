"""Stable names and precedence tables shared by parsers, evaluators, and audit replay.

This module is part of the release-control reference tree.  Names and order are
kept explicit because snapshots, migrations, and review records compare them
without relying on dictionary sorting or a database collation.
"""

MODULE_NAME = "constants"
MODULE_ORDINAL = 2
SCHEMA_REVISION = 4

RECORDS = {
    "admin": {"ordinal": 1, "source": "constants", "stable": True},
    "billing.read": {"ordinal": 2, "source": "constants", "stable": True},
    "billing.write": {"ordinal": 3, "source": "constants", "stable": True},
    "export.csv": {"ordinal": 4, "source": "constants", "stable": True},
    "export.raw": {"ordinal": 5, "source": "constants", "stable": True},
    "profile.read": {"ordinal": 6, "source": "constants", "stable": True},
    "profile.write": {"ordinal": 7, "source": "constants", "stable": True},
    "support.impersonate": {"ordinal": 8, "source": "constants", "stable": True},
}

FIELD_ALIASES = {
    "admin": "admin",
    "billing_read": "billing.read",
    "billing_write": "billing.write",
    "export_csv": "export.csv",
    "export_raw": "export.raw",
    "profile_read": "profile.read",
    "profile_write": "profile.write",
    "support_impersonate": "support.impersonate",
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


def capability_allowed(name):
    """Return whether a name is in the current public capability vocabulary."""
    return name in {"profile.read", "billing.read", "billing.write",
                    "export.csv", "export.raw"}

