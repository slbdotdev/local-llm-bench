"""Applies parsed ledger entries to account balances."""
from model import LedgerError, parse_entry


def apply_entries(lines):
    """Apply an iterable of ledger lines and return the balance state."""
    state = {}
    previous = None
    for raw in lines:
        text = raw.strip()
        if not text or text.startswith("#"):
            continue
        entry = parse_entry(text)
        if previous is not None and entry.date < previous:
            raise LedgerError("entry out of order: %s after %s" % (entry.date, previous))
        previous = entry.date
        account = state.setdefault(entry.account, {})
        if entry.kind == "DEP":
            account[entry.currency] = account.get(entry.currency, 0) + entry.amount
        elif entry.kind == "WDR":
            account[entry.currency] = account.get(entry.currency, 0) - entry.amount
        elif entry.kind == "XFR":
            available = account.get(entry.currency, 0)
            if available < entry.amount:
                raise LedgerError("overdraft on %s %s" % (entry.account, entry.currency))
            account[entry.currency] = available - entry.amount
            target = state.setdefault(entry.dest, {})
            target[entry.currency] = target.get(entry.currency, 0) + entry.amount
        else:
            raise LedgerError("unsupported kind: %r" % (entry.kind,))
    return state


def balance(state, account, currency):
    """The balance of one account in one currency, in minor units."""
    return state.get(account, {}).get(currency, 0)


def totals(state):
    """Sum every account's balance per currency, in first-appearance order."""
    out = {}
    for balances in state.values():
        for currency, minor in balances.items():
            out[currency] = out.get(currency, 0) + minor
    return out
