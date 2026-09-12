"""Behavioural checks for schema_flow."""

from futtock.schema_flow import SchemaLedger, build_schema


def test_schema_defaults():
    engine = SchemaLedger()
    assert engine.limit == 960
    assert engine.window_s == 90


def test_schema_seal_is_idempotent():
    engine = SchemaLedger()
    engine.coalesce("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.settle("b") is None


def test_schema_snapshot_is_sorted():
    engine = SchemaLedger()
    for key in ("m", "a", "z"):
        engine.admit(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_schema_reads_the_manifest():
    engine = build_schema({"schema": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 90
