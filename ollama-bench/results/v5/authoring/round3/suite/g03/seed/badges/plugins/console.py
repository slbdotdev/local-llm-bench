"""Console plugin with headings, rows, and compact summaries."""

from .. import core, formatting

HEADINGS = {"info": "INFO", "warn": "WARN", "error": "ERROR", "ok": "OK"}


def heading(kind):
    return HEADINGS.get(kind, "INFO")


def console_line(label, kind="info", tone="plain"):
    return "[%s] %s" % (heading(kind), core.make_tag(label, tone))


def console_lines(records, tone="plain"):
    return [console_line(record["label"], record.get("kind", "info"), tone)
            for record in records]


def console_block(records, tone="plain"):
    return "\n".join(console_lines(records, tone=tone))


def console_columns(columns, tone="plain"):
    return formatting.render_columns(columns, tone=tone)


def console_summary(records, tone="plain"):
    return {"lines": len(records), "text": console_block(records, tone=tone),
            "kinds": sorted({record.get("kind", "info") for record in records})}
