"""Stateful protocol replay and session management."""

# Constants
FLAG = 0x7E
ESC = 0x7D
W = 4          # window size
M = 16         # sequence modulus
T = 20         # idle timeout
MAX_PAYLOAD = 8
ILLEGAL_LIMIT = 3

# Message types
HELLO = 1
DATA = 2
PING = 3
CLOSE = 4
RESET = 5

VALID_TYPES = {HELLO, DATA, PING, CLOSE, RESET}


class ProtocolError(ValueError):
    """Protocol error with kind, index, and events emitted before the error."""
    def __init__(self, kind, index, events):
        self.kind = kind
        self.index = index
        self.events = events
        super().__init__(f"ProtocolError: {kind} at index {index}")


def replay(transcript, strict=False):
    """Replay a recorded byte stream of framed protocol messages.

    Args:
        transcript: bytes or bytearray to parse
        strict: if True, raise on first drop/illegal/timeout/abort event

    Returns:
        dict with state, clock, expect, deadline, window, delivered, illegal, frames, aborted, events

    Raises:
        ProtocolError: if transcript is wrong type or (in strict mode) on first problematic event
    """
    # Validate input type first
    if not isinstance(transcript, (bytes, bytearray)):
        raise ProtocolError("bad_transcript", -1, [])

    # Initialize session state
    state = "IDLE"
    clock = 0
    expect = 0
    deadline = None
    events = []
    delivered = []
    buffer = {}  # seq -> payload
    illegal_count = 0
    frame_count = 0
    aborted = False

    # Deframing phase (Part A)
    pos = 0
    while pos < len(transcript):
        # Hunt for FLAG
        junk_start = pos
        while pos < len(transcript) and transcript[pos] != FLAG:
            pos += 1

        if pos > junk_start:
            junk_event = ("junk", pos - junk_start)
            events.append(junk_event)
            if strict and junk_event[0] == "drop":
                raise ProtocolError(junk_event[2], junk_event[1], events[:-1])

        if pos >= len(transcript):
            break

        # Consume FLAG and begin frame
        pos += 1
        idx = frame_count
        frame_count += 1

        # Read body bytes with unescaping
        body = bytearray()
        drop_reason = None

        while len(body) < 5 or len(body) < 5 + body[0]:
            if pos >= len(transcript):
                drop_reason = "truncated"
                break

            b = transcript[pos]
            pos += 1

            if b == FLAG:
                drop_reason = "truncated"
                pos -= 1  # Back up so this FLAG starts next frame
                break
            elif b == ESC:
                if pos >= len(transcript):
                    drop_reason = "truncated"
                    break
                c = transcript[pos]
                pos += 1
                if c == FLAG:
                    drop_reason = "bad_escape"
                    pos -= 1  # Back up to the FLAG
                    break
                else:
                    body.append(c ^ 0x20)
            else:
                body.append(b)

        if drop_reason:
            event = ("drop", idx, drop_reason)
            events.append(event)
            if strict and drop_reason in ("truncated", "bad_escape", "bad_length", "bad_checksum"):
                raise ProtocolError(drop_reason, idx, events[:-1])
            continue

        # Parse LEN from first body byte
        length = body[0]
        if length > MAX_PAYLOAD:
            event = ("drop", idx, "bad_length")
            events.append(event)
            if strict:
                raise ProtocolError("bad_length", idx, events[:-1])
            continue

        # Check we have all body bytes (LEN, TYPE, SEQ, TICK, payload, CK)
        if len(body) != 5 + length:
            event = ("drop", idx, "truncated")
            events.append(event)
            if strict:
                raise ProtocolError("truncated", idx, events[:-1])
            continue

        # Validate checksum
        expected_ck = sum(body[:-1]) & 0xFF
        if body[-1] != expected_ck:
            event = ("drop", idx, "bad_checksum")
            events.append(event)
            if strict:
                raise ProtocolError("bad_checksum", idx, events[:-1])
            continue

        # Frame is valid, extract fields
        length = body[0]
        frame_type = body[1]
        seq = body[2]
        tick = body[3]
        payload = bytes(body[4:4+length])

        # Part B: Process the frame
        # B1: Clock advancement
        clock = (clock + tick) % 64

        # B2: Timeout check
        if deadline is not None and clock > deadline:
            if strict:
                raise ProtocolError("timeout", -1, events)
            events.append(("timeout", clock))
            old_state = state
            state = "CLOSED"
            if state != old_state:
                events.append(("state", state))
            deadline = None
            # Discard buffer
            for seq_buf in sorted(buffer.keys(), key=lambda s: (s - expect) % 16):
                events.append(("discard", seq_buf))
            buffer.clear()

        # B3: Type validation
        if frame_type not in VALID_TYPES:
            event = ("drop", idx, "bad_type")
            events.append(event)
            if strict:
                raise ProtocolError("bad_type", idx, events[:-1])
            continue

        # B4: State machine
        # Determine action based on frame type and current state
        action = None

        if frame_type == HELLO:
            if state == "IDLE":
                action = "accept"
            else:
                action = "illegal"
        elif frame_type == DATA:
            if state == "OPEN":
                action = "b5"
            elif state == "DRAINING":
                action = "drop_draining"
            else:
                action = "illegal"
        elif frame_type == PING:
            if state in ("OPEN", "DRAINING"):
                action = "accept"
            else:
                action = "illegal"
        elif frame_type == CLOSE:
            if state in ("OPEN", "DRAINING"):
                action = "accept"
            else:
                action = "illegal"
        elif frame_type == RESET:
            action = "accept"

        # Handle illegal messages
        if action == "illegal":
            event = ("illegal", idx, frame_type, state)
            events.append(event)
            if strict:
                raise ProtocolError("illegal", idx, events[:-1])
            illegal_count += 1
            if illegal_count >= ILLEGAL_LIMIT:
                event = ("abort", "illegal_limit")
                events.append(event)
                aborted = True
                state = "CLOSED"
                break
            continue

        # Handle DATA in DRAINING
        if action == "drop_draining":
            event = ("drop", idx, "draining")
            events.append(event)
            if strict:
                raise ProtocolError("draining", idx, events[:-1])
            continue

        # Process accepted messages
        if action == "accept":
            if frame_type == RESET:
                events.append(("reset", idx))
                old_state = state
                state = "IDLE"
                if state != old_state:
                    events.append(("state", state))
                deadline = None
                expect = 0
                # Discard buffer
                for seq_buf in sorted(buffer.keys(), key=lambda s: (s - expect) % 16):
                    events.append(("discard", seq_buf))
                buffer.clear()

            elif frame_type == HELLO:
                expect = seq % 16
                events.append(("hello", idx, expect))
                old_state = state
                state = "OPEN"
                if state != old_state:
                    events.append(("state", state))
                deadline = clock + T

            elif frame_type == PING:
                events.append(("ping", idx))
                deadline = clock + T

            elif frame_type == CLOSE:
                if state == "OPEN":
                    events.append(("close", idx))
                    old_state = state
                    state = "DRAINING"
                    if state != old_state:
                        events.append(("state", state))
                    # Flush buffer in ascending window order
                    sorted_seqs = sorted(buffer.keys(), key=lambda s: (s - expect) % 16)
                    for seq_buf in sorted_seqs:
                        delivered.append(buffer[seq_buf])
                        events.append(("flush", seq_buf))
                    if sorted_seqs:
                        expect = (sorted_seqs[-1] + 1) % 16
                    buffer.clear()
                    deadline = clock + T
                elif state == "DRAINING":
                    events.append(("close", idx))
                    old_state = state
                    state = "CLOSED"
                    if state != old_state:
                        events.append(("state", state))

        elif action == "b5":
            # B5: Sequence processing
            q = seq % 16
            d = (q - expect) % 16

            if d == 0:
                # In order
                delivered.append(payload)
                events.append(("deliver", idx, q))
                expect = (expect + 1) % 16
                # Flush buffered frames
                while expect in buffer:
                    delivered.append(buffer[expect])
                    events.append(("flush", expect))
                    del buffer[expect]
                    expect = (expect + 1) % 16
                deadline = clock + T

            elif 1 <= d <= 3:
                # Inside window, ahead
                if q in buffer:
                    events.append(("dup", idx, q))
                else:
                    buffer[q] = payload
                    events.append(("buf", idx, q))
                    deadline = clock + T

            elif 12 <= d <= 15:
                # Retransmission
                events.append(("dup", idx, q))

            else:  # 4 <= d <= 11
                # Outside window
                event = ("drop", idx, "out_of_window")
                events.append(event)
                if strict:
                    raise ProtocolError("out_of_window", idx, events[:-1])

    # Compute final window list in ascending window order
    final_window = []
    if buffer:
        for seq_buf in sorted(buffer.keys(), key=lambda s: (s - expect) % 16):
            final_window.append((seq_buf, buffer[seq_buf]))

    return {
        "state": state,
        "clock": clock,
        "expect": expect,
        "deadline": deadline,
        "window": final_window,
        "delivered": delivered,
        "illegal": illegal_count,
        "frames": frame_count,
        "aborted": aborted,
        "events": events,
    }
