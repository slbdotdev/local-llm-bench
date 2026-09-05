"""Permission-aware badge labels."""

from . import core

ROLES = {"owner": frozenset(("read", "write", "delete")),
         "editor": frozenset(("read", "write")),
         "viewer": frozenset(("read",)), "guest": frozenset()}


def can(role, action):
    return action in ROLES.get(role, frozenset())


def visible(label, role="viewer", tone="plain"):
    if not can(role, "read"):
        return None
    return core.make_badge(label, tone=tone)


def action_badge(label, role="viewer", action="read", tone="plain"):
    if not can(role, action):
        return "[denied]"
    return core.make_badge(label, tone=tone)


def visible_many(labels, role="viewer", tone="plain"):
    return [visible(label, role=role, tone=tone) for label in labels]


def permissions(role):
    return sorted(ROLES.get(role, frozenset()))


def audit_access(records, role="viewer", tone="plain"):
    return [{"id": record["id"], "badge": visible(record["label"], role, tone)}
            for record in records]
