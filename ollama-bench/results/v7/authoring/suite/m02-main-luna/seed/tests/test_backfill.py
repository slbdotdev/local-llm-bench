"""Behavioural checks for backfill_flow."""

from NorthstarLedger.backfill_flow import BackfillRegistry, build_backfill


def test_backfill_defaults():
    engine = BackfillRegistry()
    assert engine.limit == 960
    assert engine.window_s == 45


def test_backfill_seal_is_idempotent():
    engine = BackfillRegistry()
    engine.coalesce("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.retire("b") is None


def test_backfill_snapshot_is_sorted():
    engine = BackfillRegistry()
    for key in ("m", "a", "z"):
        engine.expand(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_backfill_reads_the_manifest():
    engine = build_backfill({"backfill": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 45
