"""Event objects and reducers for the badge application."""

from . import core

EVENT_NAMES = ("created", "renamed", "colored", "removed")


def make_event(name, label, tone="plain", **metadata):
    if name not in EVENT_NAMES:
        raise ValueError(name)
    return dict(metadata, name=name, label=label, badge=core.make_badge(label, tone=tone))


def create(label, tone="plain", **metadata):
    return make_event("created", label, tone=tone, **metadata)


def rename(old_label, new_label, tone="plain"):
    return make_event("renamed", new_label, tone=tone, old_label=old_label)


def color(label, tone="plain"):
    return make_event("colored", label, tone=tone)


def remove(label, tone="plain"):
    return make_event("removed", label, tone=tone)


def replay(events, tone="plain"):
    return [dict(item, badge=core.make_badge(item["label"], tone=tone)) for item in events]


def names(events):
    return [item["name"] for item in events]


def summarize(events, tone="plain"):
    values = replay(events, tone=tone)
    return {"names": names(values), "last": values[-1]["badge"] if values else None}
