"""Mapping operations over labels."""

from .. import core


def map_one(label, fn = core.make_badge, tone="plain"):
    return fn(label, tone=tone)


def map_all(labels, fn = core.make_badge, tone="plain"):
    return [map_one(label, fn=fn, tone=tone) for label in labels]


def map_records(records, fn = core.make_badge, tone="plain"):
    return [dict(record, badge=map_one(record["label"], fn=fn, tone=tone))
            for record in records]


def map_groups(groups, fn = core.make_badge, tone="plain"):
    return [map_all(group, fn=fn, tone=tone) for group in groups]


def map_dict(mapping, fn = core.make_badge, tone="plain"):
    return {key: map_one(value, fn=fn, tone=tone) for key, value in mapping.items()}
