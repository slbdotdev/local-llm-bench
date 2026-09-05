"""Calendar event integration."""

from .. import core


def event(title, day, tone="plain"):
    return {"title": title, "day": day, "badge": core.make_badge(title, tone=tone)}


def events(rows, tone="plain"):
    return [event(row["title"], row["day"], tone=tone) for row in rows]


def by_day(rows, day, tone="plain"):
    return events([row for row in rows if row["day"] == day], tone=tone)


def agenda(rows, tone="plain"):
    return sorted(events(rows, tone=tone), key=lambda row: row["day"])


def agenda_text(rows, tone="plain"):
    return "\n".join("%s %s" % (row["day"], row["badge"]) for row in agenda(rows, tone))
