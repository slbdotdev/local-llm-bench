"""Inventory snapshots expose every supported package surface."""

from . import core

MODULES = ("core", "flow", "registry", "formatting", "compat", "pipeline",
           "metrics", "exports", "catalog", "audit", "validation", "policies",
           "analytics", "collections", "filters", "themes", "localization",
           "permissions", "notifications", "templates", "routing", "events")


def item(name, label="Inventory", tone="plain"):
    return {"module": name, "badge": core.make_tag(label + ":" + name, tone)}


def items(label="Inventory", tone="plain"):
    return [item(name, label=label, tone=tone) for name in MODULES]


def names():
    return MODULES


def contains(name):
    return name in MODULES


def summary(label="Inventory", tone="plain"):
    values = items(label=label, tone=tone)
    return {"count": len(values), "first": values[0]["badge"], "last": values[-1]["badge"]}
