"""Behavioural checks for schema_core."""

from winterrelay.schema_core import SchemaEngine, build_schema


def test_schema_defaults():
    engine = SchemaEngine()
    assert engine.limit == 250
    assert engine.window_s == 120


def test_schema_seal_is_idempotent():
    engine = SchemaEngine()
    engine.expand("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.reconcile("b") is None


def test_schema_snapshot_is_sorted():
    engine = SchemaEngine()
    for key in ("m", "a", "z"):
        engine.retire(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_schema_reads_the_manifest():
    engine = build_schema({"schema": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 120
