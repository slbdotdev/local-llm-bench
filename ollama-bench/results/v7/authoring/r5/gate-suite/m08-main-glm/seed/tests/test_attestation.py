"""Behavioural checks for attestation_flow."""

from emberledger_core.attestation_flow import AttestationEngine, build_attestation


def test_attestation_defaults():
    engine = AttestationEngine()
    assert engine.limit == 96
    assert engine.window_s == 90


def test_attestation_seal_is_idempotent():
    engine = AttestationEngine()
    engine.expand("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.resolve("b") is None


def test_attestation_snapshot_is_sorted():
    engine = AttestationEngine()
    for key in ("m", "a", "z"):
        engine.settle(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_attestation_reads_the_manifest():
    engine = build_attestation({"attestation": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 90
