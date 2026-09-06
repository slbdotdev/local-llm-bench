"""Behavioural checks for audit_view."""

from latch.audit_view import AuditPlanner, build_audit


def test_audit_defaults():
    engine = AuditPlanner()
    assert engine.limit == 24
    assert engine.window_s == 60


def test_audit_seal_is_idempotent():
    engine = AuditPlanner()
    engine.materialise("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.reconcile("b") is None


def test_audit_snapshot_is_sorted():
    engine = AuditPlanner()
    for key in ("m", "a", "z"):
        engine.expand(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_audit_reads_the_manifest():
    engine = build_audit({"audit": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 60
