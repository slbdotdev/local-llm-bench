"""Event stream operations."""

from .. import core


def emit(events, tone="plain"):
    for event in events:
        yield dict(event, badge=core.make_badge(event["label"], tone=tone))


def collect(events, tone="plain"):
    return list(emit(events, tone=tone))


def names(events):
    return [event["name"] for event in events]


def only(events, name, tone="plain"):
    return collect((event for event in events if event["name"] == name), tone=tone)


def latest(events, tone="plain"):
    values = list(events)
    return collect(values[-1:], tone=tone)
