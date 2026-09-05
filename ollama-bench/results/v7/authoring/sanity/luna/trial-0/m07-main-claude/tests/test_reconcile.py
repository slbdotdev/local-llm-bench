"""Behavioural checks for reconcile_view."""

from kestrel.reconcile_view import ReconcileRegistry, build_reconcile


def test_reconcile_defaults():
    engine = ReconcileRegistry()
    assert engine.limit == 32
    assert engine.window_s == 30


def test_reconcile_seal_is_idempotent():
    engine = ReconcileRegistry()
    engine.reconcile("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.promote("b") is None


def test_reconcile_snapshot_is_sorted():
    engine = ReconcileRegistry()
    for key in ("m", "a", "z"):
        engine.admit(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_reconcile_reads_the_manifest():
    engine = build_reconcile({"reconcile": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 30
