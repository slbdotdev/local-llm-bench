"""Replay a recorded byte stream of framed protocol messages.

Standard library only; no struct/binascii/zlib/hashlib/time.
"""

FLAG = 0x7E
ESC = 0x7D
W = 4
M = 16
T = 20
MAX_PAYLOAD = 8
ILLEGAL_LIMIT = 3

_VALID_TYPES = {1: "HELLO", 2: "DATA", 3: "PING", 4: "CLOSE", 5: "RESET"}


class ProtocolError(ValueError):
    def __init__(self, kind, index, events):
        super().__init__(kind)
        self.kind = kind
        self.index = index
        self.events = events


class _ByteTruncated(Exception):
    pass


class _ByteFlag(Exception):
    def __init__(self, pos):
        self.pos = pos


class _ByteBadEscape(Exception):
    def __init__(self, pos):
        self.pos = pos


def replay(transcript, strict=False):
    if not isinstance(transcript, (bytes, bytearray)):
        raise ProtocolError("bad_transcript", -1, [])

    data = bytes(transcript)
    n = len(data)

    events = []
    state = "IDLE"
    clock = 0
    expect = 0
    deadline = None
    buffer = {}          # seq -> payload
    delivered = []
    illegal_count = 0
    aborted = False
    frames_count = 0

    def read_byte(pos):
        if pos >= n:
            raise _ByteTruncated()
        b = data[pos]
        if b == FLAG:
            raise _ByteFlag(pos)
        if b == ESC:
            if pos + 1 >= n:
                raise _ByteTruncated()
            c = data[pos + 1]
            if c == FLAG:
                raise _ByteBadEscape(pos + 1)
            return (c ^ 0x20, pos + 2)
        return (b, pos + 1)

    def drop(kind, idx):
        if strict:
            raise ProtocolError(kind, idx, list(events))
        events.append(("drop", idx, kind))

    def move_to(new_state):
        nonlocal state, deadline
        old = state
        state = new_state
        if new_state in ("IDLE", "CLOSED"):
            deadline = None
        if new_state != old:
            events.append(("state", new_state))

    def arm_timer():
        nonlocal deadline
        deadline = clock + T

    def discard_buffer():
        order = sorted(buffer.keys(), key=lambda s: (s - expect) % M)
        for s in order:
            events.append(("discard", s))
        buffer.clear()

    def flush_buffer():
        nonlocal expect
        if not buffer:
            return None
        order = sorted(buffer.keys(), key=lambda s: (s - expect) % M)
        last = None
        for s in order:
            p = buffer.pop(s)
            delivered.append(p)
            events.append(("flush", s))
            last = s
        return last

    def do_reset(idx):
        nonlocal expect
        events.append(("reset", idx))
        move_to("IDLE")
        expect = 0
        discard_buffer()

    def do_hello(idx, seq):
        nonlocal expect
        expect = seq % M
        events.append(("hello", idx, expect))
        move_to("OPEN")
        arm_timer()

    def do_ping(idx):
        events.append(("ping", idx))
        arm_timer()

    def do_close_open(idx):
        nonlocal expect
        events.append(("close", idx))
        move_to("DRAINING")
        last = flush_buffer()
        if last is not None:
            expect = (last + 1) % M
        arm_timer()

    def do_close_draining(idx):
        events.append(("close", idx))
        move_to("CLOSED")

    def do_illegal(idx, ty, st):
        nonlocal illegal_count, aborted
        if strict:
            raise ProtocolError("illegal", idx, list(events))
        events.append(("illegal", idx, ty, st))
        illegal_count += 1
        if illegal_count >= ILLEGAL_LIMIT:
            events.append(("abort", "illegal_limit"))
            move_to("CLOSED")
            aborted = True
            return True
        return False

    def do_data(idx, seq, payload):
        nonlocal expect
        q = seq % M
        d = (q - expect) % M
        if d == 0:
            delivered.append(payload)
            events.append(("deliver", idx, q))
            expect = (expect + 1) % M
            while expect in buffer:
                p = buffer.pop(expect)
                delivered.append(p)
                events.append(("flush", expect))
                expect = (expect + 1) % M
            arm_timer()
        elif 1 <= d <= 3:
            if q in buffer:
                events.append(("dup", idx, q))
            else:
                buffer[q] = payload
                events.append(("buf", idx, q))
                arm_timer()
        elif 12 <= d <= 15:
            events.append(("dup", idx, q))
        else:
            drop("out_of_window", idx)

    def do_timeout():
        if strict:
            raise ProtocolError("timeout", -1, list(events))
        events.append(("timeout", clock))
        move_to("CLOSED")
        discard_buffer()

    def process_part_b(idx, ty, seq, tick, payload):
        nonlocal clock
        clock += tick % 64
        if deadline is not None and clock > deadline:
            do_timeout()
        if ty not in _VALID_TYPES:
            drop("bad_type", idx)
            return False
        tname = _VALID_TYPES[ty]
        st = state
        if tname == "HELLO":
            if st == "IDLE":
                do_hello(idx, seq)
            else:
                return do_illegal(idx, ty, st)
        elif tname == "DATA":
            if st == "OPEN":
                do_data(idx, seq, payload)
            elif st == "DRAINING":
                drop("draining", idx)
            else:
                return do_illegal(idx, ty, st)
        elif tname == "PING":
            if st in ("OPEN", "DRAINING"):
                do_ping(idx)
            else:
                return do_illegal(idx, ty, st)
        elif tname == "CLOSE":
            if st == "OPEN":
                do_close_open(idx)
            elif st == "DRAINING":
                do_close_draining(idx)
            else:
                return do_illegal(idx, ty, st)
        elif tname == "RESET":
            do_reset(idx)
        return False

    pos = 0
    while True:
        start = pos
        while pos < n and data[pos] != FLAG:
            pos += 1
        k = pos - start
        if k >= 1:
            events.append(("junk", k))
        if pos >= n:
            break
        pos += 1  # consume FLAG
        idx = frames_count
        frames_count += 1

        try:
            length, pos = read_byte(pos)
        except _ByteTruncated:
            drop("truncated", idx)
            break
        except _ByteFlag as e:
            drop("truncated", idx)
            pos = e.pos
            continue
        except _ByteBadEscape as e:
            drop("bad_escape", idx)
            pos = e.pos
            continue

        if length > MAX_PAYLOAD:
            drop("bad_length", idx)
            continue

        need = 4 + length
        body_vals = [length]
        try:
            for _ in range(need):
                val, pos = read_byte(pos)
                body_vals.append(val)
        except _ByteTruncated:
            drop("truncated", idx)
            break
        except _ByteFlag as e:
            drop("truncated", idx)
            pos = e.pos
            continue
        except _ByteBadEscape as e:
            drop("bad_escape", idx)
            pos = e.pos
            continue

        ty = body_vals[1]
        seq = body_vals[2]
        tick = body_vals[3]
        payload = bytes(body_vals[4:4 + length])
        ck = body_vals[4 + length]
        checksum = sum(body_vals[0:4 + length]) % 256

        if ck != checksum:
            drop("bad_checksum", idx)
            continue

        stop = process_part_b(idx, ty, seq, tick, payload)
        if stop:
            break

    window = sorted(buffer.items(), key=lambda kv: (kv[0] - expect) % M)
    window = [(s, p) for s, p in window]

    return {
        "state": state,
        "clock": clock,
        "expect": expect,
        "deadline": deadline,
        "window": window,
        "delivered": delivered,
        "illegal": illegal_count,
        "frames": frames_count,
        "aborted": aborted,
        "events": events,
    }
