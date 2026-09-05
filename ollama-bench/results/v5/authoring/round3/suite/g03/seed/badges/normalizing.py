"""Normalization boundaries for user-provided labels."""

from . import core


def clean(label):
    return core.normalize(label)


def clean_many(labels):
    return [clean(label) for label in labels]


def render(label, tone="plain"):
    return core.make_tag(clean(label), tone)


def render_many(labels, tone="plain"):
    return [render(label, tone=tone) for label in labels]


def changed(labels):
    return [label for label in labels if clean(label) != label]


def mapping(labels, tone="plain"):
    return {label: render(label, tone=tone) for label in labels}
