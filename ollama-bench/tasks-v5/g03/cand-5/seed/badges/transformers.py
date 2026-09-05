"""Pure transformations applied before rendering a badge."""

from . import core


def uppercase(label):
    return str(label).upper()


def lowercase(label):
    return str(label).lower()


def transformed(label, transform=uppercase, tone="plain"):
    return core.make_tag(transform(label), tone)


def transformed_many(labels, transform=uppercase, tone="plain"):
    return [transformed(label, transform=transform, tone=tone) for label in labels]


def normalize_many(labels, tone="plain"):
    return [core.make_tag(core.normalize(label), tone) for label in labels]


def add_prefix(labels, prefix, tone="plain"):
    return [core.make_tag(prefix + str(label), tone) for label in labels]


def add_suffix(labels, suffix, tone="plain"):
    return [core.make_tag(str(label) + suffix, tone) for label in labels]
