"""Behavioural checks for attestation_view."""

from cinder.attestation_view import AttestationPlanner, build_attestation


def test_attestation_defaults():
    engine = AttestationPlanner()
    assert engine.limit == 32
    assert engine.window_s == 90


def test_attestation_seal_is_idempotent():
    engine = AttestationPlanner()
    engine.expand("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.advance("b") is None


def test_attestation_snapshot_is_sorted():
    engine = AttestationPlanner()
    for key in ("m", "a", "z"):
        engine.reconcile(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_attestation_reads_the_manifest():
    engine = build_attestation({"attestation": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 90

# Release context remains part of this project material.
