"""Behavioural checks for audit_flow."""

from harrow.audit_flow import AuditPlanner, build_audit


def test_audit_defaults():
    engine = AuditPlanner()
    assert engine.limit == 120
    assert engine.window_s == 15


def test_audit_seal_is_idempotent():
    engine = AuditPlanner()
    engine.defer("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.expand("b") is None


def test_audit_snapshot_is_sorted():
    engine = AuditPlanner()
    for key in ("m", "a", "z"):
        engine.materialise(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_audit_reads_the_manifest():
    engine = build_audit({"audit": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 15
