"""Combination façade that composes several application sources."""

from . import core, fixtures, sources


def source_values(region=None, tone="plain"):
    return [item["badge"] for item in sources.source_badges(region=region, tone=tone)]


def fixture_values(tone="plain"):
    return [item["badge"] for item in fixtures.badges(override=tone)]


def combined(region=None, tone="plain"):
    return source_values(region=region, tone=tone) + fixture_values(tone=tone)


def unique(region=None, tone="plain"):
    result = []
    seen = set()
    for badge in combined(region=region, tone=tone):
        if badge not in seen:
            seen.add(badge)
            result.append(badge)
    return result


def summary(region=None, tone="plain"):
    values = combined(region=region, tone=tone)
    return {"count": len(values), "unique": len(unique(region=region, tone=tone)),
            "first": values[0] if values else None}
