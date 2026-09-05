"""Join operations combine labels from independently ordered inputs."""

from .. import core


def join_pairs(left, right, tone="plain"):
    return [{"left": a, "right": b, "badge": core.make_badge(a + ":" + b, tone=tone)}
            for a, b in zip(left, right)]


def join_text(left, right, tone="plain"):
    return [item["badge"] for item in join_pairs(left, right, tone=tone)]


def cross(left, right, tone="plain"):
    return [core.make_badge(a + ":" + b, tone=tone) for a in left for b in right]


def keyed(left, right, tone="plain"):
    return {a: core.make_badge(b, tone=tone) for a, b in zip(left, right)}


def merge_text(groups, tone="plain"):
    return " / ".join(core.batch(group, tone=tone)[0] for group in groups if group)
