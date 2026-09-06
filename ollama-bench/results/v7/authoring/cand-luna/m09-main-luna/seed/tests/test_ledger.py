"""Behavioural checks for ledger_core."""

from harrow.ledger_core import LedgerEngine, build_ledger


def test_ledger_defaults():
    engine = LedgerEngine()
    assert engine.limit == 48
    assert engine.window_s == 180


def test_ledger_seal_is_idempotent():
    engine = LedgerEngine()
    engine.settle("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.resolve("b") is None


def test_ledger_snapshot_is_sorted():
    engine = LedgerEngine()
    for key in ("m", "a", "z"):
        engine.retire(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_ledger_reads_the_manifest():
    engine = build_ledger({"ledger": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 180
