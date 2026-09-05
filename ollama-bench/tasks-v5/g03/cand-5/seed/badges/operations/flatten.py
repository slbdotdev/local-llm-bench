"""Flatten nested records and render at the final boundary."""

from .. import core


def values(nested):
    return [value for group in nested for value in group]


def badges(nested, tone="plain"):
    return core.batch(values(nested), tone=tone)


def records(nested, tone="plain"):
    return [dict(record, badge=core.make_tag(record["label"], tone))
            for group in nested for record in group]


def count(nested):
    return len(values(nested))


def groups(nested, size):
    flat = values(nested)
    return [flat[index:index + size] for index in range(0, len(flat), size)]
