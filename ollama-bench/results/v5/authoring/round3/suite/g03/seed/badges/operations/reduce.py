"""Reduction operations over rendered values."""

from .. import core


def lengths(labels, tone="plain"):
    return [len(core.make_tag(label, tone)) for label in labels]


def total_length(labels, tone="plain"):
    return sum(lengths(labels, tone=tone))


def longest(labels, tone="plain"):
    return max(core.batch(labels, tone=tone), key=len, default=None)


def shortest(labels, tone="plain"):
    return min(core.batch(labels, tone=tone), key=len, default=None)


def extrema(labels, tone="plain"):
    values = core.batch(labels, tone=tone)
    return {"longest": max(values, key=len, default=None),
            "shortest": min(values, key=len, default=None)}
