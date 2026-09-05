"""Incident journey facade."""

from .. import core, notifications, routing


def incident(number, title, severity="normal", tone=None):
    route = routing.route(title, priority=severity, tone="loud" if tone is None else tone)
    return {"number": number, "title": title, "route": route,
            "badge": core.make_tag(title, "loud" if tone is None else tone)}


def incidents(rows, tone=None):
    return [incident(row["number"], row["title"], row.get("severity", "normal"), tone)
            for row in rows]


def notify(incident_value, channel="in_app", tone=None):
    message = notifications.channel_message(channel, incident_value["title"],
                                            priority=incident_value["route"]["priority"],
                                            tone=tone)
    return dict(incident_value, notification=message)


def critical(rows):
    return incidents([row for row in rows if row.get("severity") == "critical"], "loud")


def summary(rows):
    values = incidents(rows)
    return {"count": len(values), "destinations": [v["route"]["destination"] for v in values]}
