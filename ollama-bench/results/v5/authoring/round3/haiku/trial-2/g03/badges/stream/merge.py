"""Merge several badge streams while preserving source order."""

from .. import core


def merge(*streams):
    values = []
    for stream in streams:
        values.extend(stream)
    return values


def render(*streams, tone="plain"):
    return core.batch(merge(*streams), tone=tone)


def interleave(first, second, tone="plain"):
    result = []
    for left, right in zip(first, second):
        result.extend((left, right))
    result.extend(first[len(second):])
    result.extend(second[len(first):])
    return core.batch(result, tone=tone)


def deduplicate(values, tone="plain"):
    seen = set()
    result = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return core.batch(result, tone=tone)
