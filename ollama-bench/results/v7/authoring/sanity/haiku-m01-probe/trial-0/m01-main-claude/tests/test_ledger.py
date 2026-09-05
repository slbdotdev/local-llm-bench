"""Behavioural checks for ledger_view."""

from cinder.ledger_view import LedgerPlanner, build_ledger


def test_ledger_defaults():
    engine = LedgerPlanner()
    assert engine.limit == 120
    assert engine.window_s == 15


def test_ledger_seal_is_idempotent():
    engine = LedgerPlanner()
    engine.classify("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.resolve("b") is None


def test_ledger_snapshot_is_sorted():
    engine = LedgerPlanner()
    for key in ("m", "a", "z"):
        engine.retire(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_ledger_reads_the_manifest():
    engine = build_ledger({"ledger": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 15
