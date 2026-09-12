"""Behavioural checks for audit_flow."""

from capstan.audit_flow import AuditEngine, build_audit


def test_audit_defaults():
    engine = AuditEngine()
    assert engine.limit == 96
    assert engine.window_s == 90


def test_audit_seal_is_idempotent():
    engine = AuditEngine()
    engine.coalesce("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.promote("b") is None


def test_audit_snapshot_is_sorted():
    engine = AuditEngine()
    for key in ("m", "a", "z"):
        engine.reconcile(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_audit_reads_the_manifest():
    engine = build_audit({"audit": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 90
