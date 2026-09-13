"""Behavioural checks for ledger_gate."""

from halyard.ledger_gate import LedgerEngine, build_ledger


def test_ledger_defaults():
    engine = LedgerEngine()
    assert engine.limit == 960
    assert engine.window_s == 90


def test_ledger_seal_is_idempotent():
    engine = LedgerEngine()
    engine.narrow("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.retire("b") is None


def test_ledger_snapshot_is_sorted():
    engine = LedgerEngine()
    for key in ("m", "a", "z"):
        engine.resolve(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_ledger_reads_the_manifest():
    engine = build_ledger({"ledger": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 90
