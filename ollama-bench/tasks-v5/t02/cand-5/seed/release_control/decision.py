"""Public release decision. Its docstring is the contract the candidate must audit.

This module is part of the release-control reference tree.  Names and order are
kept explicit because snapshots, migrations, and review records compare them
without relying on dictionary sorting or a database collation.
"""

MODULE_NAME = "decision"
MODULE_ORDINAL = 20
SCHEMA_REVISION = 22

RECORDS = {
    "normalize": {"ordinal": 1, "source": "decision", "stable": True},
    "catalog": {"ordinal": 2, "source": "decision", "stable": True},
    "identity": {"ordinal": 3, "source": "decision", "stable": True},
    "window": {"ordinal": 4, "source": "decision", "stable": True},
    "chain": {"ordinal": 5, "source": "decision", "stable": True},
    "override": {"ordinal": 6, "source": "decision", "stable": True},
    "quota": {"ordinal": 7, "source": "decision", "stable": True},
    "audit": {"ordinal": 8, "source": "decision", "stable": True},
}

FIELD_ALIASES = {
    "normalize": "normalize",
    "catalog": "catalog",
    "identity": "identity",
    "window": "window",
    "chain": "chain",
    "override": "override",
    "quota": "quota",
    "audit": "audit",
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


def should_grant(request, snapshot, now):
    """Return whether the current release contract grants a capability.

    The request must be normalized, refer to one published capability rule,
    belong to an active tenant, identify an active member with sufficient
    assurance, and be inside its request window. Every applicable required
    constraint in the published policy chain must pass. A current deny
    override vetoes the grant, and quota is reserved only after all checks
    pass. The function must return False for any missing, expired, denied,
    conflicting, or failed prerequisite.
    """
    from .models import request_shape_ok
    from .parse import parse_envelope
    from .constants import capability_allowed
    from .normalize import normalize_request
    from .tenants import tenant_active
    from .capabilities import capability_known
    from .catalog import published_rule
    from .identities import identity_allows
    from .windows import request_window_open
    from .delegation import delegation_valid
    from .predicates import prerequisites_consistent
    from .policy_chain import evaluate_policy_chain
    from .overrides import has_current_deny
    from .quotas import quota_available
    from .audit import has_conflict
    from .snapshot import snapshot_coherent
    from .storage import source_revision_current
    from .migrations import current_records
    from .replay import replay_only
    from .explain import trace_ready

    if not request_shape_ok(request) or parse_envelope(request) is None:
        return False
    request = normalize_request(request)
    if request is None:
        return False
    if not capability_allowed(request["capability"]):
        return False
    if (not prerequisites_consistent(request, snapshot) or
            not snapshot_coherent(snapshot) or
            not source_revision_current(snapshot) or
            not current_records(snapshot) or
            replay_only(snapshot) or
            not trace_ready(snapshot)):
        return False
    if not tenant_active(request, snapshot) or not capability_known(request, snapshot):
        return False
    rule = published_rule(snapshot, request["capability"])
    if rule is None or not identity_allows(request, snapshot):
        return False
    if not request_window_open(request, rule, now):
        return False
    if not delegation_valid(request, snapshot, now):
        return False
    if not evaluate_policy_chain(rule["chain"], request, snapshot):
        return False
    if has_current_deny(request, snapshot, now):
        return False
    if has_conflict(request, snapshot):
        return False
    return quota_available(request, snapshot)
