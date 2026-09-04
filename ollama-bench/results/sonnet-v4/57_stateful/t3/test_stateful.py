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


def check(name, cond):
    status = "OK" if cond else "FAIL"
    print(f"[{status}] {name}")
    if not cond:
        raise SystemExit(1)


# Example 1
t = F(1,0,1,b"") + F(2,0,2,b"ab") + F(2,1,2,b"c") + F(4,0,1,b"")
expected_bytes = bytes.fromhex("7E0001000102" "7E020200026162C9" "7E01020102636900".replace("00","")[:0]) # placeholder unused
r = replay(t)
check("ex1 state", r["state"]=="DRAINING")
check("ex1 clock", r["clock"]==6)
check("ex1 expect", r["expect"]==2)
check("ex1 deadline", r["deadline"]==26)
check("ex1 window", r["window"]==[])
check("ex1 delivered", r["delivered"]==[b"ab", b"c"])
check("ex1 illegal", r["illegal"]==0)
check("ex1 frames", r["frames"]==4)
check("ex1 aborted", r["aborted"] is False)
check("ex1 events", r["events"]==[("hello",0,0), ("state","OPEN"), ("deliver",1,0), ("deliver",2,1), ("close",3), ("state","DRAINING")])

# Example 2
t2 = F(1,3,0,b"") + F(2,4,1,b"x") + F(2,3,1,b"w")
r2 = replay(t2)
check("ex2 state", r2["state"]=="OPEN")
check("ex2 clock", r2["clock"]==2)
check("ex2 expect", r2["expect"]==5)
check("ex2 deadline", r2["deadline"]==22)
check("ex2 window", r2["window"]==[])
check("ex2 delivered", r2["delivered"]==[b"w", b"x"])
check("ex2 frames", r2["frames"]==3)
check("ex2 events", r2["events"]==[("hello",0,3), ("state","OPEN"), ("buf",1,4), ("deliver",2,3), ("flush",4)])

# Example 3
frame_z = bytearray(F(2,0,0,b"z"))
# find checksum byte position and zero it -- last byte of unescaped body is CK,
# but escaping could affect length; since no escapes expected here, last byte is CK.
frame_z[-1] = 0
t3 = b"\x01\x02" + bytes(frame_z) + F(1,0,0,b"")
r3 = replay(t3)
check("ex3 state", r3["state"]=="OPEN")
check("ex3 clock", r3["clock"]==0)
check("ex3 expect", r3["expect"]==0)
check("ex3 deadline", r3["deadline"]==20)
check("ex3 delivered", r3["delivered"]==[])
check("ex3 frames", r3["frames"]==2)
check("ex3 events", r3["events"]==[("junk",2), ("drop",0,"bad_checksum"), ("hello",1,0), ("state","OPEN")])

# Example 4
t4 = F(2,0,0,b"q") + F(9,0,0,b"") + F(1,0,0,b"")
r4 = replay(t4)
check("ex4 state", r4["state"]=="OPEN")
check("ex4 clock", r4["clock"]==0)
check("ex4 expect", r4["expect"]==0)
check("ex4 deadline", r4["deadline"]==20)
check("ex4 illegal", r4["illegal"]==1)
check("ex4 frames", r4["frames"]==3)
check("ex4 events", r4["events"]==[("illegal",0,2,"IDLE"), ("drop",1,"bad_type"), ("hello",2,0), ("state","OPEN")])

# Strict examples
r5 = replay(t, True)
check("strict ex1 same", r5 == r)

try:
    replay(t4, True)
    check("strict ex4 raised", False)
except ProtocolError as e:
    check("strict ex4 kind", e.kind == "illegal")
    check("strict ex4 index", e.index == 0)
    check("strict ex4 events", e.events == [])

# bad_transcript
for bad in ["abc", None, [1,2,3], memoryview(b"abc"), 123]:
    try:
        replay(bad)
        check(f"bad_transcript {bad!r} raised", False)
    except ProtocolError as e:
        check(f"bad_transcript {bad!r} kind", e.kind == "bad_transcript")
        check(f"bad_transcript {bad!r} index", e.index == -1)
        check(f"bad_transcript {bad!r} events", e.events == [])
    except TypeError:
        check(f"bad_transcript {bad!r} should not raise TypeError", False)

# bytearray accepted
r6 = replay(bytearray(t))
check("bytearray accepted", r6["state"] == "DRAINING")

# empty transcript
r7 = replay(b"")
check("empty transcript", r7 == {
    "state": "IDLE", "clock": 0, "expect": 0, "deadline": None,
    "window": [], "delivered": [], "illegal": 0, "frames": 0,
    "aborted": False, "events": []
})

# illegal limit -> abort, stop entire replay
# 3 illegal frames in a row (DATA while IDLE), then more bytes that should not be parsed
t8 = F(2,0,0,b"x") + F(2,0,0,b"x") + F(2,0,0,b"x") + F(1,0,0,b"")
r8 = replay(t8)
check("abort state", r8["state"] == "CLOSED")
check("abort aborted", r8["aborted"] is True)
check("abort frames", r8["frames"] == 3)  # 4th frame never parsed
check("abort illegal", r8["illegal"] == 3)
check("abort events", r8["events"] == [
    ("illegal",0,2,"IDLE"),
    ("illegal",1,2,"IDLE"),
    ("illegal",2,2,"IDLE"),
    ("abort","illegal_limit"), ("state","CLOSED"),
])

# timeout scenario: HELLO arms deadline=20, then PING with big tick to exceed
t9 = F(1,0,0,b"") + F(3,0,25,b"")
r9 = replay(t9)
check("timeout events include timeout", any(e[0]=="timeout" for e in r9["events"]))
check("timeout state closed", r9["state"] == "CLOSED")

# out of window drop test: expect=0, seq mod16 = 8 -> d=8 -> out_of_window
t10 = F(1,0,0,b"") + F(2,8,0,b"")
r10 = replay(t10)
check("out_of_window drop", ("drop",1,"out_of_window") in r10["events"])

# RESET resets and discards buffer
t11 = F(1,0,0,b"") + F(2,1,0,b"a") + F(5,0,0,b"")
r11 = replay(t11)
check("reset state", r11["state"] == "IDLE")
check("reset expect", r11["expect"] == 0)
check("reset discard event", ("discard",1) in r11["events"])

print("ALL TESTS PASSED")
