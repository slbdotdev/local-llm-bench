"""Group labels by a key while rendering group members."""

from .. import core


def group_by(records, key, tone="plain"):
    result = {}
    for record in records:
        result.setdefault(record[key], []).append(core.make_badge(record["label"], tone=tone))
    return result


def group_labels(labels, key_fn, tone="plain"):
    result = {}
    for label in labels:
        result.setdefault(key_fn(label), []).append(core.make_badge(label, tone=tone))
    return result


def sizes(groups):
    return {key: len(values) for key, values in groups.items()}


def flatten(groups):
    return [value for values in groups.values() for value in values]


def keys(groups):
    return sorted(groups)
