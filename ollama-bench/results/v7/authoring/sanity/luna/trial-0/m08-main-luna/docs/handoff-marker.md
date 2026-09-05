# The handoff marker format

The morning handoff is a list of markers, one per stage that changed overnight, and it is read
by people rather than parsed by anything. That has kept the format stable for three years and
it is worth stating exactly once, here, so it stays that way.

## The format

A marker is the stage's name, then the separator, then the status, and nothing else:

**The separator is a single `=` character.** No spaces around it, no colon, no arrow, no
punctuation of any kind before or after. `pier-4=ready` is a marker; `pier-4 = ready`,
`pier-4: ready` and `pier-4 -> ready` are not.

## Why it is stated here and not in the code

The helper that builds a marker is one line long, and a one-line function is exactly the kind
of thing that gets rewritten by somebody who did not know the format was load-bearing. The
downstream reader is a person with a habit, and the habit is the spec.

## What is not a marker

A marker never carries a timestamp, a stage limit or a window. Those are in the manifest and in
each stage's own document; repeating them in the handoff is how the two drift apart.
