"""Protocol replay system for stateful framed message processing."""

# Constants
FLAG = 0x7E
ESC = 0x7D
W = 4  # window size
M = 16  # sequence modulus
T = 20  # idle timeout
ILLEGAL_LIMIT = 3


class ProtocolError(ValueError):
    """Exception for protocol errors during replay."""

    def __init__(self, kind, index, events):
        self.kind = kind
        self.index = index
        self.events = events
        super().__init__(f"Protocol error: {kind} at index {index}")


def replay(transcript, strict=False):
    """Replay a recorded byte stream of framed protocol messages.

    Args:
        transcript: bytes or bytearray containing the message stream
        strict: if True, raise ProtocolError on first drop/illegal/timeout/abort event

    Returns:
        dict with keys: state, clock, expect, deadline, window, delivered, illegal, frames, aborted, events

    Raises:
        ProtocolError: if input validation fails or strict mode encounters errors
    """

    # Validate transcript type
    if not isinstance(transcript, (bytes, bytearray)):
        raise ProtocolError("bad_transcript", -1, [])

    events = []
    state = "IDLE"
    clock = 0
    expect = 0
    deadline = None
    buffer = {}  # seq -> payload
    delivered = []
    illegal_count = 0
    aborted = False
    frame_count = 0

    # Part A: Deframing
    i = 0
    while i < len(transcript):
        # Hunting phase: skip until FLAG
        junk_start = i
        while i < len(transcript) and transcript[i] != FLAG:
            i += 1

        if i > junk_start:
            events.append(("junk", i - junk_start))
            # Junk doesn't trigger strict mode

        if i >= len(transcript):
            break

        # Found FLAG, start reading frame
        frame_idx = frame_count
        frame_count += 1
        i += 1  # consume FLAG

        # Read body bytes (unescaped)
        body = []

        # Read LEN
        result = read_next_byte(transcript, i)
        if result is None:
            # Truncated or bad_escape
            if i < len(transcript) and transcript[i] == FLAG:
                events_before = events[:]
                events.append(("drop", frame_idx, "truncated"))
                if strict:
                    raise ProtocolError("truncated", frame_idx, events_before)
                continue
            elif i < len(transcript) and transcript[i] == ESC:
                events_before = events[:]
                events.append(("drop", frame_idx, "bad_escape"))
                if strict:
                    raise ProtocolError("bad_escape", frame_idx, events_before)
                i += 2  # Skip ESC and next byte
                if i < len(transcript) and transcript[i] == FLAG:
                    i -= 1  # Back to FLAG
                continue
            else:
                events_before = events[:]
                events.append(("drop", frame_idx, "truncated"))
                if strict:
                    raise ProtocolError("truncated", frame_idx, events_before)
                break

        len_byte, bytes_consumed = result
        i += bytes_consumed
        body.append(len_byte)

        if len_byte > 8:
            events_before = events[:]
            events.append(("drop", frame_idx, "bad_length"))
            if strict:
                raise ProtocolError("bad_length", frame_idx, events_before)
            # Skip junk until next FLAG
            while i < len(transcript) and transcript[i] != FLAG:
                i += 1
            continue

        # Read TYPE, SEQ, TICK, payload, checksum
        for _ in range(4 + len_byte):
            result = read_next_byte(transcript, i)
            if result is None:
                # Truncated or bad_escape
                if i < len(transcript) and transcript[i] == FLAG:
                    events_before = events[:]
                    events.append(("drop", frame_idx, "truncated"))
                    if strict:
                        raise ProtocolError("truncated", frame_idx, events_before)
                    break
                elif i < len(transcript) and transcript[i] == ESC:
                    if i + 1 < len(transcript) and transcript[i + 1] == FLAG:
                        events_before = events[:]
                        events.append(("drop", frame_idx, "bad_escape"))
                        if strict:
                            raise ProtocolError("bad_escape", frame_idx, events_before)
                        break
                    else:
                        events_before = events[:]
                        events.append(("drop", frame_idx, "truncated"))
                        if strict:
                            raise ProtocolError("truncated", frame_idx, events_before)
                        break
                else:
                    events_before = events[:]
                    events.append(("drop", frame_idx, "truncated"))
                    if strict:
                        raise ProtocolError("truncated", frame_idx, events_before)
                    break
            else:
                byte_val, bytes_consumed = result
                body.append(byte_val)
                i += bytes_consumed
        else:
            # All bytes read successfully, check checksum
            if len(body) != 5 + len_byte:
                continue

            checksum = sum(body[:-1]) & 0xFF
            if body[-1] != checksum:
                events_before = events[:]
                events.append(("drop", frame_idx, "bad_checksum"))
                if strict:
                    raise ProtocolError("bad_checksum", frame_idx, events_before)
                # Resume hunting
                while i < len(transcript) and transcript[i] != FLAG:
                    i += 1
                continue

            # Frame accepted, process in Part B
            try:
                (
                    state,
                    clock,
                    expect,
                    deadline,
                    buffer,
                    delivered,
                    illegal_count,
                    aborted,
                ) = process_frame(
                    body,
                    frame_idx,
                    events,
                    state,
                    clock,
                    expect,
                    deadline,
                    buffer,
                    delivered,
                    illegal_count,
                    aborted,
                    strict,
                )
            except ProtocolError:
                raise

            if aborted:
                break

    # Build window in ascending window order
    window = []
    if buffer:
        # Sort by (seq - expect) mod 16
        seqs = sorted(
            buffer.keys(),
            key=lambda seq: (seq - expect) % 16,
        )
        for seq in seqs:
            window.append((seq, buffer[seq]))

    return {
        "state": state,
        "clock": clock,
        "expect": expect,
        "deadline": deadline,
        "window": window,
        "delivered": delivered,
        "illegal": illegal_count,
        "frames": frame_count,
        "aborted": aborted,
        "events": events,
    }


def read_next_byte(transcript, i):
    """Read next unescaped byte from transcript.

    Returns:
        (byte_value, bytes_consumed) tuple or None if truncated/error
    """
    if i >= len(transcript):
        return None

    b = transcript[i]

    if b == FLAG:
        return None  # Frame boundary

    if b == ESC:
        if i + 1 >= len(transcript):
            return None  # Truncated
        c = transcript[i + 1]
        if c == FLAG:
            return None  # Bad escape
        return (c ^ 0x20, 2)

    return (b, 1)


def process_frame(
    body,
    frame_idx,
    events,
    state,
    clock,
    expect,
    deadline,
    buffer,
    delivered,
    illegal_count,
    aborted,
    strict,
):
    """Process a deframed frame in Part B.

    Returns tuple of (state, clock, expect, deadline, buffer, delivered, illegal_count, aborted)
    """

    len_byte = body[0]
    ty = body[1]
    seq = body[2]
    tick = body[3]
    payload = bytes(body[4 : 4 + len_byte])

    # B1: Clock advance
    clock = (clock + (tick % 64)) % 64

    # B2: Timeout check
    if deadline is not None and clock > deadline:
        events_before = events[:]
        events.append(("timeout", clock))
        if strict:
            raise ProtocolError("timeout", -1, events_before)
        old_state = state
        state = "CLOSED"
        deadline = None
        # Discard buffer
        for seq_d in sorted(buffer.keys(), key=lambda s: (s - expect) % 16):
            events.append(("discard", seq_d))
        buffer.clear()
        if state != old_state:
            events.append(("state", state))

    # B3: Type check
    if ty not in (1, 2, 3, 4, 5):
        events_before = events[:]
        events.append(("drop", frame_idx, "bad_type"))
        if strict:
            raise ProtocolError("bad_type", frame_idx, events_before)
        return (state, clock, expect, deadline, buffer, delivered, illegal_count, aborted)

    # B4: State check - determine if frame is legal in current state
    # First handle the special case of DATA in DRAINING (which is drop draining, not illegal)
    if ty == 2 and state == "DRAINING":
        events_before = events[:]
        events.append(("drop", frame_idx, "draining"))
        if strict:
            raise ProtocolError("draining", frame_idx, events_before)
        return (state, clock, expect, deadline, buffer, delivered, illegal_count, aborted)

    # Check if frame is legal in current state
    legal_matrix = {
        "IDLE": {1, 5},  # HELLO, RESET
        "OPEN": {1, 2, 3, 4, 5},  # all
        "DRAINING": {3, 4, 5},  # PING, CLOSE, RESET
        "CLOSED": {5},  # RESET
    }

    if ty not in legal_matrix[state]:
        # Illegal message
        events_before = events[:]
        events.append(("illegal", frame_idx, ty, state))
        if strict:
            raise ProtocolError("illegal", frame_idx, events_before)
        illegal_count += 1
        if illegal_count >= ILLEGAL_LIMIT:
            events_before = events[:]
            events.append(("abort", "illegal_limit"))
            if strict:
                raise ProtocolError("illegal_limit", frame_idx, events_before)
            aborted = True
            old_state = state
            state = "CLOSED"
            if state != old_state:
                events.append(("state", state))
        return (state, clock, expect, deadline, buffer, delivered, illegal_count, aborted)

    # Handle accepted frames
    old_state = state

    if ty == 5:  # RESET
        events.append(("reset", frame_idx))
        state = "IDLE"
        deadline = None
        expect = 0
        # Discard buffer
        for seq_d in sorted(buffer.keys(), key=lambda s: (s - expect) % 16):
            events.append(("discard", seq_d))
        buffer.clear()
        if state != old_state:
            events.append(("state", state))

    elif ty == 1:  # HELLO
        expect = seq % 16
        events.append(("hello", frame_idx, expect))
        old_state = state
        state = "OPEN"
        deadline = clock + T
        if state != old_state:
            events.append(("state", state))

    elif ty == 3:  # PING
        events.append(("ping", frame_idx))
        deadline = clock + T

    elif ty == 4:  # CLOSE
        if state == "OPEN":
            events.append(("close", frame_idx))
            # Flush buffer
            for seq_f in sorted(buffer.keys(), key=lambda s: (s - expect) % 16):
                delivered.append(buffer[seq_f])
                events.append(("flush", seq_f))
            if buffer:
                # Update expect to seq of last flushed + 1
                last_seq = max(buffer.keys())
                expect = (last_seq + 1) % 16
            buffer.clear()
            old_state = state
            state = "DRAINING"
            deadline = clock + T
            if state != old_state:
                events.append(("state", state))
        elif state == "DRAINING":
            events.append(("close", frame_idx))
            old_state = state
            state = "CLOSED"
            if state != old_state:
                events.append(("state", state))

    elif ty == 2:  # DATA (in OPEN state)
        q = seq % 16
        d = (q - expect) % 16

        if d == 0:  # In order
            delivered.append(payload)
            events.append(("deliver", frame_idx, q))
            expect = (expect + 1) % 16
            # Flush buffered frames
            while expect in buffer:
                delivered.append(buffer[expect])
                events.append(("flush", expect))
                del buffer[expect]
                expect = (expect + 1) % 16
            deadline = clock + T

        elif 1 <= d <= 3:  # Inside window, ahead
            if q in buffer:
                events.append(("dup", frame_idx, q))
            else:
                buffer[q] = payload
                events.append(("buf", frame_idx, q))
                deadline = clock + T

        elif 12 <= d <= 15:  # Retransmission of old data
            events.append(("dup", frame_idx, q))

        elif 4 <= d <= 11:  # Outside window
            events_before = events[:]
            events.append(("drop", frame_idx, "out_of_window"))
            if strict:
                raise ProtocolError("out_of_window", frame_idx, events_before)

    return (state, clock, expect, deadline, buffer, delivered, illegal_count, aborted)
