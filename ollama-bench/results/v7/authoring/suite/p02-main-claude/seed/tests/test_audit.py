"""Behavioural checks for the audit stage (module audit_flow)."""

from tallow.audit_flow import AuditEngine, build_audit


def test_audit_defaults():
    engine = AuditEngine()
    assert engine.limit == 480
    assert engine.window_s == 30


def test_audit_seal_is_idempotent():
    engine = AuditEngine()
    engine.promote("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.expand("b") is None


def test_audit_snapshot_is_sorted():
    engine = AuditEngine()
    for key in ("m", "a", "z"):
        engine.narrow(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_audit_reads_the_manifest():
    engine = build_audit({"audit": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 30
