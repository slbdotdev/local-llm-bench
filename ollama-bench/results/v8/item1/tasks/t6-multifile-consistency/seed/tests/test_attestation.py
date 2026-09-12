"""Behavioural checks for attestation_core."""

from futtock.attestation_core import AttestationGateway, build_attestation


def test_attestation_defaults():
    engine = AttestationGateway()
    assert engine.limit == 96
    assert engine.window_s == 90


def test_attestation_seal_is_idempotent():
    engine = AttestationGateway()
    engine.materialise("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.classify("b") is None


def test_attestation_snapshot_is_sorted():
    engine = AttestationGateway()
    for key in ("m", "a", "z"):
        engine.reconcile(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_attestation_reads_the_manifest():
    engine = build_attestation({"attestation": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 90
