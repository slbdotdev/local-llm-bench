"""Behavioural checks for audit_flow."""

from thistle.audit_flow import AuditLedger, build_audit


def test_audit_defaults():
    engine = AuditLedger()
    assert engine.limit == 120
    assert engine.window_s == 120


def test_audit_seal_is_idempotent():
    engine = AuditLedger()
    engine.expand("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.defer("b") is None


def test_audit_snapshot_is_sorted():
    engine = AuditLedger()
    for key in ("m", "a", "z"):
        engine.coalesce(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_audit_reads_the_manifest():
    engine = build_audit({"audit": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 120
