"""Stable sorting and ranking of rendered labels."""

from . import core


def rank(label, tone="plain", priority=0):
    return {"priority": priority, "label": label, "badge": core.make_tag(label, tone)}


def ranked(labels, tone="plain"):
    values = [rank(label, tone=tone, priority=len(str(label))) for label in labels]
    return sorted(values, key=lambda value: (value["priority"], value["label"]))


def top(labels, count=1, tone="plain"):
    return ranked(labels, tone=tone)[-count:]


def bottom(labels, count=1, tone="plain"):
    return ranked(labels, tone=tone)[:count]


def rank_records(records, tone="plain"):
    values = [rank(record["label"], tone=tone, priority=record.get("priority", 0))
              for record in records]
    return sorted(values, key=lambda value: value["priority"], reverse=True)


def rank_text(labels, tone="plain"):
    return [value["badge"] for value in ranked(labels, tone=tone)]
