"""
Replay a recorded byte stream of framed protocol messages.
"""

class ProtocolError(ValueError):
    """Protocol parsing error with kind, index, and events attributes."""
    def __init__(self, kind, index, events):
        self.kind = kind
        self.index = index
        self.events = events
        super().__init__(f"ProtocolError: {kind} at index {index}")


def replay(transcript, strict=False):
    """
    Replay a recorded byte stream of framed protocol messages.

    Args:
        transcript: bytes or bytearray containing the protocol messages
        strict: if True, raise on first drop/illegal/timeout/abort event

    Returns:
        dict with keys: state, clock, expect, deadline, window, delivered,
                       illegal, frames, aborted, events

    Raises:
        ProtocolError: on protocol violations or bad input
    """

    # Constants
    FLAG = 0x7E
    ESC = 0x7D
    W = 4
    M = 16
    T = 20
    MAX_PAYLOAD = 8
    ILLEGAL_LIMIT = 3

    # Validate transcript type
    if not isinstance(transcript, (bytes, bytearray)):
        raise ProtocolError("bad_transcript", -1, [])

    # Initialize state
    state = "IDLE"
    clock = 0
    expect = 0
    deadline = None
    buffer = {}  # seq -> payload
    delivered = []
    illegal_count = 0
    frame_count = 0
    aborted = False
    events = []

    # Track if we're in strict mode and have seen error event
    seen_error = False

    pos = 0  # Current position in transcript

    def add_event(event):
        nonlocal seen_error
        if strict and not seen_error:
            # Check if this is an error event
            if isinstance(event, tuple) and len(event) > 0:
                event_name = event[0]
                if event_name in ("drop", "illegal", "timeout", "abort"):
                    seen_error = True
                    raise ProtocolError(
                        event[1] if event_name == "drop" else
                        "illegal" if event_name == "illegal" else
                        "timeout" if event_name == "timeout" else
                        "illegal_limit",
                        event[2] if event_name == "drop" else
                        event[1] if event_name in ("illegal", "timeout") else
                        -1,
                        events[:]
                    )
        events.append(event)

    def read_byte():
        """Read one unescaped byte from the stream."""
        nonlocal pos
        if pos >= len(transcript):
            return None, False  # (value, success)

        b = transcript[pos]
        if b == 0xFF:  # Ensure it's an int
            b = 0xFF
        pos += 1

        # Handle escaping
        if b == ESC:
            if pos >= len(transcript):
                return None, False  # Truncated
            c = transcript[pos]
            pos += 1
            if c == FLAG:
                return None, False  # Bad escape (FLAG after ESC)
            return c ^ 0x20, True

        return b, True

    def find_next_flag():
        """Find next FLAG in stream, return junk count."""
        nonlocal pos
        junk_count = 0
        while pos < len(transcript):
            if transcript[pos] == FLAG:
                break
            junk_count += 1
            pos += 1
        return junk_count

    # Part A: Deframing
    while pos < len(transcript):
        # Hunt for FLAG
        junk_count = find_next_flag()
        if junk_count > 0:
            add_event(("junk", junk_count))

        if pos >= len(transcript):
            break

        # Found FLAG, consume it
        pos += 1
        idx = frame_count
        frame_count += 1

        # Try to read frame body: LEN, TYPE, SEQ, TICK, payload, CK
        body_bytes = []

        # Read LEN
        len_byte, success = read_byte()
        if not success:
            # Truncated (when reading LEN, any failure is truncation, never bad_escape)
            add_event(("drop", idx, "truncated"))
            break

        frame_len = len_byte
        body_bytes.append(len_byte)

        # Validate payload length
        if frame_len > MAX_PAYLOAD:
            add_event(("drop", idx, "bad_length"))
            # Resume hunting from current position
            continue

        # Read TYPE, SEQ, TICK, payload, CK
        remaining = 4 + frame_len
        for _ in range(remaining):
            byte_val, success = read_byte()
            if not success:
                # Check if this is a bad escape (ESC followed by FLAG)
                # This can only happen if we've read at least TYPE, SEQ, TICK (i.e., we're in payload/checksum area)
                # body_bytes at this point has at least LEN, TYPE, SEQ, TICK (4+ elements)
                if len(body_bytes) >= 4 and pos > 0 and pos < len(transcript) + 1 and transcript[pos - 1] == FLAG:
                    # Bad escape in payload/checksum
                    add_event(("drop", idx, "bad_escape"))
                    pos -= 1
                    break
                else:
                    # Truncated
                    add_event(("drop", idx, "truncated"))
                    # End of stream
                    break
            body_bytes.append(byte_val)

        if len(body_bytes) != 5 + frame_len:
            continue

        # Verify checksum
        checksum = sum(body_bytes[:-1]) & 0xFF
        if checksum != body_bytes[-1]:
            add_event(("drop", idx, "bad_checksum"))
            continue

        # Frame accepted by deframer
        frame_type = body_bytes[1]
        frame_seq = body_bytes[2]
        frame_tick = body_bytes[3]
        frame_payload = bytes(body_bytes[4:-1])

        # Part B: Process frame

        # B1: Clock advance
        clock = (clock + frame_tick) & 0x3F  # tick mod 64

        # B2: Timeout check
        if deadline is not None and clock > deadline:
            add_event(("timeout", clock))
            old_state = state
            state = "CLOSED"
            deadline = None
            # Discard buffer
            for seq in sorted(buffer.keys(), key=lambda s: (s - expect) % M):
                add_event(("discard", s))
            buffer.clear()
            if state != old_state:
                add_event(("state", state))

        # B3: Type check
        if frame_type not in (1, 2, 3, 4, 5):
            add_event(("drop", idx, "bad_type"))
            continue

        # B4: State check
        type_names = {1: "HELLO", 2: "DATA", 3: "PING", 4: "CLOSE", 5: "RESET"}
        type_name = type_names[frame_type]

        # State transition table
        state_table = {
            ("HELLO", "IDLE"): "accept",
            ("HELLO", "OPEN"): "illegal",
            ("HELLO", "DRAINING"): "illegal",
            ("HELLO", "CLOSED"): "illegal",
            ("DATA", "IDLE"): "illegal",
            ("DATA", "OPEN"): "B5",  # Go to B5
            ("DATA", "DRAINING"): "drop_draining",
            ("DATA", "CLOSED"): "illegal",
            ("PING", "IDLE"): "illegal",
            ("PING", "OPEN"): "accept",
            ("PING", "DRAINING"): "accept",
            ("PING", "CLOSED"): "illegal",
            ("CLOSE", "IDLE"): "illegal",
            ("CLOSE", "OPEN"): "accept",
            ("CLOSE", "DRAINING"): "accept",
            ("CLOSE", "CLOSED"): "illegal",
            ("RESET", "IDLE"): "accept",
            ("RESET", "OPEN"): "accept",
            ("RESET", "DRAINING"): "accept",
            ("RESET", "CLOSED"): "accept",
        }

        action = state_table.get((type_name, state), "illegal")

        if action == "illegal":
            add_event(("illegal", idx, frame_type, state))
            illegal_count += 1
            if illegal_count >= ILLEGAL_LIMIT:
                add_event(("abort", "illegal_limit"))
                aborted = True
                break
            continue

        if action == "drop_draining":
            add_event(("drop", idx, "draining"))
            continue

        # B5: DATA frame sequence handling
        if action == "B5":
            q = frame_seq % M
            d = (q - expect) % M

            if d == 0:
                # In order
                delivered.append(frame_payload)
                add_event(("deliver", idx, q))
                expect = (expect + 1) % M

                # Flush buffered frames
                while expect in buffer:
                    payload = buffer.pop(expect)
                    delivered.append(payload)
                    add_event(("flush", expect))
                    expect = (expect + 1) % M

                deadline = clock + T
            elif 1 <= d <= 3:
                # Inside window, ahead of expect
                if q in buffer:
                    add_event(("dup", idx, q))
                else:
                    buffer[q] = frame_payload
                    add_event(("buf", idx, q))
                    deadline = clock + T
            elif 12 <= d <= 15:
                # Retransmission (already delivered)
                add_event(("dup", idx, q))
            else:  # 4 <= d <= 11
                # Out of window
                add_event(("drop", idx, "out_of_window"))
            continue

        # Handle RESET
        if action == "accept" and frame_type == 5:  # RESET
            add_event(("reset", idx))
            old_state = state
            state = "IDLE"
            deadline = None
            expect = 0
            # Discard buffer
            for seq in sorted(buffer.keys(), key=lambda s: (s - expect) % M):
                add_event(("discard", seq))
            buffer.clear()
            if state != old_state:
                add_event(("state", state))
            continue

        # Handle HELLO
        if action == "accept" and frame_type == 1:  # HELLO
            expect = frame_seq % M
            add_event(("hello", idx, expect))
            old_state = state
            state = "OPEN"
            deadline = clock + T
            if state != old_state:
                add_event(("state", state))
            continue

        # Handle PING
        if action == "accept" and frame_type == 3:  # PING
            add_event(("ping", idx))
            deadline = clock + T
            continue

        # Handle CLOSE
        if action == "accept" and frame_type == 4:  # CLOSE
            if state == "OPEN":
                add_event(("close", idx))
                old_state = state
                state = "DRAINING"

                # Flush buffer
                last_flushed = None
                for seq in sorted(buffer.keys(), key=lambda s: (s - expect) % M):
                    payload = buffer.pop(seq)
                    delivered.append(payload)
                    add_event(("flush", seq))
                    last_flushed = seq

                # If at least one frame was flushed, update expect
                if last_flushed is not None:
                    expect = (last_flushed + 1) % M

                deadline = clock + T
                if state != old_state:
                    add_event(("state", state))
            else:  # DRAINING
                add_event(("close", idx))
                old_state = state
                state = "CLOSED"
                deadline = None
                if state != old_state:
                    add_event(("state", state))
            continue

    # Build window list (ascending window order)
    window = []
    for seq in sorted(buffer.keys(), key=lambda s: (s - expect) % M):
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
