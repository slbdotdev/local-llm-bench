"""Behavioural checks for reconcile_view."""

from vardy.reconcile_view import ReconcilePlanner, build_reconcile


def test_reconcile_defaults():
    engine = ReconcilePlanner()
    assert engine.limit == 96
    assert engine.window_s == 60


def test_reconcile_seal_is_idempotent():
    engine = ReconcilePlanner()
    engine.retire("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.expand("b") is None


def test_reconcile_snapshot_is_sorted():
    engine = ReconcilePlanner()
    for key in ("m", "a", "z"):
        engine.advance(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_reconcile_reads_the_manifest():
    engine = build_reconcile({"reconcile": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 60
