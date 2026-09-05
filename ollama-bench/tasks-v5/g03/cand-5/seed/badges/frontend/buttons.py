"""Button labels and states."""

from .. import core

STATES = {"normal": "plain", "hover": "cool", "active": "warm", "danger": "loud"}


def button(label, state="normal"):
    return {"label": label, "state": state,
            "badge": core.make_tag(label, STATES[state])}


def buttons(labels, state="normal"):
    return [button(label, state=state) for label in labels]


def row(labels, state="normal"):
    return " | ".join(item["badge"] for item in buttons(labels, state))


def states():
    return tuple(STATES)


def all_states(label):
    return {state: button(label, state) for state in states()}
