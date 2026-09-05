"""Aggregations over independently rendered badge groups."""

from . import core


def aggregate(groups, tone="plain"):
    values = [core.batch(group, tone=tone) for group in groups]
    return {"groups": values, "count": sum(len(group) for group in values)}


def group_lengths(groups, tone="plain"):
    return [len(core.batch(group, tone=tone)) for group in groups]


def maximum(groups, tone="plain"):
    return max(group_lengths(groups, tone=tone), default=0)


def minimum(groups, tone="plain"):
    return min(group_lengths(groups, tone=tone), default=0)


def nonempty(groups, tone="plain"):
    return [core.batch(group, tone=tone) for group in groups if group]


def summary(groups, tone="plain"):
    value = aggregate(groups, tone=tone)
    return {"count": value["count"], "maximum": maximum(groups, tone=tone),
            "minimum": minimum(groups, tone=tone)}
