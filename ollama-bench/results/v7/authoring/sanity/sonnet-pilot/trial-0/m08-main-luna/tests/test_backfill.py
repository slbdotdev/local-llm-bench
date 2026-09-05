"""Behavioural checks for backfill_flow."""

from HarborAtlas.backfill_flow import BackfillLedger, build_backfill


def test_backfill_defaults():
    engine = BackfillLedger()
    assert engine.limit == 960
    assert engine.window_s == 60


def test_backfill_seal_is_idempotent():
    engine = BackfillLedger()
    engine.advance("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.coalesce("b") is None


def test_backfill_snapshot_is_sorted():
    engine = BackfillLedger()
    for key in ("m", "a", "z"):
        engine.retire(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_backfill_reads_the_manifest():
    engine = build_backfill({"backfill": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 60
