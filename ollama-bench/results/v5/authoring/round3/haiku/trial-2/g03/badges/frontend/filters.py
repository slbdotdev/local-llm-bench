"""Interactive filter presenters."""

from .. import core


def option(value, active=False, tone="plain"):
    return {"value": value, "active": active, "badge": core.make_badge(value, tone=tone)}


def options(values, selected=None, tone="plain"):
    return [option(value, active=value in (selected or ()), tone=tone) for value in values]


def active(values):
    return [item["value"] for item in values if item["active"]]


def filter_labels(labels, selected=(), tone="plain"):
    return options(labels, selected=selected, tone=tone)


def summary(values, tone="plain"):
    rendered = options(values, tone=tone)
    return {"total": len(rendered), "active": len(active(rendered))}
