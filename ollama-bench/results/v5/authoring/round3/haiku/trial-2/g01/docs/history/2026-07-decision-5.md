# 2026-07 decision record: signed arithmetic

Decision D-45: contribution is the signed input delta multiplied by the action
multiplier, and accepted occurrence count is independent of contribution.

The policy multipliers are add 1, remove -1, adjust 1, and hold 0. A remove of
a negative delta is therefore positive. A hold with a large or negative delta
still contributes zero. Every accepted change increments occurrences once,
including a zero raw delta and a cancellation that leaves total zero.

Context: the old importer summed raw values, and a later draft used truthiness
to decide whether to update. Both made the output look reasonable for positive
add-only samples while misrepresenting operations replay and review counts.

Consequences: the reducer checks policy membership, not multiplier truthiness,
and never infers acceptance from delta or amount. Totals remain arbitrary-size
integers. Rejected actions have no arithmetic or count effect.

The arithmetic stage has no rounding, absolute-value, clamping, or float
conversion. Its only input from policy is the multiplier and its only output to
the entry state is a signed integer amount plus one occurrence.
