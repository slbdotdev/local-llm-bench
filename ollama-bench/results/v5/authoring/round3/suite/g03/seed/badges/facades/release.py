"""Release journey facade."""

from .. import core, integrations, templates


def version_badge(version, tone="cool"):
    return core.make_tag("v" + str(version), tone)


def changelog(version, labels, tone="plain"):
    return {"version": version, "badge": version_badge(version, tone),
            "items": templates.render_many("change", labels, tone=tone)}


def announce(version, labels, tone="warm"):
    return {"version": version, "badge": version_badge(version, tone),
            "notes": integrations.releases.notes(version, labels, tone=tone)}


def release_record(version, label, tone="plain"):
    return integrations.releases.release(version, label, tone=tone)


def release_many(rows, tone="plain"):
    return [release_record(row["version"], row["label"], tone=tone) for row in rows]
