"""Higher-level workflows combining validation, policy, and output."""

from . import core, policies, validation


def prepare(labels, tone="plain"):
    good, rejected = validation.partition(labels, tone=tone)
    return {"accepted": good, "rejected": rejected,
            "badges": core.batch(good, tone=tone)}


def approve(records):
    accepted = []
    rejected = []
    for record in records:
        if validation.validate(record.get("label"), tone="plain"):
            rejected.append(record)
        else:
            accepted.append(dict(record, badge=policies.policy_badge(
                record["label"], record.get("priority", "quiet"))))
    return accepted, rejected


def reprocess(records, tone="cool"):
    return [dict(record, badge=core.make_badge(record["label"], tone=tone))
            for record in records]


def workflow_report(records):
    accepted, rejected = approve(records)
    return {"accepted": len(accepted), "rejected": len(rejected),
            "badges": [record["badge"] for record in accepted]}


def stages(labels, tones=("plain", "warm", "cool")):
    result = []
    for tone in tones:
        result.append(core.batch(labels, tone=tone))
    return result
