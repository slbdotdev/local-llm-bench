FLAG = 0x7E
ESC = 0x7D
W = 4
M = 16
T = 20
MAX_PAYLOAD = 8


class ProtocolError(ValueError):
    def __init__(self, kind, index, events):
        self.kind = kind
        self.index = index
        self.events = events
        super().__init__(kind)


def replay(transcript, strict=False):
    if not isinstance(transcript, (bytes, bytearray)):
        raise ProtocolError("bad_transcript", -1, [])

    events = []
    delivered = []
    window = {}
    state = "IDLE"
    clock = 0
    expect = 0
    deadline = None
    illegal_count = 0
    frames = 0
    aborted = False
    raw = transcript

    def emit(event):
        nonlocal events
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
            raise ProtocolError(kind, index, list(events))
        events.append(event)

    def state_to(new_state):
        nonlocal state, deadline
        if state != new_state:
            state = new_state
            emit(("state", new_state))
        if new_state in ("IDLE", "CLOSED"):
            deadline = None

    def ordered_window():
        return sorted(window, key=lambda seq: (seq - expect) % M)

    def discard_buffer():
        for seq in ordered_window():
            emit(("discard", seq))
        window.clear()

    def arm():
        nonlocal deadline
        deadline = clock + T

    def flush_buffer():
        nonlocal expect
        seqs = ordered_window()
        for seq in seqs:
            delivered.append(window[seq])
            emit(("flush", seq))
        if seqs:
            expect = (seqs[-1] + 1) % M
        window.clear()

    def process(idx, length, typ, seq, tick, payload):
        nonlocal clock, expect, deadline, illegal_count, aborted
        clock += tick % 64

        if deadline is not None and clock > deadline:
            emit(("timeout", clock))
            state_to("CLOSED")
            discard_buffer()

        if typ not in (1, 2, 3, 4, 5):
            emit(("drop", idx, "bad_type"))
            return

        if typ == 1:
            allowed = state == "IDLE"
        elif typ == 2:
            allowed = state in ("OPEN", "DRAINING")
        elif typ in (3, 4):
            allowed = state in ("OPEN", "DRAINING")
        else:
            allowed = True

        if typ == 2 and state == "DRAINING":
            emit(("drop", idx, "draining"))
            return
        if not allowed:
            emit(("illegal", idx, typ, state))
            illegal_count += 1
            if illegal_count == 3:
                emit(("abort", "illegal_limit"))
                state_to("CLOSED")
                aborted = True
            return

        if typ == 5:
            emit(("reset", idx))
            state_to("IDLE")
            expect = 0
            discard_buffer()
            return
        if typ == 1:
            expect = seq % M
            emit(("hello", idx, expect))
            state_to("OPEN")
            arm()
            return
        if typ == 3:
            emit(("ping", idx))
            arm()
            return
        if typ == 4:
            emit(("close", idx))
            if state == "OPEN":
                state_to("DRAINING")
                flush_buffer()
                arm()
            else:
                state_to("CLOSED")
            return

        q = seq % M
        d = (q - expect) % M
        if d == 0:
            delivered.append(payload)
            emit(("deliver", idx, q))
            expect = (expect + 1) % M
            while expect in window:
                delivered.append(window.pop(expect))
                emit(("flush", expect))
                expect = (expect + 1) % M
            arm()
        elif 1 <= d <= W - 1:
            if q in window:
                emit(("dup", idx, q))
            else:
                window[q] = payload
                emit(("buf", idx, q))
                arm()
        elif M - W <= d <= M - 1:
            emit(("dup", idx, q))
        else:
            emit(("drop", idx, "out_of_window"))

    try:
        pos = 0
        n = len(raw)
        while pos < n and not aborted:
            junk_start = pos
            while pos < n and raw[pos] != FLAG:
                pos += 1
            if pos > junk_start:
                emit(("junk", pos - junk_start))
            if pos >= n:
                break

            idx = frames
            frames += 1
            pos += 1

            def read_unescaped():
                nonlocal pos
                if pos >= n:
                    return None, "truncated"
                b = raw[pos]
                if b == FLAG:
                    return None, "truncated"
                if b == ESC:
                    pos += 1
                    if pos >= n:
                        return None, "truncated"
                    c = raw[pos]
                    if c == FLAG:
                        return None, "bad_escape"
                    pos += 1
                    return c ^ 0x20, None
                pos += 1
                return b, None

            length, reason = read_unescaped()
            if reason is not None:
                emit(("drop", idx, reason))
                if reason == "truncated":
                    break
                continue
            if length > MAX_PAYLOAD:
                emit(("drop", idx, "bad_length"))
                continue

            body = [length]
            failed = False
            for _ in range(4 + length):
                value, reason = read_unescaped()
                if reason is not None:
                    emit(("drop", idx, reason))
                    failed = True
                    if reason == "truncated":
                        pos = n
                    break
                body.append(value)
            if failed:
                if reason == "truncated":
                    break
                continue

            checksum = body[-1]
            if checksum != (sum(body[:-1]) & 0xFF):
                emit(("drop", idx, "bad_checksum"))
                continue
            typ, seq, tick = body[1], body[2], body[3]
            payload = bytes(body[4:-1])
            process(idx, length, typ, seq, tick, payload)

        return {
            "state": state,
            "clock": clock,
            "expect": expect,
            "deadline": deadline,
            "window": [(seq, window[seq]) for seq in ordered_window()],
            "delivered": delivered,
            "illegal": illegal_count,
            "frames": frames,
            "aborted": bool(aborted),
            "events": events,
        }
    except ProtocolError:
        raise
    except Exception as exc:
        raise ProtocolError("malformed", -1, list(events)) from exc
