"""Update endpoint preserving unknown record fields."""

from .. import core


def update(record, label=None, tone="plain", **changes):
    value = dict(record, **changes)
    if label is not None:
        value["label"] = label
    value["badge"] = core.make_badge(value["label"], tone=tone)
    return value


def update_many(records, tone="plain", **changes):
    return [update(record, tone=tone, **changes) for record in records]


def rename(record, label, tone="plain"):
    return update(record, label=label, tone=tone)


def retone(record, tone):
    return update(record, tone=tone)
