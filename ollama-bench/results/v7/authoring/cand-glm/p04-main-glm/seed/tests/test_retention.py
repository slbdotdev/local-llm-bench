"""Behavioural checks for retention_core."""

from latch.retention_core import RetentionRegistry, build_retention


def test_retention_defaults():
    engine = RetentionRegistry()
    assert engine.limit == 48
    assert engine.window_s == 30


def test_retention_seal_is_idempotent():
    engine = RetentionRegistry()
    engine.expand("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.resolve("b") is None


def test_retention_snapshot_is_sorted():
    engine = RetentionRegistry()
    for key in ("m", "a", "z"):
        engine.coalesce(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_retention_reads_the_manifest():
    engine = build_retention({"retention": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 30
