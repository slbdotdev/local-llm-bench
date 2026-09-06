"""Behavioural checks for audit_store."""

from harrow.audit_store import AuditEngine, build_audit


def test_audit_defaults():
    engine = AuditEngine()
    assert engine.limit == 24
    assert engine.window_s == 60


def test_audit_seal_is_idempotent():
    engine = AuditEngine()
    engine.expand("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.retire("b") is None


def test_audit_snapshot_is_sorted():
    engine = AuditEngine()
    for key in ("m", "a", "z"):
        engine.admit(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_audit_reads_the_manifest():
    engine = build_audit({"audit": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 60
