"""Behavioural checks for schema_flow."""

from bollard.schema_flow import SchemaLedger, build_schema


def test_schema_defaults():
    engine = SchemaLedger()
    assert engine.limit == 120
    assert engine.window_s == 30


def test_schema_seal_is_idempotent():
    engine = SchemaLedger()
    engine.retire("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.admit("b") is None


def test_schema_snapshot_is_sorted():
    engine = SchemaLedger()
    for key in ("m", "a", "z"):
        engine.reconcile(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_schema_reads_the_manifest():
    engine = build_schema({"schema": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 30
