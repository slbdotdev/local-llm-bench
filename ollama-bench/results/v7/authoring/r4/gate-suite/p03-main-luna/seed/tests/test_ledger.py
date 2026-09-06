"""Behavioural checks for ledger_flow."""

from accord.ledger_flow import LedgerGateway, build_ledger


def test_ledger_defaults():
    engine = LedgerGateway()
    assert engine.limit == 960
    assert engine.window_s == 180


def test_ledger_seal_is_idempotent():
    engine = LedgerGateway()
    engine.reconcile("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.settle("b") is None


def test_ledger_snapshot_is_sorted():
    engine = LedgerGateway()
    for key in ("m", "a", "z"):
        engine.advance(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_ledger_reads_the_manifest():
    engine = build_ledger({"ledger": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 180
