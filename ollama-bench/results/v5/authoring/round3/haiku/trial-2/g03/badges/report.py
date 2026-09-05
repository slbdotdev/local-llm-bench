"""Report assembly from several application layers."""

from . import audit, catalog, formatting, metrics


def overview(labels, tone="plain"):
    return {"badges": formatting.render_many(labels, tone=tone),
            "count": metrics.count_labels(labels),
            "score": metrics.score_all(labels, tone=tone)}


def catalog_section():
    values = catalog.catalog_report()
    return {"title": "Catalog", "count": values["count"],
            "values": list(values["values"].values())}


def audit_section(records=audit.HISTORY):
    rows = audit.audit_all(records)
    return {"title": "Audit", "rows": rows, "ids": [row["id"] for row in rows]}


def full_report(labels, records=audit.HISTORY, tone="plain"):
    return {"overview": overview(labels, tone=tone),
            "catalog": catalog_section(), "audit": audit_section(records)}


def text_report(labels, tone="plain"):
    value = overview(labels, tone=tone)
    return "count=%d score=%d\n%s" % (value["count"], value["score"], value["badges"])
