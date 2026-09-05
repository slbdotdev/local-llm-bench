"""Merge operations for badge lists and keyed badge maps."""

from . import core


def merge_labels(*groups):
    result = []
    for group in groups:
        result.extend(group)
    return result


def merge_badges(*groups, tone="plain"):
    return core.batch(merge_labels(*groups), tone=tone)


def merge_maps(first, second, tone="plain"):
    merged = dict(first)
    merged.update(second)
    return core.labeled(merged.items(), tone=tone)


def overlay(base, changes, tone="plain"):
    result = dict(base)
    for key, value in changes.items():
        result[key] = value
    return core.labeled(result.items(), tone=tone)


def zip_badges(labels, tones):
    return [core.make_badge(label, tone=tone) for label, tone in zip(labels, tones)]


def pairwise(labels, tone="plain"):
    values = core.batch(labels, tone=tone)
    return list(zip(values, values[1:]))
