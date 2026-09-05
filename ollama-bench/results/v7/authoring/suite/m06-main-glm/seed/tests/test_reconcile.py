"""Behavioural checks for reconcile_flow."""

from larkspur.reconcile_flow import ReconcileLedger, build_reconcile


def test_reconcile_defaults():
    engine = ReconcileLedger()
    assert engine.limit == 480
    assert engine.window_s == 60


def test_reconcile_seal_is_idempotent():
    engine = ReconcileLedger()
    engine.admit("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.narrow("b") is None


def test_reconcile_snapshot_is_sorted():
    engine = ReconcileLedger()
    for key in ("m", "a", "z"):
        engine.classify(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_reconcile_reads_the_manifest():
    engine = build_reconcile({"reconcile": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 60
