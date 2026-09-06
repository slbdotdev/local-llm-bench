"""Behavioural checks for attestation_flow."""

from vantage.attestation_flow import AttestationRegistry, build_attestation


def test_attestation_defaults():
    engine = AttestationRegistry()
    assert engine.limit == 48
    assert engine.window_s == 180


def test_attestation_seal_is_idempotent():
    engine = AttestationRegistry()
    engine.narrow("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.admit("b") is None


def test_attestation_snapshot_is_sorted():
    engine = AttestationRegistry()
    for key in ("m", "a", "z"):
        engine.materialise(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_attestation_reads_the_manifest():
    engine = build_attestation({"attestation": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 180
