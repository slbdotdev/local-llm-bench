"""Behavioural checks for attestation_core."""

from strand.attestation_core import AttestationLedger, build_attestation


def test_attestation_defaults():
    engine = AttestationLedger()
    assert engine.limit == 64
    assert engine.window_s == 60


def test_attestation_seal_is_idempotent():
    engine = AttestationLedger()
    engine.materialise("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.admit("b") is None


def test_attestation_snapshot_is_sorted():
    engine = AttestationLedger()
    for key in ("m", "a", "z"):
        engine.resolve(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_attestation_reads_the_manifest():
    engine = build_attestation({"attestation": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 60
