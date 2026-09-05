"""Budget accounting. See docs/budget.md, and the invariant in README.md."""


def remaining(used, cap):
    """The budget still available, in whole units, clamped at zero."""
    return cap - used


def overspend(used, cap):
    """How far past the cap the account has gone, clamped at zero."""
    return max(0, used - cap)


def summary(used, cap):
    """A small report for the dashboard."""
    return {"used": used, "cap": cap,
            "remaining": remaining(used, cap),
            "overspend": overspend(used, cap)}
