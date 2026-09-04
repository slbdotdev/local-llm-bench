"""Additional edge case tests for stateful.py"""
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

# Test truncated frame
print("Test: Truncated frame")
truncated = bytes([FLAG, 0x02, 0x02])  # FLAG, LEN=2, TYPE=2 (missing SEQ, TICK, CK)
r = replay(truncated)
print("  events:", r["events"])
assert ("drop", 0, "truncated") in r["events"], "Expected truncated drop"
print("  PASS")
print()

# Test bad escape with FLAG
print("Test: Bad escape (ESC followed by FLAG)")
bad_escape = bytes([FLAG, ESC, FLAG])  # FLAG, ESC, FLAG - bad escape
r = replay(bad_escape)
print("  events:", r["events"])
assert ("drop", 0, "bad_escape") in r["events"], "Expected bad_escape drop"
print("  PASS")
print()

# Test good escape with ESC ^ 0x20
print("Test: Good escape (FLAG byte in payload)")
# Build frame with payload containing FLAG byte (0x7E)
# After escaping, FLAG becomes ESC, 0x5E
body = bytes([1, 1, 0, 0])  # LEN=1, TYPE=1, SEQ=0, TICK=0
body += bytes([0x7E])  # payload with FLAG
body += bytes([(sum(body) & 0xFF)])  # checksum
frame_escaped = bytearray([FLAG])
for b in body:
    if b in (FLAG, ESC):
        frame_escaped += bytes([ESC, b ^ 0x20])
    else:
        frame_escaped.append(b)
r = replay(bytes(frame_escaped))
print("  frame hex:", " ".join(f"{b:02x}" for b in frame_escaped))
print("  events:", r["events"])
assert r["state"] == "OPEN", "Expected OPEN state"
print("  PASS")
print()

# Test RESET clears buffer and discard events
print("Test: RESET clears buffer and discard events")
r = replay(
    F(1, 0, 0, b"") + F(2, 1, 0, b"A") + F(5, 0, 0, b"")
)  # HELLO, DATA seq=1 (buffered), RESET
print("  events:", r["events"])
assert ("buf", 1, 1) in r["events"], "Expected buf event"
assert ("discard", 1) in r["events"], "Expected discard event"
assert r["delivered"] == [], "Expected empty delivered"
assert r["window"] == [], "Expected empty window"
assert r["expect"] == 0, "Expected expect to be 0 after reset"
assert r["state"] == "IDLE", "Expected IDLE state"
print("  PASS")
print()

# Test windowing and flushing on ordered delivery
print("Test: Buffer flushing on ordered delivery")
r = replay(
    F(1, 0, 0, b"") + F(2, 2, 0, b"C") + F(2, 1, 0, b"B") + F(2, 0, 0, b"A")
)
print("  delivered:", r["delivered"])
print("  events:", r["events"])
assert r["delivered"] == [b"A", b"B", b"C"], f"Expected [b'A', b'B', b'C'], got {r['delivered']}"
assert r["expect"] == 3, f"Expected expect=3, got {r['expect']}"
print("  PASS")
print()

# Test PING arms timer
print("Test: PING arms timer")
r = replay(F(1, 0, 0, b"") + F(3, 0, 0, b""))
print("  deadline:", r["deadline"])
print("  clock:", r["clock"])
assert r["deadline"] == 20, "Expected deadline=20 after PING"
assert r["state"] == "OPEN", "Expected OPEN state"
print("  PASS")
print()

# Test CLOSE in OPEN flushes and moves to DRAINING
print("Test: CLOSE in OPEN flushes and moves to DRAINING")
r = replay(
    F(1, 0, 0, b"") + F(2, 1, 0, b"B") + F(2, 0, 0, b"A") + F(4, 0, 0, b"")
)
print("  state:", r["state"])
print("  delivered:", r["delivered"])
print("  events:", r["events"])
assert r["state"] == "DRAINING", "Expected DRAINING state"
assert r["delivered"] == [b"A", b"B"], f"Expected [b'A', b'B'], got {r['delivered']}"
# seq 0 arrives in order and is delivered, seq 1 is flushed from buffer
assert ("deliver", 2, 0) in r["events"], "Expected deliver event for seq 0"
assert ("flush", 1) in r["events"], "Expected flush event for seq 1"
print("  PASS")
print()

# Test CLOSE in DRAINING moves to CLOSED
print("Test: CLOSE in DRAINING moves to CLOSED")
r = replay(
    F(1, 0, 0, b"") + F(2, 0, 0, b"A") + F(4, 0, 0, b"") + F(4, 0, 0, b"")
)
print("  state:", r["state"])
print("  events:", r["events"])
assert r["state"] == "CLOSED", "Expected CLOSED state"
assert ("state", "DRAINING") in r["events"], "Expected state change to DRAINING"
assert ("state", "CLOSED") in r["events"], "Expected state change to CLOSED"
print("  PASS")
print()

print("All extra tests passed!")
