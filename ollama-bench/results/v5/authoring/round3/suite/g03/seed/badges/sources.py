"""Named source feeds used by the reporting pipeline.

These records stand in for the small application's separate data providers.
Keeping them here makes source order and duplicate handling part of the API.
"""

from . import core

SOURCE_ROWS = (
    ("north-001", "Atlas", "cool"), ("north-002", "Beacon", "warm"),
    ("north-003", "Cedar", "muted"), ("north-004", "Dahlia", "plain"),
    ("north-005", "Elm", "loud"), ("north-006", "Fjord", "cool"),
    ("north-007", "Grove", "warm"), ("north-008", "Harbor", "muted"),
    ("north-009", "Iris", "plain"), ("north-010", "Juniper", "loud"),
    ("south-001", "Kite", "cool"), ("south-002", "Lumen", "warm"),
    ("south-003", "Mica", "muted"), ("south-004", "Nova", "plain"),
    ("south-005", "Orchid", "loud"), ("south-006", "Pine", "cool"),
    ("south-007", "Quartz", "warm"), ("south-008", "River", "muted"),
    ("south-009", "Sable", "plain"), ("south-010", "Tundra", "loud"),
    ("east-001", "Umber", "cool"), ("east-002", "Vale", "warm"),
    ("east-003", "Willow", "muted"), ("east-004", "Xenia", "plain"),
    ("east-005", "Yarrow", "loud"), ("east-006", "Zephyr", "cool"),
    ("east-007", "Amber", "warm"), ("east-008", "Birch", "muted"),
    ("east-009", "Cobalt", "plain"), ("east-010", "Drift", "loud"),
    ("west-001", "Ember", "cool"), ("west-002", "Flint", "warm"),
    ("west-003", "Glade", "muted"), ("west-004", "Hearth", "plain"),
    ("west-005", "Indigo", "loud"), ("west-006", "Jasper", "cool"),
    ("west-007", "Kestrel", "warm"), ("west-008", "Larch", "muted"),
    ("west-009", "Maple", "plain"), ("west-010", "Nectar", "loud"),
    ("central-001", "Opal", "cool"), ("central-002", "Plum", "warm"),
    ("central-003", "Raven", "muted"), ("central-004", "Sol", "plain"),
    ("central-005", "Thorn", "loud"), ("central-006", "Uplift", "cool"),
    ("central-007", "Violet", "warm"), ("central-008", "Wren", "muted"),
    ("central-009", "Yonder", "plain"), ("central-010", "Aster", "loud"),
)


def rows(region=None):
    return [row for row in SOURCE_ROWS if region is None or row[0].startswith(region + "-")]


def source_badges(region=None, tone=None):
    result = []
    for key, label, source_tone in rows(region):
        result.append({"key": key, "label": label,
                       "badge": core.make_tag(label, source_tone if tone is None else tone)})
    return result


def source_map(region=None, tone=None):
    return {item["key"]: item["badge"] for item in source_badges(region, tone)}


def regions():
    return tuple(sorted({key.split("-")[0] for key, _, _ in SOURCE_ROWS}))


def search(fragment, tone="plain"):
    needle = fragment.lower()
    return [item for item in source_badges(tone=tone)
            if needle in item["key"].lower() or needle in item["label"].lower()]
