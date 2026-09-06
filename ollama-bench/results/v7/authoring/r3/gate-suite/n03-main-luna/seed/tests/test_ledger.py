"""Behavioural checks for ledger_core."""

from cinder.ledger_core import LedgerRegistry, build_ledger


def test_ledger_defaults():
    engine = LedgerRegistry()
    assert engine.limit == 24
    assert engine.window_s == 120


def test_ledger_seal_is_idempotent():
    engine = LedgerRegistry()
    engine.coalesce("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.reconcile("b") is None


def test_ledger_snapshot_is_sorted():
    engine = LedgerRegistry()
    for key in ("m", "a", "z"):
        engine.expand(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_ledger_reads_the_manifest():
    engine = build_ledger({"ledger": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 120
