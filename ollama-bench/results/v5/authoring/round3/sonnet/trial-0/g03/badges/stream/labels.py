"""Label stream operations."""

from .. import core


def emit(labels, tone="plain"):
    for label in labels:
        yield core.make_badge(label, tone=tone)


def collect(labels, tone="plain"):
    return list(emit(labels, tone=tone))


def take(labels, count, tone="plain"):
    return collect(list(labels)[:count], tone=tone)


def skip(labels, count, tone="plain"):
    return collect(list(labels)[count:], tone=tone)


def enumerate_badges(labels, tone="plain"):
    return list(enumerate(emit(labels, tone=tone)))


def text(labels, tone="plain"):
    return "|".join(emit(labels, tone=tone))
