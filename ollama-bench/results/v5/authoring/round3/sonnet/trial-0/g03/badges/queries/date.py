"""Date query with tuple-based deterministic date comparisons."""

from .. import core


def date(record):
    return (record.get("year", 0), record.get("month", 0), record.get("day", 0))


def run(records, before=None, after=None, tone="plain"):
    selected = []
    for record in records:
        value = date(record)
        if before is not None and value >= before:
            continue
        if after is not None and value <= after:
            continue
        selected.append(dict(record, badge=core.make_badge(record["label"], tone=tone)))
    return selected


def sort(records, tone="plain"):
    return [dict(record, badge=core.make_badge(record["label"], tone=tone))
            for record in sorted(records, key=date)]


def first(records, tone="plain"):
    values = sort(records, tone=tone)
    return values[0] if values else None


def last(records, tone="plain"):
    values = sort(records, tone=tone)
    return values[-1] if values else None
