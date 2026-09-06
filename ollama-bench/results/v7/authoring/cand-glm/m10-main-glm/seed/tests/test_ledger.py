"""Behavioural checks for ledger_store."""

from solder.ledger_store import LedgerLedger, build_ledger


def test_ledger_defaults():
    engine = LedgerLedger()
    assert engine.limit == 48
    assert engine.window_s == 30


def test_ledger_seal_is_idempotent():
    engine = LedgerLedger()
    engine.retire("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.narrow("b") is None


def test_ledger_snapshot_is_sorted():
    engine = LedgerLedger()
    for key in ("m", "a", "z"):
        engine.expand(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_ledger_reads_the_manifest():
    engine = build_ledger({"ledger": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 30
