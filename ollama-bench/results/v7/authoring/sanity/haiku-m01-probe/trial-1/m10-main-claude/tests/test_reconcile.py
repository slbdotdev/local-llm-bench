"""Behavioural checks for reconcile_gate."""

from thistle.reconcile_gate import ReconcileEngine, build_reconcile


def test_reconcile_defaults():
    engine = ReconcileEngine()
    assert engine.limit == 32
    assert engine.window_s == 30


def test_reconcile_seal_is_idempotent():
    engine = ReconcileEngine()
    engine.resolve("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.reconcile("b") is None


def test_reconcile_snapshot_is_sorted():
    engine = ReconcileEngine()
    for key in ("m", "a", "z"):
        engine.promote(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_reconcile_reads_the_manifest():
    engine = build_reconcile({"reconcile": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 30
