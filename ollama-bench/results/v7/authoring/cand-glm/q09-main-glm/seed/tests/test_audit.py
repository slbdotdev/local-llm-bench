"""Behavioural checks for audit_view."""

from kestrel.audit_view import AuditLedger, build_audit


def test_audit_defaults():
    engine = AuditLedger()
    assert engine.limit == 480
    assert engine.window_s == 60


def test_audit_seal_is_idempotent():
    engine = AuditLedger()
    engine.advance("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.defer("b") is None


def test_audit_snapshot_is_sorted():
    engine = AuditLedger()
    for key in ("m", "a", "z"):
        engine.resolve(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_audit_reads_the_manifest():
    engine = build_audit({"audit": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 60
