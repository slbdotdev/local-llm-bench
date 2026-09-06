"""Behavioural checks for audit_view."""

from strand.audit_view import AuditGateway, build_audit


def test_audit_defaults():
    engine = AuditGateway()
    assert engine.limit == 48
    assert engine.window_s == 180


def test_audit_seal_is_idempotent():
    engine = AuditGateway()
    engine.advance("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.materialise("b") is None


def test_audit_snapshot_is_sorted():
    engine = AuditGateway()
    for key in ("m", "a", "z"):
        engine.reconcile(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_audit_reads_the_manifest():
    engine = build_audit({"audit": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 180
