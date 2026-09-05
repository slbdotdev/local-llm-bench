"""Pagination controls and rendered page labels."""

from .. import core


def page_numbers(total, size):
    if size < 1:
        raise ValueError(size)
    return list(range(1, (total + size - 1) // size + 1))


def page_labels(labels, number, size, tone="plain"):
    start = (number - 1) * size
    return core.batch(labels[start:start + size], tone=tone)


def page(records, number, size, tone="plain"):
    start = (number - 1) * size
    return [dict(record, badge=core.make_tag(record["label"], tone))
            for record in records[start:start + size]]


def all_pages(records, size, tone="plain"):
    return [page(records, number, size, tone) for number in page_numbers(len(records), size)]


def navigation(total, number, size):
    pages = page_numbers(total, size)
    return {"current": number, "previous": number - 1 if number > 1 else None,
            "next": number + 1 if number < len(pages) else None, "pages": pages}
