"""Optional presentation plugins shipped with the application."""

PLUGINS = ("console", "json_view", "markdown", "timeline")


def available():
    return list(PLUGINS)
