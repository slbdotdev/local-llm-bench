"""Replay a small framed, stateful byte protocol."""

FLAG = 0x7E
ESC = 0x7D
W = 4
M = 16
T = 20
MAX_PAYLOAD = 8


class ProtocolError(ValueError):
    def __init__(self, kind, index, events):
        super().__init__(kind)
        self.kind = kind
        self.index = index
        self.events = list(events)


def replay(transcript, strict=False):
    if not isinstance(transcript, (bytes, bytearray)):
        raise ProtocolError("bad_transcript", -1, [])

    raw = bytes(transcript)
    events = []
    delivered = []
    buffer = {}
    state = "IDLE"
    clock = 0
    expect = 0
    deadline = None
    illegal_count = 0
    frames = 0
    aborted = False

    def emit(event):
        nonlocal aborted
        name = event[0]
        if strict and name in ("drop", "illegal", "timeout", "abort"):
            if name == "drop":
                kind, index = event[2], event[1]
            elif name == "illegal":
                kind, index = "illegal", event[1]
            elif name == "timeout":
                kind, index = "timeout", -1
            else:
                kind, index = "illegal_limit", -1
            raise ProtocolError(kind, index, events)
        events.append(event)

    def change_state(new_state):
        nonlocal state, deadline
        if state != new_state:
            state = new_state
            emit(("state", new_state))
        if new_state in ("IDLE", "CLOSED"):
            deadline = None

    def ordered_buffer():
        return sorted(buffer, key=lambda seq: (seq - expect) % M)

    def discard_buffer():
        for seq in ordered_buffer():
            emit(("discard", seq))
        buffer.clear()

    def flush_buffer():
        nonlocal expect
        ordered = ordered_buffer()
        for seq in ordered:
            delivered.append(buffer[seq])
            emit(("flush", seq))
        if ordered:
            expect = (ordered[-1] + 1) % M
        buffer.clear()

    def arm():
        nonlocal deadline
        deadline = clock + T

    def process(idx, length, typ, seq, tick, payload):
        nonlocal clock, deadline, expect, illegal_count, aborted
        clock = (clock + (tick % 64))

        if deadline is not None and clock > deadline:
            emit(("timeout", clock))
            change_state("CLOSED")
            discard_buffer()

        if typ not in (1, 2, 3, 4, 5):
            emit(("drop", idx, "bad_type"))
            return

        current = state
        allowed = {
            1: current == "IDLE",
            2: current == "OPEN",
            3: current in ("OPEN", "DRAINING"),
            4: current in ("OPEN", "DRAINING"),
            5: True,
        }
        if typ == 2 and current == "DRAINING":
            emit(("drop", idx, "draining"))
            return
        if not allowed[typ]:
            emit(("illegal", idx, typ, current))
            illegal_count += 1
            if illegal_count == 3:
                emit(("abort", "illegal_limit"))
                change_state("CLOSED")
                aborted = True
            return

        if typ == 5:
            emit(("reset", idx))
            change_state("IDLE")
            expect = 0
            discard_buffer()
            return
        if typ == 1:
            expect = seq % M
            emit(("hello", idx, expect))
            change_state("OPEN")
            arm()
            return
        if typ == 3:
            emit(("ping", idx))
            arm()
            return
        if typ == 4:
            emit(("close", idx))
            if current == "OPEN":
                change_state("DRAINING")
                flush_buffer()
                arm()
            else:
                change_state("CLOSED")
            return

        q = seq % M
        d = (q - expect) % M
        if d == 0:
            delivered.append(payload)
            emit(("deliver", idx, q))
            expect = (expect + 1) % M
            while expect in buffer:
                delivered.append(buffer.pop(expect))
                emit(("flush", expect))
                expect = (expect + 1) % M
            arm()
        elif 1 <= d <= W - 1:
            if q in buffer:
                emit(("dup", idx, q))
            else:
                buffer[q] = payload
                emit(("buf", idx, q))
                arm()
        elif 12 <= d <= 15:
            emit(("dup", idx, q))
        else:
            emit(("drop", idx, "out_of_window"))

    pos = 0
    candidate = 0
    raw_len = len(raw)
    while pos < raw_len and not aborted:
        junk_start = pos
        while pos < raw_len and raw[pos] != FLAG:
            pos += 1
        if pos > junk_start:
            emit(("junk", pos - junk_start))
        if pos >= raw_len:
            break

        idx = candidate
        candidate += 1
        frames = candidate
        pos += 1
        body = []
        truncated = False
        restart_flag = False

        while True:
            if pos >= raw_len:
                emit(("drop", idx, "truncated"))
                truncated = True
                break
            b = raw[pos]
            if b == FLAG:
                emit(("drop", idx, "truncated"))
                restart_flag = True
                break
            if b == ESC:
                pos += 1
                if pos >= raw_len:
                    emit(("drop", idx, "truncated"))
                    truncated = True
                    break
                c = raw[pos]
                if c == FLAG:
                    emit(("drop", idx, "bad_escape"))
                    restart_flag = True
                    break
                body.append(c ^ 0x20)
                pos += 1
            else:
                body.append(b)
                pos += 1

            if len(body) == 1:
                if body[0] > MAX_PAYLOAD:
                    emit(("drop", idx, "bad_length"))
                    break
                target = 5 + body[0]
            if len(body) >= 1 and len(body) == target:
                length = body[0]
                checksum = sum(body[:-1]) & 0xFF
                if body[-1] != checksum:
                    emit(("drop", idx, "bad_checksum"))
                else:
                    process(idx, length, body[1], body[2], body[3], bytes(body[4:-1]))
                break

        if truncated or (restart_flag and pos < raw_len):
            continue

    return {
        "state": state,
        "clock": clock,
        "expect": expect,
        "deadline": deadline,
        "window": [(seq, buffer[seq]) for seq in ordered_buffer()],
        "delivered": delivered,
        "illegal": illegal_count,
        "frames": frames,
        "aborted": bool(aborted),
        "events": events,
    }
