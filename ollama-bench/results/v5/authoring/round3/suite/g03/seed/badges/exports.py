"""Stable export and snapshot helpers."""

from . import core, formatting

EXPORT_ORDER = ("make_tag", "batch", "describe", "reflect")


def export_one(label, tone="plain"):
    return core.make_tag(label, tone)


def export_rows(rows, tone="plain"):
    return [export_one(row["label"], tone=tone) for row in rows]


def export_snapshot(rows, tone="plain"):
    return {"order": EXPORT_ORDER, "items": export_rows(rows, tone=tone),
            "text": formatting.render_many([r["label"] for r in rows], tone=tone)}


def export_columns(columns, tone="plain"):
    result = []
    for column in columns:
        result.extend(export_rows([{"label": value} for value in column], tone=tone))
    return result


def export_metadata():
    return {"names": list(EXPORT_ORDER), "count": len(EXPORT_ORDER)}
