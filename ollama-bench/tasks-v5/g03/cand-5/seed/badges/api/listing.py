"""List endpoint."""

from .. import core


def item(record, tone="plain"):
    return {"id": record["id"], "label": record["label"],
            "badge": core.make_tag(record["label"], tone)}


def list_items(records, tone="plain"):
    return [item(record, tone=tone) for record in records]


def page(records, number=1, size=20, tone="plain"):
    start = (number - 1) * size
    return list_items(records[start:start + size], tone=tone)


def pages(records, size=20, tone="plain"):
    return [page(records, number, size, tone) for number in range(1, (len(records) + size - 1) // size + 1)]


def count(records):
    return len(records)
