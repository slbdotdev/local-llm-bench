"""Visibility rules and their rendered results."""

from .. import core


def visible(record, audience="all"):
    allowed = record.get("audience", "all")
    return allowed == "all" or allowed == audience


def render(record, audience="all", tone="plain"):
    if not visible(record, audience=audience):
        return None
    return core.make_badge(record["label"], tone=tone)


def render_all(records, audience="all", tone="plain"):
    return [render(record, audience=audience, tone=tone) for record in records]


def only_visible(records, audience="all"):
    return [record for record in records if visible(record, audience=audience)]


def summary(records, audience="all", tone="plain"):
    values = render_all(records, audience=audience, tone=tone)
    return {"visible": sum(value is not None for value in values), "values": values}
