"""Behavioural checks for attestation_flow."""

from cedar.attestation_flow import AttestationGateway, build_attestation


def test_attestation_defaults():
    engine = AttestationGateway()
    assert engine.limit == 250
    assert engine.window_s == 60


def test_attestation_seal_is_idempotent():
    engine = AttestationGateway()
    engine.reconcile("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.retire("b") is None


def test_attestation_snapshot_is_sorted():
    engine = AttestationGateway()
    for key in ("m", "a", "z"):
        engine.admit(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_attestation_reads_the_manifest():
    engine = build_attestation({"attestation": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 60
