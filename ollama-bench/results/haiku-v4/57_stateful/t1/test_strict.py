"""Test strict mode error handling"""
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

# Test 1: Strict mode on bad_transcript
print("Test: Strict mode on bad_transcript")
try:
    replay("not bytes", strict=True)
    print("  FAIL: Should have raised ProtocolError")
except ProtocolError as e:
    assert e.kind == "bad_transcript"
    assert e.index == -1
    assert e.events == []
    print("  PASS")

# Test 2: Strict mode on first drop event
print("Test: Strict mode on first drop (bad_checksum)")
try:
    replay(b"\x01\x02" + F(2, 0, 0, b"z", ck=0) + F(1, 0, 0), strict=True)
    print("  FAIL: Should have raised ProtocolError")
except ProtocolError as e:
    assert e.kind == "bad_checksum"
    assert e.index == 0
    # Should have junk event before the drop
    assert ("junk", 2) in e.events
    print("  PASS")

# Test 3: Strict mode on illegal message
print("Test: Strict mode on illegal message")
try:
    replay(F(2, 0, 0, b"q") + F(1, 0, 0), strict=True)
    print("  FAIL: Should have raised ProtocolError")
except ProtocolError as e:
    assert e.kind == "illegal"
    assert e.index == 0
    assert e.events == []
    print("  PASS")

# Test 4: Strict mode on out_of_window
print("Test: Strict mode on out_of_window")
try:
    replay(F(1, 0, 0, b"") + F(2, 5, 0, b"A"), strict=True)
    print("  FAIL: Should have raised ProtocolError")
except ProtocolError as e:
    assert e.kind == "out_of_window"
    assert e.index == 1
    print("  PASS")

# Test 5: Strict mode on timeout
print("Test: Strict mode on timeout")
try:
    replay(F(1, 0, 0, b"") + F(3, 0, 21, b""), strict=True)
    print("  FAIL: Should have raised ProtocolError")
except ProtocolError as e:
    assert e.kind == "timeout"
    assert e.index == -1
    print("  PASS")

# Test 6: Strict mode on draining drop
print("Test: Strict mode on draining drop")
try:
    replay(F(1, 0, 0, b"") + F(4, 0, 0, b"") + F(2, 0, 0, b"A"), strict=True)
    print("  FAIL: Should have raised ProtocolError")
except ProtocolError as e:
    assert e.kind == "draining"
    assert e.index == 2
    print("  PASS")

# Test 7: Non-strict mode with multiple errors continues
print("Test: Non-strict mode with multiple errors")
r = replay(
    F(2, 0, 0, b"q")  # illegal (DATA in IDLE)
    + F(2, 0, 0, b"q")  # illegal
    + F(2, 0, 0, b"q")  # illegal - hits limit
    + F(1, 0, 0, b"")  # after abort, still processed
)
assert r["aborted"] is True
assert r["illegal"] == 3
assert r["state"] == "CLOSED"
assert ("abort", "illegal_limit") in r["events"]
print("  PASS")

# Test 8: Out of window frame ranges
print("Test: Out of window frame ranges (d=4..11)")
r = replay(
    F(1, 0, 0, b"")  # expect = 0
    + F(2, 4, 0, b"A")  # d = (4 - 0) % 16 = 4 (out of window)
)
assert ("drop", 1, "out_of_window") in r["events"]
assert r["delivered"] == []
print("  PASS")

# Test 9: Window order is correct (modulo ordering)
print("Test: Window order is (seq - expect) mod 16 ascending")
r = replay(
    F(1, 5, 0, b"")  # expect = 5
    + F(2, 8, 0, b"C")  # d = (8 - 5) % 16 = 3 (buffered)
    + F(2, 6, 0, b"A")  # d = (6 - 5) % 16 = 1 (buffered)
    + F(2, 7, 0, b"B")  # d = (7 - 5) % 16 = 2 (buffered)
)
# Window should be ordered by (seq - expect) % 16: [6, 7, 8] gives distances [1, 2, 3]
assert len(r["window"]) == 3
assert r["window"][0][0] == 6  # seq, distance 1
assert r["window"][1][0] == 7  # seq, distance 2
assert r["window"][2][0] == 8  # seq, distance 3
print("  PASS")

# Test 10: Duplicate detection in window
print("Test: Duplicate detection in window")
r = replay(
    F(1, 0, 0, b"")  # expect = 0
    + F(2, 1, 0, b"A")  # buffer seq 1
    + F(2, 1, 0, b"B")  # duplicate of seq 1
)
assert ("buf", 1, 1) in r["events"]
assert ("dup", 2, 1) in r["events"]
assert r["window"] == [(1, b"A")]  # First payload kept
print("  PASS")

print("\nAll strict mode tests passed!")
