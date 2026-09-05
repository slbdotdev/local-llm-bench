"""Minimal HTML adapter with escaping at the presentation boundary."""

from html import escape

from .. import core


def badge_span(label, tone="plain"):
    value = core.make_badge(label, tone=tone)
    return '<span class="badge">%s</span>' % escape(value)


def row(record, tone="plain"):
    return "<tr><td>%s</td><td>%s</td></tr>" % (
        escape(str(record["id"])), badge_span(record["label"], tone))


def table(records, tone="plain"):
    body = "".join(row(record, tone=tone) for record in records)
    return "<table><tbody>%s</tbody></table>" % body


def list_items(labels, tone="plain"):
    return "".join("<li>%s</li>" % badge_span(label, tone) for label in labels)


def document(title, labels, tone="plain"):
    return "<h1>%s</h1><ul>%s</ul>" % (escape(title), list_items(labels, tone))
