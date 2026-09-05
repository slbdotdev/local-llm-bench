"""Deterministic sampling operations for previews."""

from .. import core


def every(values, step=1, tone="plain"):
    if step <= 0:
        raise ValueError(step)
    return core.batch(values[::step], tone=tone)


def head(values, count=5, tone="plain"):
    return core.batch(values[:count], tone=tone)


def tail(values, count=5, tone="plain"):
    return core.batch(values[-count:] if count else [], tone=tone)


def alternating(values, start=0, tone="plain"):
    return core.batch(values[start::2], tone=tone)


def sample_report(values, tone="plain"):
    return {"head": head(values, tone=tone), "tail": tail(values, tone=tone),
            "count": len(values)}
