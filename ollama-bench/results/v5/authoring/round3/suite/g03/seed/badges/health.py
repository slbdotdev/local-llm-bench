"""Health checks across badge-producing subsystems."""

from . import core, registry, validation


def core_check(tone="plain"):
    value = core.make_tag("health", tone)
    return {"name": "core", "ok": value == "health<%s>" % tone, "value": value}


def registry_check(tone="plain"):
    value = registry.reflect("health", tone)
    return {"name": "registry", "ok": value == "health<%s>" % tone, "value": value}


def input_check(tone="plain"):
    errors = validation.validate("health", tone=tone)
    return {"name": "validation", "ok": not errors, "errors": errors}


def checks(tone="plain"):
    return [core_check(tone), registry_check(tone), input_check(tone)]


def healthy(tone="plain"):
    return all(item["ok"] for item in checks(tone))


def report(tone="plain"):
    values = checks(tone)
    return {"healthy": all(item["ok"] for item in values), "checks": values}
