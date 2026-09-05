"""Time-bounded delegation grants and subject substitution rules.

This module is part of the release-control reference tree.  Names and order are
kept explicit because snapshots, migrations, and review records compare them
without relying on dictionary sorting or a database collation.
"""

MODULE_NAME = "delegation"
MODULE_ORDINAL = 10
SCHEMA_REVISION = 12

RECORDS = {
    "delegate": {"ordinal": 1, "source": "delegation", "stable": True},
    "grantor": {"ordinal": 2, "source": "delegation", "stable": True},
    "expires_at": {"ordinal": 3, "source": "delegation", "stable": True},
    "scope": {"ordinal": 4, "source": "delegation", "stable": True},
    "revoked": {"ordinal": 5, "source": "delegation", "stable": True},
    "service account": {"ordinal": 6, "source": "delegation", "stable": True},
    "break glass": {"ordinal": 7, "source": "delegation", "stable": True},
    "ticket": {"ordinal": 8, "source": "delegation", "stable": True},
}

FIELD_ALIASES = {
    "delegate": "delegate",
    "grantor": "grantor",
    "expires_at": "expires_at",
    "scope": "scope",
    "revoked": "revoked",
    "service_account": "service account",
    "break_glass": "break glass",
    "ticket": "ticket",
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


def delegation_valid(request, snapshot, now):
    """Check an optional delegation without replacing membership."""
    row = snapshot.get("delegations", {}).get(request.get("subject"))
    if row is None:
        return True
    return (row.get("tenant") == request.get("tenant") and
            row.get("capability") == request.get("capability") and
            int(row.get("expires_at", 0)) > int(now) and
            not row.get("revoked", False))

