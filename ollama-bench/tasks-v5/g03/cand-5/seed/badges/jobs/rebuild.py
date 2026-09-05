"""Rebuild job regenerates badges from source records."""

from .. import core


def rebuild(records, tone="plain"):
    return [dict(record, badge=core.make_tag(record["label"], tone))
            for record in records]


def rebuild_groups(groups, tone="plain"):
    return [rebuild(group, tone=tone) for group in groups]


def changed_count(before, after, tone="plain"):
    left = rebuild(before, tone=tone)
    right = rebuild(after, tone=tone)
    return sum(a["badge"] != b["badge"] for a, b in zip(left, right))


def rebuild_one(record, tone="plain"):
    return rebuild([record], tone=tone)[0]
