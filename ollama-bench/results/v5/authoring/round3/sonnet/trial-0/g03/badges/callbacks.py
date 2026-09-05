"""Callback-oriented consumers retain a builder for later invocation."""

from . import core


def callback(label, tone="plain"):
    builder = core.make_badge
    return lambda: builder(label, tone=tone)


def callbacks(labels, tone="plain"):
    return [callback(label, tone=tone) for label in labels]


def run_all(labels, tone="plain"):
    return [fn() for fn in callbacks(labels, tone=tone)]


def with_default(label):
    builder = core.make_badge
    return builder(label)


def invoke(builder, label, tone="plain"):
    return builder(label, tone)


def invoke_many(builder, labels, tone="plain"):
    return [invoke(builder, label, tone=tone) for label in labels]
