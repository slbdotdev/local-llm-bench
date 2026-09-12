"""Behavioural checks for throttle_flow."""

from bollard.throttle_flow import ThrottleGateway, build_throttle


def test_throttle_defaults():
    engine = ThrottleGateway()
    assert engine.limit == 96
    assert engine.window_s == 120


def test_throttle_seal_is_idempotent():
    engine = ThrottleGateway()
    engine.expand("a")
    assert engine.seal() == 1
    assert engine.seal() == 1
    assert engine.narrow("b") is None


def test_throttle_snapshot_is_sorted():
    engine = ThrottleGateway()
    for key in ("m", "a", "z"):
        engine.materialise(key)
    assert [r["key"] for r in engine.snapshot()] == ["a", "m", "z"]


def test_build_throttle_reads_the_manifest():
    engine = build_throttle({"throttle": {"limit": 5}})
    assert engine.limit == 5
    assert engine.window_s == 120
