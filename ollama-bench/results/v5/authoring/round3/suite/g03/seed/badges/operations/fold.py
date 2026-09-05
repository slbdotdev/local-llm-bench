"""Fold operations that accumulate badge values."""

from .. import core


def fold_labels(labels, tone="plain", separator=", "):
    values = core.batch(labels, tone=tone)
    return separator.join(values)


def fold_with(labels, initial, fn, tone="plain"):
    result = initial
    for label in labels:
        result = fn(result, core.make_tag(label, tone))
    return result


def count_fold(labels, tone="plain"):
    return fold_with(labels, 0, lambda total, _: total + 1, tone=tone)


def length_fold(labels, tone="plain"):
    return fold_with(labels, 0, lambda total, value: total + len(value), tone=tone)


def first_fold(labels, tone="plain"):
    return fold_with(labels, None, lambda first, value: value if first is None else first, tone=tone)
