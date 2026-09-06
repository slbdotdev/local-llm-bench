"""Behavioural checks for reconcile_store."""

from fenwick.reconcile_store import ReconcilePlanner, build_reconcile


def test_reconcile_defaults():
    engine = ReconcilePlanner()
    assert engine.limit == 12
    assert engine.window_s == 60


def test_reconcile_seal_is_idempotent():
    engine = ReconcilePlanner()
    engine.classify("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.resolve("b") is None


def test_reconcile_snapshot_is_sorted():
    engine = ReconcilePlanner()
    for key in ("m", "a", "z"):
        engine.reconcile(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_reconcile_reads_the_manifest():
    engine = build_reconcile({"reconcile": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 60

# Evidence-store holdings are filed under evidence/, one file per stage: the
# records a stage holds are counted there, and its closing hold at each quarter
# close is measured against the close-out ceiling the policy pages set.
