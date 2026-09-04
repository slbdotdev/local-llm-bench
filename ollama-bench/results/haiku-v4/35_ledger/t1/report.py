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

    # Collect all (account, currency) pairs and sort them
    rows = []
    for account, balances in state.items():
        for currency, minor in balances.items():
            rows.append((account, currency, minor))

    # Sort by account, then by currency
    rows.sort(key=lambda x: (x[0], x[1]))

    # Add sorted rows
    for account, currency, minor in rows:
        lines.append(_row(account, currency, format_amount(minor, currency)))

    # Add rule line
    lines.append("-" * WIDTH)

    # Add TOTAL rows in first-appearance order
    currency_totals = totals(state)
    for currency, total in currency_totals.items():
        lines.append(_row("TOTAL", currency, format_amount(total, currency)))

    return "".join(line + "\n" for line in lines)
