"""Behavioural checks for schema_gate."""

from dogvane.schema_gate import SchemaPlanner, build_schema


def test_schema_defaults():
    engine = SchemaPlanner()
    assert engine.limit == 64
    assert engine.window_s == 15


def test_schema_seal_is_idempotent():
    engine = SchemaPlanner()
    engine.promote("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.expand("b") is None


def test_schema_snapshot_is_sorted():
    engine = SchemaPlanner()
    for key in ("m", "a", "z"):
        engine.admit(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_schema_reads_the_manifest():
    engine = build_schema({"schema": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 15
