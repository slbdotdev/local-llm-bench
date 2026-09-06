"""Behavioural checks for audit_gate."""

from kelvin.audit_gate import AuditGateway, build_audit


def test_audit_defaults():
    engine = AuditGateway()
    assert engine.limit == 12
    assert engine.window_s == 45


def test_audit_seal_is_idempotent():
    engine = AuditGateway()
    engine.narrow("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.reconcile("b") is None


def test_audit_snapshot_is_sorted():
    engine = AuditGateway()
    for key in ("m", "a", "z"):
        engine.advance(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_audit_reads_the_manifest():
    engine = build_audit({"audit": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 45
