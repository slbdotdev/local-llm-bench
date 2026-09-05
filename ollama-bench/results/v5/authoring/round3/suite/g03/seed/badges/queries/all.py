"""All-record query."""

from .. import core


def run(records, tone="plain"):
    return [dict(record, badge=core.make_tag(record["label"], tone))
            for record in records]


def labels(records, tone="plain"):
    return [item["badge"] for item in run(records, tone=tone)]


def count(records):
    return len(records)


def page(records, number=1, size=20, tone="plain"):
    start = (number - 1) * size
    return run(records[start:start + size], tone=tone)


def ids(records):
    return [record.get("id") for record in records]
