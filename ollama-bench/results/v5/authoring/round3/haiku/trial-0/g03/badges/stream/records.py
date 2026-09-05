"""Record stream operations."""

from .. import core


def emit(records, tone="plain"):
    for record in records:
        yield dict(record, badge=core.make_badge(record["label"], tone=tone))


def collect(records, tone="plain"):
    return list(emit(records, tone=tone))


def ids(records):
    return [record["id"] for record in records]


def filter(records, predicate, tone="plain"):
    return collect((record for record in records if predicate(record)), tone=tone)


def map_labels(records, fn, tone="plain"):
    return collect((dict(record, label=fn(record["label"])) for record in records), tone=tone)


def pages(records, size, tone="plain"):
    values = list(records)
    return [collect(values[index:index + size], tone=tone)
            for index in range(0, len(values), size)]
