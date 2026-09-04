"""Replay the small framed stateful protocol described in TASK.md."""

_FLAG = 0x7E
_ESC = 0x7D
_W = 4
_M = 16
_T = 20
_MAX_LEN = 8


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
    illegal = 0
    frames = 0
    aborted = False

    def emit(event):
        nonlocal events
        if event[0] in ("drop", "illegal", "timeout", "abort") and strict:
            if event[0] == "drop":
                kind, index = event[2], event[1]
            elif event[0] == "illegal":
                kind, index = "illegal", event[1]
            elif event[0] == "timeout":
                kind, index = "timeout", -1
            else:
                kind, index = "illegal_limit", -1
            raise ProtocolError(kind, index, list(events))
        events.append(event)

    def change(new_state):
        nonlocal state, deadline
        if state != new_state:
            state = new_state
            emit(("state", new_state))
        if new_state in ("IDLE", "CLOSED"):
            deadline = None

    def ordered_keys():
        return sorted(window, key=lambda q: (q - expect) % _M)

    def discard():
        for q in ordered_keys():
            emit(("discard", q))
        window.clear()

    def flush():
        nonlocal expect
        keys = ordered_keys()
        for q in keys:
            delivered.append(window[q])
            emit(("flush", q))
        if keys:
            expect = (keys[-1] + 1) % _M
        window.clear()

    def arm():
        nonlocal deadline
        deadline = clock + _T

    data = transcript
    pos = 0
    n = len(data)
    while pos < n:
        skipped = 0
        while pos < n and data[pos] != _FLAG:
            pos += 1
            skipped += 1
        if skipped:
            emit(("junk", skipped))
        if pos >= n:
            break
        pos += 1
        idx = frames
        frames += 1

        body = []
        resume_flag = False
        while True:
            if pos >= n:
                emit(("drop", idx, "truncated"))
                return _result(state, clock, expect, deadline, window, delivered,
                               illegal, frames, aborted, events)
            b = data[pos]
            if b == _FLAG:
                emit(("drop", idx, "truncated"))
                resume_flag = True
                break
            if b == _ESC:
                if pos + 1 >= n:
                    emit(("drop", idx, "truncated"))
                    return _result(state, clock, expect, deadline, window, delivered,
                                   illegal, frames, aborted, events)
                c = data[pos + 1]
                if c == _FLAG:
                    emit(("drop", idx, "bad_escape"))
                    resume_flag = True
                    pos += 1  # leave the FLAG to begin the next candidate
                    break
                body.append(c ^ 0x20)
                pos += 2
            else:
                body.append(b)
                pos += 1

            if len(body) == 1 and body[0] > _MAX_LEN:
                emit(("drop", idx, "bad_length"))
                break
            if body and len(body) == 5 + body[0]:
                break

        if resume_flag:
            continue
        if not body or body[0] > _MAX_LEN or len(body) != 5 + body[0]:
            continue
        length, typ, seq, tick = body[:4]
        payload = bytes(body[4:4 + length])
        checksum = body[-1]
        if checksum != (sum(body[:-1]) & 0xFF):
            emit(("drop", idx, "bad_checksum"))
            continue

        clock += tick % 64
        if deadline is not None and clock > deadline:
            emit(("timeout", clock))
            change("CLOSED")
            discard()

        if typ not in (1, 2, 3, 4, 5):
            emit(("drop", idx, "bad_type"))
            continue

        st = state
        allowed = ((typ == 1 and st == "IDLE") or
                   (typ == 2 and st == "OPEN") or
                   (typ == 3 and st in ("OPEN", "DRAINING")) or
                   (typ == 4 and st in ("OPEN", "DRAINING")) or
                   typ == 5)
        if not allowed:
            emit(("illegal", idx, typ, st))
            illegal += 1
            if illegal >= 3:
                emit(("abort", "illegal_limit"))
                aborted = True
                change("CLOSED")
                break
            continue

        if typ == 5:
            emit(("reset", idx))
            change("IDLE")
            expect = 0
            deadline = None
            discard()
        elif typ == 1:
            expect = seq % _M
            emit(("hello", idx, expect))
            change("OPEN")
            arm()
        elif typ == 3:
            emit(("ping", idx))
            arm()
        elif typ == 4:
            emit(("close", idx))
            if st == "OPEN":
                change("DRAINING")
                flush()
                arm()
            else:
                change("CLOSED")
        else:
            q = seq % _M
            d = (q - expect) % _M
            if d == 0:
                delivered.append(payload)
                emit(("deliver", idx, q))
                expect = (expect + 1) % _M
                while expect in window:
                    delivered.append(window.pop(expect))
                    emit(("flush", expect))
                    expect = (expect + 1) % _M
                arm()
            elif 1 <= d <= 3:
                if q in window:
                    emit(("dup", idx, q))
                else:
                    window[q] = payload
                    emit(("buf", idx, q))
                    arm()
            elif 12 <= d <= 15:
                emit(("dup", idx, q))
            else:
                emit(("drop", idx, "out_of_window"))

    return _result(state, clock, expect, deadline, window, delivered,
                   illegal, frames, aborted, events)


def _result(state, clock, expect, deadline, window, delivered, illegal,
            frames, aborted, events):
    ordered = sorted(window, key=lambda q: (q - expect) % _M)
    return {"state": state, "clock": clock, "expect": expect,
            "deadline": deadline,
            "window": [(q, bytes(window[q])) for q in ordered],
            "delivered": list(delivered), "illegal": illegal,
            "frames": frames, "aborted": bool(aborted), "events": events}
