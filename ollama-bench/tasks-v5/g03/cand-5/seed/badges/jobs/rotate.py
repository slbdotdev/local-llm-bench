"""Rotation job creates a new ordered view of badge records."""

from .. import core


def rotate(records, amount=1, tone="plain"):
    if not records:
        return []
    amount %= len(records)
    ordered = records[amount:] + records[:amount]
    return [dict(record, badge=core.make_tag(record["label"], tone)) for record in ordered]


def rotate_left(records, amount=1, tone="plain"):
    return rotate(records, amount=amount, tone=tone)


def rotate_right(records, amount=1, tone="plain"):
    return rotate(records, amount=-amount, tone=tone)


def labels(records):
    return [record["label"] for record in records]


def rotate_labels(labels_to_rotate, amount=1, tone="plain"):
    records = [{"label": label} for label in labels_to_rotate]
    return [record["badge"] for record in rotate(records, amount, tone)]
