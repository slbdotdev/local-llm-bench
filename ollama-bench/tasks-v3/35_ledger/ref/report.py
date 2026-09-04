"""Fixed-width text rendering of a balance state."""
from engine import totals
from model import format_amount

ACCOUNT_W = 16
CUR_W = 3
AMOUNT_W = 12
WIDTH = ACCOUNT_W + CUR_W + AMOUNT_W + 2


def _row(account, currency, amount):
    return account.ljust(ACCOUNT_W) + " " + currency.ljust(CUR_W) + " " + amount.rjust(AMOUNT_W)


def render(state):
    """Render the balance state as a fixed-width report."""
    lines = [_row("ACCOUNT", "CUR", "AMOUNT"), "-" * WIDTH]
    rows = []
    for account, balances in state.items():
        for currency, minor in balances.items():
            rows.append((account, currency, minor))
    for account, currency, minor in sorted(rows, key=lambda r: (r[0], r[1])):
        lines.append(_row(account, currency, format_amount(minor, currency)))
    lines.append("-" * WIDTH)
    for currency, minor in totals(state).items():
        lines.append(_row("TOTAL", currency, format_amount(minor, currency)))
    return "".join(line + "\n" for line in lines)
