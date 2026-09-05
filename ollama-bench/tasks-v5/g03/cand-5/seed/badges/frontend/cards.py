"""Card presenters with badges in title and status slots."""

from .. import core


def card(title, status="ready", tone="plain"):
    return {"title": core.make_tag(title, tone), "status": status,
            "status_badge": core.make_tag(status, tone)}


def cards(rows, tone="plain"):
    return [card(row["title"], row.get("status", "ready"), tone) for row in rows]


def titles(rows):
    return [row["title"] for row in rows]


def status_counts(rows):
    result = {}
    for row in rows:
        state = row.get("status", "ready")
        result[state] = result.get(state, 0) + 1
    return result


def compact_card(row, tone="plain"):
    value = card(row["title"], row.get("status", "ready"), tone)
    return "%s [%s]" % (value["title"], value["status"])
