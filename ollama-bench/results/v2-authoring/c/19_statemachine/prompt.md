Create `machine.py` in the current directory with a function:

```python
def run(events: list[str]) -> list[str]
```

`run` simulates a vending-machine controller as a finite state machine. It processes the
input events one at a time, left to right, and returns the flat list of all outputs emitted,
in emission order. Each call starts a fresh machine: state `IDLE`, `stock = 2`, `ticks = 0`.
The function must be deterministic and pure: do not import `time`, `threading`, or `random`,
and never use wall-clock time or threads — the only "clock" is the event counter described
below.

Events are the strings `"c"` (coin), `"s"` (select), `"r"` (refund), `"t"` (tick), `"z"`
(reset). Any other string is treated as an invalid event (rule 3 below).

## Internal counters

- `stock`: an integer, initially 2.
- `ticks`: an integer, initially 0.

## Global rules, applied to every event in this order

1. Tick counting: if the event is `"t"`, first set `ticks = ticks + 1`. For ANY other event
   (including `"z"` and unknown strings) set `ticks = 0`. This happens before guards are
   evaluated, so guards see the updated value. Tick counting happens even if the event is
   then rejected as invalid.
2. Reset: if the event is `"z"`, emit the exit outputs of the current state (see the
   action table below), then emit `"R"`, then enter `IDLE`. `stock` is unchanged. Note
   `IDLE` has no exit or entry outputs, so resetting from `IDLE` emits only `["R"]`.
3. Otherwise, look up the current state's rows for this event in the transition table
   below and scan them top to bottom; take the FIRST row whose guard holds (this is the
   priority rule). Then:
   - If the taken row's target state differs from the current state, emit, in this exact
     order: (a) the exit outputs of the current state, (b) the row's outputs, (c) the entry
     outputs of the target state. If the row's target equals the current state (a
     self-loop), emit only the row's outputs — no exit or entry outputs.
   - If no row matches (events with no rows at all, and any event string other than
     `"c"`, `"s"`, `"r"`, `"t"`, `"z"`), emit exactly `["E"]` and stay in the current state.

## Transition table (rows in priority order per state)

- `IDLE`
  - `c` -> `ONE`, outputs `["A"]`
  - no rows for `s`, `r`, `t` (so they are invalid there)
- `ONE`
  - `c` -> `TWO`, outputs `["A"]`
  - `t` -> `IDLE`, outputs `["F"]`, guard: `ticks >= 3`
  - `t` -> `ONE`, outputs `["w"]` (always holds; only reached when `ticks < 3`)
  - `r` -> `IDLE`, outputs `["F"]`
  - `s` has no row (invalid)
- `TWO`
  - `s` -> `SERVE`, outputs `[]`, guard: `stock > 0`; taking this row also performs
    `stock = stock - 1`
  - `s` -> `OUT`, outputs `["F"]` (always holds; only reached when `stock == 0`)
  - `t` -> `IDLE`, outputs `["F"]`, guard: `ticks >= 2`
  - `t` -> `TWO`, outputs `["w"]` (always holds; only reached when `ticks < 2`)
  - `r` -> `IDLE`, outputs `["F"]`
  - `c` has no row (invalid)
- `SERVE`
  - `c` -> `IDLE`, outputs `[]`
  - `s` -> `IDLE`, outputs `[]`
  - `r` -> `IDLE`, outputs `[]`
  - `t` -> `IDLE`, outputs `[]`
- `OUT`
  - no rows at all: every event is invalid there

## Entry / exit actions

| State  | Entry outputs | Exit outputs |
|--------|---------------|--------------|
| `IDLE` | (none)        | (none)       |
| `ONE`  | `["1"]`       | (none)       |
| `TWO`  | `["2"]`       | `["x"]`      |
| `SERVE`| `["D"]`       | `["d"]`      |
| `OUT`  | `["O"]`       | (none)       |

Entry and exit outputs are emitted only when the state actually changes (including via
rule 2, which always emits the current state's exit outputs). Entry outputs of `IDLE` are
none, and exit outputs of `IDLE` are none.

## Worked examples

```python
run([]) == []
run(["c"]) == ["A", "1"]
run(["c", "c", "s"]) == ["A", "1", "A", "2", "x", "D"]
run(["c", "c", "s", "c"]) == ["A", "1", "A", "2", "x", "D", "d"]
run(["c", "t", "t", "t"]) == ["A", "1", "w", "w", "F"]
run(["c", "c", "c"]) == ["A", "1", "A", "2", "E"]
run(["c", "c", "r"]) == ["A", "1", "A", "2", "x", "F"]
run(["c", "c", "s", "r", "c", "c", "s"]) == ["A", "1", "A", "2", "x", "D", "d", "A", "1", "A", "2", "x", "D"]
run(["c", "c", "s", "r", "c", "c", "s", "r", "c", "c", "s"]) ==
    ["A", "1", "A", "2", "x", "D", "d", "A", "1", "A", "2", "x", "D", "d", "A", "1", "A", "2", "x", "F", "O"]
run(["c", "c", "z"]) == ["A", "1", "A", "2", "x", "R"]
run(["z"]) == ["R"]
run(["t", "t", "c", "t", "t"]) == ["E", "E", "A", "1", "w", "w"]
```

Explanation of two of them: in `["c","t","t","t"]` the three ticks are counted while in
`ONE`; at the third tick `ticks` reaches 3, so the timeout row fires (refund `F` to `IDLE`,
and `ONE` has no exit outputs). In `["c","c","s",...]` the select leaves `TWO` (exit output
`x`) and enters `SERVE` (entry output `D`); the next event then closes the hatch (`d`, the
exit action of `SERVE`) returning to `IDLE`.

Standard library only; no third-party packages; no network.

Write a few quick checks of your own and run them with `python`, then reply "done".