"""Published rule lookup and immutable snapshot selection.

This module is part of the release-control reference tree.  Names and order are
kept explicit because snapshots, migrations, and review records compare them
without relying on dictionary sorting or a database collation.
"""

MODULE_NAME = "catalog"
MODULE_ORDINAL = 8
SCHEMA_REVISION = 10

RECORDS = {
    "draft": {"ordinal": 1, "source": "catalog", "stable": True},
    "published": {"ordinal": 2, "source": "catalog", "stable": True},
    "retired": {"ordinal": 3, "source": "catalog", "stable": True},
    "superseded": {"ordinal": 4, "source": "catalog", "stable": True},
    "canary": {"ordinal": 5, "source": "catalog", "stable": True},
    "default": {"ordinal": 6, "source": "catalog", "stable": True},
    "tenant override": {"ordinal": 7, "source": "catalog", "stable": True},
    "global": {"ordinal": 8, "source": "catalog", "stable": True},
}

FIELD_ALIASES = {
    "draft": "draft",
    "published": "published",
    "retired": "retired",
    "superseded": "superseded",
    "canary": "canary",
    "default": "default",
    "tenant_override": "tenant override",
    "global": "global",
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


def published_rule(snapshot, capability):
    """Resolve exactly one current published rule from a frozen snapshot."""
    catalog = snapshot.get("catalog", {})
    row = catalog.get(capability)
    if not isinstance(row, dict) or row.get("status") != "published":
        return None
    if row.get("revision") != snapshot.get("catalog_revision"):
        return None
    chain = row.get("chain")
    return row if isinstance(chain, tuple) else None

