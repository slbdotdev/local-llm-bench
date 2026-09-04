import stateful as S

FLAG = 0x7E
ESC = 0x7D

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

def check(cond, msg):
    if not cond:
        raise AssertionError(msg)

# Example 1
t = F(1,0,1,b"") + F(2,0,2,b"ab") + F(2,1,2,b"c") + F(4,0,1,b"")
r = S.replay(t)
check(r["state"] == "DRAINING", r["state"])
check(r["clock"] == 6, r["clock"])
check(r["expect"] == 2, r["expect"])
check(r["deadline"] == 26, r["deadline"])
check(r["window"] == [], r["window"])
check(r["delivered"] == [b"ab", b"c"], r["delivered"])
check(r["illegal"] == 0, r["illegal"])
check(r["frames"] == 4, r["frames"])
check(r["aborted"] is False, r["aborted"])
expected_events = [("hello",0,0), ("state","OPEN"), ("deliver",1,0), ("deliver",2,1), ("close",3), ("state","DRAINING")]
check(r["events"] == expected_events, r["events"])
print("example1 ok")

# Example 1 strict
r2 = S.replay(t, True)
check(r2 == r, "strict example1 mismatch")
print("example1 strict ok")

# Example 2
t2 = F(1,3,0,b"") + F(2,4,1,b"x") + F(2,3,1,b"w")
r = S.replay(t2)
check(r["state"] == "OPEN", r["state"])
check(r["clock"] == 2, r["clock"])
check(r["expect"] == 5, r["expect"])
check(r["deadline"] == 22, r["deadline"])
check(r["window"] == [], r["window"])
check(r["delivered"] == [b"w", b"x"], r["delivered"])
check(r["frames"] == 3, r["frames"])
expected2 = [("hello",0,3), ("state","OPEN"), ("buf",1,4), ("deliver",2,3), ("flush",4)]
check(r["events"] == expected2, r["events"])
print("example2 ok")

# Example 3
frame_z = bytearray(F(2,0,0,b"z"))
# find checksum byte position: it's the last byte before escaping complexity; easier: build manually
body = bytes([1,2,0,0]) + b"z"
ck = sum(body) % 256
body_bad = body + bytes([0])  # replaced checksum with 0 (assuming real ck != 0)
def escape(body):
    out = bytearray([FLAG])
    for b in body:
        if b == FLAG or b == ESC:
            out.append(ESC); out.append(b^0x20)
        else:
            out.append(b)
    return bytes(out)
frame_bad_ck = escape(body_bad)
t3 = b"\x01\x02" + frame_bad_ck + F(1,0,0,b"")
r = S.replay(t3)
check(r["state"] == "OPEN", r["state"])
check(r["clock"] == 0, r["clock"])
check(r["expect"] == 0, r["expect"])
check(r["deadline"] == 20, r["deadline"])
check(r["delivered"] == [], r["delivered"])
check(r["frames"] == 2, r["frames"])
expected3 = [("junk",2), ("drop",0,"bad_checksum"), ("hello",1,0), ("state","OPEN")]
check(r["events"] == expected3, r["events"])
print("example3 ok")

# Example 4
t4 = F(2,0,0,b"q") + F(9,0,0,b"") + F(1,0,0,b"")
r = S.replay(t4)
check(r["state"] == "OPEN", r["state"])
check(r["clock"] == 0, r["clock"])
check(r["expect"] == 0, r["expect"])
check(r["deadline"] == 20, r["deadline"])
check(r["illegal"] == 1, r["illegal"])
check(r["frames"] == 3, r["frames"])
expected4 = [("illegal",0,2,"IDLE"), ("drop",1,"bad_type"), ("hello",2,0), ("state","OPEN")]
check(r["events"] == expected4, r["events"])
print("example4 ok")

# Example strict 4
try:
    S.replay(t4, True)
    raise AssertionError("expected raise")
except S.ProtocolError as e:
    check(e.kind == "illegal", e.kind)
    check(e.index == 0, e.index)
    check(e.events == [], e.events)
print("example4 strict ok")

# bad transcript
for bad in ["abc", None, memoryview(b"abc"), [1,2,3], 123, 1.5]:
    try:
        S.replay(bad)
        raise AssertionError("expected raise for " + repr(bad))
    except S.ProtocolError as e:
        check(e.kind == "bad_transcript", e.kind)
        check(e.index == -1, e.index)
        check(e.events == [], e.events)
print("bad_transcript ok")

# bool should NOT be bytes/bytearray -> also rejected
try:
    S.replay(True)
    raise AssertionError("expected raise for bool")
except S.ProtocolError as e:
    check(e.kind == "bad_transcript", e.kind)
print("bool rejected ok")

# empty transcript
r = S.replay(b"")
check(r["state"] == "IDLE", r["state"])
check(r["frames"] == 0, r["frames"])
check(r["events"] == [], r["events"])
print("empty ok")

# illegal limit -> abort
t5 = F(2,0,0,b"") + F(2,0,0,b"") + F(2,0,0,b"") + F(1,0,0,b"")
r = S.replay(t5)
check(r["aborted"] is True, r["aborted"])
check(r["state"] == "CLOSED", r["state"])
check(r["illegal"] == 3, r["illegal"])
check(r["frames"] == 3, r["frames"])  # stopped, 4th never parsed
print(r["events"])
print("abort ok")

# RESET always accepted, disarms timer, discards buffer
t6 = F(1,0,0,b"") + F(2,1,0,b"x") + F(2,2,0,b"y") + F(5,0,0,b"")
r = S.replay(t6)
check(r["state"] == "IDLE", r["state"])
check(r["expect"] == 0, r["expect"])
check(r["deadline"] is None, r["deadline"])
check(r["window"] == [], r["window"])
print(r["events"])
print("reset ok")

# truncated frame at end
t7 = bytes([FLAG, 0x05, 0x01])
r = S.replay(t7)
check(r["events"] == [("drop",0,"truncated")], r["events"])
check(r["frames"] == 1, r["frames"])
print("truncated ok")

# bad_length
t8 = bytes([FLAG, 0x09]) + b"junkjunk" + bytes([FLAG]) + F(1,0,0,b"")[1:]
r = S.replay(t8)
print(r["events"])
check(r["events"][0] == ("drop",0,"bad_length"), r["events"][0])
print("bad_length ok")

print("ALL OK")
