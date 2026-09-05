"""Scheduled export job combines multiple output formats."""

from .. import catalog, formatting, sources
from ..adapters import csv, plain


def export_source(region=None, tone="plain"):
    records = sources.source_badges(region=region, tone=tone)
    return [{"key": item["key"], "label": item["label"], "badge": item["badge"]}
            for item in records]


def export_lines(region=None, tone="plain"):
    return plain.lines([item["label"] for item in export_source(region, tone)], tone=tone)


def export_csv(records, tone="plain"):
    return csv.table(records, tone=tone)


def export_catalog(tone="plain"):
    return catalog.select(catalog.names(), tone=tone)


def export_bundle(region=None, tone="plain"):
    records = export_source(region, tone=tone)
    return {"records": records, "text": "\n".join(export_lines(region, tone)),
            "csv": export_csv(records, tone=tone)}
