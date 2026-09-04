"""Replay a recorded byte stream of framed protocol messages."""

FLAG = 0x7E
ESC = 0x7D
W = 4
M = 16
T = 20
MAX_PAYLOAD = 8
ILLEGAL_LIMIT = 3


class ProtocolError(ValueError):
    def __init__(self, kind, index, events):
        super().__init__(kind)
        self.kind = kind
        self.index = index
        self.events = events


def replay(transcript, strict=False):
    if type(transcript) is not bytes and type(transcript) is not bytearray:
        raise ProtocolError("bad_transcript", -1, [])

    n = len(transcript)
    events = []

    clock = 0
    deadline = None
    state = "IDLE"
    expect = 0
    illegal_count = 0
    aborted = False
    window = {}          # seq -> payload
    delivered = []

    def emit(ev):
        name = ev[0]
        if strict and name in ("drop", "illegal", "timeout", "abort"):
            if name == "drop":
                kind = ev[2]
                index = ev[1]
            elif name == "illegal":
                kind = "illegal"
                index = ev[1]
            elif name == "timeout":
                kind = "timeout"
                index = -1
            else:  # abort
                kind = "illegal_limit"
                index = -1
            raise ProtocolError(kind, index, list(events))
        events.append(ev)

    def ascending_window_order():
        return sorted(window.items(), key=lambda kv: (kv[0] - expect) % M)

    def set_state(new):
        nonlocal state, deadline
        changed = state != new
        state = new
        if new in ("IDLE", "CLOSED"):
            deadline = None
        if changed:
            emit(("state", new))

    def deadline_arm():
        nonlocal deadline
        deadline = clock + T

    def discard_buffer():
        nonlocal window
        for seq, _payload in ascending_window_order():
            emit(("discard", seq))
        window = {}

    def flush_buffer():
        nonlocal expect, window
        ordered = ascending_window_order()
        last_seq = None
        for seq, payload in ordered:
            delivered.append(payload)
            emit(("flush", seq))
            last_seq = seq
        if ordered:
            expect = (last_seq + 1) % M
        window = {}

    def do_illegal(cur_idx, TYPE, st):
        nonlocal illegal_count, aborted
        emit(("illegal", cur_idx, TYPE, st))
        illegal_count += 1
        if illegal_count >= ILLEGAL_LIMIT:
            emit(("abort", "illegal_limit"))
            set_state("CLOSED")
            aborted = True

    def handle_data(cur_idx, SEQ, payload):
        nonlocal expect, window
        q = SEQ % M
        d = (q - expect) % M
        if d == 0:
            delivered.append(payload)
            emit(("deliver", cur_idx, q))
            expect = (expect + 1) % M
            while expect in window:
                p = window.pop(expect)
                delivered.append(p)
                emit(("flush", expect))
                expect = (expect + 1) % M
            deadline_arm()
        elif 1 <= d <= 3:
            if q in window:
                emit(("dup", cur_idx, q))
            else:
                window[q] = payload
                emit(("buf", cur_idx, q))
                deadline_arm()
        elif 12 <= d <= 15:
            emit(("dup", cur_idx, q))
        else:  # 4..11
            emit(("drop", cur_idx, "out_of_window"))

    def process_frame(cur_idx, TYPE, SEQ, TICK, payload):
        nonlocal clock, expect
        # B1 clock
        clock += TICK % 64
        # B2 timeout
        if deadline is not None and clock > deadline:
            emit(("timeout", clock))
            set_state("CLOSED")
            discard_buffer()
        # B3 type
        if TYPE not in (1, 2, 3, 4, 5):
            emit(("drop", cur_idx, "bad_type"))
            return False
        st = state
        if TYPE == 1:  # HELLO
            if st == "IDLE":
                expect = SEQ % M
                emit(("hello", cur_idx, expect))
                set_state("OPEN")
                deadline_arm()
            else:
                do_illegal(cur_idx, TYPE, st)
                if aborted:
                    return True
            return False
        if TYPE == 2:  # DATA
            if st == "OPEN":
                handle_data(cur_idx, SEQ, payload)
            elif st == "DRAINING":
                emit(("drop", cur_idx, "draining"))
            else:
                do_illegal(cur_idx, TYPE, st)
                if aborted:
                    return True
            return False
        if TYPE == 3:  # PING
            if st in ("OPEN", "DRAINING"):
                emit(("ping", cur_idx))
                deadline_arm()
            else:
                do_illegal(cur_idx, TYPE, st)
                if aborted:
                    return True
            return False
        if TYPE == 4:  # CLOSE
            if st == "OPEN":
                emit(("close", cur_idx))
                set_state("DRAINING")
                flush_buffer()
                deadline_arm()
            elif st == "DRAINING":
                emit(("close", cur_idx))
                set_state("CLOSED")
            else:
                do_illegal(cur_idx, TYPE, st)
                if aborted:
                    return True
            return False
        # TYPE == 5 RESET, accepted in every state
        emit(("reset", cur_idx))
        set_state("IDLE")
        expect = 0
        discard_buffer()
        return False

    def read_body(pos, cur_idx):
        def read_one(p):
            if p >= n:
                return ('truncated', None, p)
            b = transcript[p]
            if b == FLAG:
                return ('flag', None, p)
            if b == ESC:
                if p + 1 >= n:
                    return ('truncated', None, p)
                c = transcript[p + 1]
                if c == FLAG:
                    return ('bad_escape', None, p + 1)
                return ('ok', c ^ 0x20, p + 2)
            return ('ok', b, p + 1)

        status, val, pos = read_one(pos)
        if status == 'truncated':
            emit(("drop", cur_idx, "truncated"))
            return ('end', None)
        if status == 'flag':
            emit(("drop", cur_idx, "truncated"))
            return ('resume_flag', pos)
        if status == 'bad_escape':
            emit(("drop", cur_idx, "bad_escape"))
            return ('resume_flag', pos)
        LEN = val
        if LEN > MAX_PAYLOAD:
            emit(("drop", cur_idx, "bad_length"))
            return ('hunt', pos)

        remaining = 4 + LEN
        vals = []
        for _ in range(remaining):
            status, val, pos = read_one(pos)
            if status == 'truncated':
                emit(("drop", cur_idx, "truncated"))
                return ('end', None)
            if status == 'flag':
                emit(("drop", cur_idx, "truncated"))
                return ('resume_flag', pos)
            if status == 'bad_escape':
                emit(("drop", cur_idx, "bad_escape"))
                return ('resume_flag', pos)
            vals.append(val)

        TYPE, SEQ, TICK = vals[0], vals[1], vals[2]
        payload_vals = vals[3:3 + LEN]
        payload = bytes(payload_vals)
        CK = vals[3 + LEN]
        expected_ck = (LEN + TYPE + SEQ + TICK + sum(payload_vals)) % 256
        if CK != expected_ck:
            emit(("drop", cur_idx, "bad_checksum"))
            return ('hunt', pos)
        return ('accepted', LEN, TYPE, SEQ, TICK, payload, pos)

    pos = 0
    idx = 0
    while True:
        start = pos
        while pos < n and transcript[pos] != FLAG:
            pos += 1
        k = pos - start
        if k >= 1:
            emit(("junk", k))
        if pos >= n:
            break
        pos += 1  # consume FLAG
        cur_idx = idx
        idx += 1

        result = read_body(pos, cur_idx)
        tag = result[0]
        if tag == 'end':
            break
        if tag == 'resume_flag':
            pos = result[1]
            continue
        if tag == 'hunt':
            pos = result[1]
            continue

        _, LEN, TYPE, SEQ, TICK, payload, pos = result
        should_stop = process_frame(cur_idx, TYPE, SEQ, TICK, payload)
        if should_stop:
            break

    window_list = ascending_window_order()

    return {
        "state": state,
        "clock": clock,
        "expect": expect,
        "deadline": deadline,
        "window": window_list,
        "delivered": list(delivered),
        "illegal": illegal_count,
        "frames": idx,
        "aborted": aborted,
        "events": list(events),
    }
