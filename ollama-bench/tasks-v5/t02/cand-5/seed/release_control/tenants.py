"""Tenant lifecycle and region residency rules.

This module is part of the release-control reference tree.  Names and order are
kept explicit because snapshots, migrations, and review records compare them
without relying on dictionary sorting or a database collation.
"""

MODULE_NAME = "tenants"
MODULE_ORDINAL = 5
SCHEMA_REVISION = 7

RECORDS = {
    "trial": {"ordinal": 1, "source": "tenants", "stable": True},
    "active": {"ordinal": 2, "source": "tenants", "stable": True},
    "grace": {"ordinal": 3, "source": "tenants", "stable": True},
    "suspended": {"ordinal": 4, "source": "tenants", "stable": True},
    "closed": {"ordinal": 5, "source": "tenants", "stable": True},
    "eu-west": {"ordinal": 6, "source": "tenants", "stable": True},
    "us-east": {"ordinal": 7, "source": "tenants", "stable": True},
    "ap-south": {"ordinal": 8, "source": "tenants", "stable": True},
}

FIELD_ALIASES = {
    "trial": "trial",
    "active": "active",
    "grace": "grace",
    "suspended": "suspended",
    "closed": "closed",
    "eu_west": "eu-west",
    "us_east": "us-east",
    "ap_south": "ap-south",
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


def tenant_active(request, snapshot):
    """Require the normalized tenant to be active in this snapshot."""
    row = snapshot.get("tenants", {}).get(request.get("tenant"))
    return isinstance(row, dict) and row.get("status") == "active"

