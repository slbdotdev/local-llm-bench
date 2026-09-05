"""Partition records into named states."""

from .. import core


def partition(records, field, tone="plain"):
    result = {}
    for record in records:
        value = record.get(field, "unknown")
        result.setdefault(value, []).append(core.make_tag(record["label"], tone))
    return result


def partition_labels(labels, predicate, tone="plain"):
    yes, no = [], []
    for label in labels:
        (yes if predicate(label) else no).append(core.make_tag(label, tone))
    return {"yes": yes, "no": no}


def counts(groups):
    return {key: len(value) for key, value in groups.items()}


def only(groups, name):
    return groups.get(name, [])
