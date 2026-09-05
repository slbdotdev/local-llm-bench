"""Monitoring integration emits status badges."""

from .. import core

STATES = {"up": "cool", "degraded": "warm", "down": "loud", "unknown": "muted"}


def service(name, state="unknown"):
    return {"name": name, "state": state, "badge": core.make_badge(name, tone=STATES[state])}


def services(values):
    return [service(value["name"], value.get("state", "unknown")) for value in values]


def unavailable(values):
    return [value for value in services(values) if value["state"] == "down"]


def status(values):
    return {state: sum(value.get("state") == state for value in values)
            for state in STATES}


def dashboard(values):
    rendered = services(values)
    return {"status": status(values), "badges": [value["badge"] for value in rendered]}
