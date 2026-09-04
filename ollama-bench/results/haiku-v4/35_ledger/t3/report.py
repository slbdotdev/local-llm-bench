"""Fixed-width text rendering of a balance state."""
from model import format_amount
from engine import totals

ACCOUNT_W = 16
CUR_W = 3
AMOUNT_W = 12
WIDTH = ACCOUNT_W + CUR_W + AMOUNT_W + 2


def _row(account, currency, amount):
    return account.ljust(ACCOUNT_W) + " " + currency.ljust(CUR_W) + " " + amount.rjust(AMOUNT_W)


def render(state):
    """Render the balance state as a fixed-width report."""
    lines = [_row("ACCOUNT", "CUR", "AMOUNT"), "-" * WIDTH]

    # Collect and sort all (account, currency) pairs
    rows = []
    for account in state:
        for currency in state[account]:
            rows.append((account, currency, state[account][currency]))
    rows.sort()

    # Add sorted data rows
    for account, currency, minor in rows:
        lines.append(_row(account, currency, format_amount(minor, currency)))

    # Add separator and totals
    lines.append("-" * WIDTH)
    tot = totals(state)
    for currency in tot:
        lines.append(_row("TOTAL", currency, format_amount(tot[currency], currency)))

    return "".join(line + "\n" for line in lines)
