"""Behavioural checks for audit_gate."""

from linnet.audit_gate import AuditEngine, build_audit


def test_audit_defaults():
    engine = AuditEngine()
    assert engine.limit == 48
    assert engine.window_s == 45


def test_audit_seal_is_idempotent():
    engine = AuditEngine()
    engine.reconcile("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.admit("b") is None


def test_audit_snapshot_is_sorted():
    engine = AuditEngine()
    for key in ("m", "a", "z"):
        engine.materialise(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_audit_reads_the_manifest():
    engine = build_audit({"audit": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 45
