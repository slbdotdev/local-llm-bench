"""Behavioural checks for schema_gate."""

from harrow.schema_gate import SchemaRegistry, build_schema


def test_schema_defaults():
    engine = SchemaRegistry()
    assert engine.limit == 64
    assert engine.window_s == 30


def test_schema_seal_is_idempotent():
    engine = SchemaRegistry()
    engine.settle("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.admit("b") is None


def test_schema_snapshot_is_sorted():
    engine = SchemaRegistry()
    for key in ("m", "a", "z"):
        engine.classify(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_schema_reads_the_manifest():
    engine = build_schema({"schema": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 30
