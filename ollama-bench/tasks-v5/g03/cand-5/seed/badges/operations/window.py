"""Sliding window operations."""

from .. import core


def windows(values, width):
    if width < 1:
        raise ValueError(width)
    return [values[index:index + width] for index in range(max(0, len(values) - width + 1))]


def badge_windows(values, width, tone="plain"):
    return [core.batch(window, tone=tone) for window in windows(values, width)]


def pairs(values, tone="plain"):
    return badge_windows(values, 2, tone=tone)


def centered(values, width, tone="plain"):
    selected = windows(values, width)
    return [core.make_tag(window[len(window) // 2], tone) for window in selected]


def window_count(values, width):
    return len(windows(values, width))
