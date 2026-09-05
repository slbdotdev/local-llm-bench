"""Scheduled notification job groups messages by owner."""

from .. import notifications, policies


def notify_record(record, tone=None):
    return notifications.notification(record["label"],
                                      priority=record.get("priority", "quiet"),
                                      tone=tone)


def notify_records(records, tone=None):
    return [notify_record(record, tone=tone) for record in records]


def owner_groups(records):
    result = {}
    for record in records:
        result.setdefault(record["owner"], []).append(record)
    return result


def owner_notifications(records, tone=None):
    return {owner: notify_records(values, tone=tone)
            for owner, values in owner_groups(records).items()}


def escalation(records):
    urgent = [dict(record, priority="urgent") for record in records]
    return notify_records(urgent, tone=policies.tone_for("urgent"))


def digest_text(records, tone=None):
    return "\n".join(message["badge"] for message in notify_records(records, tone=tone))
