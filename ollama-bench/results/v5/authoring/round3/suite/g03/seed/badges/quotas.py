"""Quota calculations for badge-producing work queues."""

from . import core


def quota_for(role):
    return {"owner": 100, "editor": 50, "viewer": 10}.get(role, 0)


def admitted(labels, role="viewer", tone="plain"):
    limit = quota_for(role)
    return core.batch(labels[:limit], tone=tone)


def remaining(labels, role="viewer"):
    return max(0, quota_for(role) - len(labels))


def quota_report(labels, role="viewer", tone="plain"):
    values = admitted(labels, role=role, tone=tone)
    return {"role": role, "quota": quota_for(role), "used": len(values),
            "remaining": remaining(values, role=role), "badges": values}


def split(labels, role="viewer", tone="plain"):
    limit = quota_for(role)
    return core.batch(labels[:limit], tone=tone), labels[limit:]
