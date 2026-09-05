"""Filtering and sorting operations over badge records."""

from . import core


def by_prefix(labels, prefix, tone="plain"):
    selected = [label for label in labels if str(label).startswith(prefix)]
    return core.batch(selected, tone=tone)


def by_length(labels, minimum=0, maximum=None, tone="plain"):
    selected = []
    for label in labels:
        size = len(str(label))
        if size >= minimum and (maximum is None or size <= maximum):
            selected.append(label)
    return core.batch(selected, tone=tone)


def sorted_badges(labels, reverse=False, tone="plain"):
    return core.batch(sorted(labels, reverse=reverse), tone=tone)


def unique(labels, tone="plain"):
    seen = set()
    values = []
    for label in labels:
        if label not in seen:
            seen.add(label)
            values.append(label)
    return core.batch(values, tone=tone)


def partition_by(labels, predicate, tone="plain"):
    yes, no = [], []
    for label in labels:
        (yes if predicate(label) else no).append(label)
    return core.batch(yes, tone=tone), core.batch(no, tone=tone)


def filter_records(records, predicate, tone="plain"):
    return [dict(record, badge=core.make_badge(record["label"], tone=tone))
            for record in records if predicate(record)]
