"""Behavioural checks for schema_gate."""

from harrow.schema_gate import SchemaLedger, build_schema


def test_schema_defaults():
    engine = SchemaLedger()
    assert engine.limit == 24
    assert engine.window_s == 60


def test_schema_seal_is_idempotent():
    engine = SchemaLedger()
    engine.narrow("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.materialise("b") is None


def test_schema_snapshot_is_sorted():
    engine = SchemaLedger()
    for key in ("m", "a", "z"):
        engine.defer(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_schema_reads_the_manifest():
    engine = build_schema({"schema": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 60
