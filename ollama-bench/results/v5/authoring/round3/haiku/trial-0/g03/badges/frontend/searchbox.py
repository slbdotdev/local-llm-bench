"""Search-box view model."""

from .. import core


def query(text, tone="plain"):
    return {"text": text, "badge": core.make_badge(text, tone=tone), "empty": not bool(text)}


def suggestions(values, prefix, tone="plain"):
    return [core.make_badge(value, tone=tone) for value in values
            if value.lower().startswith(prefix.lower())]


def result_count(values, prefix):
    return sum(value.lower().startswith(prefix.lower()) for value in values)


def state(values, prefix, tone="plain"):
    return {"query": query(prefix, tone=tone), "count": result_count(values, prefix),
            "suggestions": suggestions(values, prefix, tone=tone)}
