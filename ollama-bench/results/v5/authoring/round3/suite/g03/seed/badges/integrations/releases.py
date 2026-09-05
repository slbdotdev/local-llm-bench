"""Release integration for version announcements."""

from .. import core, templates


def release(version, label, tone="plain"):
    return {"version": version, "label": label, "badge": core.make_tag(label, tone)}


def releases(rows, tone="plain"):
    return [release(row["version"], row["label"], tone=tone) for row in rows]


def notes(version, labels, tone="plain"):
    return {"version": version, "items": templates.render_many("announce", labels, tone=tone)}


def latest(rows, tone="plain"):
    return releases(rows[-1:], tone=tone)


def version_text(row, tone="plain"):
    value = release(row["version"], row["label"], tone=tone)
    return "%s: %s" % (value["version"], value["badge"])
