"""Final formatting functions for logs, labels, and diagnostic output."""

from . import core


def log_line(level, message, tone="plain"):
    return "%s %s" % (level.upper(), core.make_tag(message, tone))


def log_lines(entries, tone="plain"):
    return [log_line(entry["level"], entry["message"], tone) for entry in entries]


def log_text(entries, tone="plain"):
    return "\n".join(log_lines(entries, tone=tone))


def key_value(key, value, tone="plain"):
    return "%s=%s" % (key, core.make_tag(value, tone))


def key_values(values, tone="plain"):
    return [key_value(key, value, tone=tone) for key, value in values.items()]


def envelope(label, source="app", tone="plain"):
    return {"source": source, "badge": core.make_tag(label, tone), "label": label}
