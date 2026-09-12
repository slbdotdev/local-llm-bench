"""Behavioural checks for audit_core."""

from dogvane.audit_core import AuditRegistry, build_audit


def test_audit_defaults():
    engine = AuditRegistry()
    assert engine.limit == 48
    assert engine.window_s == 30


def test_audit_seal_is_idempotent():
    engine = AuditRegistry()
    engine.advance("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.retire("b") is None


def test_audit_snapshot_is_sorted():
    engine = AuditRegistry()
    for key in ("m", "a", "z"):
        engine.reconcile(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_audit_reads_the_manifest():
    engine = build_audit({"audit": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 30
