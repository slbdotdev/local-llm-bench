"""Dispatch table containing direct and reflected builder references."""

from . import core

HANDLERS = {"tag": core.make_tag, "badge": core.make_tag,
            "batch": core.batch}


def handler(name="tag"):
    return HANDLERS[name]


def call(name, label, tone="plain"):
    selected = handler(name)
    if name == "batch":
        return selected(label, tone=tone)
    return selected(label, tone)


def call_many(name, labels, tone="plain"):
    return [call(name, label, tone=tone) for label in labels]


def replace(name, fn):
    old = HANDLERS.get(name)
    HANDLERS[name] = fn
    return old


def names():
    return tuple(HANDLERS)


def dispatch_report(labels, tone="plain"):
    return {name: call_many(name, labels, tone=tone) for name in ("tag", "badge")}
