"""XML-shaped adapter with explicit escaping."""

from xml.sax.saxutils import escape

from .. import core


def element(label, tone="plain"):
    return "<badge>%s</badge>" % escape(core.make_tag(label, tone))


def record(value, tone="plain"):
    return "<record id=\"%s\">%s</record>" % (escape(str(value["id"])),
                                                   element(value["label"], tone))


def records(values, tone="plain"):
    return [record(value, tone=tone) for value in values]


def document(values, tone="plain"):
    return "<records>%s</records>" % "".join(records(values, tone=tone))


def fragments(labels, tone="plain"):
    return [element(label, tone=tone) for label in labels]
