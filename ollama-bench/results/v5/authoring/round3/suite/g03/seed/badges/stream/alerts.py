"""Alert stream with thresholded badge values."""

from .. import core, policies


def alert(label, level=1, tone=None):
    actual = policies.tone_for(level) if tone is None else tone
    return {"label": label, "level": level, "badge": core.make_tag(label, actual)}


def emit(labels, level=1, tone=None):
    for label in labels:
        yield alert(label, level=level, tone=tone)


def collect(labels, level=1, tone=None):
    return list(emit(labels, level=level, tone=tone))


def above(labels, minimum, level=1, tone=None):
    return collect([label for label in labels if len(str(label)) >= minimum], level, tone)


def badges(labels, level=1, tone=None):
    return [item["badge"] for item in collect(labels, level, tone)]
