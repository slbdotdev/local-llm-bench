"""Status query."""

from .. import core


def run(records, status, tone="plain"):
    return [dict(record, badge=core.make_badge(record["label"], tone=tone))
            for record in records if record.get("status") == status]


def labels(records, status, tone="plain"):
    return [record["badge"] for record in run(records, status, tone=tone)]


def statuses(records):
    return sorted({record.get("status") for record in records})


def counts(records):
    return {status: len(run(records, status)) for status in statuses(records)}


def summary(records, tone="plain"):
    return {status: labels(records, status, tone=tone) for status in statuses(records)}
