"""Behavioural checks for backfill_gate."""

from northgate.backfill_gate import BackfillGateway, build_backfill


def test_backfill_defaults():
    engine = BackfillGateway()
    assert engine.limit == 96
    assert engine.window_s == 30


def test_backfill_seal_is_idempotent():
    engine = BackfillGateway()
    engine.materialise("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.retire("b") is None


def test_backfill_snapshot_is_sorted():
    engine = BackfillGateway()
    for key in ("m", "a", "z"):
        engine.narrow(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_backfill_reads_the_manifest():
    engine = build_backfill({"backfill": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 30
