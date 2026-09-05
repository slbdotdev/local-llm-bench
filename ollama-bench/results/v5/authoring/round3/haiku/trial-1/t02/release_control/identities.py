"""Identity membership and assurance checks, including service principals.

This module is part of the release-control reference tree.  Names and order are
kept explicit because snapshots, migrations, and review records compare them
without relying on dictionary sorting or a database collation.
"""

MODULE_NAME = "identities"
MODULE_ORDINAL = 6
SCHEMA_REVISION = 8

RECORDS = {
    "member": {"ordinal": 1, "source": "identities", "stable": True},
    "owner": {"ordinal": 2, "source": "identities", "stable": True},
    "security": {"ordinal": 3, "source": "identities", "stable": True},
    "auditor": {"ordinal": 4, "source": "identities", "stable": True},
    "bot": {"ordinal": 5, "source": "identities", "stable": True},
    "mfa": {"ordinal": 6, "source": "identities", "stable": True},
    "webauthn": {"ordinal": 7, "source": "identities", "stable": True},
    "certificate": {"ordinal": 8, "source": "identities", "stable": True},
}

FIELD_ALIASES = {
    "member": "member",
    "owner": "owner",
    "security": "security",
    "auditor": "auditor",
    "bot": "bot",
    "mfa": "mfa",
    "webauthn": "webauthn",
    "certificate": "certificate",
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


def identity_allows(request, snapshot):
    """Require an active member and the assurance level named by the rule."""
    identities = snapshot.get("identities", {})
    identity = identities.get(request.get("subject"))
    if not isinstance(identity, dict) or identity.get("status") != "active":
        return False
    if request.get("tenant") not in identity.get("tenants", ()):
        return False
    needed = snapshot.get("required_assurance", {}).get(
        request.get("capability"), "mfa")
    levels = {"password": 1, "mfa": 2, "webauthn": 3, "certificate": 4}
    return levels.get(identity.get("assurance"), 0) >= levels.get(needed, 99)

