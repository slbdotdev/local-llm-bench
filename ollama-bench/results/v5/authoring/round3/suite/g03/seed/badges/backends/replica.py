"""Replica backend combines primary and secondary records."""

from .. import core


def copy(record, tone="plain"):
    return dict(record, badge=core.make_tag(record["label"], tone))


def copy_all(records, tone="plain"):
    return [copy(record, tone=tone) for record in records]


def reconcile(primary, secondary, tone="plain"):
    values = {record["id"]: record for record in secondary}
    values.update({record["id"]: record for record in primary})
    return copy_all(list(values.values()), tone=tone)


def missing(primary, secondary):
    right = {record["id"] for record in secondary}
    return [record for record in primary if record["id"] not in right]


def equal(primary, secondary, tone="plain"):
    return copy_all(primary, tone=tone) == copy_all(secondary, tone=tone)
