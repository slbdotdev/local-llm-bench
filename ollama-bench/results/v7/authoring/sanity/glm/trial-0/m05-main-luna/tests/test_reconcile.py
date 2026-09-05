"""Behavioural checks for reconcile_view."""

from CedarSignal.reconcile_view import ReconcileLedger, build_reconcile


def test_reconcile_defaults():
    engine = ReconcileLedger()
    assert engine.limit == 960
    assert engine.window_s == 60


def test_reconcile_seal_is_idempotent():
    engine = ReconcileLedger()
    engine.advance("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.reconcile("b") is None


def test_reconcile_snapshot_is_sorted():
    engine = ReconcileLedger()
    for key in ("m", "a", "z"):
        engine.defer(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_reconcile_reads_the_manifest():
    engine = build_reconcile({"reconcile": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 60
