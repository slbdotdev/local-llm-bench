"""Calendar dashboard view."""

from .. import core


def day(event, tone="plain"):
    return {"date": (event["year"], event["month"], event["day"]),
            "badge": core.make_badge(event["label"], tone=tone)}


def days(events, tone="plain"):
    return [day(event, tone=tone) for event in events]


def month(events, year, month, tone="plain"):
    values = [event for event in events if event["year"] == year and event["month"] == month]
    return days(sorted(values, key=lambda event: event["day"]), tone=tone)


def years(events):
    return sorted({event["year"] for event in events})


def dates(events):
    return [value["date"] for value in days(events)]


def text(events, tone="plain"):
    return "\n".join("%04d-%02d-%02d %s" % (y, m, d, value["badge"])
                       for (y, m, d), value in zip(dates(events), days(events, tone)))
