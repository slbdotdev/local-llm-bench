"""Fixture records used by integration tests and examples."""

from . import core

FIXTURES = (
    {"id": "f01", "label": "Alpha", "owner": "ann", "tone": "cool"},
    {"id": "f02", "label": "Bravo", "owner": "bob", "tone": "warm"},
    {"id": "f03", "label": "Charlie", "owner": "cy", "tone": "muted"},
    {"id": "f04", "label": "Delta", "owner": "dee", "tone": "plain"},
    {"id": "f05", "label": "Echo", "owner": "eli", "tone": "loud"},
    {"id": "f06", "label": "Foxtrot", "owner": "fay", "tone": "cool"},
    {"id": "f07", "label": "Golf", "owner": "gus", "tone": "warm"},
    {"id": "f08", "label": "Hotel", "owner": "hal", "tone": "muted"},
    {"id": "f09", "label": "India", "owner": "ivy", "tone": "plain"},
    {"id": "f10", "label": "Juliett", "owner": "jay", "tone": "loud"},
    {"id": "f11", "label": "Kilo", "owner": "kim", "tone": "cool"},
    {"id": "f12", "label": "Lima", "owner": "lee", "tone": "warm"},
    {"id": "f13", "label": "Mike", "owner": "max", "tone": "muted"},
    {"id": "f14", "label": "November", "owner": "nia", "tone": "plain"},
    {"id": "f15", "label": "Oscar", "owner": "oli", "tone": "loud"},
    {"id": "f16", "label": "Papa", "owner": "pam", "tone": "cool"},
    {"id": "f17", "label": "Quebec", "owner": "quinn", "tone": "warm"},
    {"id": "f18", "label": "Romeo", "owner": "rae", "tone": "muted"},
    {"id": "f19", "label": "Sierra", "owner": "sam", "tone": "plain"},
    {"id": "f20", "label": "Tango", "owner": "tai", "tone": "loud"},
    {"id": "f21", "label": "Uniform", "owner": "uma", "tone": "cool"},
    {"id": "f22", "label": "Victor", "owner": "vic", "tone": "warm"},
    {"id": "f23", "label": "Whiskey", "owner": "wes", "tone": "muted"},
    {"id": "f24", "label": "Xray", "owner": "xan", "tone": "plain"},
    {"id": "f25", "label": "Yankee", "owner": "yas", "tone": "loud"},
    {"id": "f26", "label": "Zulu", "owner": "zane", "tone": "cool"},
)


def records():
    return [dict(record) for record in FIXTURES]


def badges(records_to_use=None, override=None):
    values = FIXTURES if records_to_use is None else records_to_use
    result = []
    for record in values:
        tone = record["tone"] if override is None else override
        result.append(dict(record, badge=core.make_tag(record["label"], tone)))
    return result


def owned_by(owner, tone=None):
    values = [record for record in FIXTURES if record["owner"] == owner]
    return badges(values, override=tone)


def owners():
    return tuple(record["owner"] for record in FIXTURES)


def fixture_summary():
    value = badges()
    return {"count": len(value), "ids": [record["id"] for record in value],
            "badges": [record["badge"] for record in value]}
