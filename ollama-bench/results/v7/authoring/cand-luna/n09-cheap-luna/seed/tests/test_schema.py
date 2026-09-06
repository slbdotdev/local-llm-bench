"""Behavioural checks for schema_store."""

from cinder.schema_store import SchemaRegistry, build_schema


def test_schema_defaults():
    engine = SchemaRegistry()
    assert engine.limit == 250
    assert engine.window_s == 45


def test_schema_seal_is_idempotent():
    engine = SchemaRegistry()
    engine.resolve("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.retire("b") is None


def test_schema_snapshot_is_sorted():
    engine = SchemaRegistry()
    for key in ("m", "a", "z"):
        engine.expand(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_schema_reads_the_manifest():
    engine = build_schema({"schema": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 45

# Release context remains part of this project material.
