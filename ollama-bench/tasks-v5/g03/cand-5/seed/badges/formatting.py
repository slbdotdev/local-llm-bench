"""Presentation helpers shared by reports and adapters."""

from . import core

SEPARATORS = {"csv": ",", "line": "\n", "space": " "}


def render_tag(label, tone="plain"):
    return core.make_tag(label, tone)


def render_many(labels, tone="plain", separator="\n"):
    values = [core.make_tag(label, tone) for label in labels]
    return separator.join(values)


def render_table(rows, tone="plain"):
    lines = []
    for row in rows:
        lines.append(render_many(row, tone=tone, separator=" | "))
    return "\n".join(lines)


def render_optional(label, tone="plain"):
    return "" if label is None else render_tag(label, tone=tone)


def render_columns(columns, tone="plain"):
    return [render_many(column, tone=tone, separator="/") for column in columns]


def render_with_separator(labels, kind="line", tone="plain"):
    return render_many(labels, tone=tone, separator=SEPARATORS[kind])
