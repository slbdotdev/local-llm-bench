"""Behavioural checks for ledger_flow."""

from pellworth.ledger_flow import LedgerLedger, build_ledger


def test_ledger_defaults():
    engine = LedgerLedger()
    assert engine.limit == 32
    assert engine.window_s == 90


def test_ledger_seal_is_idempotent():
    engine = LedgerLedger()
    engine.narrow("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.admit("b") is None


def test_ledger_snapshot_is_sorted():
    engine = LedgerLedger()
    for key in ("m", "a", "z"):
        engine.retire(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_ledger_reads_the_manifest():
    engine = build_ledger({"ledger": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 90
