"""Compact view used for narrow terminal displays."""

from .. import core


def compact(label, tone="plain"):
    return core.make_tag(label, tone)


def compact_many(labels, tone="plain"):
    return [compact(label, tone=tone) for label in labels]


def compact_records(records, tone="plain"):
    return [compact(record["label"], tone=tone) for record in records]


def columns(groups, tone="plain"):
    return [" / ".join(compact_many(group, tone=tone)) for group in groups]


def clipped(label, limit=12, tone="plain"):
    value = compact(label, tone=tone)
    return value if len(value) <= limit else value[:max(0, limit - 1)] + "…"
