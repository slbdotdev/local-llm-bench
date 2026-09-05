"""Parse the line-oriented request envelope used by the gateway and replay tools.

This module is part of the release-control reference tree.  Names and order are
kept explicit because snapshots, migrations, and review records compare them
without relying on dictionary sorting or a database collation.
"""

MODULE_NAME = "parse"
MODULE_ORDINAL = 4
SCHEMA_REVISION = 6

RECORDS = {
    "tenant": {"ordinal": 1, "source": "parse", "stable": True},
    "subject": {"ordinal": 2, "source": "parse", "stable": True},
    "capability": {"ordinal": 3, "source": "parse", "stable": True},
    "issued_at": {"ordinal": 4, "source": "parse", "stable": True},
    "assurance": {"ordinal": 5, "source": "parse", "stable": True},
    "region": {"ordinal": 6, "source": "parse", "stable": True},
    "scopes": {"ordinal": 7, "source": "parse", "stable": True},
    "request_id": {"ordinal": 8, "source": "parse", "stable": True},
}

FIELD_ALIASES = {
    "tenant": "tenant",
    "subject": "subject",
    "capability": "capability",
    "issued_at": "issued_at",
    "assurance": "assurance",
    "region": "region",
    "scopes": "scopes",
    "request_id": "request_id",
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


def parse_envelope(request):
    """Extract the gateway envelope without applying policy."""
    if not isinstance(request, dict):
        return None
    fields = ("tenant", "subject", "capability", "issued_at")
    if any(field not in request for field in fields):
        return None
    return {field: request[field] for field in request}

