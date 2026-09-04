class ProtocolError(ValueError):
    """An error raised while replaying a protocol transcript."""

    def __init__(self, kind, index, events):
        self.kind = kind
        self.index = index
        self.events = list(events)
        ValueError.__init__(self, kind)


def replay(transcript, strict=False):
    """Deframe and replay a recorded protocol transcript."""

    if not isinstance(transcript, (bytes, bytearray)):
        raise ProtocolError("bad_transcript", -1, [])

    events = []

    try:
        wire = bytes(transcript)
        try:
            strict_mode = bool(strict)
        except Exception:
            strict_mode = False

        flag = 0x7E
        esc = 0x7D
        window_size = 4
        modulus = 16
        timeout = 20
        max_length = 8

        state = "IDLE"
        clock = 0
        expect = 0
        deadline = None
        buffered = {}
        delivered = []
        illegal_count = 0
        frame_count = 0
        aborted = False
        position = 0

        def emit(event):
            name = event[0]
            if strict_mode and name in ("drop", "illegal", "timeout", "abort"):
                if name == "drop":
                    error_kind = event[2]
                    error_index = event[1]
                elif name == "illegal":
                    error_kind = "illegal"
                    error_index = event[1]
                elif name == "timeout":
                    error_kind = "timeout"
                    error_index = -1
                else:
                    error_kind = "illegal_limit"
                    error_index = -1
                raise ProtocolError(error_kind, error_index, events)
            events.append(event)

        def move_state(new_state):
            nonlocal state, deadline
            if state != new_state:
                state = new_state
                emit(("state", new_state))
            if new_state == "IDLE" or new_state == "CLOSED":
                deadline = None

        def window_order():
            return sorted(buffered, key=lambda seq: (seq - expect) % modulus)

        def discard_buffer():
            for seq in window_order():
                emit(("discard", seq))
            buffered.clear()

        def flush_buffer():
            nonlocal expect
            last_sequence = None
            for seq in window_order():
                delivered.append(buffered[seq])
                emit(("flush", seq))
                last_sequence = seq
            buffered.clear()
            if last_sequence is not None:
                expect = (last_sequence + 1) % modulus

        def read_unescaped():
            nonlocal position
            if position >= len(wire):
                return None, "truncated"

            value = wire[position]
            if value == flag:
                return None, "truncated"
            if value == esc:
                position += 1
                if position >= len(wire):
                    return None, "truncated"
                escaped = wire[position]
                if escaped == flag:
                    return None, "bad_escape"
                position += 1
                return escaped ^ 0x20, None

            position += 1
            return value, None

        while position < len(wire) and not aborted:
            skipped = 0
            while position < len(wire) and wire[position] != flag:
                position += 1
                skipped += 1
            if skipped:
                emit(("junk", skipped))
            if position >= len(wire):
                break

            position += 1
            index = frame_count
            frame_count += 1

            length, reason = read_unescaped()
            if reason is not None:
                emit(("drop", index, reason))
                if position >= len(wire):
                    break
                continue

            if length > max_length:
                emit(("drop", index, "bad_length"))
                continue

            body = [length]
            failed = False
            ended = False
            for _ in range(4 + length):
                value, reason = read_unescaped()
                if reason is not None:
                    emit(("drop", index, reason))
                    failed = True
                    if position >= len(wire):
                        ended = True
                    break
                body.append(value)

            if failed:
                if ended:
                    break
                continue

            checksum = 0
            for value in body[:-1]:
                checksum = (checksum + value) & 0xFF
            if body[-1] != checksum:
                emit(("drop", index, "bad_checksum"))
                continue

            frame_type = body[1]
            sequence = body[2]
            tick = body[3]
            payload = bytes(body[4:-1])

            clock += tick % 64
            if deadline is not None and clock > deadline:
                emit(("timeout", clock))
                move_state("CLOSED")
                discard_buffer()

            if frame_type not in (1, 2, 3, 4, 5):
                emit(("drop", index, "bad_type"))
                continue

            if frame_type == 5:
                emit(("reset", index))
                move_state("IDLE")
                expect = 0
                deadline = None
                discard_buffer()
                continue

            if frame_type == 1:
                if state != "IDLE":
                    illegal_count += 1
                    emit(("illegal", index, frame_type, state))
                    if illegal_count >= 3:
                        emit(("abort", "illegal_limit"))
                        aborted = True
                        move_state("CLOSED")
                    continue

                expect = sequence % modulus
                emit(("hello", index, expect))
                move_state("OPEN")
                deadline = clock + timeout
                continue

            if frame_type == 2:
                if state == "IDLE" or state == "CLOSED":
                    illegal_count += 1
                    emit(("illegal", index, frame_type, state))
                    if illegal_count >= 3:
                        emit(("abort", "illegal_limit"))
                        aborted = True
                        move_state("CLOSED")
                    continue
                if state == "DRAINING":
                    emit(("drop", index, "draining"))
                    continue

                sequence_number = sequence % modulus
                distance = (sequence_number - expect) % modulus
                if distance == 0:
                    delivered.append(payload)
                    emit(("deliver", index, sequence_number))
                    expect = (expect + 1) % modulus
                    while expect in buffered:
                        delivered.append(buffered.pop(expect))
                        emit(("flush", expect))
                        expect = (expect + 1) % modulus
                    deadline = clock + timeout
                elif 1 <= distance <= window_size - 1:
                    if sequence_number in buffered:
                        emit(("dup", index, sequence_number))
                    else:
                        buffered[sequence_number] = payload
                        emit(("buf", index, sequence_number))
                        deadline = clock + timeout
                elif 12 <= distance <= 15:
                    emit(("dup", index, sequence_number))
                else:
                    emit(("drop", index, "out_of_window"))
                continue

            if frame_type == 3:
                if state != "OPEN" and state != "DRAINING":
                    illegal_count += 1
                    emit(("illegal", index, frame_type, state))
                    if illegal_count >= 3:
                        emit(("abort", "illegal_limit"))
                        aborted = True
                        move_state("CLOSED")
                    continue

                emit(("ping", index))
                deadline = clock + timeout
                continue

            if state == "OPEN":
                emit(("close", index))
                move_state("DRAINING")
                flush_buffer()
                deadline = clock + timeout
            elif state == "DRAINING":
                emit(("close", index))
                move_state("CLOSED")
            else:
                illegal_count += 1
                emit(("illegal", index, frame_type, state))
                if illegal_count >= 3:
                    emit(("abort", "illegal_limit"))
                    aborted = True
                    move_state("CLOSED")

        return {
            "state": state,
            "clock": clock,
            "expect": expect,
            "deadline": deadline,
            "window": [(seq, buffered[seq]) for seq in window_order()],
            "delivered": delivered,
            "illegal": illegal_count,
            "frames": frame_count,
            "aborted": bool(aborted),
            "events": events,
        }
    except ProtocolError:
        raise
    except Exception:
        raise ProtocolError("bad_transcript", -1, events) from None
