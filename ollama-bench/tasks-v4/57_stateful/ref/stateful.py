"""Reference: framed-protocol session replay (incremental class + deframer generator)."""

FLAG = 0x7E
ESC = 0x7D
WINDOW = 4
TIMEOUT = 20
MAXPAY = 8
ILLEGAL_LIMIT = 3

TYPES = {1: "HELLO", 2: "DATA", 3: "PING", 4: "CLOSE", 5: "RESET"}
RAISING = ("drop", "illegal", "timeout", "abort")


class ProtocolError(ValueError):
    def __init__(self, kind, index=-1, events=None):
        ValueError.__init__(self, kind)
        self.kind = kind
        self.index = index
        self.events = list(events) if events else []


def _deframe(data):
    """Yield ('junk', n) / ('drop', idx, reason) / ('frame', idx, ty, seq, tick, payload)."""
    n = len(data)

    def rd(i):
        if i >= n:
            return ("eos", 0, n)
        b = data[i]
        if b == FLAG:
            return ("flag", 0, i)
        if b == ESC:
            if i + 1 >= n:
                return ("eos", 0, n)
            c = data[i + 1]
            if c == FLAG:
                return ("badesc", 0, i + 1)
            return ("ok", c ^ 0x20, i + 2)
        return ("ok", b, i + 1)

    i = 0
    idx = 0
    while True:
        start = i
        while i < n and data[i] != FLAG:
            i += 1
        if i > start:
            yield ("junk", i - start)
        if i >= n:
            return
        i += 1
        my = idx
        idx += 1
        vals = []
        broke = None
        need = 1
        while len(vals) < need:
            st, v, i2 = rd(i)
            if st == "ok":
                vals.append(v)
                i = i2
                if len(vals) == 1:
                    if v > MAXPAY:
                        broke = ("bad_length", i2)
                        break
                    need = 5 + v
                continue
            if st == "eos":
                broke = ("truncated", n)
            elif st == "flag":
                broke = ("truncated", i2)
            else:
                broke = ("bad_escape", i2)
            break
        if broke is not None:
            yield ("drop", my, broke[0])
            i = broke[1]
            continue
        ln, ty, seq, tick = vals[0], vals[1], vals[2], vals[3]
        pay = bytes(vals[4:4 + ln])
        ck = vals[4 + ln]
        if ck != (ln + ty + seq + tick + sum(pay)) & 0xFF:
            yield ("drop", my, "bad_checksum")
            continue
        yield ("frame", my, ty, seq, tick, pay)


class _Session(object):
    def __init__(self, strict):
        self.strict = bool(strict)
        self.state = "IDLE"
        self.clock = 0
        self.expect = 0
        self.deadline = None
        self.window = {}
        self.delivered = []
        self.illegal = 0
        self.frames = 0
        self.aborted = False
        self.events = []

    def _emit(self, e):
        if self.strict and e[0] in RAISING:
            if e[0] == "drop":
                kind, index = e[2], e[1]
            elif e[0] == "illegal":
                kind, index = "illegal", e[1]
            elif e[0] == "timeout":
                kind, index = "timeout", -1
            else:
                kind, index = e[1], -1
            raise ProtocolError(kind, index, self.events)
        self.events.append(e)

    def _goto(self, s):
        if s != self.state:
            self.state = s
            self.events.append(("state", s))
            if s in ("IDLE", "CLOSED"):
                self.deadline = None

    def _order(self):
        return [(self.expect + d) % 16 for d in range(16)
                if (self.expect + d) % 16 in self.window]

    def _discard(self):
        for s in self._order():
            self.events.append(("discard", s))
        self.window = {}

    def _illegal(self, idx, ty, st):
        self._emit(("illegal", idx, ty, st))
        self.illegal += 1
        if self.illegal >= ILLEGAL_LIMIT:
            self.aborted = True
            self._emit(("abort", "illegal_limit"))
            self._goto("CLOSED")

    def feed(self, idx, ty, seq, tick, pay):
        self.clock += tick & 63
        if self.deadline is not None and self.clock > self.deadline:
            self._emit(("timeout", self.clock))
            self._goto("CLOSED")
            self._discard()
        if ty not in TYPES:
            self._emit(("drop", idx, "bad_type"))
            return
        name = TYPES[ty]
        st = self.state
        if name == "RESET":
            self.events.append(("reset", idx))
            self._goto("IDLE")
            self.deadline = None
            self.expect = 0
            self._discard()
            return
        if name == "HELLO":
            if st != "IDLE":
                return self._illegal(idx, ty, st)
            self.expect = seq % 16
            self.events.append(("hello", idx, self.expect))
            self._goto("OPEN")
            self.deadline = self.clock + TIMEOUT
            return
        if name == "PING":
            if st not in ("OPEN", "DRAINING"):
                return self._illegal(idx, ty, st)
            self.events.append(("ping", idx))
            self.deadline = self.clock + TIMEOUT
            return
        if name == "CLOSE":
            if st == "OPEN":
                self.events.append(("close", idx))
                self._goto("DRAINING")
                order = self._order()
                for s in order:
                    self.delivered.append(self.window.pop(s))
                    self.events.append(("flush", s))
                if order:
                    self.expect = (order[-1] + 1) % 16
                self.deadline = self.clock + TIMEOUT
            elif st == "DRAINING":
                self.events.append(("close", idx))
                self._goto("CLOSED")
            else:
                self._illegal(idx, ty, st)
            return
        # DATA
        if st == "DRAINING":
            self._emit(("drop", idx, "draining"))
            return
        if st != "OPEN":
            return self._illegal(idx, ty, st)
        q = seq % 16
        d = (q - self.expect) % 16
        if d == 0:
            self.delivered.append(pay)
            self.events.append(("deliver", idx, q))
            self.expect = (self.expect + 1) % 16
            while self.expect in self.window:
                self.delivered.append(self.window.pop(self.expect))
                self.events.append(("flush", self.expect))
                self.expect = (self.expect + 1) % 16
            self.deadline = self.clock + TIMEOUT
        elif d < WINDOW:
            if q in self.window:
                self.events.append(("dup", idx, q))
            else:
                self.window[q] = pay
                self.events.append(("buf", idx, q))
                self.deadline = self.clock + TIMEOUT
        elif d >= 16 - WINDOW:
            self.events.append(("dup", idx, q))
        else:
            self._emit(("drop", idx, "out_of_window"))


def replay(transcript, strict=False):
    if type(transcript) is not bytes and type(transcript) is not bytearray:
        raise ProtocolError("bad_transcript", -1, [])
    data = bytes(transcript)
    s = _Session(strict)
    for item in _deframe(data):
        if item[0] == "junk":
            s.events.append(item)
            continue
        s.frames += 1
        if item[0] == "drop":
            s._emit(item)
            continue
        s.feed(item[1], item[2], item[3], item[4], item[5])
        if s.aborted:
            break
    return {
        "state": s.state,
        "clock": s.clock,
        "expect": s.expect,
        "deadline": s.deadline,
        "window": [(q, s.window[q]) for q in s._order()],
        "delivered": list(s.delivered),
        "illegal": s.illegal,
        "frames": s.frames,
        "aborted": s.aborted,
        "events": list(s.events),
    }
