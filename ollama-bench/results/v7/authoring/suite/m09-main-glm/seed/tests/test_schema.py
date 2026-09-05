"""Behavioural checks for schema_gate."""

from cinder.schema_gate import SchemaGateway, build_schema


def test_schema_defaults():
    engine = SchemaGateway()
    assert engine.limit == 24
    assert engine.window_s == 45


def test_schema_seal_is_idempotent():
    engine = SchemaGateway()
    engine.resolve("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.classify("b") is None


def test_schema_snapshot_is_sorted():
    engine = SchemaGateway()
    for key in ("m", "a", "z"):
        engine.promote(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_schema_reads_the_manifest():
    engine = build_schema({"schema": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 45
