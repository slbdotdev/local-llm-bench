"""Tone query applies one requested tone to matching records."""

from .. import core


def run(records, requested, tone="plain"):
    return [dict(record, badge=core.make_badge(record["label"], tone=tone))
            for record in records if record.get("tone") == requested]


def labels(records, requested, tone="plain"):
    return [record["badge"] for record in run(records, requested, tone=tone)]


def counts(records):
    tones = sorted({record.get("tone") for record in records})
    return {tone: sum(record.get("tone") == tone for record in records) for tone in tones}


def available(records):
    return sorted({record.get("tone") for record in records})
