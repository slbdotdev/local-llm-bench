"""Replay a recorded byte stream of framed protocol messages."""

FLAG = 0x7E
ESC = 0x7D
W = 4
M = 16
T = 20
MAXLEN = 8
ILLEGAL_LIMIT = 3


class ProtocolError(ValueError):
    def __init__(self, kind, index, events):
        super().__init__(kind)
        self.kind = kind
        self.index = index
        self.events = events


_RAISING_KINDS = ("drop", "illegal", "timeout", "abort")


class _Session:
    def __init__(self, strict):
        self.strict = strict
        self.events = []
        self.state = "IDLE"
        self.clock = 0
        self.expect = 0
        self.deadline = None
        self.buffer = {}
        self.delivered = []
        self.illegal = 0
        self.aborted = False

    def emit(self, ev):
        if self.strict and ev[0] in _RAISING_KINDS:
            if ev[0] == "drop":
                kind = ev[2]
                index = ev[1]
            elif ev[0] == "illegal":
                kind = "illegal"
                index = ev[1]
            elif ev[0] == "timeout":
                kind = "timeout"
                index = -1
            else:  # abort
                kind = "illegal_limit"
                index = -1
            raise ProtocolError(kind, index, list(self.events))
        self.events.append(ev)

    def window_order(self):
        expect = self.expect
        return sorted(self.buffer.keys(), key=lambda s: (s - expect) % 16)

    def set_state(self, new):
        changed = self.state != new
        self.state = new
        if changed:
            self.emit(("state", new))
        if new in ("IDLE", "CLOSED"):
            self.deadline = None

    def discard_buffer(self):
        for seq in self.window_order():
            self.emit(("discard", seq))
        self.buffer.clear()

    def flush_all(self):
        order = self.window_order()
        last_seq = None
        for seq in order:
            payload = self.buffer.pop(seq)
            self.delivered.append(payload)
            self.emit(("flush", seq))
            last_seq = seq
        if last_seq is not None:
            self.expect = (last_seq + 1) % 16

    def illegal_frame(self, idx, TYPE, st):
        self.emit(("illegal", idx, TYPE, st))
        self.illegal += 1
        if self.illegal >= ILLEGAL_LIMIT:
            self.emit(("abort", "illegal_limit"))
            self.set_state("CLOSED")
            self.aborted = True
            return True
        return False

    def process_data(self, idx, SEQ):
        q = SEQ % 16
        d = (q - self.expect) % 16
        if d == 0:
            payload = self._pending_payload
            self.delivered.append(payload)
            self.emit(("deliver", idx, q))
            self.expect = (self.expect + 1) % 16
            while self.expect in self.buffer:
                p = self.buffer.pop(self.expect)
                self.delivered.append(p)
                self.emit(("flush", self.expect))
                self.expect = (self.expect + 1) % 16
            self.deadline = self.clock + T
        elif 1 <= d <= 3:
            if q in self.buffer:
                self.emit(("dup", idx, q))
            else:
                self.buffer[q] = self._pending_payload
                self.emit(("buf", idx, q))
                self.deadline = self.clock + T
        elif 12 <= d <= 15:
            self.emit(("dup", idx, q))
        else:
            self.emit(("drop", idx, "out_of_window"))
        return False

    def process_frame(self, idx, TYPE, SEQ, TICK, payload):
        # B1
        self.clock = self.clock + (TICK % 64)
        # B2
        if self.deadline is not None and self.clock > self.deadline:
            self.emit(("timeout", self.clock))
            self.set_state("CLOSED")
            self.discard_buffer()
        # B3
        if TYPE not in (1, 2, 3, 4, 5):
            self.emit(("drop", idx, "bad_type"))
            return False
        st = self.state
        if TYPE == 1:  # HELLO
            if st == "IDLE":
                self.expect = SEQ % 16
                self.emit(("hello", idx, self.expect))
                self.set_state("OPEN")
                self.deadline = self.clock + T
            else:
                return self.illegal_frame(idx, TYPE, st)
        elif TYPE == 2:  # DATA
            if st == "OPEN":
                self._pending_payload = payload
                return self.process_data(idx, SEQ)
            elif st == "DRAINING":
                self.emit(("drop", idx, "draining"))
            else:
                return self.illegal_frame(idx, TYPE, st)
        elif TYPE == 3:  # PING
            if st in ("OPEN", "DRAINING"):
                self.emit(("ping", idx))
                self.deadline = self.clock + T
            else:
                return self.illegal_frame(idx, TYPE, st)
        elif TYPE == 4:  # CLOSE
            if st == "OPEN":
                self.emit(("close", idx))
                self.set_state("DRAINING")
                self.flush_all()
                self.deadline = self.clock + T
            elif st == "DRAINING":
                self.emit(("close", idx))
                self.set_state("CLOSED")
            else:
                return self.illegal_frame(idx, TYPE, st)
        else:  # TYPE == 5, RESET
            self.emit(("reset", idx))
            self.set_state("IDLE")
            self.expect = 0
            self.discard_buffer()
        return False


def _read_byte(data, pos):
    n = len(data)
    if pos >= n:
        return ("eof", None, pos)
    b = data[pos]
    if b == FLAG:
        return ("flaghit", None, pos)
    if b == ESC:
        if pos + 1 >= n:
            return ("esceof", None, pos + 1)
        c = data[pos + 1]
        if c == FLAG:
            return ("badescape", None, pos + 1)
        return ("ok", c ^ 0x20, pos + 2)
    return ("ok", b, pos + 1)


def _read_n_bytes(data, pos, count):
    vals = []
    for _ in range(count):
        status, val, newpos = _read_byte(data, pos)
        if status != "ok":
            return status, vals, newpos
        vals.append(val)
        pos = newpos
    return "ok", vals, pos


def _process_candidate(data, pos, idx):
    status, val, newpos = _read_byte(data, pos)
    if status in ("eof", "esceof"):
        return {"event": ("drop", idx, "truncated"), "resume": "stop", "pos": newpos}
    if status == "flaghit":
        return {"event": ("drop", idx, "truncated"), "resume": "flag", "pos": newpos}
    if status == "badescape":
        return {"event": ("drop", idx, "bad_escape"), "resume": "flag", "pos": newpos}

    LEN = val
    pos = newpos
    if LEN > MAXLEN:
        return {"event": ("drop", idx, "bad_length"), "resume": "hunt", "pos": pos}

    status2, vals, pos2 = _read_n_bytes(data, pos, 4 + LEN)
    if status2 in ("eof", "esceof"):
        return {"event": ("drop", idx, "truncated"), "resume": "stop", "pos": pos2}
    if status2 == "flaghit":
        return {"event": ("drop", idx, "truncated"), "resume": "flag", "pos": pos2}
    if status2 == "badescape":
        return {"event": ("drop", idx, "bad_escape"), "resume": "flag", "pos": pos2}

    TYPE, SEQ, TICK = vals[0], vals[1], vals[2]
    payload_vals = vals[3:3 + LEN]
    CK = vals[3 + LEN]
    checksum = (LEN + TYPE + SEQ + TICK + sum(payload_vals)) % 256
    if CK != checksum:
        return {"event": ("drop", idx, "bad_checksum"), "resume": "hunt", "pos": pos2}

    return {
        "accepted": True,
        "TYPE": TYPE,
        "SEQ": SEQ,
        "TICK": TICK,
        "payload": bytes(payload_vals),
        "pos": pos2,
    }


def replay(transcript, strict=False):
    if not isinstance(transcript, (bytes, bytearray)):
        raise ProtocolError("bad_transcript", -1, [])

    data = bytes(transcript)
    n = len(data)
    sess = _Session(strict)

    pos = 0
    idx = 0
    frames = 0
    mode = "hunt"
    resume_flag_pos = None

    while True:
        if mode == "hunt":
            start = pos
            while pos < n and data[pos] != FLAG:
                pos += 1
            k = pos - start
            if k >= 1:
                sess.emit(("junk", k))
            if pos >= n:
                break
            pos += 1  # consume FLAG
        else:  # mode == "flag"
            pos = resume_flag_pos + 1  # consume that FLAG

        frames += 1
        cur_idx = idx
        idx += 1

        result = _process_candidate(data, pos, cur_idx)

        if "event" in result:
            sess.emit(result["event"])
            resume = result["resume"]
            if resume == "stop":
                break
            elif resume == "hunt":
                pos = result["pos"]
                mode = "hunt"
            else:  # "flag"
                resume_flag_pos = result["pos"]
                mode = "flag"
        else:
            pos = result["pos"]
            abort = sess.process_frame(
                cur_idx, result["TYPE"], result["SEQ"], result["TICK"], result["payload"]
            )
            if abort:
                break
            mode = "hunt"

    window = [(s, sess.buffer[s]) for s in sess.window_order()]

    return {
        "state": sess.state,
        "clock": sess.clock,
        "expect": sess.expect,
        "deadline": sess.deadline,
        "window": window,
        "delivered": list(sess.delivered),
        "illegal": sess.illegal,
        "frames": frames,
        "aborted": sess.aborted,
        "events": list(sess.events),
    }
