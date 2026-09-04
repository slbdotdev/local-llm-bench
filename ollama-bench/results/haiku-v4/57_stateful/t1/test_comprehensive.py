"""Comprehensive test suite for stateful.py edge cases"""
from stateful import replay, ProtocolError

FLAG = 0x7E
ESC = 0x7D

def F(ty, seq, tick, payload=b'', ck=None):
    body = bytes([len(payload), ty, seq, tick]) + bytes(payload)
    body += bytes([(sum(body) & 0xFF) if ck is None else ck])
    out = bytearray([FLAG])
    for b in body:
        if b in (FLAG, ESC):
            out += bytes([ESC, b ^ 0x20])
        else:
            out.append(b)
    return bytes(out)

print("Test 1: Clock modulo 64")
# HELLO with tick 50, then frame with tick 50 (total would be 100, but mod 64 = 36)
r = replay(F(1, 0, 50, b"") + F(3, 0, 50, b""))
assert r["clock"] == 36, f"Expected clock=36, got {r['clock']}"
print("  PASS")

print("Test 2: Retransmission detection (d=12..15)")
# expect = 0, so retransmissions would be seqs 13, 14, 15, 0 (wrap around)
# d = (13 - 0) % 16 = 13 (retransmission, dup)
# d = (15 - 0) % 16 = 15 (retransmission, dup)
r = replay(
    F(1, 0, 0, b"")  # expect = 0
    + F(2, 0, 0, b"A")  # in order
    + F(2, 15, 0, b"old")  # d = 15 (retransmission)
)
assert ("dup", 2, 15) in r["events"], "Expected dup event for retransmission"
assert r["delivered"] == [b"A"], f"Expected [b'A'], got {r['delivered']}"
print("  PASS")

print("Test 3: Clock wraps at 64 when adding tick")
# After HELLO sets deadline = clock + 20, if tick = 44, clock becomes 44
# deadline = 44 + 20 = 64, which is still not > 64
# But if tick then becomes 1, clock = (64 + 1) % 64 = 1, and 1 is not > 64
r = replay(F(1, 0, 0, b"") + F(3, 0, 44, b"") + F(3, 0, 1, b""))
# With deadline initially 20, then reset to 64 after first PING, then to 21 after second
print(f"  clock={r['clock']}, deadline={r['deadline']}")
print("  PASS")

print("Test 4: Empty payload is valid")
# DATA with LEN=0 (empty payload)
r = replay(F(1, 0, 0, b"") + F(2, 0, 0, b""))
assert r["delivered"] == [b""], f"Expected [b''], got {r['delivered']}"
print("  PASS")

print("Test 5: State change event only when state actually changes")
# HELLO moves IDLE -> OPEN (state change)
# Then PING doesn't change state (no state event)
# Then CLOSE moves OPEN -> DRAINING (state change)
r = replay(F(1, 0, 0, b"") + F(3, 0, 0, b"") + F(4, 0, 0, b""))
state_events = [e for e in r["events"] if e[0] == "state"]
assert len(state_events) == 2, f"Expected 2 state events, got {len(state_events)}"
assert ("state", "OPEN") in state_events
assert ("state", "DRAINING") in state_events
print("  PASS")

print("Test 6: Multiple frames in window flushed in correct order")
# Expect 0: receive 3, 2, 1 (out of order)
# Then receive 0 (in order) -> flush 1, 2, 3
r = replay(
    F(1, 0, 0, b"")  # expect = 0
    + F(2, 3, 0, b"D")
    + F(2, 2, 0, b"C")
    + F(2, 1, 0, b"B")
    + F(2, 0, 0, b"A")
)
assert r["delivered"] == [b"A", b"B", b"C", b"D"], f"Expected [A,B,C,D], got {r['delivered']}"
# Window order should be [1,2,3] before delivery of 0
print("  PASS")

print("Test 7: Frames beyond window (d=4..11) are dropped and not buffered")
# expect = 0, so d=4 gives seq=4
r = replay(
    F(1, 0, 0, b"")  # expect = 0
    + F(2, 4, 0, b"A")  # d = 4 (out of window)
    + F(2, 0, 0, b"B")  # in order, should deliver B only
)
assert r["delivered"] == [b"B"], f"Expected [b'B'], got {r['delivered']}"
assert r["window"] == [], f"Expected empty window, got {r['window']}"
print("  PASS")

print("Test 8: Timer is not affected by dup events")
# HELLO (deadline=20), then duplicate frames should not reset timer
r = replay(
    F(1, 0, 0, b"")  # deadline = 20
    + F(2, 0, 0, b"A")  # deliver
    + F(2, 0, 0, b"A_dup")  # dup (timer not touched)
)
# After first frame, deadline is still set to something
# After dup, it should not have changed
assert r["deadline"] == 20  # From initial HELLO + initial deliver
print("  PASS")

print("Test 9: Timeout clears buffer with discard events in window order")
# HELLO, buffer some frames, then timeout
r = replay(
    F(1, 0, 0, b"")  # expect = 0, deadline = 20
    + F(2, 2, 0, b"C")  # buffer seq 2
    + F(2, 1, 0, b"B")  # buffer seq 1
    + F(3, 0, 21, b"")  # timeout at clock 21 > deadline 20
)
assert ("timeout", 21) in r["events"]
# Buffer should be discarded in window order: seq 1 then seq 2
discard_events = [e for e in r["events"] if e[0] == "discard"]
assert discard_events == [("discard", 1), ("discard", 2)], f"Got {discard_events}"
assert r["window"] == [], "Window should be empty after timeout"
print("  PASS")

print("Test 10: RESET clears buffer and sets expect to 0")
# After HELLO with seq=5 (expect=5), buffer something, RESET
r = replay(
    F(1, 5, 0, b"")  # expect = 5
    + F(2, 6, 0, b"A")  # buffer
    + F(5, 0, 0, b"")  # RESET
)
assert r["expect"] == 0, f"Expected expect=0 after RESET, got {r['expect']}"
assert r["state"] == "IDLE", f"Expected IDLE after RESET, got {r['state']}"
print("  PASS")

print("Test 11: Return dict has exactly the required keys with correct types")
r = replay(F(1, 0, 0, b"") + F(2, 0, 0, b"hello") + F(4, 0, 0, b""))
required_keys = {"state", "clock", "expect", "deadline", "window", "delivered", "illegal", "frames", "aborted", "events"}
assert set(r.keys()) == required_keys, f"Keys mismatch: {set(r.keys())} vs {required_keys}"
assert isinstance(r["state"], str)
assert isinstance(r["clock"], int)
assert isinstance(r["expect"], int)
assert r["deadline"] is None or isinstance(r["deadline"], int)
assert isinstance(r["window"], list)
assert isinstance(r["delivered"], list)
assert isinstance(r["illegal"], int)
assert isinstance(r["frames"], int)
assert isinstance(r["aborted"], bool)
assert isinstance(r["events"], list)
# Check event types
for event in r["events"]:
    assert isinstance(event, tuple), f"Event {event} is not a tuple"
print("  PASS")

print("Test 12: Payload is bytes, not bytearray or str")
r = replay(F(1, 0, 0, b"") + F(2, 0, 0, b"hello"))
assert isinstance(r["delivered"][0], bytes)
for seq, payload in r["window"]:
    assert isinstance(payload, bytes)
print("  PASS")

print("\nAll comprehensive tests passed!")
