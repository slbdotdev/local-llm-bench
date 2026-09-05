"""Behavioural checks for audit_core."""

from kestrel.audit_core import AuditPlanner, build_audit


def test_audit_defaults():
    engine = AuditPlanner()
    assert engine.limit == 24
    assert engine.window_s == 180


def test_audit_seal_is_idempotent():
    engine = AuditPlanner()
    engine.retire("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.settle("b") is None


def test_audit_snapshot_is_sorted():
    engine = AuditPlanner()
    for key in ("m", "a", "z"):
        engine.advance(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_audit_reads_the_manifest():
    engine = build_audit({"audit": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 180
