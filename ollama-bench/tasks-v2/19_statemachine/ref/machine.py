"""Reference solution for 19_statemachine."""


def run(events):
    state = "IDLE"
    stock = 2
    ticks = 0
    out = []

    ENTRY = {"IDLE": [], "ONE": ["1"], "TWO": ["2"], "SERVE": ["D"], "OUT": ["O"]}
    EXIT = {"IDLE": [], "ONE": [], "TWO": ["x"], "SERVE": ["d"], "OUT": []}

    for ev in events:
        if ev == "t":
            ticks += 1
        else:
            ticks = 0

        if ev == "z":
            out.extend(EXIT[state])
            out.append("R")
            state = "IDLE"
            continue

        row = None  # (target, outputs)
        if state == "IDLE" and ev == "c":
            row = ("ONE", ["A"])
        elif state == "ONE" and ev == "c":
            row = ("TWO", ["A"])
        elif state == "ONE" and ev == "t":
            row = ("IDLE", ["F"]) if ticks >= 3 else ("ONE", ["w"])
        elif state == "ONE" and ev == "r":
            row = ("IDLE", ["F"])
        elif state == "TWO" and ev == "s":
            if stock > 0:
                stock -= 1
                row = ("SERVE", [])
            else:
                row = ("OUT", ["F"])
        elif state == "TWO" and ev == "t":
            row = ("IDLE", ["F"]) if ticks >= 2 else ("TWO", ["w"])
        elif state == "TWO" and ev == "r":
            row = ("IDLE", ["F"])
        elif state == "SERVE" and ev in ("c", "s", "r", "t"):
            row = ("IDLE", [])

        if row is None:
            out.append("E")
            continue

        target, emits = row
        if target != state:
            out.extend(EXIT[state])
        out.extend(emits)
        if target != state:
            out.extend(ENTRY[target])
        state = target

    return out