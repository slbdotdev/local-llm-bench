Create `stateful.py` in the current directory. It replays a recorded byte stream of framed
protocol messages and reports the resulting session state and an event log.

**Bans.** Standard library only, and you must NOT import or use `struct`, `binascii`, `zlib`,
`hashlib`, or `time` (no `time.time`, `time.monotonic`, `time.sleep` — the clock in this
protocol is purely logical). Write the byte handling and the arithmetic yourself.

The module defines exactly this API:

- `ProtocolError` — an exception class you define; it must subclass `ValueError`. Every
  instance carries three attributes: `.kind` (a `str` from the fixed list below), `.index`
  (an `int`) and `.events` (a `list` of the event tuples emitted before the error).
- `replay(transcript, strict=False)` — `transcript` must be a `bytes` or a `bytearray`; any
  other type (including `str`, `memoryview`, a list of ints, or `None`) is rejected
  immediately, before anything is parsed, by raising `ProtocolError` with
  `.kind == "bad_transcript"`, `.index == -1` and `.events == []`. Otherwise it returns the
  `dict` described in "Return value" below.
  `ProtocolError` is the **only** exception `replay` may ever raise: no `TypeError`,
  `IndexError`, `ValueError`, `KeyError` or `AssertionError` may escape it for any input, and
  no malformed frame may ever be skipped silently.

Constants used throughout: `FLAG = 0x7E`, `ESC = 0x7D`, window size `W = 4`, sequence modulus
`M = 16`, idle timeout `T = 20`, maximum payload length `8`, illegal-message limit `3`.

## Part A — deframing (applied first, to raw bytes)

A frame **body** is the byte sequence `LEN, TYPE, SEQ, TICK, P0 .. P(LEN-1), CK`
(so `5 + LEN` bytes). `CK` is the sum of every body byte *before* it — that is
`(LEN + TYPE + SEQ + TICK + P0 + ... + P(LEN-1)) mod 256`. The checksum is computed on the
**unescaped** body bytes; escaping is applied afterwards, on the way out to the wire.

On the wire, a frame is `FLAG` followed by the escaped body. Escaping replaces a body byte
equal to `FLAG` or `ESC` by the two bytes `ESC, byte XOR 0x20`; all other body bytes go out
unchanged. So `FLAG` never occurs inside an escaped body and can be used to resynchronise.

The parser walks the stream once, alternating between *hunting* and *reading a frame*:

1. **Hunting.** Skip bytes until a `FLAG` is found or the stream ends. If `k >= 1` bytes were
   skipped, append the event `("junk", k)` (one event per contiguous skipped run; nothing is
   appended when `k` is 0). If the stream ended, deframing is over.
2. Consume the `FLAG`. This begins a candidate frame. Candidate frames are numbered
   `idx = 0, 1, 2, ...` in the order their starting `FLAG` is consumed; **every** candidate is
   numbered, including ones that are dropped below.
3. Read unescaped body bytes one at a time. To read one byte, look at the next raw byte `b`:
   - if the stream has ended: the frame is **truncated** — append `("drop", idx, "truncated")`
     and deframing is over.
   - if `b == FLAG`: the frame is **truncated** — append `("drop", idx, "truncated")`; the
     parser does *not* hunt, it resumes at this `FLAG`, which is consumed as the start of the
     next candidate frame (step 2).
   - if `b == ESC`: look at the byte `c` after it. If the stream ends there, the frame is
     **truncated** (as above, and deframing is over). If `c == FLAG`, append
     `("drop", idx, "bad_escape")` and resume at that `FLAG` exactly as in the truncated case.
     Otherwise the unescaped byte is `c XOR 0x20` (this rule is applied for *every* `c`, not
     only for `0x5E` and `0x5D`), and 2 raw bytes are consumed.
   - otherwise the unescaped byte is `b` and 1 raw byte is consumed.
4. The first byte read is `LEN`. If `LEN > 8`, append `("drop", idx, "bad_length")` and go
   back to hunting (step 1) from the current position — the rest of the body is not read and
   is skipped as junk.
5. Otherwise read `4 + LEN` further body bytes with the same rule, giving `TYPE`, `SEQ`,
   `TICK`, the payload, and `CK`.
6. If `CK` does not equal the sum defined above, append `("drop", idx, "bad_checksum")` and go
   back to hunting (step 1) from the current position.
7. Otherwise the frame is **accepted by the deframer** and handed to Part B.

Note the asymmetry: `truncated` and `bad_escape` resume at the `FLAG` they stopped on (no junk
run and no hunting), while `bad_length` and `bad_checksum` resume by hunting.

## Part B — order of checks for one deframed frame

Everything below applies **only** to frames accepted in step 7, and strictly in this order.
When one frame breaks several rules, the first applicable rule decides the outcome and the
later ones are not even evaluated.

B1. **Clock.** `clock += TICK mod 64`. The clock starts at 0 and is *never* advanced by a
frame dropped in Part A, and never decreases or resets.

B2. **Timeout.** If the timer is armed (`deadline` is not `None`) and `clock > deadline`
(strictly greater — `clock == deadline` is *not* a timeout), a timeout fires *before* the
frame is processed: append `("timeout", clock)`, move to state `CLOSED`, and discard the
buffer (see "buffer discard"). The current frame is then still processed, in state `CLOSED`.

B3. **Type.** `TYPE` must be one of 1 `HELLO`, 2 `DATA`, 3 `PING`, 4 `CLOSE`, 5 `RESET`. Any
other value: append `("drop", idx, "bad_type")` and stop processing this frame. This is not an
illegal message and does not touch the timer.

B4. **State.** The session state is one of `"IDLE"` (initial), `"OPEN"`, `"DRAINING"`,
`"CLOSED"`. The full table, where `st` is the state at this point (i.e. after B2):

| TYPE  | IDLE    | OPEN            | DRAINING        | CLOSED  |
|-------|---------|-----------------|-----------------|---------|
| HELLO | accept  | illegal         | illegal         | illegal |
| DATA  | illegal | go to B5        | drop `draining` | illegal |
| PING  | illegal | accept          | accept          | illegal |
| CLOSE | illegal | accept          | accept          | illegal |
| RESET | accept  | accept          | accept          | accept  |

`drop draining` means: append `("drop", idx, "draining")` and stop; it is *not* illegal and
does not touch the timer. **Illegal** means: append `("illegal", idx, TYPE, st)`, increment the
illegal counter, and stop processing the frame; nothing else about the session changes and the
timer is not touched. When the illegal counter reaches 3, the session **aborts**: append
`("abort", "illegal_limit")`, move to state `CLOSED`, set the `aborted` flag, and stop the
whole replay immediately — no further bytes are parsed, so no further events of any kind are
appended. An abort does **not** discard the buffer.

The accepted, non-`DATA` actions are:

- `RESET`: append `("reset", idx)`, move to state `IDLE`, disarm the timer, set `expect = 0`,
  then discard the buffer.
- `HELLO`: set `expect = SEQ mod 16`, append `("hello", idx, expect)`, move to state `OPEN`,
  then arm the timer (`deadline = clock + 20`).
- `PING`: append `("ping", idx)`, then arm the timer.
- `CLOSE` in `OPEN`: append `("close", idx)`, move to state `DRAINING`, then **flush the whole
  buffer**: for every buffered frame, in ascending window order, append its payload to
  `delivered` and append `("flush", seq)`; if at least one frame was flushed, set
  `expect = (seq of the last flushed frame + 1) mod 16`; the buffer is then empty. Finally arm
  the timer.
- `CLOSE` in `DRAINING`: append `("close", idx)` and move to state `CLOSED`.

B5. **Sequence** (only reached by `DATA` in state `OPEN`). Let `q = SEQ mod 16` and
`d = (q - expect) mod 16`, so `d` is in `0..15`.

- `d == 0` — in order: append the payload to `delivered`, append `("deliver", idx, q)`, set
  `expect = (expect + 1) mod 16`, then repeatedly, while a buffered frame with sequence number
  `expect` exists, remove it, append its payload to `delivered`, append `("flush", expect)` and
  advance `expect` by 1 (mod 16). Finally arm the timer.
- `1 <= d <= 3` — inside the window, ahead of `expect`: if a frame with sequence number `q` is
  already buffered, append `("dup", idx, q)` and do nothing else (the timer is **not** touched).
  Otherwise buffer this frame's payload under `q`, append `("buf", idx, q)` and arm the timer.
- `12 <= d <= 15` — the four sequence numbers just *below* `expect`, i.e. a retransmission of
  something already delivered: append `("dup", idx, q)`. Nothing else; the timer is not touched.
- `4 <= d <= 11` — outside the window: append `("drop", idx, "out_of_window")`. Nothing else;
  the timer is not touched.

A `DATA` frame with `LEN == 0` is perfectly legal and delivers the empty payload `b""`.

**Ascending window order** of the buffer means: the buffered sequence numbers sorted by
`(seq - expect) mod 16`, using the value of `expect` at that moment.

**Buffer discard** means: for every buffered frame in ascending window order append
`("discard", seq)`, then empty the buffer. It is used by `RESET` and by a timeout, and by
nothing else.

**The timer.** `deadline` starts as `None` (disarmed). "Arm the timer" sets
`deadline = clock + 20`, using the clock value *after* B1. Moving into state `IDLE` or
`CLOSED` always sets `deadline = None`. The timer is only ever armed or reset by the actions
listed above; in particular `bad_type`, `draining`, `illegal`, `dup` and `out_of_window` frames
never touch it. Timeouts are only ever checked at B2 — never at the end of the stream.

**State events.** Whenever the state actually changes value, append `("state", NEW)`
immediately after the action's own event and before any flush/discard events. If an action
"moves to" a state that is already the current state, nothing is appended.

## Strict mode

`replay(transcript, True)` computes exactly the same replay, but the moment it is about to
append its **first** event whose name is `"drop"`, `"illegal"`, `"timeout"` or `"abort"`, it
instead raises `ProtocolError` and appends nothing. `"junk"`, `"state"`, `"hello"`, `"ping"`,
`"close"`, `"reset"`, `"deliver"`, `"buf"`, `"flush"`, `"dup"` and `"discard"` events never
raise, so a transcript containing only those replays to completion in strict mode too.

On that raise:

- `.kind` is the drop reason for a `"drop"` event — one of `"truncated"`, `"bad_escape"`,
  `"bad_length"`, `"bad_checksum"`, `"bad_type"`, `"draining"`, `"out_of_window"` — or the
  literal string `"illegal"` for an `"illegal"` event, `"timeout"` for a `"timeout"` event, and
  `"illegal_limit"` for an `"abort"` event. (An `"abort"` is always preceded by an `"illegal"`
  in the same frame, so in strict mode `"illegal_limit"` is in fact unreachable; the rule is
  stated for completeness.)
- `.index` is the candidate frame index `idx` for a `"drop"` or `"illegal"` event, and `-1` for
  a `"timeout"` event.
- `.events` is the list of events emitted **before** the raising one, the raising event itself
  excluded.

Because the raise happens at the first such event, strict mode is a direct probe of the
precedence order of Part A and Part B: a frame that is simultaneously badly checksummed, out of
window and illegal in the current state must report `"bad_checksum"`, and one that is both an
unknown `TYPE` and illegal in the current state must report `"bad_type"`.

## Return value

`replay` returns a dict with exactly these ten keys and no others. The Python types are part
of the specification: every event is a `tuple` (not a list), every payload is `bytes` (not
`str`, not `bytearray`), `"aborted"` is a real `bool` (not `0`/`1`), and the four counters are
plain `int`s.

- `"state"` — final state name, one of the four strings.
- `"clock"` — final clock, an `int`.
- `"expect"` — final expected sequence number, an `int` in `0..15`.
- `"deadline"` — `None` or an `int`.
- `"window"` — a `list` of `(seq, payload)` **tuples**, one per buffered frame, in ascending
  window order computed with the final value of `expect` (never a dict, never sorted by raw
  `seq`). `seq` is an `int`, `payload` is `bytes`. Empty list if nothing is buffered.
- `"delivered"` — a `list` of `bytes`, one entry per delivered `DATA` payload, in delivery
  order.
- `"illegal"` — `int`, number of illegal messages seen.
- `"frames"` — `int`, number of candidate frames (Part A step 2), including dropped ones.
- `"aborted"` — `bool`.
- `"events"` — the `list` of event tuples described above, in order.

## Examples

Writing `F(ty, seq, tick, payload)` for a correctly framed and checksummed frame:

- `replay(F(1,0,1,b"") + F(2,0,2,b"ab") + F(2,1,2,b"c") + F(4,0,1,b""))`, whose bytes are
  `7E 00 01 00 01 02 7E 02 02 00 02 61 62 C9 7E 01 02 01 02 63 69 7E 00 04 00 01 05`, gives
  state `"DRAINING"`, `clock` 6, `expect` 2, `deadline` 26, `window` `[]`, `delivered`
  `[b"ab", b"c"]`, `illegal` 0, `frames` 4, `aborted` `False`, and events
  `[("hello",0,0), ("state","OPEN"), ("deliver",1,0), ("deliver",2,1), ("close",3), ("state","DRAINING")]`.
- `replay(F(1,3,0,b"") + F(2,4,1,b"x") + F(2,3,1,b"w"))` gives state `"OPEN"`, `clock` 2,
  `expect` 5, `deadline` 22, `window` `[]`, `delivered` `[b"w", b"x"]`, `frames` 3, and events
  `[("hello",0,3), ("state","OPEN"), ("buf",1,4), ("deliver",2,3), ("flush",4)]`.
  (That third frame's checksum byte is `0x7E`, so on the wire it is escaped to `7D 5E`.)
- `replay(b"\x01\x02" + F(2,0,0,b"z") with its checksum byte replaced by 0 + F(1,0,0,b""))`
  gives state `"OPEN"`, `clock` 0, `expect` 0, `deadline` 20, `delivered` `[]`, `frames` 2, and
  events `[("junk",2), ("drop",0,"bad_checksum"), ("hello",1,0), ("state","OPEN")]`.
- `replay(F(2,0,0,b"q") + F(9,0,0,b"") + F(1,0,0,b""))` gives state `"OPEN"`, `clock` 0,
  `expect` 0, `deadline` 20, `illegal` 1, `frames` 3, and events
  `[("illegal",0,2,"IDLE"), ("drop",1,"bad_type"), ("hello",2,0), ("state","OPEN")]`.

- `replay(F(1,0,1,b"") + F(2,0,2,b"ab") + F(2,1,2,b"c") + F(4,0,1,b""), True)` returns the
  same dict as the first example (no drop/illegal/timeout/abort event occurs), while
  `replay(F(2,0,0,b"q") + F(9,0,0,b"") + F(1,0,0,b""), True)` raises `ProtocolError` with
  `.kind == "illegal"`, `.index == 0` and `.events == []`.

Write a few quick checks of your own and run them with `python`, then reply "done".
