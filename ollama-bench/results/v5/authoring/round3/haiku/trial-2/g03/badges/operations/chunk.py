"""Chunk operations preserve the input sequence while rendering each part."""

from .. import core


def chunks(values, size):
    if size <= 0:
        raise ValueError(size)
    return [values[index:index + size] for index in range(0, len(values), size)]


def badge_chunks(values, size, tone="plain"):
    return [core.batch(chunk, tone=tone) for chunk in chunks(values, size)]


def chunk_records(records, size, tone="plain"):
    return [list(map(lambda record: dict(record, badge=core.make_badge(record["label"], tone=tone)), chunk))
            for chunk in chunks(records, size)]


def chunk_count(values, size):
    return len(chunks(values, size))


def flatten(chunks_to_flatten):
    return [value for chunk in chunks_to_flatten for value in chunk]
