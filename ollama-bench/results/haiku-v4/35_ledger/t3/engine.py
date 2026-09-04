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
            # Check for overdraft
            current_balance = account.get(entry.currency, 0)
            if current_balance < entry.amount:
                raise LedgerError("insufficient funds for transfer")
            # Update source account (before destination)
            account[entry.currency] = current_balance - entry.amount
            # Update destination account
            dest_account = state.setdefault(entry.dest, {})
            dest_account[entry.currency] = dest_account.get(entry.currency, 0) + entry.amount
        else:
            raise LedgerError("unsupported kind: %r" % (entry.kind,))
    return state


def balance(state, account, currency):
    """The balance of one account in one currency, in minor units."""
    return state.get(account, {}).get(currency, 0)


def totals(state):
    """Sum balances by currency in first-appearance order."""
    result = {}
    for account in state:
        for currency in state[account]:
            if currency not in result:
                result[currency] = 0
            result[currency] += state[account][currency]
    return result
