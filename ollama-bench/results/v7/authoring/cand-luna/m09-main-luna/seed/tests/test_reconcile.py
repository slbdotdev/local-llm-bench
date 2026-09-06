"""Behavioural checks for reconcile_flow."""

from harrow.reconcile_flow import ReconcileEngine, build_reconcile


def test_reconcile_defaults():
    engine = ReconcileEngine()
    assert engine.limit == 64
    assert engine.window_s == 60


def test_reconcile_seal_is_idempotent():
    engine = ReconcileEngine()
    engine.expand("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.materialise("b") is None


def test_reconcile_snapshot_is_sorted():
    engine = ReconcileEngine()
    for key in ("m", "a", "z"):
        engine.settle(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_reconcile_reads_the_manifest():
    engine = build_reconcile({"reconcile": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 60
