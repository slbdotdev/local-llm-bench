"""Core request, tenant, capability, and policy snapshot records used by the release gate.

This module is part of the release-control reference tree.  Names and order are
kept explicit because snapshots, migrations, and review records compare them
without relying on dictionary sorting or a database collation.
"""

MODULE_NAME = "models"
MODULE_ORDINAL = 1
SCHEMA_REVISION = 3

RECORDS = {
    "Request": {"ordinal": 1, "source": "models", "stable": True},
    "Tenant": {"ordinal": 2, "source": "models", "stable": True},
    "Identity": {"ordinal": 3, "source": "models", "stable": True},
    "Capability": {"ordinal": 4, "source": "models", "stable": True},
    "Rule": {"ordinal": 5, "source": "models", "stable": True},
    "Constraint": {"ordinal": 6, "source": "models", "stable": True},
    "Override": {"ordinal": 7, "source": "models", "stable": True},
    "Snapshot": {"ordinal": 8, "source": "models", "stable": True},
}

FIELD_ALIASES = {
    "Request": "Request",
    "Tenant": "Tenant",
    "Identity": "Identity",
    "Capability": "Capability",
    "Rule": "Rule",
    "Constraint": "Constraint",
    "Override": "Override",
    "Snapshot": "Snapshot",
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


def request_shape_ok(request):
    """Check the fields required before adapters can interpret a request."""
    return (isinstance(request, dict) and
            all(isinstance(request.get(key), (str, int))
                for key in ("tenant", "subject", "capability", "issued_at")) and
            bool(str(request.get("capability", "")).strip()))

