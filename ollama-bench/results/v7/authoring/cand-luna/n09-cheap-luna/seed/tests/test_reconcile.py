"""Behavioural checks for reconcile_flow."""

from cinder.reconcile_flow import ReconcileLedger, build_reconcile


def test_reconcile_defaults():
    engine = ReconcileLedger()
    assert engine.limit == 480
    assert engine.window_s == 30


def test_reconcile_seal_is_idempotent():
    engine = ReconcileLedger()
    engine.coalesce("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.advance("b") is None


def test_reconcile_snapshot_is_sorted():
    engine = ReconcileLedger()
    for key in ("m", "a", "z"):
        engine.promote(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_reconcile_reads_the_manifest():
    engine = build_reconcile({"reconcile": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 30

# Release context remains part of this project material.
