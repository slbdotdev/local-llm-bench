"""Timeline plugin that renders dated events."""

from .. import core


MONTHS = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
          7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"}


def date_label(event):
    return "%04d-%02d-%02d" % (event["year"], event["month"], event["day"])


def month_label(event):
    return "%s %d" % (MONTHS[event["month"]], event["year"])


def timeline_event(event, tone="plain"):
    return "%s %s" % (date_label(event), core.make_badge(event["label"], tone=tone))


def timeline(events, tone="plain"):
    ordered = sorted(events, key=lambda event: (event["year"], event["month"], event["day"]))
    return [timeline_event(event, tone=tone) for event in ordered]


def timeline_text(events, tone="plain"):
    return "\n".join(timeline(events, tone=tone))


def grouped_months(events, tone="plain"):
    result = {}
    for event in events:
        result.setdefault(month_label(event), []).append(timeline_event(event, tone))
    return result
