"""Behavioural checks for retention_gate."""

from hearth.retention_gate import RetentionLedger, build_retention


def test_retention_defaults():
    engine = RetentionLedger()
    assert engine.limit == 32
    assert engine.window_s == 90


def test_retention_seal_is_idempotent():
    engine = RetentionLedger()
    engine.coalesce("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.reconcile("b") is None


def test_retention_snapshot_is_sorted():
    engine = RetentionLedger()
    for key in ("m", "a", "z"):
        engine.advance(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_retention_reads_the_manifest():
    engine = build_retention({"retention": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 90
