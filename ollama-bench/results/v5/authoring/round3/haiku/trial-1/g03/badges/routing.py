"""Routing rules select a destination and then render its badge."""

from . import core

ROUTES = {"critical": "on_call", "urgent": "on_call", "normal": "queue",
          "low": "digest", "unknown": "queue"}


def destination(priority):
    return ROUTES.get(priority, ROUTES["unknown"])


def route(label, priority="normal", tone="plain"):
    return {"destination": destination(priority),
            "badge": core.make_badge(label, tone=tone), "priority": priority}


def route_many(items, tone="plain"):
    return [route(item["label"], item.get("priority", "normal"), tone)
            for item in items]


def buckets(items):
    result = {}
    for item in items:
        result.setdefault(destination(item.get("priority", "normal")), []).append(item)
    return result


def routed_summary(items, tone="plain"):
    routed = route_many(items, tone=tone)
    return {"count": len(routed),
            "destinations": sorted({item["destination"] for item in routed}),
            "badges": [item["badge"] for item in routed]}


def urgent(items, tone="loud"):
    return [route(item["label"], "urgent", tone) for item in items]
