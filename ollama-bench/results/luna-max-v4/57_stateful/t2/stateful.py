"""Replay the small framed stateful protocol described by the task."""


_FLAG = 0x7E
_ESC = 0x7D
_WINDOW = 4
_MODULUS = 16
_TIMEOUT = 20
_MAX_PAYLOAD = 8
_ILLEGAL_LIMIT = 3


class ProtocolError(ValueError):
    """An error detected while replaying a protocol transcript."""

    def __init__(self, kind, index, events):
        self.kind = kind
        self.index = index
        self.events = list(events)
        ValueError.__init__(self, kind)


def replay(transcript, strict=False):
    """Deframe and replay *transcript*, returning the resulting session data."""

    if not isinstance(transcript, (bytes, bytearray)):
        raise ProtocolError("bad_transcript", -1, [])

    events = []

    try:
        # Make a stable immutable snapshot, including for a mutable bytearray.
        raw = bytes(transcript)
        strict_mode = bool(strict)

        state = "IDLE"
        clock = 0
        expect = 0
        deadline = None
        window = {}
        delivered = []
        illegal_count = 0
        frame_count = 0
        aborted = False

        def emit(event):
            name = event[0]
            if strict_mode and name in ("drop", "illegal", "timeout", "abort"):
                if name == "drop":
                    kind = event[2]
                    index = event[1]
                elif name == "illegal":
                    kind = "illegal"
                    index = event[1]
                elif name == "timeout":
                    kind = "timeout"
                    index = -1
                else:
                    kind = "illegal_limit"
                    index = -1
                raise ProtocolError(kind, index, events)
            events.append(event)

        def move_to(new_state):
            nonlocal state, deadline
            changed = state != new_state
            state = new_state
            if changed:
                emit(("state", new_state))
            if new_state in ("IDLE", "CLOSED"):
                deadline = None

        def arm_timer():
            nonlocal deadline
            deadline = clock + _TIMEOUT

        def ordered_window_keys():
            return sorted(window, key=lambda seq: (seq - expect) % _MODULUS)

        def discard_window():
            for seq in ordered_window_keys():
                emit(("discard", seq))
            window.clear()

        def flush_window():
            nonlocal expect
            keys = ordered_window_keys()
            last_seq = None
            for seq in keys:
                payload = window.pop(seq)
                delivered.append(payload)
                emit(("flush", seq))
                last_seq = seq
            if last_seq is not None:
                expect = (last_seq + 1) % _MODULUS

        def illegal_frame(index, message_type):
            nonlocal illegal_count, aborted
            emit(("illegal", index, message_type, state))
            illegal_count += 1
            if illegal_count >= _ILLEGAL_LIMIT:
                emit(("abort", "illegal_limit"))
                aborted = True
                move_to("CLOSED")

        def handle_frame(index, message_type, sequence, tick, payload):
            nonlocal clock, expect, illegal_count, aborted

            # B1: only accepted-by-deframer frames reach this point.
            clock += tick % 64

            # B2: a timeout is processed before the current frame.
            if deadline is not None and clock > deadline:
                emit(("timeout", clock))
                move_to("CLOSED")
                discard_window()

            # B3: type validation precedes all state validation.
            if message_type not in (1, 2, 3, 4, 5):
                emit(("drop", index, "bad_type"))
                return

            # B4: state validation and the non-DATA actions.
            if message_type == 1:  # HELLO
                if state != "IDLE":
                    illegal_frame(index, message_type)
                    return
                expect = sequence % _MODULUS
                emit(("hello", index, expect))
                move_to("OPEN")
                arm_timer()
                return

            if message_type == 5:  # RESET
                emit(("reset", index))
                move_to("IDLE")
                expect = 0
                discard_window()
                return

            if message_type == 3:  # PING
                if state not in ("OPEN", "DRAINING"):
                    illegal_frame(index, message_type)
                    return
                emit(("ping", index))
                arm_timer()
                return

            if message_type == 4:  # CLOSE
                if state == "OPEN":
                    emit(("close", index))
                    move_to("DRAINING")
                    flush_window()
                    arm_timer()
                    return
                if state == "DRAINING":
                    emit(("close", index))
                    move_to("CLOSED")
                    return
                illegal_frame(index, message_type)
                return

            # DATA is the only action that reaches B5.
            if state == "DRAINING":
                emit(("drop", index, "draining"))
                return
            if state != "OPEN":
                illegal_frame(index, message_type)
                return

            sequence_number = sequence % _MODULUS
            distance = (sequence_number - expect) % _MODULUS

            if distance == 0:
                delivered.append(payload)
                emit(("deliver", index, sequence_number))
                expect = (expect + 1) % _MODULUS
                while expect in window:
                    buffered_payload = window.pop(expect)
                    delivered.append(buffered_payload)
                    emit(("flush", expect))
                    expect = (expect + 1) % _MODULUS
                arm_timer()
                return

            if 1 <= distance < _WINDOW:
                if sequence_number in window:
                    emit(("dup", index, sequence_number))
                else:
                    window[sequence_number] = payload
                    emit(("buf", index, sequence_number))
                    arm_timer()
                return

            if 12 <= distance <= 15:
                emit(("dup", index, sequence_number))
                return

            emit(("drop", index, "out_of_window"))

        def read_unescaped(position, size):
            """Read one byte from raw, returning (value, new_position, reason)."""
            if position >= size:
                return None, position, "truncated"

            byte = raw[position]
            if byte == _FLAG:
                # Leave this FLAG for the next candidate frame.
                return None, position, "truncated"

            if byte == _ESC:
                if position + 1 >= size:
                    return None, size, "truncated"
                escaped = raw[position + 1]
                if escaped == _FLAG:
                    # Consume ESC but leave the offending FLAG in place.
                    return None, position + 1, "bad_escape"
                return escaped ^ 0x20, position + 2, None

            return byte, position + 1, None

        position = 0
        raw_size = len(raw)
        while position < raw_size:
            # Hunting phase.
            junk_start = position
            while position < raw_size and raw[position] != _FLAG:
                position += 1
            if position > junk_start:
                emit(("junk", position - junk_start))
            if position >= raw_size:
                break

            # Candidate numbering happens for every consumed starting FLAG.
            position += 1
            frame_index = frame_count
            frame_count += 1

            length, position, reason = read_unescaped(position, raw_size)
            if reason is not None:
                emit(("drop", frame_index, reason))
                continue

            if length > _MAX_PAYLOAD:
                emit(("drop", frame_index, "bad_length"))
                continue

            body = [length]
            body_failed = False
            for _ in range(4 + length):
                value, position, reason = read_unescaped(position, raw_size)
                if reason is not None:
                    emit(("drop", frame_index, reason))
                    body_failed = True
                    break
                body.append(value)
            if body_failed:
                continue

            checksum = 0
            for value in body[:-1]:
                checksum = (checksum + value) & 0xFF
            if body[-1] != checksum:
                emit(("drop", frame_index, "bad_checksum"))
                continue

            message_type = body[1]
            sequence = body[2]
            tick = body[3]
            payload = bytes(body[4:-1])
            handle_frame(frame_index, message_type, sequence, tick, payload)
            if aborted:
                break

        window_result = []
        for sequence in ordered_window_keys():
            window_result.append((sequence, window[sequence]))

        return {
            "state": state,
            "clock": clock,
            "expect": expect,
            "deadline": deadline,
            "window": window_result,
            "delivered": delivered,
            "illegal": illegal_count,
            "frames": frame_count,
            "aborted": aborted,
            "events": events,
        }

    except ProtocolError:
        raise
    except Exception:
        # Keep the public contract intact even if an unexpected Python error is
        # encountered while handling an unusual bytes-like subclass or input.
        raise ProtocolError("bad_transcript", -1, events)


__all__ = ["ProtocolError", "replay"]
