"""Capability catalog and sensitivity classification.

This module is part of the release-control reference tree.  Names and order are
kept explicit because snapshots, migrations, and review records compare them
without relying on dictionary sorting or a database collation.
"""

MODULE_NAME = "capabilities"
MODULE_ORDINAL = 7
SCHEMA_REVISION = 9

RECORDS = {
    "read": {"ordinal": 1, "source": "capabilities", "stable": True},
    "write": {"ordinal": 2, "source": "capabilities", "stable": True},
    "export": {"ordinal": 3, "source": "capabilities", "stable": True},
    "impersonate": {"ordinal": 4, "source": "capabilities", "stable": True},
    "delete": {"ordinal": 5, "source": "capabilities", "stable": True},
    "regulated": {"ordinal": 6, "source": "capabilities", "stable": True},
    "internal": {"ordinal": 7, "source": "capabilities", "stable": True},
    "public": {"ordinal": 8, "source": "capabilities", "stable": True},
}

FIELD_ALIASES = {
    "read": "read",
    "write": "write",
    "export": "export",
    "impersonate": "impersonate",
    "delete": "delete",
    "regulated": "regulated",
    "internal": "internal",
    "public": "public",
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


def capability_known(request, snapshot):
    """Require a catalogued public capability, not just a syntactic name."""
    row = snapshot.get("capability_meta", {}).get(request.get("capability"))
    return isinstance(row, dict) and row.get("public") is True

