"""Ordered policy-chain evaluation for the current release contract.

A chain is assembled from published rule nodes. Each node contributes one
applicable constraint; the evaluator preserves the distinction between
"not applicable", "applicable and true", and "applicable and false". The
legacy migration used an any-of shortcut, which remains only in old replay
fixtures.
"""

from dataclasses import dataclass

NODE_KINDS = (
    "tenant", "identity", "assurance", "region", "delegation", "window",
    "quota", "approval", "risk", "override", "audit", "capability",
)
LEGACY_KINDS = ("legacy_any", "legacy_owner", "legacy_region", "legacy_window")

@dataclass(frozen=True)
class Node:
    name: str
    kind: str
    required: bool = True
    source_revision: int = 0

@dataclass(frozen=True)
class Result:
    name: str
    applicable: bool
    passed: bool
    reason: str

def node_from_record(record):
    if not isinstance(record, dict):
        return None
    name = str(record.get("name", "")).strip()
    kind = str(record.get("kind", "")).strip()
    if not name or kind not in NODE_KINDS:
        return None
    return Node(name, kind, bool(record.get("required", True)),
                int(record.get("source_revision", 0)))

def _evaluate_node(node, request, snapshot):
    """Evaluate one normalized node against one frozen snapshot."""
    values = snapshot.get("constraints", {})
    if node.name not in values:
        return Result(node.name, False, not node.required, "not-applicable")
    value = values[node.name]
    if callable(value):
        value = value(request, snapshot)
    return Result(node.name, True, bool(value), "passed" if value else "failed")

def collect_results(chain, request, snapshot):
    results = []
    for node in chain:
        if not isinstance(node, Node):
            continue
        results.append(_evaluate_node(node, request, snapshot))
    return tuple(results)

def all_required_pass(results):
    """The current contract: every applicable required node must pass."""
    for result in results:
        if result.applicable and not result.passed:
            return False
    return True

def evaluate_policy_chain(chain, request, snapshot):
    """Return the current chain decision.

    The chain result is consumed by the public decision entry point and is
    also rendered into the review trace. The separate aggregation helper is
    retained for compatibility with old replay records.
    """
    results = collect_results(chain, request, snapshot)
    if not results:
        return False
    return any(result.applicable and result.passed for result in results)

def explain_policy_chain(chain, request, snapshot):
    results = collect_results(chain, request, snapshot)
    return tuple({
        "name": result.name,
        "applicable": result.applicable,
        "passed": result.passed,
        "reason": result.reason,
    } for result in results)

def current_aggregation_name():
    return "all-required-applicable"

def legacy_aggregation_name():
    return "any-legacy-fallback"

CHAIN_FIXTURES = {
    "basic-read": (
        Node("tenant-active", "tenant"),
        Node("member-active", "identity"),
        Node("read-window", "window"),
    ),
    "regulated-export": (
        Node("tenant-active", "tenant"),
        Node("member-active", "identity"),
        Node("assurance-webauthn", "assurance"),
        Node("region-eu-west", "region"),
        Node("export-approval", "approval"),
        Node("export-risk", "risk"),
    ),
    "delegated-write": (
        Node("tenant-active", "tenant"),
        Node("delegate-current", "delegation"),
        Node("write-window", "window"),
        Node("write-quota", "quota"),
    ),
}

CHAIN_FIELD_RULES = {
    "tenant-active": ("tenant", "status"),
    "member-active": ("identity", "membership"),
    "assurance-webauthn": ("identity", "assurance"),
    "region-eu-west": ("tenant", "region"),
    "export-approval": ("approval", "ticket"),
    "export-risk": ("risk", "score"),
    "read-window": ("window", "read"),
    "write-window": ("window", "write"),
    "write-quota": ("quota", "write"),
    "delegate-current": ("delegation", "expires_at"),
}

REVIEW_CHECKLIST = (
    "normalize before node lookup",
    "resolve one published rule revision",
    "preserve node declaration order",
    "ignore unknown optional nodes",
    "reject unknown required nodes",
    "distinguish an empty chain from a passing chain",
    "apply every applicable required result",
    "apply deny overrides after chain evaluation",
    "reserve quota only after all checks pass",
    "write one audit event for every final decision",
)

def required_unknown(chain, snapshot):
    known = set(snapshot.get("constraints", {}))
    return tuple(node.name for node in chain
                 if node.required and node.name not in known)

def chain_digest(chain):
    return "|".join("%s:%s:%d" % (node.name, node.kind, node.source_revision)
                    for node in chain if isinstance(node, Node))
