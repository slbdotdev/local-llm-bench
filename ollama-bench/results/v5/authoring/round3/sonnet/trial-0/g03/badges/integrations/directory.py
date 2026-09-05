"""Directory integration renders display names and groups."""

from .. import core


def person(user, tone="plain"):
    return {"id": user["id"], "name": user["name"],
            "badge": core.make_badge(user["name"], tone=tone)}


def people(users, tone="plain"):
    return [person(user, tone=tone) for user in users]


def group(users, group_name, tone="plain"):
    return {"group": group_name, "members": people(users, tone=tone)}


def find(users, text, tone="plain"):
    return people([user for user in users if text.lower() in user["name"].lower()], tone=tone)


def names(users):
    return [user["name"] for user in users]
