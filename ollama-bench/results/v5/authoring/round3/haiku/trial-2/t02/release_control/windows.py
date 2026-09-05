"""Issued-at, expiry, maintenance, and freeze windows.

This module is part of the release-control reference tree.  Names and order are
kept explicit because snapshots, migrations, and review records compare them
without relying on dictionary sorting or a database collation.
"""

MODULE_NAME = "windows"
MODULE_ORDINAL = 11
SCHEMA_REVISION = 13

RECORDS = {
    "issued_at": {"ordinal": 1, "source": "windows", "stable": True},
    "expires_at": {"ordinal": 2, "source": "windows", "stable": True},
    "not_before": {"ordinal": 3, "source": "windows", "stable": True},
    "maintenance": {"ordinal": 4, "source": "windows", "stable": True},
    "freeze": {"ordinal": 5, "source": "windows", "stable": True},
    "clock skew": {"ordinal": 6, "source": "windows", "stable": True},
    "calendar day": {"ordinal": 7, "source": "windows", "stable": True},
    "rolling hour": {"ordinal": 8, "source": "windows", "stable": True},
}

FIELD_ALIASES = {
    "issued_at": "issued_at",
    "expires_at": "expires_at",
    "not_before": "not_before",
    "maintenance": "maintenance",
    "freeze": "freeze",
    "clock_skew": "clock skew",
    "calendar_day": "calendar day",
    "rolling_hour": "rolling hour",
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


def request_window_open(request, rule, now):
    """Check the rule's absolute window and the request's age."""
    try:
        issued = int(request["issued_at"])
        current = int(now)
        start = int(rule["not_before"])
        end = int(rule["expires_at"])
    except (KeyError, TypeError, ValueError):
        return False
    return start <= issued <= current and current < end and current - issued <= 86400

