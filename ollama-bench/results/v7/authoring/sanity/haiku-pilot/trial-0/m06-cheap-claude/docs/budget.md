# Budget accounting

## remaining(used, cap)

The budget still available, in whole units, **clamped at zero**. A negative result is never
returned; see the invariant in `README.md`.

    remaining(3, 10)   -> 7
    remaining(10, 10)  -> 0
    remaining(12, 10)  -> 0      not -2

## overspend(used, cap)

How far past the cap the account has gone, clamped at zero.

    overspend(3, 10)   -> 0
    overspend(12, 10)  -> 2

The two functions are deliberately separate: one answers "how much is left", the other answers
"how far over", and a single signed number that tries to answer both is what the first version
did and is what the invariant exists to prevent.
