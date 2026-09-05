"""Markdown plugin for release notes and review tables."""

from .. import core, formatting


def markdown_badge(label, tone="plain"):
    return "`%s`" % core.make_badge(label, tone=tone)


def markdown_item(label, detail="", tone="plain"):
    suffix = " — %s" % detail if detail else ""
    return "- %s%s" % (markdown_badge(label, tone), suffix)


def markdown_list(items, tone="plain"):
    return "\n".join(markdown_item(item, tone=tone) for item in items)


def markdown_table(rows, tone="plain"):
    header = "| Label | Badge |"
    rule = "| --- | --- |"
    body = ["| %s | %s |" % (row, markdown_badge(row, tone)) for row in rows]
    return "\n".join([header, rule] + body)


def markdown_sections(sections, tone="plain"):
    blocks = []
    for title, labels in sections:
        blocks.append("## %s\n%s" % (title, markdown_list(labels, tone=tone)))
    return "\n\n".join(blocks)


def markdown_inline(labels, tone="plain"):
    return formatting.render_many([core.normalize(label) for label in labels],
                                  tone=tone, separator=" · ")
