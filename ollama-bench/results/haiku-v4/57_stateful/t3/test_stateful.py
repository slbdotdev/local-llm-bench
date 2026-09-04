"""Visible examples for stateful.py.  Run with `python test_stateful.py`."""
from stateful import replay, ProtocolError

FLAG = 0x7E
ESC = 0x7D


def F(ty, seq, tick, payload=b"", ck=None):
    """Build one correctly framed message (ck overrides the checksum byte)."""
    body = bytes([len(payload), ty, seq, tick]) + bytes(payload)
    body += bytes([(sum(body) & 0xFF) if ck is None else ck])
    out = bytearray([FLAG])
    for b in body:
        if b in (FLAG, ESC):
            out += bytes([ESC, b ^ 0x20])
        else:
            out.append(b)
    return bytes(out)


r = replay(F(1, 0, 1) + F(2, 0, 2, b"ab") + F(2, 1, 2, b"c") + F(4, 0, 1))
assert r["state"] == "DRAINING", r["state"]
assert r["clock"] == 6 and r["expect"] == 2 and r["deadline"] == 26
assert r["window"] == [] and r["delivered"] == [b"ab", b"c"]
assert r["illegal"] == 0 and r["frames"] == 4 and r["aborted"] is False
assert r["events"] == [("hello", 0, 0), ("state", "OPEN"), ("deliver", 1, 0),
                       ("deliver", 2, 1), ("close", 3), ("state", "DRAINING")], r["events"]

r = replay(F(1, 3, 0) + F(2, 4, 1, b"x") + F(2, 3, 1, b"w"))
assert r["state"] == "OPEN" and r["clock"] == 2 and r["expect"] == 5
assert r["deadline"] == 22 and r["window"] == []
assert r["delivered"] == [b"w", b"x"] and r["frames"] == 3
assert r["events"] == [("hello", 0, 3), ("state", "OPEN"), ("buf", 1, 4),
                       ("deliver", 2, 3), ("flush", 4)], r["events"]

r = replay(b"\x01\x02" + F(2, 0, 0, b"z", ck=0) + F(1, 0, 0))
assert r["state"] == "OPEN" and r["clock"] == 0 and r["expect"] == 0
assert r["deadline"] == 20 and r["delivered"] == [] and r["frames"] == 2
assert r["events"] == [("junk", 2), ("drop", 0, "bad_checksum"),
                       ("hello", 1, 0), ("state", "OPEN")], r["events"]

r = replay(F(2, 0, 0, b"q") + F(9, 0, 0) + F(1, 0, 0))
assert r["state"] == "OPEN" and r["clock"] == 0 and r["expect"] == 0
assert r["deadline"] == 20 and r["illegal"] == 1 and r["frames"] == 3
assert r["events"] == [("illegal", 0, 2, "IDLE"), ("drop", 1, "bad_type"),
                       ("hello", 2, 0), ("state", "OPEN")], r["events"]

assert replay(F(1, 0, 1) + F(2, 0, 2, b"ab") + F(2, 1, 2, b"c") + F(4, 0, 1), True) ==     replay(F(1, 0, 1) + F(2, 0, 2, b"ab") + F(2, 1, 2, b"c") + F(4, 0, 1))

try:
    replay(F(2, 0, 0, b"q") + F(9, 0, 0) + F(1, 0, 0), True)
    raise AssertionError("expected ProtocolError")
except ProtocolError as e:
    assert isinstance(e, ValueError)
    assert e.kind == "illegal" and e.index == 0 and e.events == []

try:
    replay("not bytes")
    raise AssertionError("expected ProtocolError")
except ProtocolError as e:
    assert e.kind == "bad_transcript" and e.index == -1 and e.events == []

print("visible examples OK")
