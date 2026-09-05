"""Behavioural checks for ledger_core."""

from cinder.ledger_core import LedgerLedger, build_ledger


def test_ledger_defaults():
    engine = LedgerLedger()
    assert engine.limit == 12
    assert engine.window_s == 120


def test_ledger_seal_is_idempotent():
    engine = LedgerLedger()
    engine.defer("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.expand("b") is None


def test_ledger_snapshot_is_sorted():
    engine = LedgerLedger()
    for key in ("m", "a", "z"):
        engine.narrow(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_ledger_reads_the_manifest():
    engine = build_ledger({"ledger": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 120
