"""Issue tracker integration."""

from .. import core, policies


STATUSES = ("open", "blocked", "closed")


def issue(number, title, status="open", tone=None):
    actual = policies.tone_for("urgent") if status == "blocked" and tone is None else tone
    actual = "plain" if actual is None else actual
    return {"number": number, "title": title, "status": status,
            "badge": core.make_tag(title, actual)}


def issues(rows, tone=None):
    return [issue(row["number"], row["title"], row.get("status", "open"), tone)
            for row in rows]


def open_issues(rows, tone="plain"):
    return issues([row for row in rows if row.get("status") == "open"], tone=tone)


def blocked_issues(rows):
    return issues([row for row in rows if row.get("status") == "blocked"])


def count_by_status(rows):
    return {status: sum(row.get("status") == status for row in rows) for status in STATUSES}
