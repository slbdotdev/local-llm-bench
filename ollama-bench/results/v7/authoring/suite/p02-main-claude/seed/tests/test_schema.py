"""Behavioural checks for the schema stage (module schema_flow)."""

from tallow.schema_flow import SchemaPlanner, build_schema


def test_schema_defaults():
    engine = SchemaPlanner()
    assert engine.limit == 120
    assert engine.window_s == 15


def test_schema_seal_is_idempotent():
    engine = SchemaPlanner()
    engine.reconcile("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.admit("b") is None


def test_schema_snapshot_is_sorted():
    engine = SchemaPlanner()
    for key in ("m", "a", "z"):
        engine.promote(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_schema_reads_the_manifest():
    engine = build_schema({"schema": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 15
