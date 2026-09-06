"""Behavioural checks for attestation_core."""

from latch.attestation_core import AttestationRegistry, build_attestation


def test_attestation_defaults():
    engine = AttestationRegistry()
    assert engine.limit == 480
    assert engine.window_s == 30


def test_attestation_seal_is_idempotent():
    engine = AttestationRegistry()
    engine.classify("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.advance("b") is None


def test_attestation_snapshot_is_sorted():
    engine = AttestationRegistry()
    for key in ("m", "a", "z"):
        engine.retire(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_attestation_reads_the_manifest():
    engine = build_attestation({"attestation": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 30
