"""Pure transformations applied before rendering a badge."""

from . import core


def uppercase(label):
    return str(label).upper()


def lowercase(label):
    return str(label).lower()


def transformed(label, transform=uppercase, tone="plain"):
    return core.make_badge(transform(label), tone=tone)


def transformed_many(labels, transform=uppercase, tone="plain"):
    return [transformed(label, transform=transform, tone=tone) for label in labels]


def normalize_many(labels, tone="plain"):
    return [core.make_badge(core.normalize(label), tone=tone) for label in labels]


def add_prefix(labels, prefix, tone="plain"):
    return [core.make_badge(prefix + str(label), tone=tone) for label in labels]


def add_suffix(labels, suffix, tone="plain"):
    return [core.make_badge(str(label) + suffix, tone=tone) for label in labels]
