"""Priority rules map numeric levels to tones."""

from .. import core

LEVELS = ((0, "muted"), (1, "plain"), (2, "warm"), (3, "loud"))


def tone(level):
    selected = "plain"
    for minimum, value in LEVELS:
        if level >= minimum:
            selected = value
    return selected


def render(label, level=1):
    return core.make_badge(label, tone=tone(level))


def render_records(records):
    return [dict(record, badge=render(record["label"], record.get("level", 1)))
            for record in records]


def levels(records):
    return sorted(record.get("level", 1) for record in records)


def highest(records):
    return max(levels(records), default=0)


def high_badges(records):
    top = highest(records)
    return [render(record["label"], top) for record in records]
