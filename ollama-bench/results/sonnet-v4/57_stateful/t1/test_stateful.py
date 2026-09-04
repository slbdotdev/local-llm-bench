from stateful import replay, ProtocolError, FLAG, ESC

def F(ty, seq, tick, payload):
    body = bytes([len(payload), ty, seq, tick]) + payload
    ck = sum(body) % 256
    body = body + bytes([ck])
    out = bytearray([FLAG])
    for b in body:
        if b == FLAG or b == ESC:
            out.append(ESC)
            out.append(b ^ 0x20)
        else:
            out.append(b)
    return bytes(out)

# Example 1
t = F(1,0,1,b"") + F(2,0,2,b"ab") + F(2,1,2,b"c") + F(4,0,1,b"")
expected_bytes = bytes.fromhex("7E0001000102" "7E020200026162C9" "7E010201026369" "7E0004000105")
assert t == expected_bytes, (t.hex(), expected_bytes.hex())
r = replay(t)
assert r["state"] == "DRAINING"
assert r["clock"] == 6
assert r["expect"] == 2
assert r["deadline"] == 26
assert r["window"] == []
assert r["delivered"] == [b"ab", b"c"]
assert r["illegal"] == 0
assert r["frames"] == 4
assert r["aborted"] is False
assert r["events"] == [("hello",0,0), ("state","OPEN"), ("deliver",1,0), ("deliver",2,1), ("close",3), ("state","DRAINING")]
print("example1 ok")

r2 = replay(t, True)
assert r2 == r
print("example1 strict ok")

# Example 2
t2 = F(1,3,0,b"") + F(2,4,1,b"x") + F(2,3,1,b"w")
r = replay(t2)
assert r["state"] == "OPEN"
assert r["clock"] == 2
assert r["expect"] == 5
assert r["deadline"] == 22
assert r["window"] == []
assert r["delivered"] == [b"w", b"x"]
assert r["frames"] == 3
assert r["events"] == [("hello",0,3), ("state","OPEN"), ("buf",1,4), ("deliver",2,3), ("flush",4)]
print("example2 ok")

# Example 3
frame_z = bytearray(F(2,0,0,b"z"))
# find checksum byte position -- last byte of frame (no escaping needed here)
frame_z[-1] = 0
t3 = b"\x01\x02" + bytes(frame_z) + F(1,0,0,b"")
r = replay(t3)
assert r["state"] == "OPEN"
assert r["clock"] == 0
assert r["expect"] == 0
assert r["deadline"] == 20
assert r["delivered"] == []
assert r["frames"] == 2
assert r["events"] == [("junk",2), ("drop",0,"bad_checksum"), ("hello",1,0), ("state","OPEN")]
print("example3 ok")

# Example 4
t4 = F(2,0,0,b"q") + F(9,0,0,b"") + F(1,0,0,b"")
r = replay(t4)
assert r["state"] == "OPEN"
assert r["clock"] == 0
assert r["expect"] == 0
assert r["deadline"] == 20
assert r["illegal"] == 1
assert r["frames"] == 3
assert r["events"] == [("illegal",0,2,"IDLE"), ("drop",1,"bad_type"), ("hello",2,0), ("state","OPEN")]
print("example4 ok")

try:
    replay(t4, True)
    assert False, "expected raise"
except ProtocolError as e:
    assert e.kind == "illegal"
    assert e.index == 0
    assert e.events == []
    print("example4 strict ok")

# bad transcript
for bad in ["abc", None, [1,2,3], memoryview(b"abc"), 5, 3.5]:
    try:
        replay(bad)
        assert False, f"expected raise for {bad!r}"
    except ProtocolError as e:
        assert e.kind == "bad_transcript"
        assert e.index == -1
        assert e.events == []
print("bad_transcript ok")

# escape example check: third frame's checksum byte is 0x7E
f3 = F(2,3,1,b"w")
assert f3 == bytes.fromhex("7e01020301777d5e")
print("escape check ok")

# abort test: three illegal frames in a row from IDLE
tabort = F(2,0,0,b"") + F(2,0,0,b"") + F(2,0,0,b"") + F(1,0,0,b"")
r = replay(tabort)
assert r["aborted"] is True
assert r["state"] == "CLOSED"
assert r["illegal"] == 3
assert r["frames"] == 3  # 4th frame never parsed
assert ("abort", "illegal_limit") in r["events"]
assert r["events"][-2:] == [("abort", "illegal_limit"), ("state", "CLOSED")]
print("abort ok")

# strict abort unreachable -> raises on first illegal
try:
    replay(tabort, True)
    assert False
except ProtocolError as e:
    assert e.kind == "illegal"
    assert e.index == 0
print("abort strict ok")

# truncated frame test
trunc = bytes([FLAG, 2, 1, 0])  # LEN=2 but stream ends before enough bytes
r = replay(trunc)
assert r["events"] == [("drop", 0, "truncated")]
assert r["frames"] == 1
print("truncated ok")

# bad_length test
badlen = bytes([FLAG, 9])  # LEN=9 > 8
r = replay(badlen + bytes([FLAG]))  # after bad_length, hunt again, no more FLAG found before end -> actually FLAG starts new candidate but stream ends
r2 = replay(badlen)
assert r2["events"][0] == ("drop", 0, "bad_length")
print("bad_length ok")

# timeout test: HELLO then wait past deadline then DATA
# deadline = clock+20 after hello with tick0 => 20; next frame tick that pushes clock to 21 triggers timeout
thello = F(1,0,0,b"")
tdata_late = F(2,0,21,b"x")
r = replay(thello + tdata_late)
assert r["events"][0] == ("hello",0,0)
assert r["events"][1] == ("state","OPEN")
# clock after 2nd frame = 21, deadline=20, 21>20 timeout fires
assert ("timeout", 21) in r["events"]
assert r["state"] in ("OPEN","CLOSED")
print("timeout test events:", r["events"])

print("ALL OK")
