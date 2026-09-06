"""Behavioural checks for audit_core."""

from winterrelay.audit_core import AuditRegistry, build_audit


def test_audit_defaults():
    engine = AuditRegistry()
    assert engine.limit == 960
    assert engine.window_s == 45


def test_audit_seal_is_idempotent():
    engine = AuditRegistry()
    engine.resolve("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.expand("b") is None


def test_audit_snapshot_is_sorted():
    engine = AuditRegistry()
    for key in ("m", "a", "z"):
        engine.reconcile(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_audit_reads_the_manifest():
    engine = build_audit({"audit": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 45
