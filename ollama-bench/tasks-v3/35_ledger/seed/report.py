"""Fixed-width text rendering of a balance state."""
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
    for account, balances in state.items():
        for currency, minor in balances.items():
            lines.append(_row(account, currency, format_amount(minor, currency)))
    return "".join(line + "\n" for line in lines)
