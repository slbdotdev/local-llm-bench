"""Behavioural checks for reconcile_gate."""

from northgate.reconcile_gate import ReconcilePlanner, build_reconcile


def test_reconcile_defaults():
    engine = ReconcilePlanner()
    assert engine.limit == 12
    assert engine.window_s == 120


def test_reconcile_seal_is_idempotent():
    engine = ReconcilePlanner()
    engine.advance("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.reconcile("b") is None


def test_reconcile_snapshot_is_sorted():
    engine = ReconcilePlanner()
    for key in ("m", "a", "z"):
        engine.materialise(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_reconcile_reads_the_manifest():
    engine = build_reconcile({"reconcile": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 120
