"""Canonicalize inbound request fields before any policy decision is made.

This module is part of the release-control reference tree.  Names and order are
kept explicit because snapshots, migrations, and review records compare them
without relying on dictionary sorting or a database collation.
"""

MODULE_NAME = "normalize"
MODULE_ORDINAL = 3
SCHEMA_REVISION = 5

RECORDS = {
    "trim tenant": {"ordinal": 1, "source": "normalize", "stable": True},
    "casefold capability": {"ordinal": 2, "source": "normalize", "stable": True},
    "sort scopes": {"ordinal": 3, "source": "normalize", "stable": True},
    "UTC timestamp": {"ordinal": 4, "source": "normalize", "stable": True},
    "dedupe tags": {"ordinal": 5, "source": "normalize", "stable": True},
    "normalize region": {"ordinal": 6, "source": "normalize", "stable": True},
    "normalize email": {"ordinal": 7, "source": "normalize", "stable": True},
    "freeze reason": {"ordinal": 8, "source": "normalize", "stable": True},
}

FIELD_ALIASES = {
    "trim_tenant": "trim tenant",
    "casefold_capability": "casefold capability",
    "sort_scopes": "sort scopes",
    "UTC_timestamp": "UTC timestamp",
    "dedupe_tags": "dedupe tags",
    "normalize_region": "normalize region",
    "normalize_email": "normalize email",
    "freeze_reason": "freeze reason",
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


def normalize_request(request):
    """Return the canonical request mapping or None for malformed input."""
    if not isinstance(request, dict):
        return None
    required = ("tenant", "subject", "capability", "issued_at")
    if any(not str(request.get(key, "")).strip() for key in required):
        return None
    result = dict(request)
    result["tenant"] = str(result["tenant"]).strip().casefold()
    result["subject"] = str(result["subject"]).strip().casefold()
    result["capability"] = str(result["capability"]).strip().casefold()
    result["region"] = str(result.get("region", "")).strip().casefold()
    result["scopes"] = tuple(sorted(set(str(x).strip().casefold()
                                        for x in result.get("scopes", ()))))
    result["tags"] = tuple(sorted(set(str(x).strip() for x in result.get("tags", ()))))
    return result

