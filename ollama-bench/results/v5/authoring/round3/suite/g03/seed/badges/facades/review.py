"""Review journey facade."""

from .. import core, policies, report


def review_item(item, tone=None):
    priority = item.get("priority", "quiet")
    actual = policies.tone_for(priority) if tone is None else tone
    return {"id": item["id"], "badge": core.make_tag(item["label"], actual),
            "priority": priority}


def review_items(items, tone=None):
    return [review_item(item, tone=tone) for item in items]


def pending(items, tone="warm"):
    return review_items([item for item in items if item.get("state") == "pending"], tone)


def approved(items, tone="cool"):
    return review_items([item for item in items if item.get("state") == "approved"], tone)


def dashboard(items, tone=None):
    return {"all": review_items(items, tone=tone),
            "pending": len(pending(items)), "approved": len(approved(items))}


def text(items, tone=None):
    return report.text_report([item["label"] for item in review_items(items, tone)],
                              tone="plain" if tone is None else tone)
