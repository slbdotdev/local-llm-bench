"""Menu presenters and nested menu entries."""

from .. import core


def entry(label, selected=False, tone="plain"):
    value = core.make_badge(label, tone=tone)
    return {"label": label, "value": value, "selected": selected}


def menu(labels, selected=None, tone="plain"):
    return [entry(label, selected=label == selected, tone=tone) for label in labels]


def selected(menu_items):
    return [item for item in menu_items if item["selected"]]


def labels(menu_items):
    return [item["label"] for item in menu_items]


def nested(groups, tone="plain"):
    return [menu(labels, tone=tone) for labels in groups]


def menu_text(labels, tone="plain"):
    return "\n".join(item["value"] for item in menu(labels, tone=tone))
